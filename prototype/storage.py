"""Private files and password-encrypted local state; never print their contents."""

from __future__ import annotations

import base64
import datetime as dt
import ipaddress
import json
import os
import stat
import tempfile
from pathlib import Path

from cryptography import x509
from cryptography.fernet import Fernet, InvalidToken
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives.kdf.scrypt import Scrypt
from cryptography.x509.oid import NameOID

ROOT = Path(__file__).resolve().parents[1]
LIVE_DIR = ROOT / ".local-bank"
DEMO_DIR = ROOT / ".local-bank-demo"


class LocalError(Exception):
    """An intentionally sanitized error safe to show locally."""


def private_dir(path: Path) -> None:
    if path.is_symlink():
        raise LocalError("Datamappen kan ikke være en symbolsk lenke.")
    path.mkdir(mode=0o700, parents=True, exist_ok=True)
    info = path.stat()
    if info.st_uid != os.getuid() or stat.S_IMODE(info.st_mode) != 0o700:
        raise LocalError("Datamappen må eies av deg og ha rettigheter 700.")


def write_private(path: Path, data: bytes) -> None:
    private_dir(path.parent)
    fd, temporary = tempfile.mkstemp(prefix=".write-", dir=path.parent)
    try:
        with os.fdopen(fd, "wb") as stream:
            stream.write(data)
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temporary, path)
    finally:
        if os.path.exists(temporary):
            os.unlink(temporary)


def read_private(path: Path) -> bytes:
    fd = os.open(path, os.O_RDONLY | os.O_NOFOLLOW)
    with os.fdopen(fd, "rb") as stream:
        info = os.fstat(stream.fileno())
        if info.st_uid != os.getuid() or stat.S_IMODE(info.st_mode) & 0o077:
            raise LocalError("En lokal datafil har for vide rettigheter; bruk 600.")
        if info.st_size > 25_000_000:
            raise LocalError("Den lokale datafilen er større enn prototypens grense.")
        return stream.read()


def certificate(key, common_name: str, localhost: bool = False) -> bytes:
    now = dt.datetime.now(dt.timezone.utc)
    name = x509.Name([x509.NameAttribute(NameOID.COMMON_NAME, common_name)])
    builder = (x509.CertificateBuilder().subject_name(name).issuer_name(name)
               .public_key(key.public_key()).serial_number(x509.random_serial_number())
               .not_valid_before(now - dt.timedelta(minutes=5))
               .not_valid_after(now + dt.timedelta(days=365)))
    if localhost:
        builder = builder.add_extension(x509.SubjectAlternativeName([
            x509.DNSName("localhost"), x509.IPAddress(ipaddress.ip_address("127.0.0.1"))
        ]), critical=False)
    return builder.sign(key, hashes.SHA256()).public_bytes(serialization.Encoding.PEM)


def initialize(path: Path, password: str) -> None:
    if len(password) < 12:
        raise LocalError("Bruk en lokal passfrase på minst 12 tegn.")
    private_dir(path)
    if any(path.iterdir()):
        raise LocalError("Oppsettet finnes allerede; ingen filer ble overskrevet.")
    key = rsa.generate_private_key(public_exponent=65537, key_size=4096)
    write_private(path / "application-key.pem", key.private_bytes(
        serialization.Encoding.PEM, serialization.PrivateFormat.PKCS8,
        serialization.BestAvailableEncryption(password.encode())))
    write_private(path / "application-certificate.pem", certificate(key, "OpenHousehold personal prototype"))
    # The TLS key also stays encrypted; the same passphrase unlocks the process.
    tls = rsa.generate_private_key(public_exponent=65537, key_size=2048)
    write_private(path / "localhost-key.pem", tls.private_bytes(
        serialization.Encoding.PEM, serialization.PrivateFormat.PKCS8,
        serialization.BestAvailableEncryption(password.encode())))
    write_private(path / "localhost-certificate.pem", certificate(tls, "localhost", True))
    write_private(path / "salt", os.urandom(16))


class Vault:
    def __init__(self, path: Path, password: str):
        private_dir(path)
        self.path = path
        try:
            self.key = serialization.load_pem_private_key(
                read_private(path / "application-key.pem"), password.encode())
            derived = Scrypt(salt=read_private(path / "salt"), length=32, n=2**17, r=8, p=1).derive(password.encode())
            self.cipher = Fernet(base64.urlsafe_b64encode(derived))
        except (ValueError, TypeError, FileNotFoundError):
            raise LocalError("Feil passfrase eller ufullstendig lokalt oppsett.") from None

    def read(self) -> dict:
        path = self.path / "state.enc"
        if not path.exists():
            return {"session": None, "snapshot": None, "revocation_pending": None}
        try:
            return json.loads(self.cipher.decrypt(read_private(path)))
        except (InvalidToken, ValueError):
            raise LocalError("Kan ikke åpne kryptert tilstand; ingen data ble endret.") from None

    def save(self, data: dict) -> None:
        payload = json.dumps(data, ensure_ascii=False, allow_nan=False).encode()
        if len(payload) > 20_000_000:
            raise LocalError("Resultatet er for stort; velg færre kontoer eller et kortere tidsrom.")
        write_private(self.path / "state.enc", self.cipher.encrypt(payload))
