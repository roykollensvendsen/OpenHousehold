# Review of the initial specification

Reviewed 2026-09-20. Input: [original draft](source/voice-spec-v0.1.md).

The draft establishes a useful boundary: a shared savings goal, weekly bank reads
and human decisions. It needs more precise behavior to make correctness testable.

| Finding | Consequence | Resolution in v0.2 |
| --- | --- | --- |
| Progress lacks a funding rule and baseline. | All cash or internal transfers might be called new savings. | Dedicated balances and comparable snapshots; owner decision Q-01. |
| Shared view does not define privacy. | Bank consent could unintentionally disclose data to the partner. | Separate consent and sharing, private default, revoke behavior; Q-02. |
| Joint-account duplication is unspecified. | Both owners import the same money twice. | Canonical identity, alias mapping and ambiguity quarantine. |
| Automatic bank access is assumed feasible. | The UI could depend on an unavailable provider. | Provider proof before bank-dependent implementation. |
| Former Sør interface is changing. | Hard-coded institution routes could stop working. | Migration/reconsent scenario and source-dated research. |
| Failure, missing history and pending data are undefined. | Zero balances, duplicates and false trends appear authoritative. | Atomic publication, coverage windows, idempotency and status distinctions. |
| Independent logins are described as eventual. | Phase 1 might use a shared identity. | Separate identities are a first-phase requirement. |
| Self-hosting lacks recovery. | Disk or key loss could destroy manual work. | Proposed recovery objectives and restore rehearsal. |
| Threat modeling waits for financial writes. | Sensitive read-only data is exposed before review. | Threat model now, security gate before live data. |
| Extensibility lists many future entities. | Speculation overwhelms the useful first slice. | Small present model and deferred modules with triggers. |
| Advice and AI have no boundary. | Unexplained suggestions or disclosure to third parties. | Deterministic observations, no external LLM in Phase 1. |
| Qualitative goals lack measurable tests. | “Safe” and “easy” cannot serve as release evidence. | Numbered requirements and planned scenarios. |

Product decisions concern goal semantics, sharing, retention, provider budget and
fallback scope. Architecture decisions concern reuse, authentication, persistence,
hosting and keys. The [question register](open-questions.md) separates them.

Expensive choices include account identity, precision, authorization boundaries,
source-of-truth policy, provider terms and reuse licensing. Resolve these early.
Framework and layout choices can follow. New policies and thresholds are proposed,
not assertions about what the owners said in the voice session.
