"""Check downloaded C evidence offline; no container execution is claimed."""
import csv
import hashlib
import importlib.util
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
BASE = Path(__file__).resolve().parent
EVIDENCE = BASE / "evidence"
GATE = EVIDENCE / "run/gate"
spec = importlib.util.spec_from_file_location(
    "c_evidence_gate", ROOT / "A-buildchecker/scripts/run_e7_a_gate.py"
)
gate = importlib.util.module_from_spec(spec)
spec.loader.exec_module(gate)


def read_json(path):
    return json.loads(path.read_text(encoding="utf-8"))


def verify():
    summary = read_json(GATE / "gate-result.json")
    with (GATE / "results.csv").open(encoding="utf-8", newline="") as f:
        rows = list(csv.DictReader(f))
    names = ["unit-tests", "original-1", "original-2", "original-3",
             "fixed", "build-failed", "unsupported", "timeout"]
    assert summary["passed"] is True
    assert summary["intentional_failure"] is False
    assert [r["case"] for r in summary["cases"]] == names
    assert [r["case"] for r in rows] == names
    for item, row in zip(summary["cases"], rows):
        name = item["case"]
        case = GATE / name
        assert item["passed"] is True and row["passed"] == "True", name
        assert str(item["exit_code"]) == row["exit_code"], name
        for field in ("detector_status", "trace_id"):
            assert item.get(field, "") == row[field], (name, field)
        for filename in ("command.json", "stdout.log", "stderr.log"):
            assert (case / filename).is_file(), (name, filename)
        if name == "unit-tests":
            assert item["exit_code"] == 0
            assert "21 passed" in (case / "stdout.log").read_text()
            continue
        report = read_json(case / "evidence/findings.json")
        gate.evaluate(name, item["exit_code"], report)
        assert report["status"] == item["detector_status"]
        assert report["trace_id"] == item["trace_id"]
        if report["status"] == "SUCCEEDED":
            for filename in ("actual-graph.json", "declared-graph.json",
                             "processes.json", "make-db.txt"):
                assert (case / "evidence" / filename).is_file()
            assert list((case / "evidence/trace").glob("t.*"))

    def inputs(name):
        return {p.name: hashlib.sha256(p.read_bytes()).hexdigest()
                for p in (GATE / name / "fixture").iterdir() if p.is_file()}

    original = inputs("original-1")
    assert original == inputs("original-2") == inputs("original-3")
    fixed = inputs("fixed")
    assert original.keys() == fixed.keys()
    changed = sorted(k for k in original if original[k] != fixed[k])
    assert changed == ["Makefile"]
    before = (GATE / "original-1/fixture/Makefile").read_text()
    after = (GATE / "fixed/fixture/Makefile").read_text()
    assert after == before.replace("main.o: main.c unused.h", "main.o: main.c config.h")
    assert not (EVIDENCE / "worktree-status.txt").read_text().strip()
    for filename, label in (("oracle-exit.txt", "ORACLE_EXIT_CODE"),
                            ("build-exit.txt", "BUILD_EXIT_CODE"),
                            ("gate-exit.txt", "GATE_EXIT_CODE")):
        assert (EVIDENCE / filename).read_text().strip() == label + "=0"
    assert "Ran 7 tests" in (EVIDENCE / "oracle.log").read_text()
    image = read_json(EVIDENCE / "image-inspect.json")[0]
    assert summary["image"] in image["RepoTags"]
    return {"passed": True, "scope": "offline downloaded evidence verification",
            "source_sha": (EVIDENCE / "source-commit.txt").read_text().strip(),
            "image_id": image["Id"], "service_tests": 21, "independent_tests": 7,
            "gate_rows": 8, "original_inputs_identical": True,
            "fixed_changed_files": changed, "json_csv_match": True}


if __name__ == "__main__":
    print(json.dumps(verify(), ensure_ascii=False, indent=2))
