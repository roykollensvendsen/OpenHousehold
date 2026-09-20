# Feasibility and reuse review

Research date: 2026-09-20. Documentation findings, not live integration tests.
Recheck provider terms and bank routing before implementation and release.

## Banking

| Candidate | Evidence | Assessment and unresolved proof |
| --- | --- | --- |
| Direct PSD2 | [Bank developer portal](https://developer.spvapi.no/documentation/psd2/) requires qualified QWAC certificates and mutual TLS. | Not assumed available to an ordinary household app; prefer an eligible aggregator. |
| Enable Banking | [Terms dated 2026-01-09](https://enablebanking.com/terms/) describe free personal/evaluation access with linked accounts and restrictions concerning other people's accounts. | Candidate only. Confirm how two independent owners can participate, bank coverage, credential separation and any agreement needed. |
| GoCardless | [Actual's documentation](https://actualbudget.org/docs/advanced/bank-sync/gocardless/) reports new Bank Account Data registrations closed since July 2025. | Not the baseline for a new user; existing eligibility requires separate proof. |

The bank portal announces the former Sør interface ending on **2026-10-09** and
the former Vest interface continuing. This is a schedule, not proof migration has
occurred. Demonstrate each owner's actual institution route and reconnect without
duplicating history. The continuing interface also documents limits on unattended
reads and history. Record capabilities per connection rather than assuming
unlimited history or permanently valid consent.

The provider's [API reference](https://enablebanking.com/docs/api/reference/),
read on 2026-09-20, documents the mechanics the prototype is built on: RS256 JWT
authorization with the application id as `kid`, `GET /aspsps` for routes and each
route's `maximum_consent_validity`, `POST /auth` with a mandatory `access.valid_until`
no later than that validity, `POST /sessions` exchanging the callback code for a
session and its accounts, `GET /accounts/{uid}/balances` and `/transactions` with
`continuation_key` pagination, and `DELETE /sessions/{id}`. Documentation, not a
live call: no provider account exists and nothing has been retrieved from a bank.

Provider evidence must record institution/version, account types, both owners'
eligibility, price and future charges, consent/renewal, history, balance semantics,
quotas, deletion, processing locations and a disconnect/reconnect trial. Any paid
agreement needs owner approval. No provider account or consent was created here.

## Existing components

| Option | Documented capability | Fit and experiment |
| --- | --- | --- |
| Actual Budget | [API](https://actualbudget.org/docs/api/) uses a Node package and local budget copy, not a conventional HTTP REST interface. [Multi-user](https://actualbudget.org/docs/config/multi-user/) supports OpenID-backed collaboration and budget access. | Evaluate as a foundation first. Prove per-account privacy, independent consent, provenance and goal calculations; avoid a large fork. |
| Actual + Enable Banking | [Integration docs](https://actualbudget.org/docs/advanced/bank-sync/enable-banking/) label the feature experimental and warn some functionality may require nightly images. | Pin and test a release; documentation does not prove production coverage. |
| Firefly III | [Upstream](https://github.com/firefly-iii/firefly-iii) documents self-hosting, REST API, double-entry bookkeeping, savings piggy banks and AGPL-3.0 licensing. | Trial household authorization and consent semantics. Review licensing for the actual integration before copying or distributing code. |
| Small OpenHousehold core | Project proposal, no existing implementation. | Fallback if reuse fails mandatory scenarios; offers explicit domain control with greater maintenance cost. |

No candidate was installed or benchmarked. Unknown means untested, not absent.
Check licenses and maintenance at pinned releases before adoption.

## Comparable experiment

Use synthetic people A and B, one private account each and a jointly visible
account. Compare Actual and Firefly on separate login, explicit sharing,
deduplication, export, reconnect, one goal and traceable calculations. Record
version, results, gaps and operational steps. Adopt directly if mandatory
requirements work without a major fork; add an adapter only with one declared
source of truth; build a new core only after recording failed requirements and
maintenance costs. No foundation or provider has been selected.
