# OpenHousehold — software requirements specification

Version: 0.2 · Date: 2026-09-20 · Status: **proposed, awaiting owner review**

## 1. Purpose and authority

OpenHousehold helps a household understand its finances and progress toward a
shared savings goal. Collection is automated where feasible; consequential
financial decisions remain with people. This repository contains a specification
and validation tools, not an implemented financial application.

The [original voice-session draft](docs/source/voice-spec-v0.1.md) is preserved
verbatim as received after the project rename. The [review](docs/review.md)
explains what needed clarification. This version supersedes that draft for
design discussion; it is not an owner-approved implementation baseline.

[Requirements](spec/requirements.md) become the normative product contract once
approved. “Shall” expresses a requirement. Architecture describes a candidate
solution. The entire v0.2 baseline, including numeric targets and derived privacy
policies, is proposed until approval; none of those additions is attributed to
the voice conversation.

## 2. Stakeholders and needs

Roy and the second adult are product owners. Both approve shared-finance and
privacy semantics. The maintainer implements and operates the chosen design.
Account ownership, permission to access an account at a bank, and permission to
share it in OpenHousehold are separate relationships.

| Need | Outcome | Origin in original draft |
| --- | --- | --- |
| N-01 | Two adults understand a shared view without losing ownership. | Sections 2, 3, 9, 17 |
| N-02 | Sparebanken Norge data updates weekly with little manual work. | Sections 4, 17 |
| N-03 | One shared savings goal has correct, understandable progress. | Sections 4, 8, 17 |
| N-04 | People retain control; Phase 1 cannot move money. | Sections 4, 5, 15, 16 |
| N-05 | Sensitive information, consent and credentials are protected. | Sections 9, 12, 18 |
| N-06 | Self-hosting, recovery and maintenance are practical. | Sections 10, 11, 12, 18 |
| N-07 | Both adults can use mobile and desktop browsers. | Sections 3, 13, 14 |
| N-08 | Later financial domains can be added without provider lock-in. | Sections 6–11, 17 |

## 3. Scope and environment

Phase 1 serves one self-hosted household with two independent adult logins.
Membership is a collection without a hard-coded two-user limit. Hosting unrelated
households as a service is outside Phase 1. Isolation tests still use a synthetic
second household to detect accidental data leakage.

Included: read-only bank account information, balances and booked transactions;
independent consents; explicit account sharing; one active savings goal; weekly
collection; freshness and coverage; reproducible progress observations; in-app
connection notices; export, deletion and tested recovery. Proposed initial locale:
Norwegian Bokmål, NOK goal calculations and Europe/Oslo calendar dates. Currency
and timezone remain explicit in data.

Excluded: payments, trading, automatic debt payments, tax submission, native
mobile apps, automatic asset valuation, sophisticated forecasts and external LLM
processing. Mortgage, investment, insurance, tax, crypto and nonfinancial assets
remain extension directions, not Phase 1 implementation tasks.

Bank feasibility is a release gate. The bank announces migration of the former
Sør PSD2 interface on 9 October 2026. Provider coverage, two-owner terms, history
and renewal must be demonstrated for the actual accounts. A manual import can
support an explicitly approved interim pilot; it cannot satisfy the automated
weekly-bank acceptance gate. See [research](docs/research.md).

## 4. Primary journey

1. Each adult signs in separately and joins the household.
2. Each connects their banking relationship through independent provider consent.
3. Each selects which accounts to share after seeing the data-sharing scope.
   Newly discovered accounts remain private until explicitly shared.
4. The shared view shows deduplicated accounts, owners, balances and freshness.
   Private accounts do not influence shared totals or observations.
5. The adults define one savings goal and dedicate selected shared accounts to it.
6. Weekly collection refreshes the view. Failed updates retain previous valid
   data with a warning rather than replacing it with zero.
7. Progress is explained from comparable data. People decide what to do.

See [domain rules](spec/domain.md) for the proposed goal and sharing semantics.
These policies require the decisions recorded as Q-01 and Q-02.

## 5. Specification set

| Document | Responsibility |
| --- | --- |
| [Requirements](spec/requirements.md) | Stable IDs, parent needs, rationale and verification links |
| [Acceptance plan](spec/acceptance.md) | Observable pass/fail scenarios; product checks currently planned |
| [Domain model](spec/domain.md) | Money, ownership, goal formulas and lifecycle semantics |
| [Interfaces](spec/interfaces.md) | Provider contract, failure handling and API constraints |
| [Architecture](spec/architecture.md) | Tailored arc42 views, deployment and alternatives |
| [Threat model](spec/threat-model.md) | Trust boundaries, threats and verification |
| [Operations](spec/operations.md) | Retention, restore, monitoring and incident procedures |
| [Open questions](docs/open-questions.md) | Owners, recommendations and decision triggers |
| [Decisions](decisions/README.md) | Rationale and status of design and process choices |
| [Delivery plan](docs/delivery-plan.md) | Review and implementation gates |

## 6. Quality and verification

The requirements use unique IDs, rationale and verifiable outcomes, informed by
ISO/IEC/IEEE 29148:2018 and NASA's public requirements guidance. Architecture uses
a tailored arc42 structure. Security work references OWASP threat modeling and
ASVS 5.0.0. Accessibility targets WCAG 2.2 AA for the included journeys.
See [standards and tailoring](docs/standards.md).

No certification or full standards conformance is claimed. The public ISO catalog
was consulted; the full paid standard was not audited. Documentation checks prove
traceability and repository integrity, not financial correctness or security.
All product acceptance scenarios remain planned until implemented and run.

## 7. Baseline, release and change control

Before implementation, the owners review v0.2 and the proposed architecture and
resolve baseline blockers in the question register. Record approved commit,
decisions, reviewers and date. Before real data, bank feasibility and security
gates must pass. Every Must requirement needs passing revision-specific evidence
before Phase 1 release.

IDs are permanent; do not renumber to close gaps. A change updates the affected
requirement, scenario, decision and changelog together. Retired requirements keep
their IDs and reasons. Future scope enters through a reviewed specification change.

## 8. Glossary

**AIS:** account information services. **PIS:** payment initiation services.
**Consent:** one person's bank/provider authorization. **Sharing grant:**
permission to expose an account inside the household. **Canonical account:** one
internal identity for a real account across connections. **Booked balance:** bank
balance excluding pending reservations. **Snapshot:** immutable observation with
source and retrieval times. **Stale:** beyond the agreed freshness threshold.
**Partial:** required sources are missing, stale or unresolved. **ADR:**
architecture decision record. **RPO:** maximum lost-data interval. **RTO:** maximum
recovery time.
