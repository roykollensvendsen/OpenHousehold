# ADR-002 — evaluate reuse before selecting the core

Status: Proposed, 2026-09-20. Decision owners: Roy and maintainer.

Context: Actual Budget and Firefly III offer overlapping financial capabilities.
Actual's documented API is a Node client with local budget state. Shared budget
access does not prove the required account privacy and independent consent model.
A large fork would add maintenance risk. See the dated research for sources.

Proposal: test direct adoption against the mandatory household scenarios first.
Choose an adapter only if source ownership and permission boundaries remain
explicit. If those trials fail, use a modular monolith with a separately
permissioned connector and relational storage. PostgreSQL is a candidate, not an
approved dependency. Do not build microservices or a generic plugin platform.

Alternatives: direct adoption (least new domain code), integration (extra state and
permission mapping), fork (ongoing upstream merge costs), new core (maximum new
maintenance). Evidence needed: pinned release trials, gaps, export/recovery and
licensing review. No choice is accepted until Q-06 and Q-07 close.
