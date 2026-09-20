"""Run dependency-free smoke checks for the E2 contract examples."""

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
VALID_EXAMPLES = [
    ROOT / "docs" / "examples" / "full-check" / "request.json",
    ROOT / "docs" / "examples" / "full-check" / "accepted-response.json",
    ROOT / "docs" / "examples" / "full-check" / "succeeded-response.json",
    ROOT / "docs" / "examples" / "incremental-check" / "request.json",
    ROOT / "docs" / "examples" / "incremental-check" / "succeeded-response.json",
]
INVALID_EXAMPLE = (
    ROOT / "docs" / "examples" / "invalid" / "incremental-without-baseline.json"
)


def load_json(path: Path) -> dict:
    with path.open(encoding="utf-8") as stream:
        return json.load(stream)


def check_job(job: dict) -> None:
    required = {"schema_version", "job_type", "input"}
    missing = required - job.keys()
    if missing:
        raise ValueError(f"missing fields: {sorted(missing)}")
    if job["schema_version"] != "1.0":
        raise ValueError("unsupported schema_version")
    if job["job_type"] not in {"FULL_CHECK", "INCREMENTAL_CHECK"}:
        raise ValueError("unsupported job_type")

    common_input = {
        "repository",
        "environment",
        "build",
        "configuration_id",
        "commit",
        "defined_by",
        "idempotency_key",
    }
    missing_input = common_input - job["input"].keys()
    if missing_input:
        raise ValueError(f"missing input fields: {sorted(missing_input)}")
    if job["job_type"] == "INCREMENTAL_CHECK":
        incremental = {"base_commit", "baseline"}
        missing_incremental = incremental - job["input"].keys()
        if missing_incremental:
            raise ValueError(
                f"missing incremental fields: {sorted(missing_incremental)}"
            )


def main() -> None:
    for example in VALID_EXAMPLES:
        check_job(load_json(example))
        print(f"PASS valid: {example.relative_to(ROOT)}")

    try:
        check_job(load_json(INVALID_EXAMPLE))
    except ValueError:
        print(f"PASS rejected: {INVALID_EXAMPLE.relative_to(ROOT)}")
    else:
        raise SystemExit("Invalid example unexpectedly passed validation")


if __name__ == "__main__":
    main()
