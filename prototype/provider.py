"""Narrow Enable Banking AIS client. Payments are outside its capability list."""

from __future__ import annotations

import datetime as dt
import json
import re
import time
import urllib.error
import urllib.parse
import urllib.request
import uuid

import jwt

from .storage import LocalError

BASE = "https://api.enablebanking.com"
ORIGIN = "https://localhost:8767"
CALLBACK = ORIGIN + "/callback"
UUID = r"[0-9a-fA-F-]{36}"
ALLOWED = {
    "GET": re.compile(rf"/(?:application|aspsps|sessions/{UUID}|accounts/{UUID}/(?:balances|transactions))"),
    "POST": re.compile(r"/(?:auth|sessions)"),
    "DELETE": re.compile(rf"/sessions/{UUID}"),
}


class NoRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        raise LocalError("Uventet API-videresending ble blokkert.")


def uid(value: str) -> str:
    try:
        return str(uuid.UUID(value))
    except (ValueError, TypeError, AttributeError):
        raise LocalError("Leverandøren returnerte en ugyldig identifikator.") from None


class EnableBanking:
    def __init__(self, app_id: str, key):
        self.app_id = uid(app_id)
        self.key = key
        # No environment proxy: credentials go only to the fixed, TLS-verified API.
        self.opener = urllib.request.build_opener(urllib.request.ProxyHandler({}), NoRedirect())
        self.retry_after = 0.0

    def request(self, method: str, path: str, body=None, query=None) -> dict:
        if method not in ALLOWED or not ALLOWED[method].fullmatch(path):
            raise LocalError("Operasjonen er ikke tillatt i prototypen med lesetilgang.")
        if time.monotonic() < self.retry_after:
            raise LocalError("Leverandørens ventetid gjelder fortsatt. Prøv igjen senere.")
        now = int(time.time())
        token = jwt.encode({"iss": "enablebanking.com", "aud": "api.enablebanking.com",
                            "iat": now, "exp": now + 300}, self.key, algorithm="RS256",
                           headers={"kid": self.app_id})
        url = BASE + path + ("?" + urllib.parse.urlencode(query) if query else "")
        request = urllib.request.Request(url, method=method,
            data=json.dumps(body).encode() if body is not None else None,
            headers={"Authorization": "Bearer " + token, "Accept": "application/json",
                     "Content-Type": "application/json"})
        try:
            with self.opener.open(request, timeout=30) as response:
                data = response.read(2_000_001)
            if len(data) > 2_000_000:
                raise LocalError("Leverandørsvaret overskred prototypens størrelsesgrense.")
            result = json.loads(data) if data else {}
            if not isinstance(result, dict):
                raise LocalError("Uventet svarformat fra leverandøren.")
            return result
        except urllib.error.HTTPError as error:
            if error.code == 429:
                # Honor seconds and HTTP-date Retry-After; never retry automatically.
                from email.utils import parsedate_to_datetime
                value = error.headers.get("Retry-After", "60")
                try:
                    delay = float(value)
                except ValueError:
                    try:
                        delay = parsedate_to_datetime(value).timestamp() - time.time()
                    except (ValueError, TypeError, OverflowError):
                        delay = 60
                self.retry_after = time.monotonic() + max(1, delay)
                raise LocalError("Leverandøren begrenser antall forespørsler. Vent før nytt forsøk.") from None
            messages = {401: "Kontroller applikasjons-ID og sertifikat.",
                        403: "Tilgang avslått. Kontroller aktivering og lenking av egne kontoer.",
                        404: "Bankruten eller økten finnes ikke lenger; kontroller oppsettet.",
                        409: "Leverandøren er opptatt; prøv igjen senere."}
            raise LocalError(messages.get(error.code, f"Leverandørkallet feilet (HTTP {error.code}). Ingen råfeil vises.")) from None
        except (urllib.error.URLError, TimeoutError, OSError, ValueError):
            raise LocalError("Nettverksfeil eller ugyldig leverandørsvar. Tidligere data er beholdt.") from None

    def check_application(self) -> dict:
        app = self.request("GET", "/application")
        if not app.get("active"):
            raise LocalError("Applikasjonen er ikke aktiv. Lenk dine egne kontoer i kontrollpanelet.")
        if app.get("environment") != "PRODUCTION":
            raise LocalError("Denne flyten krever en Production-applikasjon for egne kontoer.")
        if set(app.get("services", [])) != {"AIS"}:
            raise LocalError("Applikasjonen må ha bare AIS (kontoinformasjon), uten betalingsrettigheter.")
        if CALLBACK not in app.get("redirect_urls", []):
            raise LocalError("Registrer https://localhost:8767/callback som returadresse.")
        return app

    def banks(self) -> list[dict]:
        records = self.request("GET", "/aspsps", query={"country": "NO", "service": "AIS"}).get("aspsps", [])
        # Display current names from the API; never silently choose a legacy route.
        return [b for b in records if b.get("country") == "NO" and "personal" in b.get("psu_types", [])
                and any(term in b.get("name", "").casefold() for term in ("sparebanken norge", "sparebanken sør", "sparebanken vest"))]

    def begin(self, bank: dict, state: str) -> str:
        validity = min(int(bank["maximum_consent_validity"]), 24 * 3600)
        if validity < 60:
            raise LocalError("Bankens oppgitte gyldighet er for kort for dette forsøket.")
        until = dt.datetime.now(dt.timezone.utc) + dt.timedelta(seconds=validity)
        response = self.request("POST", "/auth", {
            "access": {"valid_until": until.isoformat(), "balances": True, "transactions": True},
            "aspsp": {"name": bank["name"], "country": "NO"}, "state": state,
            "redirect_url": CALLBACK, "psu_type": "personal", "language": "no",
        })
        url = response.get("url", "")
        parsed = urllib.parse.urlsplit(url)
        if parsed.scheme != "https" or parsed.hostname != "auth.enablebanking.com" or parsed.username or parsed.password or parsed.port not in (None, 443):
            raise LocalError("Leverandøren returnerte en uventet innloggingsadresse.")
        return url

    def complete(self, code: str) -> dict:
        result = self.request("POST", "/sessions", {"code": code})
        uid(result.get("session_id"))
        if not isinstance(result.get("accounts"), list):
            raise LocalError("Kontolisten mangler i leverandørsvaret.")
        return result

    def snapshot(self, session: dict, selected: list[str], days: int) -> dict:
        if not 1 <= days <= 90:
            raise LocalError("Velg mellom 1 og 90 dager.")
        active = self.request("GET", "/sessions/" + uid(session["session_id"]))
        if active.get("status") != "AUTHORIZED":
            raise LocalError("Bankøkten er ikke lenger autorisert. Koble til på nytt.")
        accounts = {a["uid"]: a for a in session["accounts"] if a.get("uid")}
        if not selected or len(selected) > 20 or len(set(selected)) != len(selected) or any(a not in accounts for a in selected):
            raise LocalError("Velg 1–20 forskjellige kontoer fra din autoriserte liste.")
        today = dt.datetime.now(dt.timezone.utc).date()
        since = today - dt.timedelta(days=days - 1)
        collected = []
        for account_id in selected:
            account_id = uid(account_id)
            balances = self.request("GET", f"/accounts/{account_id}/balances")
            transactions, seen, cursor = [], set(), None
            for _ in range(100):
                query = {"date_from": since.isoformat(), "date_to": today.isoformat(), "transaction_status": "BOOK"}
                if cursor:
                    query["continuation_key"] = cursor
                page = self.request("GET", f"/accounts/{account_id}/transactions", query=query)
                batch = page.get("transactions")
                if not isinstance(batch, list) or len(transactions) + len(batch) > 10_000:
                    raise LocalError("Ugyldig eller for stor transaksjonsliste. Tidligere resultat beholdes.")
                transactions.extend(batch)
                cursor = page.get("continuation_key")
                if not cursor:
                    break
                if not isinstance(cursor, str) or cursor in seen:
                    raise LocalError("Leverandøren gjentok en side; innhentingen ble avbrutt.")
                seen.add(cursor)
            else:
                raise LocalError("Sidegrensen ble nådd; prøv et kortere tidsrom.")
            # This is a replaceable observation, not an accumulating ledger. Do
            # not deduplicate ambiguous entries or silently rewrite bank facts.
            collected.append({"account": accounts[account_id], "balances": balances,
                              "transactions": transactions})
        return {"retrieved_at": dt.datetime.now(dt.timezone.utc).isoformat(),
                "requested_from": since.isoformat(), "requested_to": today.isoformat(),
                "accounts": collected, "provider": "Enable Banking", "schema_version": 1}

    def disconnect(self, session_id: str) -> None:
        self.request("DELETE", "/sessions/" + uid(session_id))
