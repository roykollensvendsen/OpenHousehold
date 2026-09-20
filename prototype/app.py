"""Local read-only page on 127.0.0.1; it renders bank data and never forwards it."""

from __future__ import annotations

import html
import http.server
import secrets
import ssl
import threading
import urllib.parse
from pathlib import Path

from .storage import LocalError, Vault, read_private

HOST = "127.0.0.1"
PORT = 8767
BODY_LIMIT = 100_000
STYLE = """
body{font:16px/1.5 system-ui,sans-serif;margin:0 auto;padding:2rem;max-width:56rem;color:#1a1a1a}
h1{font-size:1.4rem} h2{font-size:1.1rem;margin-top:2rem}
.note{background:#f4f4f5;border-left:4px solid #9a9aa2;padding:.75rem 1rem;margin:1rem 0}
.warn{border-left-color:#b45309;background:#fff7ed}
table{border-collapse:collapse;width:100%;margin:.5rem 0} th,td{border-bottom:1px solid #ddd;padding:.35rem .5rem;text-align:left}
td.num{text-align:right;font-variant-numeric:tabular-nums;white-space:nowrap}
.debit{color:#991b1b} button{font:inherit;padding:.4rem .9rem;margin-right:.5rem}
fieldset{border:1px solid #ddd;margin:1rem 0} label{display:block;padding:.15rem 0}
"""


def esc(value) -> str:
    return html.escape("" if value is None else str(value), quote=True)


def mask(value: str) -> str:
    text = str(value or "")
    return "••• " + text[-4:] if len(text) > 4 else text


def label(account: dict) -> str:
    identification = account.get("account_id") or {}
    name = account.get("name") or account.get("product") or "Konto"
    return f"{name} ({mask(identification.get('iban') or account.get('uid', ''))})"


def money(amount: dict, debit: bool = False) -> str:
    if not isinstance(amount, dict):
        return ""
    value = str(amount.get("amount", ""))
    return f"{'-' if debit and not value.startswith('-') else ''}{value} {amount.get('currency', '')}"


