# OpenHousehold --- Product Specification

**Version:** 0.1\
**Status:** Draft for review\
**Purpose:** Initial specification for critique by Codex before
implementation.

## 1. Vision

Build a privacy-conscious, modular family-finance system that gives a
household a clear and understandable view of its finances and helps the
household make better financial decisions.

Automation should reduce manual work, but humans remain in control of
important financial decisions.

The project should be designed so that it can later be useful to other
households, with replaceable integrations for different banks, brokers,
crypto systems, and other data sources.

## 2. Primary goals

1.  Give both adults a shared, comprehensible view of household
    finances.
2.  Keep the overview updated with as little manual work as practical.
3.  Help identify concrete opportunities to improve the household's
    finances.
4.  Support planning toward financial goals.
5.  Eventually cover cash flow, debt, investments, assets, insurance,
    taxes, and other relevant financial information.
6.  Preserve explicit human approval for important decisions and
    financial actions.
7.  Prefer reuse of mature open-source components over rebuilding
    existing functionality.

## 3. Users

### Initial users

Two adults in one household.

Both should eventually be able to authenticate separately and contribute
their own financial accounts to one shared household view.

### Future users

The data model should not assume exactly two users. Additional household
members may be supported later.

## 4. Phase 1 --- first useful vertical slice

Phase 1 should deliberately be small.

### Required data source

**Sparebanken Norge** (formerly Sparebanken Sør) is the required first
financial data source.

The preferred approach is automated read-only account aggregation
through an appropriate Open Banking / PSD2 integration where feasible.

Each bank-account owner must authenticate and consent independently
where required.

### Refresh frequency

Weekly synchronization is sufficient for the initial product.

Real-time synchronization is not a Phase 1 requirement.

### Financial actions

Phase 1 is read-only.

The system must not initiate payments, transfers, trades, or other
financial transactions.

### First decision scenario

The first complete user scenario is:

**Saving toward one shared financial goal.**

The household should be able to:

-   define one savings goal;
-   specify a target amount and, optionally, a target date;
-   see current progress;
-   understand recent progress based on actual financial data;
-   receive useful observations or suggestions;
-   make the decisions themselves.

Supporting multiple simultaneous goals can come later.

## 5. Human decision-making

The system is intended to advise and inform, not silently make
consequential financial decisions.

Recommendations should explain the relevant evidence and assumptions.

Future transaction capabilities may be considered, but consequential
actions should require explicit user approval unless a narrowly scoped
automation has been deliberately configured by the users.

Examples of possible future actions include transfers to savings, debt
payments, and investment transactions. These are explicitly outside
Phase 1.

## 6. Household assets

The long-term overview should include assets that are not bank accounts.

Known asset categories include:

-   home/property;
-   car;
-   boat.

These values do not require frequent automated updates. An annual manual
valuation is acceptable initially.

The architecture should allow additional asset types later.

## 7. Future financial scope

The following areas are important but are not required for the first
vertical slice.

### Debt

The system should eventually provide an overview of debt and help
evaluate debt-reduction strategies.

The household's mortgage is currently associated with the primary bank
relationship.

### Investments

Future integrations should include investment holdings, including
Nordnet and other externally held shares.

The system should eventually help analyze investment allocation, while
leaving investment decisions to the users.

### Cryptocurrency

Future scope includes cryptocurrency acquired through services such as
NBX and assets held in self-custody, including Ledger-managed wallets
and Bittensor holdings.

Where possible, public blockchain data should be used without exposing
private keys or seed phrases.

### Insurance

Insurance policies, premiums, coverage, and relevant renewal information
should eventually be included in the household overview.

### Tax and public-sector information

Potential future integrations or imports may include relevant
information from Skatteetaten and public/municipal charges.

These should be evaluated separately because access mechanisms,
permissions, and update frequencies differ from ordinary banking data.

## 8. Financial improvement and analysis

The long-term product should do more than display balances.

It should help the household discover ways to improve its finances.

Potential analysis areas include:

-   savings opportunities;
-   spending patterns and unusually high spending;
-   recurring expenses;
-   debt-repayment alternatives;
-   progress toward goals;
-   investment allocation;
-   cash-flow forecasts;
-   changes in net worth;
-   scenario analysis.

Recommendations must distinguish observations from assumptions and
recommendations.

Users should be able to understand why a recommendation was produced.

## 9. Shared household model

The system should distinguish between:

-   individual users;
-   individually owned accounts/assets;
-   jointly owned accounts/assets;
-   the household as a shared analytical view.

Ownership must not be lost merely because information is aggregated into
one household dashboard.

This is particularly important for bank authorization and future
transaction permissions.

## 10. Architecture principles

### Modular integrations

External systems should be connected through adapters/connectors behind
stable internal interfaces.

A bank-specific implementation should not leak throughout the
application.

Likewise, brokers, blockchain sources, asset valuations, tax imports,
and other sources should be replaceable modules.

### Separate ingestion from analysis

