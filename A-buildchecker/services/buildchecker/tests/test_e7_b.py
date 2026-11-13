"""B-role CI-facing regression tests for the service contract."""
import tempfile
import unittest
from pathlib import Path

from buildchecker.fullcheck import VERSION, full_check


class TestE7BServiceBoundary(unittest.TestCase):
    def test_full_check_refuses_evidence_directory_inside_source_fixture(self):
        """Evidence must never be created inside the input copied for analysis."""
        with tempfile.TemporaryDirectory() as temp:
            fixture = Path(temp) / "fixture"
            fixture.mkdir()
            (fixture / "Makefile").write_text("app:\n\ttrue\n", encoding="utf-8")

            with self.assertRaisesRegex(ValueError, "Output must be outside the fixture"):
                full_check(fixture, fixture / "evidence")

    def test_teaching_detector_version_is_explicit_for_ci_provenance(self):
        """The CI record can identify the detector implementation it exercised."""
        self.assertEqual(VERSION, "0.2.0-teaching")


if __name__ == "__main__":
    unittest.main()
