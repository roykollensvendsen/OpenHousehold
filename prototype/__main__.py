"""Command line for the local prototype: init, import-key, serve, demo."""

from __future__ import annotations

import argparse
import getpass
import sys
import uuid
from pathlib import Path

from . import app, demo, provider, storage
from .storage import DEMO_DIR, LIVE_DIR, LocalError, Vault

DEMO_PASSPHRASE = "openhousehold-demo"


def passphrase(confirm: bool = False) -> str:
    value = getpass.getpass("Lokal passfrase: ")
    if confirm and value != getpass.getpass("Gjenta passfrasen: "):
        raise LocalError("Passfrasene var ikke like.")
    return value


def application_id(directory: Path, given: str | None) -> str:
    path = directory / "application-id"
    if given:
        try:
            uuid.UUID(given)
        except ValueError:
            raise LocalError("Applikasjons-ID-en er ikke en gyldig UUID.") from None
        storage.write_private(path, given.encode())
        return given
    if not path.exists():
        raise LocalError("Mangler applikasjons-ID. Kjør på nytt med --app-id <UUID> etter registrering.")
    return storage.read_private(path).decode().strip()


def command_init(args) -> None:
    storage.initialize(LIVE_DIR, passphrase(confirm=True))
    print(f"""Oppsettet ligger i {LIVE_DIR} (kun lesbart for deg).

Neste steg, som bare du kan gjøre, i kontrollpanelet hos Enable Banking:
  1. Logg inn og registrer en applikasjon i Production-miljøet.
  2. Registrer {provider.CALLBACK} som returadresse.
  3. Velg tjenesten AIS (kontoinformasjon) alene, uten betalingsrettigheter.
  4. Aktiver applikasjonen ved å lenke dine egne bankkontoer.

Om nøkkelen, velg én av to veier:
  A. La nettleseren lage nøkkelen. Den lastes ned som <applikasjons-ID>.pem.
     Kjør så: uv run python -m prototype import-key ~/Downloads/<applikasjons-ID>.pem
  B. Oppgi vår egen offentlige nøkkel ved registrering:
     {LIVE_DIR / 'application-public-key.pem'}
     Kjør så: uv run python -m prototype serve --app-id <applikasjons-ID>""")


def command_import(args) -> None:
    source = Path(args.key).expanduser()
    if not source.is_file():
        raise LocalError("Fant ikke nøkkelfilen.")
    secret = passphrase()
    storage.adopt(LIVE_DIR, source, secret)
    identifier = application_id(LIVE_DIR, args.app_id or source.stem)
    Vault(LIVE_DIR, secret)  # Fail here rather than mid-flow if the passphrase is wrong.
    print(f"""Nøkkelen er lagret kryptert i {LIVE_DIR} for applikasjon {identifier}.
Slett nedlastingen: shred -u {source}
Kjør så: uv run python -m prototype serve""")


def command_serve(args) -> None:
    secret = passphrase()
    vault = Vault(LIVE_DIR, secret)
    identifier = application_id(LIVE_DIR, args.app_id)
    client = provider.EnableBanking(identifier, vault.key)
    console = app.Console(vault, client)
    console.application = client.check_application()
    console.banks = client.banks()
    app.serve(console, LIVE_DIR, secret, args.port)


def command_demo(args) -> None:
    if not (DEMO_DIR / "salt").exists():
        storage.initialize(DEMO_DIR, DEMO_PASSPHRASE)
    vault = Vault(DEMO_DIR, DEMO_PASSPHRASE)
    console = app.Console(vault, demo.DemoBank(f"https://localhost:{args.port}/callback"))
    console.application = console.provider.check_application()
    console.banks = console.provider.banks()
    print("Demomodus: alle tall er oppdiktede, og ingen bank kontaktes.")
    app.serve(console, DEMO_DIR, DEMO_PASSPHRASE, args.port)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="prototype", description=__doc__)
    subcommands = parser.add_subparsers(dest="command", required=True)
    subcommands.add_parser("init", help="lag lokale nøkler og sertifikater").set_defaults(run=command_init)
    adopt = subcommands.add_parser("import-key", help="ta i bruk nøkkelen kontrollpanelet lagde")
    adopt.add_argument("key", help="nedlastet <applikasjons-ID>.pem")
    adopt.add_argument("--app-id", help="brukes hvis filnavnet ikke er applikasjons-ID-en")
    adopt.set_defaults(run=command_import)
    serve = subcommands.add_parser("serve", help="kjør mot banken med lesetilgang")
    serve.add_argument("--app-id", help="applikasjons-ID fra leverandørens kontrollpanel")
    serve.set_defaults(run=command_serve)
    subcommands.add_parser("demo", help="kjør hele flyten med syntetiske data").set_defaults(run=command_demo)
    for name in ("serve", "demo"):
        subcommands.choices[name].add_argument("--port", type=int, default=app.PORT)
    args = parser.parse_args(argv)
    try:
        args.run(args)
    except LocalError as error:
        print(str(error), file=sys.stderr)
        return 1
    except KeyboardInterrupt:
        return 130
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
