# OpenHousehold repository instructions

Read SPEC.md before changing scope. This is a specification repository; product
implementation requires explicit owner approval of specification and architecture.
Treat proposed decisions as unapproved. Preserve docs/source/voice-spec-v0.1.md.
Keep requirement IDs, parent needs and acceptance mappings consistent. Record
current external facts with primary sources and a research date. Never use real
financial data or credentials in tests or committed artifacts.

Run python3 scripts/check_spec.py and python3 -m unittest discover -s tests -v after
spec/checker changes, and python3 scripts/check_commits.py --all before delivery.
These validate the repository, not the product. Follow CONTRIBUTING.md for exact
commit rules. Do not claim forge protection, standards compliance or product tests
passed without corresponding evidence.
