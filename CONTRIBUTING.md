# Contributing

This repository is in design review. Do not implement the financial product until
the owners approve the specification and architecture. Use synthetic examples;
never commit live bank responses, account exports, tokens or household finances.

## Change process

For requirement changes, update the same permanent ID, rationale, scenario and
related decision. Do not reuse IDs. Keep source/voice-spec-v0.1.md immutable under
docs; it is evidence of the starting point. New product choices remain proposed
until approval is recorded. Add changelog entries for substantive changes.

Use a branch and pull request for review when collaborating. Initial bootstrap
and maintenance may use direct pushes while forge protection is unavailable.
A suggested review process is not a claim of server-side enforcement. Actual
GitHub protection and security settings are recorded in the verification report.
No force push over shared main history is part of this process.

## Required executable checks

Run from the repository root with Python 3.12+:

```sh
python3 scripts/check_spec.py
python3 -m unittest discover -s tests -v
python3 scripts/check_commits.py --all
```

The spec checker rejects missing/duplicate requirement and acceptance IDs,
inconsistent forward/reverse links, unknown parent needs, unreferenced scenarios,
missing local Markdown files and altered source provenance. Tests deliberately
break examples to verify detection. External URLs are reviewed in research rather
than fetched on every CI run. Semantic correctness still requires human review.

Commit subject format: type, optional scope, optional breaking-change exclamation,
colon-space, a nonempty description; maximum 72 characters. Allowed types are
build, chore, ci, docs, feat, fix, perf, refactor, revert, style and test. Example:
`docs: Define household savings and privacy requirements`. These are the exact
rules enforced by the local hook and CI; imperative mood is writing guidance,
not a claim of grammatical validation. Merge commits are not linted as authored
changes. All other reachable commits are checked, including the first commit.

Enable the optional hook in a fresh clone:

```sh
git config core.hooksPath .githooks
```

The hook is bypassable; CI supplies an independent check. Python tooling is for
the spec repository only. Add a pinned dependency environment, language-specific
lint/type checks and real domain/security tests once the product stack is chosen.
The product release gate requires the acceptance evidence described in the spec.
