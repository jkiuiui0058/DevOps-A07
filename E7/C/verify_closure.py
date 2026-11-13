"""Verify locally saved PR #9 closure evidence without GitHub credentials."""
import importlib.util
import json
from pathlib import Path

BASE = Path(__file__).resolve().parent / "e7-rejection"
ROOT = Path(__file__).resolve().parents[2]
spec = importlib.util.spec_from_file_location(
    "closure_gate", ROOT / "A-buildchecker/scripts/run_e7_a_gate.py")
gate = importlib.util.module_from_spec(spec)
spec.loader.exec_module(gate)


def verify():
    protection = json.loads((BASE / "main-protection.json").read_text())
    checks = protection["required_status_checks"]
    assert checks["strict"] is True
    assert {"context": "e7-a-quality-gate", "app_id": 15368} in checks["checks"]
    assert protection["enforce_admins"]["enabled"] is True
    assert protection["required_pull_request_reviews"]["required_approving_review_count"] == 0
    assert "base branch policy prohibits the merge" in (BASE / "merge-rejection.log").read_text()
    assert (BASE / "merge-exit.txt").read_text().strip() == "MERGE_ATTEMPT_EXIT_CODE=1"
    records = json.loads((BASE / "github-records.json").read_text())
    assert records["pr"]["merged"] is True
    assert records["pr"]["head_sha"] == "2fd0dca37142982f2ed0a8d95d2ac77eb06bdd88"
    assert records["pr"]["merge_commit_sha"] == "0328959115c5ad7e5239edd35a33295ebd5f086d"
    stages = [
        ("failure-43427014659", False, "c3a2400c63d1e834a7e0c95a2e750dc23e7e32f6"),
        ("recovery-43428201601", True, "09b75b327840b3bcc7a777d4777e6388e9fb6cef"),
        ("main-43428975185", True, records["pr"]["merge_commit_sha"]),
    ]
    result = []
    for folder, passed, checkout in stages:
        files = list((BASE / folder).rglob("gate-result.json"))
        assert len(files) == 1
        summary_file = files[0]
        summary = json.loads(summary_file.read_text())
        artifact = summary_file.parent.parent
        assert (artifact / "commit.txt").read_text().strip() == checkout
        assert summary["passed"] is passed
        tests = (summary_file.parent / "unit-tests/stdout.log").read_text()
        if passed:
            assert "21 passed" in tests
            expected = ["unit-tests", "original-1", "original-2", "original-3",
                        "fixed", "build-failed", "unsupported", "timeout"]
            assert [c["case"] for c in summary["cases"]] == expected
            for case in summary["cases"]:
                assert case["passed"] is True
                if case["case"] != "unit-tests":
                    report = json.loads((summary_file.parent / case["case"] /
                                         "evidence/findings.json").read_text())
                    gate.evaluate(case["case"], case["exit_code"], report)
        else:
            assert "1 failed, 20 passed" in tests
            assert "AssertionError: '0.2.0-teaching' != '1'" in tests
            assert summary["cases"][0]["exit_code"] == 1
        result.append({"stage": folder, "expected_gate_passed": passed,
                       "checkout_sha": checkout, "verified": True})
    return {"passed": True, "scope": "offline closure evidence verification",
            "required_check": "e7-a-quality-gate", "app_id": 15368,
            "strict": True, "enforce_admins": True, "required_approvals": 0,
            "merge_rejection_exit": 1, "merged_at": records["pr"]["merged_at"],
            "stages": result}


if __name__ == "__main__":
    print(json.dumps(verify(), ensure_ascii=False, indent=2))