def render(view: dict) -> str:
    out = ["<!doctype html><html lang='no'><head><meta charset='utf-8'>",
           "<title>OpenHousehold – lokal bankprototype</title>",
           f"<style>{STYLE}</style></head><body>",
           "<h1>OpenHousehold – lokal bankprototype</h1>",
           "<p class='note'>Kun lesetilgang, kun på denne maskinen. Dette er en "
           "gjennomførbarhetstest, ikke husholdningsproduktet.</p>"]
    if view.get("message"):
        out.append(f"<p class='note warn'>{esc(view['message'])}</p>")
    token = esc(view["csrf"])

    application = view.get("application") or {}
    out.append("<h2>Tilgang</h2><table>"
               f"<tr><th>Applikasjon</th><td>{esc(application.get('name', '–'))}</td></tr>"
               f"<tr><th>Miljø</th><td>{esc(application.get('environment', '–'))}</td></tr>"
               f"<tr><th>Tjenester</th><td>{esc(', '.join(application.get('services', [])) or '–')}</td></tr>"
               f"<tr><th>Bankøkt</th><td>{esc(view['session_status'])}</td></tr></table>")

    if not view.get("session"):
        out.append("<h2>Koble til banken</h2><form method='post' action='/connect'>"
                   f"<input type='hidden' name='csrf' value='{token}'><fieldset>")
        for index, bank in enumerate(view.get("banks", [])):
            checked = " checked" if index == 0 else ""
            out.append(f"<label><input type='radio' name='bank' value='{esc(bank['name'])}'{checked}> "
                       f"{esc(bank['name'])}</label>")
        if not view.get("banks"):
            out.append("<p>Fant ingen aktuell bankrute. Kontroller land og tjeneste i kontrollpanelet.</p>")
        out.append("</fieldset><button type='submit'>Logg inn i banken</button></form>")
    else:
        accounts = view["session"].get("accounts", [])
        out.append("<h2>Hent kontodata</h2><form method='post' action='/fetch'>"
                   f"<input type='hidden' name='csrf' value='{token}'><fieldset>")
        for account in accounts:
            out.append(f"<label><input type='checkbox' name='account' value='{esc(account.get('uid'))}' checked> "
                       f"{esc(label(account))}</label>")
        out.append("</fieldset><label>Antall dager historikk: "
                   "<input type='number' name='days' value='30' min='1' max='90'></label>"
                   "<button type='submit'>Hent</button></form>"
                   f"<form method='post' action='/disconnect'><input type='hidden' name='csrf' value='{token}'>"
                   "<button type='submit'>Koble fra banken</button></form>")

    snapshot = view.get("snapshot")
    if snapshot:
        out.append(f"<h2>Data hentet {esc(snapshot.get('retrieved_at', ''))}</h2>"
                   f"<p>Periode {esc(snapshot.get('requested_from'))} – {esc(snapshot.get('requested_to'))}, "
                   f"kilde {esc(snapshot.get('provider'))}.</p>")
        for entry in snapshot.get("accounts", []):
            out.append(f"<h3>{esc(label(entry.get('account', {})))}</h3><table>")
            for balance in (entry.get("balances") or {}).get("balances", []):
                out.append(f"<tr><th>{esc(balance.get('name') or balance.get('balance_type'))}</th>"
                           f"<td class='num'>{esc(money(balance.get('balance_amount')))}</td></tr>")
            out.append("</table>")
            transactions = entry.get("transactions") or []
            out.append(f"<table><tr><th>Dato</th><th>Tekst</th><th>Beløp</th></tr>")
            for transaction in transactions:
                debit = transaction.get("credit_debit_indicator") == "DBIT"
                text = " ".join(transaction.get("remittance_information") or []) or "–"
                out.append(f"<tr><td>{esc(transaction.get('booking_date') or transaction.get('value_date'))}</td>"
                           f"<td>{esc(text)}</td>"
                           f"<td class='num{" debit" if debit else ""}'>"
                           f"{esc(money(transaction.get('transaction_amount'), debit))}</td></tr>")
            if not transactions:
                out.append("<tr><td colspan='3'>Ingen bokførte transaksjoner i perioden.</td></tr>")
            out.append("</table>")
        out.append(f"<form method='post' action='/forget'><input type='hidden' name='csrf' value='{token}'>"
                   "<button type='submit'>Slett de lokale dataene</button></form>")
    out.append("</body></html>")
    return "".join(out)


class Console:
    """Process-local state; the bank code and CSRF token are never written to disk."""

    def __init__(self, vault: Vault, provider):
        self.vault = vault
        self.provider = provider
        self.lock = threading.Lock()
        self.csrf = secrets.token_urlsafe(32)
        self.pending: tuple[str, dict] | None = None
        self.message = ""
        self.application: dict = {}
        self.banks: list[dict] = []

    def view(self) -> dict:
        state = self.vault.read()
        session = state.get("session")
        status = "ikke tilkoblet"
        if state.get("revocation_pending"):
            status = "frakobling ikke bekreftet av leverandøren"
        elif session:
            status = "autorisert" if session.get("accounts") else "tilkoblet uten kontoer"
        view = {"csrf": self.csrf, "message": self.message, "application": self.application,
                "banks": self.banks, "session": session, "snapshot": state.get("snapshot"),
                "session_status": status}
        self.message = ""
        return view


