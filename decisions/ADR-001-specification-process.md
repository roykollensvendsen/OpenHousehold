# ADR-001 — reviewable specification before implementation

Status: Accepted for repository setup, 2026-09-20.
Authority: user's request to analyze the draft and establish this folder as a repo;
the original draft explicitly calls for owner review before product implementation.

Context: the voice draft contains strong goals but ambiguous calculations,
permissions and acceptance measures. Generating a Python application from the
start-repo template would prematurely select a stack.

Decision: preserve the source; use a small SRS plus linked domain, architecture,
security and operations documents. Keep permanent requirement and scenario IDs.
Run offline checks for traceability, links, source integrity and commit format.
Use Conventional Commits with the subset in CONTRIBUTING. Python standard-library
tooling requires no dependency installation or product runtime decision.

Consequences: documentation CI cannot prove the application meets requirements.
Product scenarios are explicitly planned. Runtime scaffolding, packaging, API
schemas and product tests arrive with the approved stack and first vertical slice.
Forge rules depend on visibility/account capabilities and are reported from
verified settings. The user subsequently authorized public publication.
