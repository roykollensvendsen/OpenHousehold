# Acceptance and verification plan

All product scenarios below have status **Planned**. No application exists yet.
The repository integrity checks are a separate executable tool, described in
[CONTRIBUTING](../CONTRIBUTING.md). They do not execute these scenarios.

Before release, record tested commit, environment, fixture version, expected and
actual results, operator/reviewer and sanitized evidence path for every scenario.
A failure blocks its Must requirements. No real account payloads belong in Git.
Use unit/property tests for arithmetic, contract tests for provider behavior,
integration tests for authorization and storage, and human review for usability
and actual provider eligibility. Live provider checks run separately from public
or pull-request CI, with owner consent and minimum data.

## AC-001 — Independent identities and membership

Requirements: OH-001, OH-002

Status: Planned

Method: Integration + demonstration

Given A and B in one household, sign in separately and verify distinct actor IDs. Add synthetic member C without a schema change; revoke B and verify old sessions lose access. No shared application password is required.

## AC-002 — Authorization and default privacy

Requirements: OH-003, OH-004, OH-043

Status: Planned

Method: Integration + adversarial

Given private account A1, shared A2 and an unrelated household H2, request A1 through B and H2 by guessed IDs, export, search and aggregate routes. Every attempt is denied with no balance, existence detail or derived observation disclosed. A can explicitly share A1; B then sees only the granted scope. Newly discovered A3 stays private.

## AC-003 — Ownership versus access

Requirements: OH-005

Status: Planned

Method: Integration + demonstration

Import an account visible to A as an authorized bank user with no ownership metadata. Display ownership unknown, not A as owner. Record separately verified joint owners A and B without changing the consent holder. Neither lookup nor ownership annotation broadens application access.

## AC-004 — Actual bank feasibility

Requirements: OH-006, OH-007

Status: Planned

Method: Provider integration + owner demonstration

Record the provider terms and pricing applicable to two owners. Each owner completes their own bank authentication. Import known selected account balances and booked entries through the current Sparebanken Norge route; reconcile against bank-visible values at their observation times. Capture bank identifier, API/release version, coverage and redacted evidence. A sandbox-only run fails this release gate.

## AC-005 — Weekly and manual scheduling

Requirements: OH-008, OH-009

Status: Planned

Method: Integration with controlled clock

Advance a controlled clock fourteen days for two active connections: exactly two weekly jobs per connection become due. Overlap a manual trigger with a scheduled run; at most one run per connection proceeds. Simulate 429 with Retry-After, a restart and a transient timeout; honor quota/backoff, resume safely and do not generate duplicate imports. Expired consent generates no data-fetch request.

## AC-006 — Partial and stale observations

Requirements: OH-010, OH-011, OH-012

Status: Planned

Method: Integration + UI

Start with two complete account snapshots. Fail page two of an update: that account retains its previous full snapshot and last-success time. Allow the other account to succeed and show different observation times. Advance time beyond eight days or remove a required balance: label the combined value partial, list coverage and suppress definitive goal success. Unknown is not zero. A provider with no source timestamp displays that fact.

## AC-007 — Replay, lifecycle and source revisions

Requirements: OH-013, OH-015, OH-041

Status: Planned

Method: Contract + integration

Replay two pages and overlapping windows; stable source IDs yield one canonical booked entry. Transition a pending reservation to booked without counting both. Preserve a corrected source amount as a revision with provenance; a manual annotation never overwrites it. Where a provider supplies no stable identity, two distinct identical-amount purchases remain distinct or unresolved, never silently collapsed.

## AC-008 — Joint account identity

Requirements: OH-014

Status: Planned

Method: Integration

A and B each connect the same joint account containing NOK 10,000. A verified alias mapping produces one account and NOK 10,000, not NOK 20,000. Matching names or masked numbers alone do not merge accounts. Ambiguous duplicates are flagged and excluded from authoritative combined conclusions pending resolution.

## AC-009 — Money and currencies

Requirements: OH-016

Status: Planned

