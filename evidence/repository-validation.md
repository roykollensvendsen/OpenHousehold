# Repository validation record

Date: 2026-09-20. Scope: specification repository, not product acceptance.

## Reproducible checks

From the repository root:

```sh
python3 scripts/check_spec.py
python3 -m unittest discover -s tests -v
python3 scripts/check_commits.py --all
```

The validator checks requirement/scenario traceability in both directions, parent
needs, local file links and the original draft's SHA-256. Negative fixtures check
that broken references, altered provenance and unsupported pass claims fail.
Commit checking covers every non-merge commit reachable from HEAD.

## Results

Local Python 3.14.7: specification integrity PASS; all 15 validator tests PASS.
The suite includes negative fixtures for broken traceability, links, source
integrity and pass claims without evidence. Commit-subject check PASS.

The initial commit `cfdde4ee411bd37a10ef1bc8ff87c9a8c2075156` passed all three
checks on GitHub's Ubuntu 24.04 runner:
[successful workflow run](https://github.com/roykollensvendsen/OpenHousehold/actions/runs/35505080448).
Subsequent commits run the same workflow; consult the run for the specific revision.
No product acceptance scenario has run. Provider integration, standards conformance,
ASVS assessment, usability and recovery remain unverified design/release work.

## Forge configuration

Created [roykollensvendsen/OpenHousehold](https://github.com/roykollensvendsen/OpenHousehold),
initially private and made **public at the user's explicit request** on 2026-09-20.
Readback confirmed `private: false`, default branch `main`, and local origin
tracking. No account upgrade or paid feature was enabled.

Verified via the GitHub repository and branch-protection APIs:

- Main requires a pull request and the successful `specification` check against
  an up-to-date base; administrators are included.
- Zero approving reviews are required, allowing a sole maintainer to merge.
  Product-baseline owner approval is still a separate process requirement.
- Linear history and conversation resolution are required; force pushes and
  main-branch deletion are disabled.
- Only rebase merges are enabled; merged branches are deleted automatically.
- Secret scanning and secret-scanning push protection are enabled.
- The local commit-message hook is enabled; Dependabot monitors Action pins.

Only the ordinary `specification` job is required. Dependabot's maintenance check
does not run on every PR and therefore is intentionally not a required context.
The stock start-repo helper discovers all contexts; the protection payload was
tailored to prevent that maintenance check from blocking unrelated PRs.

GitHub initially refused protection/scanning while the repo was private. After
public conversion, a temporary repository lock delayed protection; a retry with
the correct context succeeded. Readback, rather than the earlier refusal, is the
source of the current state above. Scanning does not prove absence of all secrets
and does not replace the product threat model.
