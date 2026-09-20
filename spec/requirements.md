# Phase 1 requirement register

Status: proposed. All rows are **Must** for the Phase 1 release. Numeric policies
and added safeguards require owner approval with the v0.2 baseline. Parent needs
are defined in [SPEC.md](../SPEC.md). Each statement is read as “OpenHousehold shall …”.
Domain and operations references are local normative details of this proposal.

| ID | Need | Priority | Requirement | Rationale | Verification |
| --- | --- | --- | --- | --- | --- |
| OH-001 | N-01 | Must | Authenticate each adult with a distinct application identity. | Avoid shared credentials and ambiguous attribution. | AC-001 |
| OH-002 | N-01 | Must | Represent household membership without a fixed two-person schema limit. | Preserve future household membership without building hosted multi-tenancy. | AC-001 |
| OH-003 | N-05 | Must | Deny access to an account unless an active ownership/access relationship or sharing grant authorizes the requesting member. | Authentication alone does not authorize financial access. | AC-002 |
| OH-004 | N-05 | Must | Keep newly discovered accounts private until their authorized contributor explicitly shares them. | Bank consent is not household sharing consent. | AC-002 |
| OH-005 | N-01 | Must | Display known legal owners separately from the people who authorized bank access, including an unknown-ownership state. | Bank access need not imply legal ownership. | AC-003 |
| OH-006 | N-02 | Must | Associate every bank connection with the individual who independently authorized it. | One owner cannot impersonate the other. | AC-004 |
| OH-007 | N-02 | Must | Import balances and booked transactions from the verified Sparebanken Norge route for each participating owner. | A supported bank name alone is insufficient evidence. | AC-004 |
| OH-008 | N-02 | Must | Attempt one unattended refresh per active connection every seven days, subject to provider quotas and valid consent. | Weekly automation is the primary collection requirement. | AC-005 |
| OH-009 | N-02 | Must | Expose an idempotent manual refresh using the same quota and concurrency controls as scheduled refresh. | Allow recovery without creating a second import path. | AC-005 |
| OH-010 | N-02 | Must | Retain the last complete account snapshot when a refresh fails before atomic publication. | A partial import must not corrupt the visible account. | AC-006 |
| OH-011 | N-02 | Must | Display each account balance with source time when supplied, retrieval time, balance kind and connection health. | Users must understand what observation they are seeing. | AC-006 |
| OH-012 | N-03 | Must | Mark a shared calculation partial when a required account is missing, ambiguous or has not been refreshed within eight days. | Incomplete totals must not masquerade as complete finances. | AC-006 |
| OH-013 | N-02 | Must | Prevent a retried or overlapping import from duplicating the same source transaction. | Retries are expected in banking networks. | AC-007 |
| OH-014 | N-01 | Must | Count a jointly visible bank account once in household calculations after verified canonical-account matching. | Separate consent must not double the household balance. | AC-008 |
| OH-015 | N-03 | Must | Exclude pending transactions from booked progress and booked cash-flow calculations. | Reservations can change or disappear. | AC-007 |
| OH-016 | N-03 | Must | Calculate monetary results with exact fixed-point arithmetic in explicitly identified currencies. | Floating-point rounding or implicit FX can change financial results. | AC-009 |
| OH-017 | N-03 | Must | Exclude confirmed transfers between included household accounts from household income and expense totals. | Moving existing money is not household income. | AC-010 |
| OH-018 | N-03 | Must | Support exactly one active household savings goal with a positive NOK target and an optional target date. | Keep the first decision scenario bounded. | AC-011 |
| OH-019 | N-03 | Must | Calculate goal progress according to the dedicated-account rules in domain.md. | Give progress one reproducible meaning. | AC-012 |
| OH-020 | N-03 | Must | Compare goal progress only between complete observations with the same funding-account configuration. | Funding changes and missing accounts cannot be presented as savings. | AC-013 |
| OH-021 | N-03 | Must | Explain each progress observation using its input snapshots, calculation rule, observation period and limitations. | People need to understand the evidence. | AC-014 |
| OH-022 | N-04 | Must | Exclude financial transaction execution capabilities from the deployed Phase 1 application. | Human approval alone would not meet the read-only requirement. | AC-015 |
| OH-023 | N-05 | Must | Reject banking passwords, crypto seed phrases and wallet private keys as application inputs or stored credentials. | These secrets are unnecessary for AIS. | AC-015 |
| OH-024 | N-05 | Must | Restrict decryptable provider credentials to the connector execution boundary. | Presentation and analysis do not need bank tokens. | AC-016 |
| OH-025 | N-05 | Must | Exclude financial payloads, credentials and account identifiers from routine telemetry and error logs. | Operational diagnostics must not become a second financial database. | AC-016 |
| OH-026 | N-05 | Must | Stop use of a revoked or disconnected bank connection before its next provider request. | Revocation must affect background work as well as the UI. | AC-017 |
| OH-027 | N-05 | Must | Remove a withdrawn sharing grant from shared queries and derived views before the next response to a household member. | Old totals and observations can reveal unshared information. | AC-017 |
| OH-028 | N-07 | Must | Show one actionable in-app notice per unresolved connection problem without duplicating it on retries. | Users need renewal and failure guidance without notification noise. | AC-018 |
| OH-029 | N-05 | Must | Keep financial data within the self-hosted deployment except for the explicitly configured bank/provider exchange. | No external LLM, analytics or error-reporting data transfer in Phase 1. | AC-019 |
| OH-030 | N-06 | Must | Export authorized normalized financial data, provenance and goal configuration in a documented versioned format. | Users need portability independent of a provider or application. | AC-020 |
| OH-031 | N-05 | Must | Delete an authorized account or household dataset according to the reviewed retention and deletion policy. | Disconnection and deletion are distinct actions. | AC-020 |
| OH-032 | N-06 | Must | Restore the household deployment from encrypted backup within four hours with at most 24 hours of lost committed data. | Proposed small-household recovery targets; owner review required. | AC-021 |
| OH-033 | N-06 | Must | Keep schema migration failure from making the last validated backup unusable. | Upgrades require a recovery path. | AC-021 |
| OH-034 | N-07 | Must | Provide the included journeys in Norwegian Bokmål on mobile and desktop without horizontal page scrolling at 360 CSS pixels. | Both household members need a usable initial interface. | AC-022 |
| OH-035 | N-07 | Must | Meet applicable WCAG 2.2 AA criteria for login, connection, overview and goal journeys. | Accessibility is testable beyond visual design. | AC-022 |
| OH-036 | N-06 | Must | Return authenticated local overview responses within one second at the 95th percentile under the performance profile in operations.md. | The page should remain usable without waiting for the bank. | AC-023 |
| OH-037 | N-08 | Must | Pass the provider contract suite using both a synthetic adapter and the selected bank adapter without changing goal calculation rules. | Make replaceability demonstrable. | AC-024 |
| OH-038 | N-06 | Must | Record security-relevant connection, sharing and goal changes with actor, time, action and opaque object ID. | Trace configuration changes without copying account contents into logs. | AC-025 |
| OH-039 | N-05 | Must | Protect authenticated sessions and state-changing requests according to the reviewed identity policy. | Web threats remain relevant to a read-only financial app. | AC-026 |
| OH-040 | N-06 | Must | Install and operate on one documented Linux host without a mandatory proprietary analytics or application-hosting service. | Self-hosting includes repeatable operations. | AC-023 |
| OH-041 | N-03 | Must | Preserve source financial observations separately from user annotations and later source revisions. | Manual edits must not silently replace bank facts. | AC-007 |
| OH-042 | N-02 | Must | Preserve canonical account identity and transaction deduplication when a bank route or consent is replaced. | The announced bank migration makes reconnect a first-phase concern. | AC-027 |
| OH-043 | N-03 | Must | Suppress shared financial conclusions that depend on private or withdrawn accounts. | Aggregates can disclose information even without listing the accounts. | AC-002 |
| OH-044 | N-06 | Must | Expose separate last-attempt and last-success status for each connection. | Successful scheduling does not prove successful data collection. | AC-018 |

See [acceptance scenarios](acceptance.md), [domain rules](domain.md),
[operations](operations.md) and [interface contracts](interfaces.md). Each scenario
links back to its requirements. CI checks both directions; planned is not passed.
