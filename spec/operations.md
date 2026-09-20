# Proposed operational policy

All thresholds are review proposals (Q-05/Q-06), not existing service guarantees.
Requirements and scenarios define the release checks.

## Deployment and identity

Reference performance host: Linux, 2 CPU cores, 4 GiB RAM, SSD storage, local
application/database network. Dataset: 20 accounts and 100,000 synthetic booked
transactions. Two authenticated users, 200 overview requests after 20 warmup
requests; measure server p95 <=1 second and zero response errors. Bank latency is
excluded because the overview reads local published data. Record hardware,
release, test fixture and measurement method with results.

Use a mature authentication/session implementation. Proposed policy: invite-only
membership; invitation expires in 24 hours and is single-use; 30-minute session
idle expiry; 12-hour absolute expiry; rotation at login; immediate logout and
membership revocation. Rate limits start at five failed login attempts per
identity/IP in fifteen minutes, with bounded recovery and no permanent lockout.
An external OIDC provider is optional; local identity remains an option. Validate
exact choices in Q-04 before implementation, including account recovery and MFA.

## Retention and deletion

| Data | Proposed lifetime | Enforcement |
| --- | --- | --- |
| Normalized financial observations and goal history | While the account is retained by its owner | Account deletion removes live records and derived data within 24 hours. |
| Complete raw provider payloads | Not persistently retained by default | Normalize in memory/staging; retain minimal necessary source evidence. |
| Temporary encrypted import staging | At most 24 hours after a failed/finished run | Cleanup job; no tokens in payload storage. |
| Routine sanitized operational logs | 30 days | Rotation/expiry, never account contents. |
| Metadata-only audit events | 90 days | Access-controlled retention with opaque IDs. |
| Encrypted backups | 30 days | Expiry on backup destination, deletion replay on restore. |
| Deletion ledger | 31 days after live deletion completes | Opaque IDs only; protected independently of restorable data. |
| Revoked connection credentials | Delete after revocation succeeds or within 24 hours locally | Never reuse during provider revocation retries. |

Preserve minimal original fields and content hashes for reconciliation when
needed; a hash alone cannot reproduce a normalized value. Document fields and
mapping versions without keeping full bank responses by default. Retention
changes require explicit review, including whether provider terms impose limits.
Deleting one connection does not delete a canonical account still validly
contributed by another person. Account ownership and deletion authority must be
resolved before applying the policy to a joint account.

## Backup, restoration and upgrades

Target RPO 24 hours and RTO four hours. Take encrypted daily backups of financial
records, goal/configuration revisions and schema metadata. Protect keys separately;
a backup without a key/reconnection procedure is not a recovery strategy. Keep
the deletion ledger in a separately protected current location, and back it up
so a data restore cannot resurrect deleted records.

Restore runbook to implement and rehearse:

1. Start the pinned compatible application/database release on an isolated host.
2. Restore encrypted data using separately recovered keys; keep user ingress and
   provider egress disabled.
3. Replay all deletions after the backup timestamp, including related derivatives.
   If the current deletion ledger is unavailable, fail closed until reconstructed.
4. Check schema version, integrity, identity mappings, ownership and goal fixtures.
5. Reauthorize connections when credential recovery is unavailable or unsafe.
6. Re-enable access after checks, then scheduler; record measured RPO/RTO.

Before each schema upgrade, create and validate a recoverable backup. On failure,
restore with the prior compatible release rather than trusting an untested reverse
migration. Rehearse recovery before live use and after changes to storage or keys.

## Monitoring and incidents

Track per-connection due time, last attempt, last success, error category and
coverage. A daily health process independent of the scheduler checks whether
jobs stopped running; show unresolved notices in the app. Add external delivery
only after channel preferences are approved. In-app notices alone cannot reach
users while the host is down; the operator is responsible for host/backup health.

On credential exposure: pause the affected connector, revoke at the provider,
rotate keys, preserve sanitized incident metadata and assess affected access.
On corrupted/duplicate data: stop publication, retain last complete snapshots,
reconcile in staging, then publish only after invariants pass. Never fix balances
by editing bank source facts without a recorded correction.
