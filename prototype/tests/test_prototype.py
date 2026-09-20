"""Offline tests: guard rails, local storage and the whole local flow.

Every figure here is synthetic. No credential, bank response or household
number belongs in this file.
"""

from __future__ import annotations

import http.client
import json
import shutil
import ssl
import tempfile
import threading
import unittest
import urllib.error
import urllib.parse
from pathlib import Path

from prototype import app, demo, provider, storage
from prototype.storage import LocalError, Vault

PASSPHRASE = "a-local-test-passphrase"
VAULT_DIR: Path


def setUpModule() -> None:
    # One 4096-bit key for the module; generating it per test is needlessly slow.
    global VAULT_DIR
    VAULT_DIR = Path(tempfile.mkdtemp(prefix="openhousehold-test-"))
    storage.initialize(VAULT_DIR, PASSPHRASE)


def tearDownModule() -> None:
    shutil.rmtree(VAULT_DIR, ignore_errors=True)


class Recorded(provider.EnableBanking):
    """The real client with its single network call replaced by canned answers."""

    def __init__(self, answers):
        self.answers = answers
        self.calls = []
        self.retry_after = 0.0
        self.app_id = "44444444-4444-4444-8444-444444444444"

    def request(self, method, path, body=None, query=None):
        self.calls.append((method, path, query, body))
        answer = self.answers[len(self.calls) - 1] if isinstance(self.answers, list) else self.answers
        if isinstance(answer, Exception):
            raise answer
        return answer


class GuardRails(unittest.TestCase):
    def test_write_operations_are_refused(self):
        # The real client, not a stub: the allowlist runs before any network call.
        client = provider.EnableBanking("44444444-4444-4444-8444-444444444444",
                                        Vault(VAULT_DIR, PASSPHRASE).key)
        for method, path in [("POST", "/payments"), ("PUT", "/accounts"), ("DELETE", "/application"),
                             ("GET", "/accounts/not-a-uuid/transactions"), ("GET", "/../application"),
                             ("POST", "/sessions/33333333-3333-4333-8333-333333333333")]:
            with self.assertRaises(LocalError) as caught:
                client.request(method, path)
            self.assertIn("lesetilgang", str(caught.exception))

    def test_application_must_be_active_production_ais_with_our_callback(self):
        good = {"active": True, "environment": "PRODUCTION", "services": ["AIS"],
                "redirect_urls": [provider.CALLBACK]}
        self.assertEqual(Recorded(good).check_application(), good)
        for broken in [{**good, "active": False}, {**good, "environment": "SANDBOX"},
                       {**good, "services": ["AIS", "PIS"]}, {**good, "redirect_urls": []}]:
            with self.assertRaises(LocalError):
                Recorded(broken).check_application()

    def test_authorization_url_must_come_from_the_provider(self):
        bank = {"name": "Demo", "maximum_consent_validity": 86400}
        self.assertTrue(Recorded({"url": "https://auth.enablebanking.com/ais/start?sessionid=x"})
                        .begin(bank, "state").startswith("https://auth.enablebanking.com/"))
        for bad in ["http://auth.enablebanking.com/x", "https://evil.example/x",
                    "https://auth.enablebanking.com.evil.example/x", "https://user@auth.enablebanking.com/x", ""]:
            with self.assertRaises(LocalError):
                Recorded({"url": bad}).begin(bank, "state")

    def test_consent_validity_is_capped_at_a_day(self):
        import datetime as dt
        client = Recorded({"url": "https://auth.enablebanking.com/ais/start"})
        client.begin({"name": "Demo", "maximum_consent_validity": 90 * 86400}, "state")
        method, path, _, body = client.calls[0]
        self.assertEqual((method, path), ("POST", "/auth"))
        granted = dt.datetime.fromisoformat(body["access"]["valid_until"]) - dt.datetime.now(dt.timezone.utc)
        self.assertLessEqual(granted, dt.timedelta(hours=24))
        self.assertGreater(granted, dt.timedelta(hours=23))
        self.assertEqual(body["access"], {"valid_until": body["access"]["valid_until"],
                                          "balances": True, "transactions": True})
        self.assertNotIn("payments", json.dumps(body))
        with self.assertRaises(LocalError):
            Recorded({}).begin({"name": "Demo", "maximum_consent_validity": 30}, "state")

    def test_snapshot_refuses_an_unauthorized_session(self):
        session = {"session_id": "33333333-3333-4333-8333-333333333333",
                   "accounts": [{"uid": "11111111-1111-4111-8111-111111111111"}]}
        client = Recorded({"status": "REVOKED"})
        with self.assertRaises(LocalError):
            client.snapshot(session, ["11111111-1111-4111-8111-111111111111"], 7)

    def test_snapshot_validates_the_selection_and_the_period(self):
        uid = "11111111-1111-4111-8111-111111111111"
        session = {"session_id": "33333333-3333-4333-8333-333333333333", "accounts": [{"uid": uid}]}
        for selected, days in [([], 7), ([uid, uid], 7), (["22222222-2222-4222-8222-222222222222"], 7),
                               ([uid], 0), ([uid], 91)]:
            with self.assertRaises(LocalError):
                Recorded({"status": "AUTHORIZED"}).snapshot(session, selected, days)

    def test_pagination_stops_on_a_repeated_cursor(self):
        uid = "11111111-1111-4111-8111-111111111111"
        session = {"session_id": "33333333-3333-4333-8333-333333333333", "accounts": [{"uid": uid}]}
        answers = [{"status": "AUTHORIZED"}, {"balances": []},
                   {"transactions": [], "continuation_key": "same"},
                   {"transactions": [], "continuation_key": "same"}]
        with self.assertRaises(LocalError):
            Recorded(answers).snapshot(session, [uid], 7)

    def test_pagination_collects_every_page(self):
        uid = "11111111-1111-4111-8111-111111111111"
        session = {"session_id": "33333333-3333-4333-8333-333333333333", "accounts": [{"uid": uid, "name": "K"}]}
        answers = [{"status": "AUTHORIZED"}, {"balances": [{"name": "Saldo"}]},
                   {"transactions": [{"entry_reference": "a"}], "continuation_key": "next"},
                   {"transactions": [{"entry_reference": "b"}]}]
        result = Recorded(answers).snapshot(session, [uid], 7)
        self.assertEqual([t["entry_reference"] for t in result["accounts"][0]["transactions"]], ["a", "b"])
        self.assertEqual(result["schema_version"], 1)


