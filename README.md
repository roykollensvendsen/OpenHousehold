# OpenHousehold

A self-hosted household finance project: shared understanding, one savings goal,
independent bank consent and human control over financial decisions.

**Status: specification and design review. No financial application is implemented.**
This private repository is being established for Roy and the household. Product
policies and architecture in version 0.2 await owner approval.

## Start here

1. [Specification](SPEC.md) — scope, needs and links to the complete design.
2. [Review of the voice draft](docs/review.md) — gaps and proposed resolutions.
3. [Owner decisions](docs/open-questions.md) — choices needed before implementation.
4. [Requirements](spec/requirements.md) and [acceptance scenarios](spec/acceptance.md).
5. [Architecture](spec/architecture.md), [threat model](spec/threat-model.md) and
   [bank/reuse research](docs/research.md).
6. [Delivery gates](docs/delivery-plan.md) and [decision records](decisions/README.md).

The initial product reads Sparebanken Norge data approximately weekly and explains
progress toward one shared goal. Payments, trades and external LLM processing are
outside Phase 1. Bank/provider eligibility for both adults remains unverified;
the announced former Sør interface migration is part of the feasibility review.

## Validate this repository

Python 3.12 or newer and Git are sufficient. No third-party Python packages.
Run from the repository root:

```sh
python3 scripts/check_spec.py
python3 -m unittest discover -s tests -v
python3 scripts/check_commits.py --all
```

These commands check document integrity and commit subjects. They do not execute
the planned product acceptance scenarios. GitHub Actions runs the same checks.
See [contribution guide](CONTRIBUTING.md), [security](SECURITY.md),
[verification evidence](evidence/repository-validation.md) and [changelog](CHANGELOG.md).

Original project material is under [Apache-2.0](LICENSE). Third-party components
and references keep their own licenses. [Standards and tailoring](docs/standards.md)
explain the requirements and architecture approach without claiming certification.