Data acquisition, normalization, storage, analysis, recommendation
generation, presentation, and action execution should be separate
concerns.

### Canonical financial model

Imported data should be normalized into a provider-independent internal
model.

At minimum, future modeling should consider:

-   users;
-   households;
-   institutions/providers;
-   accounts;
-   transactions;
-   balances;
-   liabilities;
-   assets;
-   holdings;
-   valuations;
-   goals;
-   recommendations;
-   consents/connections;
-   provenance.

### Provenance

The system should retain where important financial facts came from and
when they were last updated.

Manual values should be visibly distinguishable from automatically
synchronized values.

### Extensibility

The core should not assume Norwegian banking is the only environment.

Norwegian integrations can be first-class modules while the domain model
remains reusable.

## 11. Open-source reuse

Before implementing major functionality, evaluate existing open-source
projects and libraries.

Actual Budget is one candidate worth investigating, but no decision has
yet been made to adopt, fork, embed, or merely integrate with it.

The project should prefer composition and supported APIs over
maintaining a large fork when practical.

Codex should investigate reusable components before proposing custom
implementations.

## 12. Security and privacy principles

Financial information is highly sensitive.

Initial principles:

-   self-hosting should be supported;
-   never store banking passwords;
-   never store crypto seed phrases or private keys;
-   secrets must not be committed to Git;
-   use least-privilege access;
-   prefer read-only permissions for ingestion;
-   encrypt sensitive credentials/tokens appropriately;
-   isolate provider credentials from analytical code;
-   keep an audit trail for future financial actions;
-   treat each household member's authorization independently;
-   require explicit approval before adding write-capable financial
    integrations.

A formal threat model is required before any write-capable financial
functionality is implemented.

## 13. Notifications

The web application should eventually support notifications.

An early important use case is warning users when a banking consent or
connection requires renewal.

Other future notifications may include:

-   synchronization failures;
-   unusual financial changes;
-   goal milestones;
-   recommendations requiring review.

Notifications should be useful rather than noisy.

## 14. Client experience

A web application is the preferred initial client because the household
uses both Android and iPhone.

The application should work well on both mobile and desktop browsers.

Native mobile applications are not required initially.

## 15. Automation philosophy

Automate data collection and repetitive bookkeeping aggressively where
it is safe to do so.

Do not equate automation with autonomous decision-making.

The desired model is:

**automatic collection → transparent analysis → recommendation → human
decision → optional explicitly approved action**

This boundary may evolve, but changes should be deliberate.

## 16. Non-goals for Phase 1

Phase 1 does not need:

-   payment initiation;
-   automated transfers;
-   investment trading;
-   automated debt payments;
-   tax filing;
-   real-time bank synchronization;
-   automatic home/car/boat valuation;
-   native Android or iOS apps;
-   every investment or crypto integration;
-   sophisticated AI agents making financial decisions.

## 17. Phase 1 success criteria

Phase 1 is successful when:

1.  Both adults can use the system as intended.
2.  Relevant Sparebanken Norge data can be brought into the system
    through a safe, maintainable mechanism.
3.  The data can be refreshed approximately weekly with minimal manual
    work.
4.  The household can see a clear shared financial overview while
    preserving account ownership.
5.  One shared savings goal can be created and tracked.
6.  The system can provide understandable information about progress
    toward that goal.
7.  No financial transaction can occur from the application.
8.  The design leaves credible extension points for later assets, debt,
    investments, crypto, insurance, tax/public-sector data, and
    financial actions.

## 18. Questions deliberately left open

These should be challenged before implementation:

-   Should Actual Budget be used as a foundation, integrated as a
    component, or not used?
-   Which Open Banking provider is the best fit for Sparebanken Norge
    and two independent account holders?
-   What are the provider's current pricing, consent-renewal, and
    non-commercial-use constraints?
-   Should the application store raw imported transactions as well as
    normalized records?
-   What should be the source of truth when imported and manually
    entered data conflict?
-   What authentication mechanism should be used for the household web
    application?
-   What database and deployment model best support simple self-hosting?
-   How should recommendations be generated and explained?
-   What information may be sent to an external LLM, if any?
-   What backup and disaster-recovery model is appropriate?
-   How should shared versus individual financial privacy work inside
    one household?
-   Which requirements are specific to Norway and which belong in
    reusable core modules?

## 19. Instructions for the first Codex review

Before writing implementation code, review this specification
critically.

Codex should:

1.  identify missing requirements, contradictions, security risks, and
    hidden assumptions;
2.  distinguish product questions from architecture questions;
3.  investigate relevant existing open-source components before
    proposing custom implementations;
4.  propose a minimal Phase 1 architecture with replaceable provider
    adapters;
5.  identify decisions that would be expensive to reverse later;
6.  propose a threat-modeling approach;
7.  suggest acceptance criteria or tests for the Phase 1 requirements;
8.  explicitly list questions that require human decisions;
9.  avoid implementing the product until the specification and
    architecture have been reviewed by the human owners.

The goal of the first Codex pass is **critique and design review, not
coding**.
