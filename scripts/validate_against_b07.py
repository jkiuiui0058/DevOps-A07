#!/usr/bin/env python3
"""Validate A07's request and Job examples with B07's validator.

Usage (from a checkout containing both repositories):
  uv run --project ../E2-B07 python scripts/validate_against_b07.py --b07-root ../E2-B07

The B07 checkout is deliberately supplied as an argument so this check cannot silently
validate against a copied or stale schema. The report records the exact B07 commit.
"""
from __future__ import annotations

import argparse
import importlib.util
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SAMPLE_FILES = [
    "docs/examples/full-check/request.json",
    "docs/examples/full-check/accepted-response.json",
    "docs/examples/full-check/succeeded-response.json",
    "docs/examples/incremental-check/request.json",
    "docs/examples/incremental-check/succeeded-response.json",
]
NEGATIVE_FILES = ["docs/examples/invalid/incremental-without-baseline.json"]


def load_b07_validator(b07_root: Path):
    path = b07_root / "docs/contracts/validate.py"
    spec = importlib.util.spec_from_file_location("b07_validate", path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def git_head(path: Path) -> str:
    return subprocess.check_output(
        ["git", "-C", str(path), "rev-parse", "HEAD"], text=True
    ).strip()


def validate_file(module, path: Path, root: Path, schema: dict) -> list[str]:
    document = json.loads(path.read_text(encoding="utf-8"))
    payloads = []
    module._walk(document, [], str(path.relative_to(root)), payloads)
    errors = []
    if not payloads:
        errors.append("no payload discovered")
    for payload in payloads:
        violations = module.all_violations(payload, schema)
        for violation in violations:
            errors.append(f"{payload.ref}: {violation.pointer or '/'} {violation.keyword}")
    return errors


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--b07-root", type=Path, required=True)
    args = parser.parse_args()
    b07 = args.b07_root.resolve()
    module = load_b07_validator(b07)
    schema = module.load_schema()
    results = []
    failures = 0
    for rel in SAMPLE_FILES:
        path = ROOT / rel
        errors = validate_file(module, path, ROOT, schema)
        status = "PASS" if not errors else "FAIL"
        results.append(f"{status} valid {rel}")
        results.extend(f"  {e}" for e in errors)
        failures += bool(errors)
    # The invalid fixture must be rejected for the required baseline violation.
    path = ROOT / NEGATIVE_FILES[0]
    data = json.loads(path.read_text(encoding="utf-8"))
    payloads = []
    module._walk(data, [], str(path.relative_to(ROOT)), payloads)
    violations = module.all_violations(payloads[0], schema)
    rejected = any(v.keyword == "required" and "baseline" in v.message for v in violations)
    results.append(("PASS" if rejected else "FAIL") + " rejected docs/examples/invalid/incremental-without-baseline.json")
    if not rejected:
        results.append("  expected required/baseline violation was not observed")
        failures += 1
    report = [
        "# A07 使用 B07 校验记录",
        "",
        f"- A07 commit: `{git_head(ROOT)}`",
        f"- B07 commit: `{git_head(b07)}`",
        "- 校验来源：B07 `docs/contracts/validate.py`，直接加载 B07 工作树，不复制校验逻辑",
        "",
        *[f"- {line}" for line in results],
        "",
        f"结果：`{'PASS' if failures == 0 else 'FAIL'}`",
    ]
    output = ROOT / "docs/validation/B07-VALIDATION-RESULTS.md"
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text("\n".join(report) + "\n", encoding="utf-8")
    print("\n".join(report))
    return 1 if failures else 0


if __name__ == "__main__":
    raise SystemExit(main())