Method: Unit + property tests

Sum NOK 0.10 and NOK 0.20 to exactly NOK 0.30. Reject invalid scale, nonfinite or overflowing values. Keep NOK and EUR in separate totals; refuse EUR as goal funding in Phase 1. Verify negative balances, rounding of displayed percentages, large supported values and Europe/Oslo dates across a daylight-saving transition.

## AC-010 — Internal transfers

Requirements: OH-017

Status: Planned

Method: Unit + integration

Transfer NOK 1,000 between two included shared accounts: household income and expenses each change by zero. Transfer into a goal-designated account: goal balance may rise, while text does not call it newly earned income. An unconfirmed potential transfer remains explicitly unclassified; private account details cannot be inferred through explanations.

## AC-011 — Goal lifecycle and concurrent edits

Requirements: OH-018

Status: Planned

Method: Integration

Create a NOK 100,000 goal with and without a future target date. Reject zero/negative targets and a second active goal. Reject a past date on creation; allow a previously created goal to become overdue. Concurrent edits use version checks so one cannot silently overwrite the other. Archive and create a replacement while preserving permitted history.

## AC-012 — Goal arithmetic

Requirements: OH-019

Status: Planned

Method: Unit + integration

Designate two confirmed unique shared NOK accounts with booked balances 10,000 and 5,000 against a target of 20,000: current 15,000, remaining 5,000, progress 75%. Repeat with -1,000 and 5,000: current 4,000, remaining 16,000, progress 20%. At 25,000 show 125% and remaining zero. A missing input suppresses definitive completion. No pending amount or manual duplicate top-up is added.

## AC-013 — Comparable progress

Requirements: OH-020

Status: Planned

Method: Unit + integration

With unchanged funding accounts and complete snapshots fourteen days apart, current changes from 12,000 to 15,000: show +3,000 over the actual fourteen-day period. With only one snapshot show insufficient history. Add an account or withdraw sharing: end the prior comparison series, invalidate its shared derivatives where needed and start a new baseline; do not call the configuration change savings.

## AC-014 — Explainable observations

Requirements: OH-021

Status: Planned

Method: Demonstration + integration

Open the explanation for the +3,000 change and trace to both snapshot sets, timestamps and formula version. Show assumptions and unavailable history. For a goal with a date, distinguish required savings pace from prediction or affordability advice. Stale or partial inputs suppress positive on-track/completion conclusions; no external model is needed.

## AC-015 — No financial execution or prohibited secrets

Requirements: OH-022, OH-023

Status: Planned

Method: Architecture inspection + negative integration

Inspect routes, capabilities, dependencies and deployed credentials for the selected adapter. Attempt payment, transfer and trade requests through UI and API: no execution path or provider PIS capability exists. Dedicated secret-collection fields do not accept bank passwords, seed phrases or wallet keys. AIS authorization may use POST; an HTTP-method ban is not the control.

## AC-016 — Credential and log isolation

Requirements: OH-024, OH-025

Status: Planned

Method: Security integration

Use synthetic marked secrets, IBAN and transaction descriptions in success and failure paths. Browser responses, analysis storage and routine logs contain none. Connector credentials are encrypted at rest; an analysis/UI service identity cannot read the credential store or decryption key. A database-only backup cannot decrypt tokens without separately protected key material.

## AC-017 — Disconnect and unshare

Requirements: OH-026, OH-027

Status: Planned

Method: Integration with concurrent worker

Queue a sync then disconnect before the next provider request: the worker stops, including retries. Withdraw sharing while a dashboard request is pending: authorization is rechecked before response and affected shared caches, snapshots and observations are invalidated. Fresh direct/export requests cannot retrieve withdrawn data. Already downloaded copies cannot be recalled and the UI says so.

## AC-018 — Actionable connection status

Requirements: OH-028, OH-044

Status: Planned

Method: Integration + UI