class Handler(http.server.BaseHTTPRequestHandler):
    protocol_version = "HTTP/1.1"
    server_version = "OpenHouseholdPrototype"
    sys_version = ""

    @property
    def console(self) -> Console:
        return self.server.console

    def log_message(self, fmt, *args):
        # The callback query carries the bank authorization code: never log it.
        self.log_date_time_string()

    def respond(self, status: int, body: bytes = b"", location: str = "") -> None:
        self.send_response(status)
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-store")
        self.send_header("Referrer-Policy", "no-referrer")
        self.send_header("X-Content-Type-Options", "nosniff")
        self.send_header("Content-Security-Policy", "default-src 'none'; style-src 'unsafe-inline'; form-action 'self'")
        if location:
            self.send_header("Location", location)
        if body:
            self.send_header("Content-Type", "text/html; charset=utf-8")
        self.end_headers()
        self.wfile.write(body)

    def page(self) -> None:
        self.respond(200, render(self.console.view()).encode())

    def fail(self, error: Exception) -> None:
        self.console.message = str(error) if isinstance(error, LocalError) else "Uventet lokal feil."
        self.respond(303, location="/")

    def form(self) -> dict:
        length = int(self.headers.get("Content-Length") or 0)
        if length > BODY_LIMIT:
            raise LocalError("Skjemaet var uventet stort.")
        data = urllib.parse.parse_qs(self.rfile.read(length).decode("utf-8", "replace"))
        if not secrets.compare_digest((data.get("csrf") or [""])[0], self.console.csrf):
            raise LocalError("Siden var utdatert. Last den inn på nytt.")
        return data

    def do_GET(self):
        path, _, query = self.path.partition("?")
        if path == "/":
            return self.page()
        if path != "/callback":
            return self.respond(404, b"<p>Ukjent side.</p>")
        with self.console.lock:
            try:
                fields = urllib.parse.parse_qs(query)
                expected = self.console.pending
                self.console.pending = None
                if not expected or not secrets.compare_digest((fields.get("state") or [""])[0], expected[0]):
                    raise LocalError("Innloggingen kunne ikke knyttes til dette forsøket.")
                code = (fields.get("code") or [""])[0]
                if not code:
                    raise LocalError("Banken avbrøt innloggingen. Ingen tilgang ble gitt.")
                session = self.console.provider.complete(code)
                state = self.console.vault.read()
                state["session"] = session
                self.console.vault.save(state)
                self.console.message = "Banken er tilkoblet. Velg kontoene du vil lese."
            except (LocalError, ValueError) as error:
                return self.fail(error)
        return self.respond(303, location="/")

    def do_POST(self):
        with self.console.lock:
            try:
                data = self.form()
                if self.path == "/connect":
                    name = (data.get("bank") or [""])[0]
                    bank = next((b for b in self.console.banks if b["name"] == name), None)
                    if bank is None:
                        raise LocalError("Velg en bank fra listen.")
                    state = secrets.token_urlsafe(32)
                    url = self.console.provider.begin(bank, state)
                    self.console.pending = (state, bank)
                    return self.respond(303, location=url)
                if self.path == "/fetch":
                    stored = self.console.vault.read()
                    session = stored.get("session")
                    if not session:
                        raise LocalError("Ingen aktiv bankøkt. Koble til banken først.")
                    days = int((data.get("days") or ["30"])[0] or 30)
                    stored["snapshot"] = self.console.provider.snapshot(session, data.get("account") or [], days)
                    self.console.vault.save(stored)
                    self.console.message = "Dataene er hentet og lagret kryptert lokalt."
                elif self.path == "/disconnect":
                    stored = self.console.vault.read()
                    session = stored.get("session") or {}
                    stored["session"] = None
                    try:
                        if session.get("session_id"):
                            self.console.provider.disconnect(session["session_id"])
                        stored["revocation_pending"] = None
                        self.console.message = "Bankøkten er avsluttet hos leverandøren."
                    except LocalError:
                        stored["revocation_pending"] = session.get("session_id")
                        self.console.message = ("Frakoblingen ble ikke bekreftet. Trekk samtykket i "
                                                "nettbanken, og prøv igjen.")
                    self.console.vault.save(stored)
                elif self.path == "/forget":
                    stored = self.console.vault.read()
                    stored["snapshot"] = None
                    self.console.vault.save(stored)
                    self.console.message = "De lokale bankdataene er slettet."
                else:
                    return self.respond(404, b"<p>Ukjent side.</p>")
            except (LocalError, ValueError) as error:
                return self.fail(error)
        return self.respond(303, location="/")


def serve(console: Console, directory: Path, password: str, port: int = PORT) -> None:
    context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
    context.minimum_version = ssl.TLSVersion.TLSv1_2
    certificate = directory / "localhost-certificate.pem"
    key = directory / "localhost-key.pem"
    read_private(key)  # Refuse to start if the local key is readable by others.
    context.load_cert_chain(certificate, key, password=password)
    server = http.server.ThreadingHTTPServer((HOST, port), Handler)
    server.console = console
    server.socket = context.wrap_socket(server.socket, server_side=True)
    print(f"Åpne https://localhost:{port}/ i nettleseren. Avslutt med Ctrl+C.")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()
