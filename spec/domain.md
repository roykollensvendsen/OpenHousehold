# Domain model and calculation rules

Status: proposed; approve Q-01 and Q-02 before implementation. Implements the
[requirement register](requirements.md), not a new financial ledger product.

## Identities and ownership

| Entity | Minimum meaning and relationships |
| --- | --- |
| User | Stable opaque identity; authentication identity reference, never a bank login. |
| Household / Membership | Shared workspace; user membership and role with active/revoked state. |
| Institution | Provider-independent bank identity with versioned provider aliases. |
| Connection / Consent | Exactly one authorizing user, provider route, scopes, external reference, optional expiry and status. |
| Account | Canonical ID, institution, currency, account kind, verified identity evidence and separately known legal owners. |
| AccountAccess | User's evidenced access to a canonical account, origin connection, valid/revoked state. Access is not legal ownership. |
| SharingGrant | Contributor, canonical account, household, scope, grant/revocation time. |
| AccountAlias | Provider/connection account reference mapped to canonical identity with evidence. |
| SyncRun | Attempt, status, coverage, adapter version, cursor and error category. |
| BalanceSnapshot | Canonical account, amount, currency, kind, source time if supplied, retrieval time and source revision. |
| Transaction | Account-scoped source identity, amount/currency, booked/pending status, dates and provenance. |
| Annotation | User note/classification separately versioned from provider facts. |
| Goal / FundingSelection | Positive target, NOK, optional date, active/archived state, revision and designated shared accounts. |
| GoalObservation | Input snapshot references, funding revision, computed values, coverage and calculation version. |
| Notice / AuditEvent | Deduplicated user action notice; separate metadata-only security history. |

No holdings, property, insurance or tax tables are needed yet. Stable identity,
Money and provenance are the extension points, not empty tables for every idea.

## Sharing policy proposed for Phase 1

Each adult can contribute bank-authorized accounts. Sharing exposes the selected
account's balance and transactions to the household; this scope is displayed
before confirmation. Private accounts are excluded from shared totals, exports,
goals and suggestions. There is no aggregate-only privacy mode in this slice.

For a verified joint account, each contributor controls their own sharing grant.
If one grant is withdrawn but another valid grant remains, the account stays
shared through that grant; explain this to both adults. Withdrawal cannot revoke
another person's lawful bank access. A revoked membership cannot query anything.
The host administrator can access plaintext at runtime and is a trusted operator;
application permissions do not protect data from a compromised host/root user.

Grant withdrawal invalidates derivatives contributed solely through that grant
before the next shared response. Historical summaries that expose the withdrawn
account are removed from shared access too. Private owner history may remain
according to retention. A goal losing a funding account becomes incomplete and
requires a new confirmed funding revision. Previously downloaded exports cannot
be recalled. Disconnecting a connection stops ingestion but does not by itself
withdraw sharing or delete history; the UI offers these as distinct actions.

## Exact monetary values and dates

Persist money as signed integer minor units with ISO currency code and explicit
scale. NOK has scale 2. Reject unknown scale, malformed amounts and values outside
signed 64-bit storage; use checked arithmetic to reject aggregate overflow.
No binary floating point in storage or calculations. No implicit FX conversion:
non-NOK accounts can appear in currency-separated views but cannot fund a Phase 1
goal. Ratios use exact decimal arithmetic; display percentages to one decimal
with half-up rounding. Retain uncapped values even if the progress bar caps at 100%.

Store instants as UTC and preserve provider booking/value dates as dates. Target
dates use Europe/Oslo, including daylight-saving changes. A missing source time
is unknown, never invented from the retrieval time. Label both when available.

## Savings-goal definition

The proposed model dedicates **full booked balances of selected shared NOK
accounts** to one goal. This is simplest when the household uses dedicated
savings accounts. It does not allocate budget envelopes or promise spendable cash.
If the owners need partial allocations, revise this rule before implementation.

Let S be the confirmed set of unique funding accounts and T > 0 the target.
For one complete observation, B(a) is the latest published booked balance of a.

- Current funds C = sum of B(a) for a in S, including negative balances.
- Remaining R = max(T - C, 0).
- Progress P = 100 × C / T; negative and above-100 values are valid results.
- Goal reached means C >= T **and** all inputs are present, fresh and resolved.
- Change Δ = C(new) - C(old), only for complete observations of the same S/revision.

Example: balances NOK 10,000 + 5,000, target 20,000: C=15,000, R=5,000, P=75%.
If a withdrawal reduces one balance by 2,000, C falls by 2,000. Never add a manual
“contribution” on top of these balances. A transfer into S can increase goal funds
without increasing household net wealth. State that distinction in observations.

No baseline is backfilled from incomplete transactions. The first complete
observation starts history. Compare to the immediately preceding complete
observation and show the actual elapsed period, not an assumed week. Changing S
or sharing eligibility starts a new series; changing the target updates the
percentage without reclassifying the balance change as savings. Keep revisions.

Empty S means unconfigured, not zero. Missing/ambiguous/stale inputs produce a
partial view with known subtotal and coverage; no definitive progress, completion
or on-track claim. Eight days since last successful retrieval is the proposed
staleness threshold. Old provider-dated values also show their source age and
cannot be called a newer bank observation merely because they were fetched again.

Optional required daily pace = R / days remaining, rounded up to a whole øre.
Use only complete inputs and a future target date. No date means no pace; overdue
means show remaining and overdue state, never divide by zero. This is arithmetic,
not a prediction of affordability or future returns.

## Imports and source of truth

Bank observations are authoritative for imported balances and booked entries.
Annotations add context and never overwrite those facts. Preserve minimal source
fields and revision/provenance links needed for reconciliation. Raw payload policy
is in [operations](operations.md). Corrections create revisions; never silently
rewrite prior evidence. Historical calculations retain their snapshot references
unless privacy deletion requires removal.

Stable source identity is namespaced by institution/account/provider semantics.
Provider account IDs can change after reconsent. Verified identity, such as exact
bank-provided account identifiers and institution, can support alias mapping;
masked numbers or display names cannot. Reconcile cross-provider migration
explicitly. Identity uncertainty quarantines ambiguous records and marks affected
calculations incomplete. Never deduplicate solely on date, amount and description.

Pending records do not enter booked results. A reservation becoming booked may
change ID and amount; follow documented provider linkage or reconcile explicitly.
Do not delete old booked transactions simply because a limited history window
stops returning them. Record the imported coverage start/end and gaps.

Transfers are neutral only between included accounts with confirmed pairing.
A heuristic can suggest a match, but ambiguity stays unclassified. Goal movements
remain balance changes, separate from income and expense classification.
