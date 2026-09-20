# Initial threat model

Status: design review, no mitigations verified in a product implementation.
Method: trust-boundary analysis and STRIDE-inspired scenarios following
[OWASP guidance](https://cheatsheetseries.owasp.org/cheatsheets/Threat_Modeling_Cheat_Sheet.html).

Assets: financial records, ownership/sharing metadata, identity sessions, consent
credentials, provider signing keys, goal configuration, backups and deletion state.
Actors: two adults, host operator, identity/provider/bank services, unauthenticated
attacker, compromised member/browser and compromised dependency.

Trust boundaries: browser -> application; user/household authorization boundaries;
application -> connector credential store; connector -> provider -> bank; storage
-> backup destination; source/dependencies -> build/runtime. See the
[architecture diagram](architecture.md) for data flow.

| Threat | Impact | Proposed mitigation | Verification | Residual risk / owner |
| --- | --- | --- | --- | --- |
| T-01 Guessed account IDs or cached shared totals | Private-data disclosure | Server-side object authorization and derivative invalidation | AC-002, AC-017 | Exported copies cannot be recalled; owners approve sharing scope. |
| T-02 Stolen session or forged bank callback | Account takeover or connection attached to wrong user | Mature sessions, single-use bound state, CSRF and origin checks | AC-026 | Compromised user device; operator and owners choose MFA/recovery. |
| T-03 Token in logs, browser or database dump | Unauthorized bank reads | Credential boundary, separate keys, redaction and minimal scopes | AC-016 | Compromised host/root sees runtime plaintext; operator. |
| T-04 Malformed bank description or import payload | Injection, XSS, corrupted facts | Treat data as untrusted, output encoding, bounded validation and parameterized queries | AC-007, AC-026 | Provider still supplies potentially incorrect data; maintainer. |
| T-05 Replay, concurrent sync or partial import | Incorrect balances or repeated entries | Leases/fencing, idempotency and atomic account publication | AC-005, AC-006, AC-007 | Ambiguous provider identity requires reconciliation; maintainer. |
| T-06 Joint account counted twice | False savings progress | Evidenced canonical mapping, quarantine uncertain matches | AC-008, AC-027 | Identity metadata can be insufficient; owners confirm evidence. |
| T-07 Revoked consent used by queued worker | Continued unauthorized collection | State checks before requests and publication | AC-017 | Already in-flight requests may complete but cannot publish after revocation; maintainer. |
| T-08 Backup loss, ransomware or lost key | Lost household data | Separate encrypted backup, key recovery and restore rehearsal | AC-021 | Operator access/host compromise; operator. |
| T-09 Old backup resurrects deleted data | Privacy violation | Current deletion ledger replay before serving | AC-020, AC-021 | Backup copies outside configured control; operator. |
| T-10 Provider outage or stale source | Misleading financial advice | Freshness/coverage, partial states and bounded retry | AC-006, AC-014, AC-018 | Provider availability is external; owners accept limits. |
| T-11 Accidental payment capability | Money moved despite read-only scope | AIS-only contract and credentials; omit all execution routes | AC-015 | Future dependencies may broaden capabilities; maintainer reviews changes. |
| T-12 Supply-chain compromise | Exfiltration or unauthorized code | Pin versions/actions, least-privilege CI, dependency review and secret hygiene | AC-019, AC-026 | Signed/pinned code can still be malicious; maintainer. |
| T-13 External model/telemetry disclosure | Sensitive data leaves household | No external financial-data processors in Phase 1, egress review | AC-019 | Identity/provider metadata exists externally by design; owners. |
| T-14 Resource exhaustion | Unusable app or expensive provider traffic | Import size bounds, pagination limits, quotas and request limits | AC-005, AC-023, AC-026 | Host/network outage; operator. |

Before live use, the maintainer maps applicable ASVS **5.0.0** Level 2 controls to
versioned control IDs, scenarios and evidence, explains exclusions, and resolves
high-impact unmitigated risks with the owners. A prose table is not an ASVS pass.
Expand security tests for malformed inputs and supply-chain configuration during
implementation. No automatic release is allowed just because document checks pass.

Revisit this model when changing provider, identity, sharing, storage, deployment,
external processing or introducing financial actions. Write-capable features
require a new explicit owner decision, threat review and separate authorization
design. They are outside this baseline.