Simulate consent expiry, temporary failure and recovery. Repeated failures update one in-app notice, distinguish last attempt from last success and link renewal to the correct owner. Unknown expiry never displays an invented renewal date. Recovery resolves the notice. A scheduler that stops entirely is detected by the independent health check.

## AC-019 — Outbound data boundary

Requirements: OH-029

Status: Planned

Method: Security integration

Exercise login, bank sync, overview, explanation and error handling while recording egress on a test deployment. Only approved identity and bank/provider endpoints are contacted with the documented minimum data; no external LLM, analytics, font or error-collection service receives financial content. Synthetic tests use no live credentials.

## AC-020 — Export, deletion and retention

Requirements: OH-030, OH-031

Status: Planned

Method: Integration + restore rehearsal

Export as A and B and confirm each receives only authorized records, versioned format and provenance, never tokens. Delete an account as an authorized owner after confirmation: live data and derivatives disappear within 24 hours. Restore a pre-deletion backup in isolation and replay the deletion ledger before serving requests. Expired backups are removed within the approved 30-day bound.

## AC-021 — Backup and migration recovery

Requirements: OH-032, OH-033

Status: Planned

Method: Operational rehearsal

On a clean host, restore an encrypted backup and separately protected keys or reconnect credentials, then verify balances, ownership, goals and deletion state. Measure elapsed time <=4 hours and missing committed-data interval <=24 hours. Inject a migration failure, restore the pre-upgrade backup with its compatible release and verify the same facts. Record versions and timings without real financial payloads.

## AC-022 — Cross-device and accessible journeys

Requirements: OH-034, OH-035

Status: Planned

Method: Browser + manual accessibility

Complete login, consent return, overview, goal editing and renewal on the current stable Android Chrome, iOS Safari and desktop Firefox at release. Record exact versions. At 360 CSS pixels the page does not scroll horizontally. Review applicable WCAG 2.2 AA criteria, keyboard navigation, visible focus, labels, screen-reader announcements and error recovery; record each applicable criterion and result.

## AC-023 — Self-hosting and performance

Requirements: OH-036, OH-040

Status: Planned

Method: Operational + load test

Install from the reviewed runbook on the reference host in operations.md. Load synthetic 100,000 transactions and 20 accounts; with two authenticated users make 200 overview requests after warmup. p95 server latency is <=1 second, response-error count is zero and the overview performs no synchronous bank call. Disconnect the provider and keep the local overview usable with stale-state warnings.

## AC-024 — Replaceable provider contract

Requirements: OH-037

Status: Planned

Method: Contract + architecture inspection

Run the same normalization, pagination, retry, quota, revocation and reconciliation suite against synthetic and selected adapters. Replace the adapter behind the contract; goal-rule source files stay unchanged. Record supported and unsupported capabilities explicitly. Provider-specific objects never reach domain calculations.

## AC-025 — Auditability

Requirements: OH-038

Status: Planned

Method: Integration

Create and edit a goal, share/unshare, connect/disconnect and delete synthetic data. Each accepted change has actor ID, UTC time, action, opaque object ID and result. Rejected changes do not appear successful. Audit output has no token, amount, payee, account number or transaction payload. Validate the reviewed retention period.

## AC-026 — Identity and request protection

Requirements: OH-039

Status: Planned

Method: Security integration + review

Using the selected mature identity component, verify single-use invitation, closed registration, HTTPS, secure HttpOnly cookies, CSRF/origin defenses for changes, rotation on login, logout revocation, idle and absolute expiry, rate limiting and object-level authorization. Replayed bank callback state and callbacks bound to another identity fail without attaching an account. Complete and record the applicable ASVS 5.0.0 Level 2 control assessment.

## AC-027 — Bank migration and reconsent

Requirements: OH-042

Status: Planned

Method: Contract + provider integration

Replace the legacy Sør institution/consent with the verified continuing route. Match accounts using verified identity mappings, overlap historical retrieval and confirm no doubled balances or entries. Where identity is not provable, flag reconciliation and preserve last valid data. Demonstrate renewal separately for each owner and document current bank routing before live release.