class LocalStorage(unittest.TestCase):
    def test_state_round_trips_and_stays_unreadable_without_the_passphrase(self):
        vault = Vault(VAULT_DIR, PASSPHRASE)
        vault.save({"session": None, "snapshot": {"marker": "synthetic"}, "revocation_pending": None})
        self.assertEqual(Vault(VAULT_DIR, PASSPHRASE).read()["snapshot"], {"marker": "synthetic"})
        self.assertNotIn(b"synthetic", (VAULT_DIR / "state.enc").read_bytes())
        with self.assertRaises(LocalError):
            Vault(VAULT_DIR, "a-wrong-test-passphrase")

    def test_setup_refuses_a_weak_passphrase_and_an_existing_directory(self):
        empty = Path(tempfile.mkdtemp(prefix="openhousehold-test-"))
        try:
            with self.assertRaises(LocalError):
                storage.initialize(empty, "kort")
            with self.assertRaises(LocalError):
                storage.initialize(VAULT_DIR, PASSPHRASE)
        finally:
            shutil.rmtree(empty, ignore_errors=True)

    def test_a_world_readable_file_is_refused(self):
        path = VAULT_DIR / "loose"
        storage.write_private(path, b"x")
        path.chmod(0o644)
        with self.assertRaises(LocalError):
            storage.read_private(path)
        path.unlink()


class Rendering(unittest.TestCase):
    def test_bank_text_cannot_inject_markup(self):
        page = app.render({"csrf": "t", "message": "", "application": {}, "banks": [],
                           "session_status": "autorisert",
                           "session": {"accounts": [{"uid": "u", "name": "<script>alert(1)</script>"}]},
                           "snapshot": None})
        self.assertNotIn("<script>alert(1)</script>", page)
        self.assertIn("&lt;script&gt;", page)

    def test_account_numbers_are_masked_and_debits_are_signed(self):
        self.assertEqual(app.mask("NO9386011117947"), "••• 7947")
        self.assertEqual(app.money({"amount": "10.00", "currency": "NOK"}, debit=True), "-10.00 NOK")
        self.assertEqual(app.money({"amount": "10.00", "currency": "NOK"}), "10.00 NOK")


