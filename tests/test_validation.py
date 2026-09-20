"""Negative fixtures show that the repository gates catch broken evidence."""

from __future__ import annotations

import hashlib
import importlib.util
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def load(name: str):
    spec = importlib.util.spec_from_file_location(name, ROOT / "scripts" / f"{name}.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


checker = load("check_spec")
commits = load("check_commits")


class SpecificationChecks(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.put("SPEC.md", "| N-01 | Need | Source |\n")
        self.put("spec/requirements.md", "| OH-001 | N-01 | Must | Protect data. | Privacy. | AC-001 |\n")
        self.put("spec/acceptance.md", "## AC-001 — Protection\n\nRequirements: OH-001\n\nStatus: Planned\n\nMethod: Test\n")
        self.put("docs/source/voice-spec-v0.1.md", "original\n")
        digest = hashlib.sha256(b"original\n").hexdigest()
        self.put("docs/source/README.md", f"SHA-256: `{digest}`\n")

    def put(self, name, text):
        path = self.root / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text)

    def replace(self, name, old, new):
        path = self.root / name
        path.write_text(path.read_text().replace(old, new))

    def errors(self):
        return "\n".join(checker.check(self.root))

    def test_valid_fixture(self):
        self.assertEqual([], checker.check(self.root))

    def test_missing_acceptance_is_rejected(self):
        self.replace("spec/requirements.md", "AC-001", "AC-099")
        self.assertIn("unknown acceptance scenario AC-099", self.errors())

    def test_missing_reverse_trace_is_rejected(self):
        self.replace("spec/acceptance.md", "Requirements: OH-001", "Requirements: OH-099")
        self.assertIn("missing reverse trace", self.errors())

    def test_missing_forward_trace_is_rejected(self):
        p = self.root / "spec/acceptance.md"
        p.write_text(p.read_text() + "\n## AC-002 — Extra\n\nRequirements: OH-001\n\nStatus: Planned\n\nMethod: Test\n")
        self.assertIn("missing forward trace", self.errors())

    def test_duplicate_requirement_is_rejected(self):
        p = self.root / "spec/requirements.md"
        p.write_text(p.read_text() * 2)
        self.assertIn("duplicate requirement", self.errors())

    def test_duplicate_acceptance_is_rejected(self):
        p = self.root / "spec/acceptance.md"
        p.write_text(p.read_text() * 2)
        self.assertIn("duplicate acceptance scenario", self.errors())

    def test_unknown_parent_is_rejected(self):
        self.replace("spec/requirements.md", "N-01", "N-99")
        self.assertIn("unknown parent need", self.errors())

    def test_broken_link_is_rejected(self):
        self.put("README.md", "[Missing](missing.md)\n")
        self.assertIn("broken local link", self.errors())

    def test_link_outside_repository_is_rejected(self):
        self.put("README.md", "[Outside](/etc/passwd)\n")
        self.assertIn("broken local link", self.errors())

    def test_changed_original_is_rejected(self):
        self.put("docs/source/voice-spec-v0.1.md", "rewritten\n")
        self.assertIn("differs from recorded source hash", self.errors())

    def test_pass_without_evidence_is_rejected(self):
        self.replace("spec/acceptance.md", "Status: Planned", "Status: Passed")
        self.assertIn("passed status needs an evidence link", self.errors())

    def test_missing_rationale_is_rejected(self):
        self.replace("spec/requirements.md", "Privacy.", "")
        self.assertIn("missing obligation or rationale", self.errors())


class CommitChecks(unittest.TestCase):
    def test_accepted_forms(self):
        for subject in ("docs: Define the specification", "feat(goals)!: Change allocation rules", "ci: Bump checkout"):
            with self.subTest(subject=subject):
                self.assertTrue(commits.valid(subject))

    def test_rejected_forms(self):
        for subject in ("", "Update docs", "banana: Update docs", "docs: ", "docs: " + "x" * 67):
            with self.subTest(subject=subject):
                self.assertFalse(commits.valid(subject))

    def test_ci_runs_documented_gates_with_pinned_actions(self):
        workflow = (ROOT / ".github/workflows/checks.yml").read_text()
        guide = (ROOT / "CONTRIBUTING.md").read_text()
        for command in (
            "python3 scripts/check_spec.py",
            "python3 -m unittest discover -s tests -v",
            "python3 scripts/check_commits.py --all",
        ):
            self.assertIn(command, guide)
            self.assertIn(f"run: {command}", workflow)
        import re
        actions = re.findall(r"uses: (\S+)", workflow)
        self.assertTrue(actions)
        for action in actions:
            self.assertRegex(action, r"@([0-9a-f]{40})$")
        self.assertIn("contents: read", workflow)


if __name__ == "__main__":
    unittest.main()
