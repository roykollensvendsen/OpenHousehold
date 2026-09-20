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
uv run python -m prototype init          # local keys and certificates
```

`init` prints the remaining steps, which only the account owner can perform:
register an application in the provider's control panel, upload
`.local-bank/application-certificate.pem`, select the AIS service alone,
register `https://localhost:8767/callback` as the redirect URL, and link your
own accounts. Then:

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
