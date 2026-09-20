#!/usr/bin/env python3
"""Validate the documented Conventional Commit subject subset."""

from __future__ import annotations

import argparse
import re
import subprocess
from pathlib import Path

TYPES = "build|chore|ci|docs|feat|fix|perf|refactor|revert|style|test"
SUBJECT = re.compile(rf"(?:{TYPES})(?:\([a-zA-Z0-9_.-]+\))?!?: \S.*")
ROOT = Path(__file__).resolve().parents[1]


def valid(subject: str) -> bool:
    return len(subject) <= 72 and SUBJECT.fullmatch(subject) is not None


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--all", action="store_true", help="check all non-merge commits reachable from HEAD")
    mode.add_argument("--message", type=Path, help="check the subject of a commit message file")
    args = parser.parse_args()
    if args.message:
        lines = args.message.read_text(encoding="utf-8").splitlines()
        subjects = [("commit message", lines[0] if lines else "")]
    else:
        result = subprocess.run(
            ["git", "log", "--no-merges", "--format=%h%x09%s", "HEAD"],
            cwd=ROOT, text=True, capture_output=True, check=False,
        )
        if result.returncode:
            print("Commit validation requires an initialized repository with a commit.")
            return 1
        subjects = [tuple(line.split("\t", 1)) for line in result.stdout.splitlines()]
    invalid = [(commit, subject) for commit, subject in subjects if not valid(subject)]
    for commit, subject in invalid:
        print(f"ERROR: {commit}: invalid commit subject: {subject!r}")
    if invalid:
        return 1
    print(f"Commit subjects: PASS ({len(subjects)} checked)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
