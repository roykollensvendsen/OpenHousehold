"""Synthetic bank used to exercise the flow offline. No real data, ever."""

from __future__ import annotations

import datetime as dt
import random

from .storage import LocalError

BANKS = [{"name": "Sparebanken Norge (demo)", "country": "NO", "psu_types": ["personal"],
          "maximum_consent_validity": 86400}]
ACCOUNTS = [
    {"uid": "11111111-1111-4111-8111-111111111111", "name": "Brukskonto",
     "currency": "NOK", "account_id": {"iban": "NO9386011117947"}},
    {"uid": "22222222-2222-4222-8222-222222222222", "name": "Sparekonto",
     "currency": "NOK", "account_id": {"iban": "NO9386011112233"}},
]
PAID = ["Dagligvarer", "Strøm", "Barnehage", "Kollektivtransport",
        "Overføring sparing", "Apotek", "Drivstoff", "Forsikring", "Kafé"]
RECEIVED = ["Lønn", "Tilbakebetaling", "Overføring fra felleskonto"]


class DemoBank:
    """Mirrors the provider's capability list; every figure below is invented."""

    def __init__(self, callback: str = "https://localhost:8767/callback"):
        self.callback = callback
        self.session_id = "33333333-3333-4333-8333-333333333333"
        self.revoked = False

    def check_application(self) -> dict:
        return {"name": "OpenHousehold demo", "environment": "DEMO", "services": ["AIS"],
                "active": True, "redirect_urls": [self.callback]}

    def banks(self) -> list[dict]:
        return list(BANKS)

    def begin(self, bank: dict, state: str) -> str:
        if bank not in BANKS:
            raise LocalError("Ukjent demobank.")
        # The demo stands in for the bank's own login and returns straight to us.
        return f"{self.callback}?code=demo-code&state={state}"

    def complete(self, code: str) -> dict:
        if not code.startswith("demo-"):
            raise LocalError("Demokoden er ugyldig.")
        self.revoked = False
        return {"session_id": self.session_id, "accounts": [dict(a) for a in ACCOUNTS],
                "aspsp": BANKS[0], "psu_type": "personal"}

    def snapshot(self, session: dict, selected: list[str], days: int) -> dict:
        if self.revoked:
            raise LocalError("Bankøkten er ikke lenger autorisert. Koble til på nytt.")
        if not 1 <= days <= 90:
            raise LocalError("Velg mellom 1 og 90 dager.")
        known = {a["uid"]: a for a in session["accounts"]}
        if not selected or any(uid not in known for uid in selected):
            raise LocalError("Velg 1–20 forskjellige kontoer fra din autoriserte liste.")
        today = dt.datetime.now(dt.timezone.utc).date()
        since = today - dt.timedelta(days=days - 1)
        collected = []
        for index, uid in enumerate(selected):
            generator = random.Random(f"{uid}:{days}")
            transactions = []
            for offset in range(0, days, max(1, days // 12)):
                debit = generator.random() > 0.2
                transactions.append({
                    "entry_reference": f"demo-{uid[:8]}-{offset}",
                    "booking_date": (since + dt.timedelta(days=offset)).isoformat(),
                    "transaction_amount": {"currency": "NOK",
                                           "amount": f"{generator.randrange(50, 9000)}.{generator.randrange(0, 99):02d}"},
                    "credit_debit_indicator": "DBIT" if debit else "CRDT",
                    "remittance_information": [generator.choice(PAID if debit else RECEIVED)],
                    "status": "BOOK"})
            collected.append({
                "account": known[uid],
                "balances": {"balances": [{"name": "Bokført saldo", "balance_type": "CLBD",
                                           "balance_amount": {"currency": "NOK",
                                                              "amount": f"{12000 + index * 47000}.00"},
                                           "reference_date": today.isoformat()}]},
                "transactions": transactions})
        return {"retrieved_at": dt.datetime.now(dt.timezone.utc).isoformat(),
                "requested_from": since.isoformat(), "requested_to": today.isoformat(),
                "accounts": collected, "provider": "Demo (syntetiske data)", "schema_version": 1}

    def disconnect(self, session_id: str) -> None:
        if session_id != self.session_id:
            raise LocalError("Ukjent demoøkt.")
        self.revoked = True
