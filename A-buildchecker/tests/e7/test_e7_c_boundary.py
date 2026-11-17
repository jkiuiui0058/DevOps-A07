"""C: reject duplicate findings even when the edge set is correct."""

import copy
import importlib.util
from pathlib import Path
import unittest


gate_path = (
    Path(__file__).resolve().parents[2]
    / "scripts"
    / "run_e7_a_gate.py"
)
spec = importlib.util.spec_from_file_location("e7_c_gate", gate_path)
gate = importlib.util.module_from_spec(spec)
spec.loader.exec_module(gate)


class CBoundaryTests(unittest.TestCase):
    def test_duplicate_finding_is_rejected(self):
        # Synthetic reports, not evidence from an actual build.
        findings = [
            {
                "type": kind,
                "target": target,
                "dependency": dependency,
                "evidence": ["synthetic-anchor"],
            }
            for kind, target, dependency in sorted(gate.EXPECTED)
        ]
        report = {
            "trace_id": "synthetic-c-boundary",
            "status": "SUCCEEDED",
            "clean_exit_code": 0,
            "build_exit_code": 0,
            "findings": findings,
        }

        # Control: the exact two findings must pass.
        gate.evaluate("original-1", 1, report)

        # The edge set stays the same, but one finding appears twice.
        duplicate_report = copy.deepcopy(report)
        duplicate_report["findings"].append(copy.deepcopy(findings[0]))

        with self.assertRaisesRegex(ValueError, "Oracle mismatch"):
            gate.evaluate("original-1", 1, duplicate_report)


if __name__ == "__main__":
    unittest.main()