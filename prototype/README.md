# Bank read prototype

A local feasibility probe, not the household product. It answers one question:
can this household read its own accounts, balances and booked transactions from
its bank through an aggregator, well enough to build on? The owner approved a
single-owner, read-only probe on 2026-09-20; the product baseline in
[SPEC.md](../SPEC.md) remains gated on specification review.

## What it does and does not do

It runs on one machine, binds to `127.0.0.1`, and shows the data on a local HTTPS
page. It holds an account-information (AIS) consent only: the client refuses any
request outside a fixed read-only allowlist, so a payment call cannot be made
even by mistake. The bank login happens at the bank; this code never sees a bank
password. Everything it keeps — the provider key, the retrieved data — is
encrypted under a local passphrase in `.local-bank/`, which is git-ignored. No
household figure is sent anywhere, including to a language model.

It is single-owner, has no sharing, no goal arithmetic and no durable data model.
Those belong to the product, after the open questions in
[docs/open-questions.md](../docs/open-questions.md) are decided.

## Setup

The provider is Enable Banking, chosen as a candidate in
[docs/research.md](../docs/research.md); its suitability is still unproven.

```sh
uv sync --locked
uv run python -m prototype init
```

The remaining steps are in the provider's control panel and only the account
owner can perform them. They follow its
[documentation](https://enablebanking.com/docs/api/control-panel/), read
2026-09-20:

1. Sign in, open **API applications**, and fill out **Add a new application**.
2. Choose the **Production** environment. Sandbox serves the provider's test
   banks, not yours.
3. Whitelist `https://localhost:8767/callback` as the redirect URL. The
   documentation does not say whether a localhost URL is accepted; if it is
   refused, the callback has to move before a live run is possible.
4. Select the AIS service alone, with no payment rights. The client refuses
   payment paths regardless, but the consent itself should not carry them.
5. Activate the application in **restricted mode** by linking your own bank
   accounts, which limits retrieval to exactly those accounts. Unrestricted
   activation requires a contract, KYC and billing, and is not this probe's path.

Registering a production application also asks for a description, a data
protection email, a privacy policy URL and a terms of service URL.

The key pair can come from either side:

- **The panel generates it.** The browser creates the private key and downloads
  it as `<application id>.pem`, which carries the application id in its name.
  ```sh
  uv run python -m prototype import-key ~/Downloads/<application id>.pem
  shred -u ~/Downloads/<application id>.pem
  uv run python -m prototype serve
  ```
- **We generate it.** Provide `.local-bank/application-public-key.pem` during
  registration instead, and keep the private key where `init` put it.
  ```sh
  uv run python -m prototype serve --app-id <application id>
  ```

Open `https://localhost:8767/`. The certificate is self-signed and local, so the
browser will warn once; verify the fingerprint against
`.local-bank/localhost-certificate.pem` before accepting it. The application id
is stored after the first run, so later runs need only `serve`.

To see the page and the whole flow without a bank, with invented figures:

```sh
uv run python -m prototype demo
```

## Deleting the data

"Slett de lokale dataene" on the page removes the retrieved data;
"Koble fra banken" also revokes the session at the provider. Withdraw the consent
in your bank as well, since a revoked session is not always a withdrawn consent.
Removing `.local-bank/` deletes the local keys and everything held under them.

## Tests

```sh
uv run python -m unittest discover -s prototype/tests -t . -v
```

They run offline against a synthetic bank and cover the read-only allowlist, the
consent cap, pagination, local file permissions, encryption, markup escaping and
the whole connect/fetch/disconnect flow. They are the prototype's own tests and
prove nothing about the product's acceptance criteria.

## What a live run must record

The evidence list in [docs/research.md](../docs/research.md) applies: the actual
institution route, both owners' eligibility, price, consent lifetime and renewal,
available history, balance semantics, quotas, deletion, and a disconnect and
reconnect trial. Until a live run happens, this directory proves only that the
client is written and the local flow works.
