# External boundaries and contracts

Status: proposed. Concrete transport schemas follow the reuse/provider decision.
An OpenAPI file is deferred until an actual HTTP API surface is selected; this
document is a reviewable semantic contract rather than invented endpoints.

## Bank adapter

| Operation | Input | Output / obligation |
| --- | --- | --- |
| capabilities | Provider and institution route/version | Account types, history limit, pagination, quotas, balance kinds, identity stability, consent expiry support. |
| begin_consent | Authenticated user, callback allowlist entry, AIS scopes | Short-lived state bound to user/session and consent request; provider redirect. |
| complete_consent | Single-use state and provider response | Connection belonging to the original user; external authorization reference. |
| list_accounts | Active connection | External aliases, currency, account type, identity evidence; no invented owner identity. |
| fetch_balances | Connection, account alias | Typed balances with source and retrieval times, explicit unsupported/missing states. |
| fetch_transactions | Alias, coverage window and opaque cursor | Bounded page of observations, next cursor, coverage and source identity semantics. |
| disconnect | Connection | Local revocation immediately; provider revocation where supported, retry status otherwise. |

Normalized values are exact money, UTC instants, dates, opaque IDs and known
status enums. Keep provider-specific payloads inside the adapter. Persist minimal
provenance and mapping version. The credential handle, not credential value,
crosses the application-to-connector boundary. Provider signing keys are allowed
connector credentials; they are not crypto-wallet private keys.

Error categories: authentication_required, consent_expired, revoked, rate_limited,
provider_unavailable, unsupported_account, invalid_data and identity_ambiguous.
Return sanitized code, retryability and retry-after where provided. Do not expose
raw provider messages to clients. Authentication/consent errors await user action;
transient failures use bounded backoff with jitter and respect Retry-After.

## Consistency and interruption

One active run per connection, protected with a renewable lease and fencing token.
Before every provider request and before publication, recheck connection state.
Stage paginated results; publish one account's reconciled batch transactionally
with its cursor. A crash before commit preserves previous visible data. A retry
is idempotent. Other accounts may succeed independently; shared views show the
individual observation times and any partial coverage.

The adapter contract suite exercises duplicate pages, cursor restart, 429,
timeouts, changed IDs, unknown currency, absent timestamps, partial accounts,
consent revocation mid-run and migration from the legacy bank route.

## Browser/application boundary

The server derives user and household scope from the authenticated session;
client-supplied object IDs never grant access. Apply authorization to direct reads,
aggregates, export, caches and explanations. Revalidate before a response if a
concurrent sharing/membership change occurred. Use opaque identifiers and
nonrevealing unauthorized responses.

Goal/annotation edits carry an expected revision; conflicting writes produce a
conflict response rather than last-write-wins. Destructive deletion requires
explicit in-app confirmation and appropriate authority. Connection redirects use
an allowlist and single-use state. Cookies are Secure and HttpOnly; state-changing
requests use CSRF/origin checks appropriate to the chosen session library.

The eventual API describes error shapes, validation limits, versioning and
idempotency in a pinned schema with contract tests. No endpoint or dependency
exposes payment, transfer or trade execution. Creating AIS consent can legitimately
use POST; read-only is defined by financial capability, not HTTP verb.

## Export boundary

Proposed export: UTF-8 JSON manifest with schema_version, exported_at, caller scope,
accounts, transactions, snapshots, goals, annotations and provenance references.
Money is a string of integer minor units with currency and scale, preserving
64-bit values for JavaScript readers. Include coverage and revisions. Exclude all
credentials and unauthorized records. Schema migration compatibility and round-trip
import are separate: Phase 1 guarantees a documented export, not arbitrary import.
