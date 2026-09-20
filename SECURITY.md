# Security

No deployed financial application or supported product release exists yet.
The [threat model](spec/threat-model.md) is proposed design, not an audit result.

Report a sensitive issue directly to repository owner Roy through an established
private channel, or GitHub private vulnerability reporting if enabled. Do not
include credentials or real financial payloads in issues, commits or screenshots.
No dedicated public reporting mailbox or response-time guarantee is configured.

If a credential is exposed, revoke/rotate it at its issuer immediately and assess
where it was copied. Deleting a Git file alone does not remove historical exposure.
No automatic scanning tool guarantees that sensitive material is absent.

For future releases, assess applicable ASVS 5.0.0 Level 2 controls before live
financial data. Authorization, backup restoration and read-only capability checks
are mandatory design gates, with evidence recorded outside sensitive payloads.
