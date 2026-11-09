from __future__ import annotations

import copy
import importlib.util
import json
from pathlib import Path
import subprocess
import sys
import unittest

ROOT = Path(__file__).resolve().parent.parent
SCRIPT = ROOT / "scripts" / "validate-report.py"
SPEC = importlib.util.spec_from_file_location("validate_report", SCRIPT)
assert SPEC is not None and SPEC.loader is not None
VALIDATOR = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(VALIDATOR)


class ReportValidationTests(unittest.TestCase):
    def setUp(self) -> None:
        self.report = json.loads(
            (ROOT / "examples" / "report.json").read_text(encoding="utf-8")
        )

    def errors_for(self, report) -> list[str]:
        return VALIDATOR.validate_report(report)

    def test_packaged_example_is_valid(self) -> None:
        self.assertEqual(self.errors_for(self.report), [])

    def test_cli_accepts_packaged_example(self) -> None:
        result = subprocess.run(
            [sys.executable, str(SCRIPT), str(ROOT / "examples" / "report.json")],
            capture_output=True,
            text=True,
            check=False,
        )
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("valid Basis report", result.stdout)

    def test_summary_counts_must_match_claims(self) -> None:
        report = copy.deepcopy(self.report)
        report["summary"]["counts"]["supported"] += 1
        self.assertTrue(
            any("claims contain 2" in error for error in self.errors_for(report))
        )

    def test_evidence_cannot_reference_unknown_source(self) -> None:
        report = copy.deepcopy(self.report)
        report["claims"][0]["evidence"][0]["source_id"] = "S99"
        self.assertTrue(
            any("unknown source S99" in error for error in self.errors_for(report))
        )

    def test_evidence_cannot_reference_unaccessed_source(self) -> None:
        report = copy.deepcopy(self.report)
        report["sources"][0]["accessed"] = False
        self.assertTrue(
            any("unaccessed source S1" in error for error in self.errors_for(report))
        )

    def test_supported_claim_requires_evidence(self) -> None:
        report = copy.deepcopy(self.report)
        report["claims"][0]["evidence"] = []
        self.assertTrue(
            any("need at least one evidence item" in error for error in self.errors_for(report))
        )

    def test_unverified_claim_cannot_use_checked_evidence(self) -> None:
        report = copy.deepcopy(self.report)
        claim = report["claims"][1]
        claim["status"] = "unverified"
        report["summary"]["counts"]["unsupported"] -= 1
        report["summary"]["counts"]["unverified"] += 1
        self.assertTrue(
            any("unverified claims cannot cite" in error for error in self.errors_for(report))
        )

    def test_disputed_claim_requires_two_sources(self) -> None:
        report = copy.deepcopy(self.report)
        claim = report["claims"][1]
        claim["status"] = "disputed"
        report["summary"]["counts"]["unsupported"] -= 1
        report["summary"]["counts"]["disputed"] += 1
        self.assertTrue(
            any("at least two sources" in error for error in self.errors_for(report))
        )

    def test_supported_claim_cannot_have_defect(self) -> None:
        report = copy.deepcopy(self.report)
        report["claims"][0]["severity"] = "low"
        report["claims"][0]["check_ids"] = [4]
        errors = self.errors_for(report)
        self.assertTrue(any("severity 'none'" in error for error in errors))
        self.assertTrue(any("cannot list defect" in error for error in errors))

    def test_check_ids_are_bounded_and_unique(self) -> None:
        report = copy.deepcopy(self.report)
        report["claims"][1]["check_ids"] = [4, 4, 25]
        errors = self.errors_for(report)
        self.assertTrue(any("invalid check 25" in error for error in errors))
        self.assertTrue(any("must not contain duplicates" in error for error in errors))

    def test_unknown_top_level_field_is_rejected(self) -> None:
        report = copy.deepcopy(self.report)
        report["accuracy_score"] = 99
        self.assertTrue(
            any("accuracy_score is not an allowed field" in error for error in self.errors_for(report))
        )

    def test_duplicate_claim_ids_are_rejected(self) -> None:
        report = copy.deepcopy(self.report)
        report["claims"][1]["id"] = report["claims"][0]["id"]
        self.assertTrue(any("duplicates C1" in error for error in self.errors_for(report)))


if __name__ == "__main__":
    unittest.main()
