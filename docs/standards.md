# Standards and deliberate tailoring

Reviewed 2026-09-20. No single specification template is universally best. This
repository combines requirements, architecture, decisions and executable checks.

| Reference | Application here | Limit |
| --- | --- | --- |
| [ISO/IEC/IEEE 29148:2018](https://www.iso.org/standard/72089.html) | Requirements engineering reference: purpose, scope, constraints, interfaces, verification. | Public catalog consulted, no audit of the complete paid standard or compliance claim. |
| [NASA requirements checklist](https://www.nasa.gov/reference/appendix-c-how-to-write-a-good-requirement/) | Unique IDs, verifiable obligations, rationale and traceability. | Writing guidance rather than aerospace process overhead. |
| [arc42](https://arc42.org/overview/) | Twelve sections scaled to the proposed architecture. | Reference other spec documents rather than duplicate policies. |
| [OWASP ASVS](https://owasp.org/projects/asvs) | Version 5.0.0, with Level 2 applicability assessment before live data. | Threat model is not a completed ASVS audit; versioned control mapping is a delivery gate. |
| [OWASP threat modeling](https://cheatsheetseries.owasp.org/cheatsheets/Threat_Modeling_Cheat_Sheet.html) | Assets, boundaries, threats, mitigations, residual risk and verification. | Describing a mitigation does not close a threat. |
| [WCAG 2.2](https://www.w3.org/TR/WCAG22/) | AA target for included user journeys. | Manual assistive-technology checks required alongside automation. |
| [Conventional Commits](https://www.conventionalcommits.org/en/v1.0.0/) | Typed, short commit subjects. | Only the subset documented in CONTRIBUTING is enforced. |

The local start-repo skill was read and its scaffold script run in dry-run mode.
CI, decisions, deferred work and verification follow its repository principles.
The generated Python application package, sample CLI and product skeleton were
omitted because the original specification requires design review before product
code. Python only validates this repository; it does not choose the product stack.
Forge protections and remote CI are reported according to observed state.