class WholeFlow(unittest.TestCase):
    """Drives the real server over TLS with the synthetic bank."""

    @classmethod
    def setUpClass(cls):
        cls.directory = Path(tempfile.mkdtemp(prefix="openhousehold-flow-"))
        storage.initialize(cls.directory, PASSPHRASE)
        cls.bank = demo.DemoBank("https://localhost:0/callback")
        console = app.Console(Vault(cls.directory, PASSPHRASE), cls.bank)
        console.application = cls.bank.check_application()
        console.banks = cls.bank.banks()
        cls.console = console
        context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
        context.load_cert_chain(cls.directory / "localhost-certificate.pem",
                                cls.directory / "localhost-key.pem", password=PASSPHRASE)
        import http.server
        cls.server = http.server.ThreadingHTTPServer(("127.0.0.1", 0), app.Handler)
        cls.server.console = console
        cls.server.socket = context.wrap_socket(cls.server.socket, server_side=True)
        cls.port = cls.server.socket.getsockname()[1]
        cls.bank.callback = f"https://localhost:{cls.port}/callback"
        cls.thread = threading.Thread(target=cls.server.serve_forever, daemon=True)
        cls.thread.start()
        cls.client_context = ssl.create_default_context(cafile=cls.directory / "localhost-certificate.pem")

    @classmethod
    def tearDownClass(cls):
        cls.server.shutdown()
        cls.server.server_close()
        cls.thread.join(timeout=5)
        shutil.rmtree(cls.directory, ignore_errors=True)

    def call(self, method: str, path: str, fields: dict | None = None):
        connection = http.client.HTTPSConnection("localhost", self.port, context=self.client_context, timeout=10)
        body, headers = None, {}
        if fields is not None:
            body = urllib.parse.urlencode(fields, doseq=True)
            headers = {"Content-Type": "application/x-www-form-urlencoded"}
        connection.request(method, path, body, headers)
        response = connection.getresponse()
        text = response.read().decode()
        location = response.getheader("Location") or ""
        self.headers = dict(response.getheaders())
        connection.close()
        return response.status, location, text

    def token(self) -> str:
        _, _, page = self.call("GET", "/")
        return page.split("name='csrf' value='")[1].split("'")[0]

    def test_the_flow_connects_fetches_disconnects_and_forgets(self):
        status, _, page = self.call("GET", "/")
        self.assertEqual(status, 200)
        self.assertIn("Kun lesetilgang", page)
        self.assertEqual(self.headers["Cache-Control"], "no-store")
        self.assertEqual(self.headers["Referrer-Policy"], "no-referrer")
        self.assertIn("default-src 'none'", self.headers["Content-Security-Policy"])

        status, location, _ = self.call("POST", "/connect",
                                        {"csrf": self.token(), "bank": demo.BANKS[0]["name"]})
        self.assertEqual(status, 303)
        self.assertIn("/callback?code=", location)

        status, _, _ = self.call("GET", urllib.parse.urlsplit(location).path + "?" + urllib.parse.urlsplit(location).query)
        self.assertEqual(status, 303)
        _, _, page = self.call("GET", "/")
        self.assertIn("Banken er tilkoblet", page)

        status, _, _ = self.call("POST", "/fetch", {"csrf": self.token(), "days": "14",
                                                    "account": [a["uid"] for a in demo.ACCOUNTS]})
        self.assertEqual(status, 303)
        _, _, page = self.call("GET", "/")
        self.assertIn("Brukskonto", page)
        self.assertIn("Sparekonto", page)
        self.assertNotIn("NO9386011117947", page)  # Masked, never the full number.

        status, _, _ = self.call("POST", "/disconnect", {"csrf": self.token()})
        self.assertEqual(status, 303)
        self.assertTrue(self.bank.revoked)
        _, _, page = self.call("GET", "/")
        self.assertIn("avsluttet hos leverandøren", page)

        self.call("POST", "/forget", {"csrf": self.token()})
        _, _, page = self.call("GET", "/")
        self.assertNotIn("Brukskonto", page)

    def test_a_stale_form_and_an_unexpected_callback_are_refused(self):
        self.call("POST", "/fetch", {"csrf": "wrong", "days": "1"})
        _, _, page = self.call("GET", "/")
        self.assertIn("utdatert", page)

        self.call("GET", "/callback?code=demo-code&state=never-issued")
        _, _, page = self.call("GET", "/")
        self.assertIn("kunne ikke knyttes", page)

    def test_an_unknown_page_is_not_served(self):
        status, _, _ = self.call("GET", "/etc/passwd")
        self.assertEqual(status, 404)


if __name__ == "__main__":
    unittest.main()
