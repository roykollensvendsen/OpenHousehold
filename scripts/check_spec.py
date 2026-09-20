#!/usr/bin/env python3
"""Check specification traceability and local documentation without dependencies."""

from __future__ import annotations

import hashlib
import re
import sys
from pathlib import Path
from urllib.parse import unquote, urlsplit

ROOT = Path(__file__).resolve().parents[1]
SKIP = {".git", ".venv", ".agents", ".codex", "__pycache__"}


def check(root: Path) -> list[str]:
    """Return actionable errors; never change the inspected repository."""
    errors: list[str] = []

    def read(name: str) -> str:
        path = root / name
        if not path.is_file():
            errors.append(f"missing required file: {name}")
            return ""
        return path.read_text(encoding="utf-8")

    spec = read("SPEC.md")
    register = read("spec/requirements.md")
    acceptance = read("spec/acceptance.md")
    needs = re.findall(r"^\| (N-\d{2}) \|", spec, re.MULTILINE)
    if not needs or len(needs) != len(set(needs)):
        errors.append("parent needs are absent or duplicated")

    requirements: dict[str, set[str]] = {}
    for line in register.splitlines():
        if not line.startswith("| OH-"):
            continue
        cells = [cell.strip() for cell in line.strip("|").split("|")]
        if len(cells) != 6:
            errors.append(f"malformed requirement row: {line}")
            continue
        req, need, priority, obligation, rationale, verification = cells
        if not re.fullmatch(r"OH-\d{3}", req):
            errors.append(f"invalid requirement ID: {req}")
        if req in requirements:
            errors.append(f"duplicate requirement: {req}")
        if need not in needs:
            errors.append(f"{req}: unknown parent need {need}")
        if priority not in {"Must", "Should", "Could"}:
            errors.append(f"{req}: invalid priority {priority}")
        if not obligation or not rationale:
            errors.append(f"{req}: missing obligation or rationale")
        refs = set(re.findall(r"AC-\d{3}", verification))
        if not refs:
            errors.append(f"{req}: no acceptance scenario")
        requirements[req] = refs
    if not requirements:
        errors.append("no requirements found")

    scenarios: dict[str, set[str]] = {}
    headings = list(re.finditer(r"^## (AC-\d{3}) — .+$", acceptance, re.MULTILINE))
    for index, match in enumerate(headings):
        ac = match[1]
        end = headings[index + 1].start() if index + 1 < len(headings) else len(acceptance)
        body = acceptance[match.end():end]
        if ac in scenarios:
            errors.append(f"duplicate acceptance scenario: {ac}")
        backrefs = re.search(r"^Requirements: (.+)$", body, re.MULTILINE)
        refs = set(re.findall(r"OH-\d{3}", backrefs[1])) if backrefs else set()
        scenarios[ac] = refs
        if not refs:
            errors.append(f"{ac}: no requirement backreferences")
        status = re.search(r"^Status: (.+)$", body, re.MULTILINE)
        if not status or status[1] not in {"Planned", "Passed", "Failed"}:
            errors.append(f"{ac}: missing or invalid status")
        elif status[1] == "Passed" and not re.search(r"^Evidence: \[.+\]\(.+\)$", body, re.MULTILINE):
            errors.append(f"{ac}: passed status needs an evidence link")
        if not re.search(r"^Method: .+", body, re.MULTILINE):
            errors.append(f"{ac}: missing verification method")
    if not scenarios:
        errors.append("no acceptance scenarios found")

    for req, refs in requirements.items():
        for ac in refs:
            if ac not in scenarios:
                errors.append(f"{req}: unknown acceptance scenario {ac}")
            elif req not in scenarios[ac]:
                errors.append(f"{req} -> {ac}: missing reverse trace")
    for ac, refs in scenarios.items():
        for req in refs:
            if req not in requirements:
                errors.append(f"{ac}: unknown requirement {req}")
            elif ac not in requirements[req]:
                errors.append(f"{ac} -> {req}: missing forward trace")

    for path in sorted(root.rglob("*.md")):
        if any(part in SKIP for part in path.relative_to(root).parts):
            continue
        # Inline local file links are the repository's link convention. External
        # availability and Markdown heading anchors are outside this check.
        for target in re.findall(r"\[[^\]\n]*\]\(([^\s)]+)\)", path.read_text(encoding="utf-8")):
            parsed = urlsplit(target.strip("<>"))
            if parsed.scheme or parsed.netloc or not parsed.path:
                continue
            destination = (path.parent / unquote(parsed.path)).resolve()
            if not destination.is_relative_to(root.resolve()) or not destination.exists():
                errors.append(f"{path.relative_to(root)}: broken local link {target}")

    provenance = read("docs/source/README.md")
    digest = re.search(r"SHA-256: `([0-9a-f]{64})`", provenance)
    original = root / "docs/source/voice-spec-v0.1.md"
    if not digest or not original.is_file():
        errors.append("source provenance or original draft is missing")
    elif hashlib.sha256(original.read_bytes()).hexdigest() != digest[1]:
        errors.append("original draft differs from recorded source hash")
    return errors


def main() -> int:
    errors = check(ROOT)
    if errors:
        for error in errors:
            print(f"ERROR: {error}", file=sys.stderr)
        return 1
    print("Specification integrity: PASS (traceability, local links, source hash)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
