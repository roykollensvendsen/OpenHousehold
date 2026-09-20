# Delivery plan and review gates

## G0 — specification repository (this delivery)

Preserve the original draft; document review findings; publish requirements,
scenarios, proposed architecture and threat model; validate links and traceability;
initialize local history and a private GitHub remote. This is repository work,
not a working financial product.

## G1 — owner-approved baseline

Resolve baseline questions in the question register. Perform comparable synthetic
reuse trials and obtain current provider eligibility evidence. Record product
choices, accepted/proposed ADR status, reviewers, date and exact approved commit.
Any provider-specific prototype using live data first satisfies G2. Product
implementation starts only after explicit owner review of spec and architecture.

## G2 — permission to process real data

Each adult authorizes their own bank connection. Confirm pricing/terms and current
bank route, assess ASVS controls, implement/verify authorization, secret handling,
retention and restoration. Record the initial applicable threat review. No live
credentials enter Git or ordinary pull-request CI.

## G3 — first complete implementation slice

After G1, build one end-to-end synthetic scenario: independent user -> synthetic
bank observation -> canonical storage -> shared authorized goal view -> explained
progress. Reuse an existing product if selected. This is the first product walking
skeleton; it is intentionally absent from the specification-only delivery.
Tests for money, authorization, duplicate imports and failure recovery precede
reliance on the behavior. Demonstrate that critical tests fail for the defects
they are meant to catch.

## G4 — real weekly household pilot

After G2 and synthetic tests, connect both owners, preserve joint-account identity,
renew separately and exercise the announced migration path. Observe at least two
scheduled refreshes one week apart, verify correctness and document manual work.
Simulated clocks test scheduling but do not prove real-world provider reliability.

## G5 — Phase 1 release

All 44 Must requirements have passing revision-specific evidence through the
acceptance scenarios. Rehearse restore, verify mobile/accessibility journeys,
review user comprehension with both adults, and resolve critical security risks.
Record browser/provider/runtime versions. No product requirement becomes passed
because a documentation check succeeds.

Reassess scope if feasibility fails. Every subsequent slice preserves the
working authorized read-only journey. Future modules follow deferred triggers.
