# Decisions requiring owner review

Status: all questions open. Recommendations below do not constitute approval.
Roy and the second adult approve product/privacy choices. The maintainer proposes
technical decisions and records evidence. “Baseline” means before product code;
“Live” means before real bank data; “Release” means before Phase 1 acceptance.

| ID | Kind | Decision and proposed default | Owner | Gate / closure evidence |
| --- | --- | --- | --- | --- |
| Q-01 | Product | Full balances of dedicated accounts fund one goal. If partial allocations are needed, revise the calculation model. | Both adults | Baseline: approve examples in domain.md. |
| Q-02 | Product/privacy | Private by default; explicit full-account sharing; independent grants for joint accounts; withdrawals remove derived shared history. | Both adults | Baseline: approve sharing, joint-account deletion authority and trusted host operator. |
| Q-03 | Product/access | Select eligible AIS provider for both adults and approve any cost; no assumed free shared access. | Roy and each account holder | Before provider-specific implementation: terms and coverage evidence; Live: successful independent consents. |
| Q-04 | Architecture/security | Mature invite-only authentication; choose local identity or OIDC, MFA and recovery. | Maintainer + both adults | Baseline: approved identity/session/recovery policy. |
| Q-05 | Product/privacy | Retain normalized data until deletion; raw payloads ephemeral; logs 30 days, audit 90, backups 30; RPO 24h/RTO 4h. | Both adults + operator | Baseline: approve retention and deletion of joint information; Live: restore proof. |
| Q-06 | Architecture/operations | One Linux host, private network with HTTPS, modular app + isolated connector; PostgreSQL candidate subject to reuse result. | Maintainer + Roy | Baseline: host resources and stack/deployment ADR, including key recovery. |
| Q-07 | Architecture/reuse | Trial Actual and Firefly against the same mandatory scenarios; adopt if sufficient, otherwise document need for a small core. | Maintainer + Roy | Baseline: evidence and selected foundation in ADR-002. |
| Q-08 | Product/scope | Manual import only as separately approved interim pilot if bank access is blocked. | Both adults | When automated access is infeasible: amended scope; never silently mark bank acceptance passed. |
| Q-09 | Product/UX | Norwegian Bokmål, NOK goals, Europe/Oslo, in-app notices initially. | Both adults | Baseline: confirm locale and notice expectations, including host-down limitations. |
| Q-10 | Release/security | Applicable ASVS 5.0.0 Level 2 controls and accepted residual risks. | Maintainer + owners | Live: versioned mapping, verification evidence and recorded risk acceptance. |

Publication choice is settled by the user's latest instruction: **public GitHub repo**.
The project name is settled: **OpenHousehold**. Neither decision approves product
implementation or bank access. No credentials or household financial records are
needed to review this baseline.
