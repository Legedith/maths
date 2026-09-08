from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


EXPECTED_PREEXECUTION_FREEZE_SHA256 = "8c490bc29364495c4eb3e154193824d8eb8cc8cd49828259745fee12a23adaea"
EXPECTED_SOURCE_PINS_SHA256 = "a54738f15cdc11aa383a452e7a464be80aafe9eb3ad609e2313f65dfaa4b2b87"
EXPECTED_RUN_RECORD_SHA256 = "096c85f7dea51516b2038b8585b42d4bc266ca1bb398663fde5207cdab51b08d"
BASELINE_FILES = {
    "author": [
        "summary.json",
        "graph-values.json",
        "pairs.jsonl",
        "witnesses.json",
        "published-p7.json",
    ],
    "independent": [
        "summary.json",
        "graph-values.json",
        "pairs.jsonl",
        "witnesses.json",
        "published-p7.json",
        "completeness.json",
    ],
}


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def file_record(root: Path, path: Path) -> dict[str, Any]:
    raw = path.read_bytes()
    return {
        "path": path.relative_to(root).as_posix(),
        "bytes": len(raw),
        "sha256": sha256_bytes(raw),
    }


def assert_file_record(root: Path, record: dict[str, Any]) -> None:
    path = root / record["path"]
    actual = file_record(root, path)
    if actual != {
        "path": record["path"],
        "bytes": record["bytes"],
        "sha256": record["sha256"],
    }:
        raise RuntimeError(f"file record mismatch: {record['path']}")


def main() -> int:
    root = Path(__file__).resolve().parent
    package = root / "experiments/kemeny-pair-minimum"
    output = root / "result-manifest.json"
    if output.exists():
        raise FileExistsError(f"refusing to overwrite {output}")

    prefreeze_path = package / "preexecution-freeze.json"
    prefreeze_raw = prefreeze_path.read_bytes()
    if sha256_bytes(prefreeze_raw) != EXPECTED_PREEXECUTION_FREEZE_SHA256:
        raise RuntimeError("preexecution freeze hash mismatch")
    prefreeze = json.loads(prefreeze_raw)
    for record in prefreeze["files"]:
        assert_file_record(package, record)

    pins_raw = (package / "source-pins.json").read_bytes()
    if sha256_bytes(pins_raw) != EXPECTED_SOURCE_PINS_SHA256:
        raise RuntimeError("source-pins.json hash mismatch")

    run_path = root / "integration-run-01/run.json"
    run_raw = run_path.read_bytes()
    if sha256_bytes(run_raw) != EXPECTED_RUN_RECORD_SHA256:
        raise RuntimeError("integration run record hash mismatch")
    run = json.loads(run_raw)
    if run["status"] != "complete_all_deterministic_outputs_byte_identical":
        raise RuntimeError("portable integration status is not complete")
    if run["deterministic_file_count"] != 11 or run["all_byte_identical"] is not True:
        raise RuntimeError("portable integration did not match all 11 outputs")
    if [child["implementation"] for child in run["children"]] != [
        "author",
        "independent",
    ]:
        raise RuntimeError("unexpected child sequence")
    for child in run["children"]:
        if child["timed_out"] or child["return_code"] != 0:
            raise RuntimeError(f"failed child record: {child['implementation']}")
        if child["logging_wrapper"]["sha256"] != (
            "b6f4c329387705b2adf67f7dd3f806bbcd0a5906d476f5214fe8278d5ea5bfa6"
        ):
            raise RuntimeError("unexpected logging-wrapper hash")

    byte_comparisons: list[dict[str, Any]] = []
    for implementation, names in BASELINE_FILES.items():
        for name in names:
            baseline = package / "baseline" / implementation / name
            reproduced = root / "integration-run-01" / implementation / name
            baseline_raw = baseline.read_bytes()
            reproduced_raw = reproduced.read_bytes()
            if reproduced_raw != baseline_raw:
                raise RuntimeError(f"nonidentical reproduced file: {implementation}/{name}")
            byte_comparisons.append(
                {
                    "implementation": implementation,
                    "path": name,
                    "bytes": len(reproduced_raw),
                    "sha256": sha256_bytes(reproduced_raw),
                    "byte_identical": True,
                }
            )

    integration_attempt = json.loads(
        (root / "evidence/integration/attempt-integration-01.json").read_bytes()
    )
    if integration_attempt["returncode"] != 0 or integration_attempt["timed_out"]:
        raise RuntimeError("outer integration wrapper record failed")
    rejection_attempt = json.loads(
        (root / "evidence/rejection/attempt-existing-dir-01.json").read_bytes()
    )
    if rejection_attempt["returncode"] != 2 or rejection_attempt["timed_out"]:
        raise RuntimeError("existing-directory rejection probe did not return 2")
    rejection_status = json.loads(
        (root / "evidence/rejection/attempt-existing-dir-01.stderr.bin").read_bytes()
    )
    if rejection_status != {
        "child_invocations": 0,
        "output_dir": (
            root / "existing-output-probe"
        ).resolve().as_posix(),
        "schema_version": "kemeny-portable-run-status-v1",
        "status": "rejected_existing_output_directory",
    }:
        raise RuntimeError("unexpected existing-directory rejection status")
    if (root / "existing-output-probe/sentinel.txt").read_bytes() != b"must remain unchanged":
        raise RuntimeError("existing-directory sentinel changed")

    artifacts: list[dict[str, Any]] = []
    for path in sorted(root.rglob("*")):
        if not path.is_file() or path == output:
            continue
        relative = path.relative_to(root)
        if ".venv" in relative.parts or "__pycache__" in relative.parts:
            continue
        if path.suffix == ".pyc":
            continue
        artifacts.append(file_record(root, path))

    manifest = {
        "schema_version": "kemeny-portable-result-manifest-v1",
        "status": "sealed_author_portable_evidence_pending_independent_adapter_audit",
        "sealed_at_utc": datetime.now(timezone.utc).isoformat(),
        "package_root": "experiments/kemeny-pair-minimum",
        "preexecution_freeze": {
            "path": "experiments/kemeny-pair-minimum/preexecution-freeze.json",
            "bytes": len(prefreeze_raw),
            "sha256": EXPECTED_PREEXECUTION_FREEZE_SHA256,
            "frozen_package_file_count": prefreeze[
                "file_count_excluding_this_manifest_and_environments"
            ],
        },
        "source_pins_sha256": EXPECTED_SOURCE_PINS_SHA256,
        "canonical_repository_root_argv": [
            "uv",
            "run",
            "--project",
            "experiments/kemeny-pair-minimum/independent",
            "--frozen",
            "python",
            "experiments/kemeny-pair-minimum/reproduce.py",
            "--output-dir",
            "work/kemeny-pair-run",
        ],
        "integration_evaluation": {
            "justification": "A single new replay was required to validate portable path adaptation, environment selection, logging, and byte comparison.",
            "outer_attempt": integration_attempt,
            "run_record": {
                "path": "integration-run-01/run.json",
                "bytes": len(run_raw),
                "sha256": EXPECTED_RUN_RECORD_SHA256,
            },
            "child_results": [
                {
                    "implementation": child["implementation"],
                    "duration_seconds": child["duration_seconds"],
                    "timeout_seconds": child["timeout_seconds_for_census"],
                    "timed_out": child["timed_out"],
                    "return_code": child["return_code"],
                    "logging_wrapper_sha256": child["logging_wrapper"]["sha256"],
                }
                for child in run["children"]
            ],
            "deterministic_file_count": 11,
            "all_byte_identical": True,
            "deterministic_files": byte_comparisons,
            "metadata_only_differences": [],
            "non_deterministic_records_note": "Commands, absolute paths, environment metadata, and timestamps are retained in run logs and are intentionally outside the deterministic 11-file comparison.",
        },
        "existing_directory_rejection_probe": {
            "outer_attempt": rejection_attempt,
            "status": rejection_status,
            "sentinel_unchanged": True,
        },
        "environment": run["environment"],
        "artifacts_excluding_environments_and_this_manifest": artifacts,
        "artifact_count": len(artifacts),
        "excluded": ["**/.venv/**", "**/__pycache__/**", "**/*.pyc", "result-manifest.json"],
        "seal_reproduction_argv": [
            "uv",
            "run",
            "--no-project",
            "--python",
            "3.12.11",
            "python",
            "seal_results.py",
        ],
        "limitations": [
            "This author-generated manifest does not self-certify the adapter; independent audit remains pending.",
            "The package retains exact frozen mathematical sources and makes no change to either computation.",
            "The portable replay is separate from, and does not repair, the chronology of earlier evidence runs.",
            "No mathematical or algorithmic novelty claim is made.",
        ],
    }
    output.write_bytes(
        (json.dumps(manifest, ensure_ascii=True, sort_keys=True, indent=2) + "\n").encode(
            "utf-8"
        )
    )
    print(
        json.dumps(
            {
                "path": output.as_posix(),
                "bytes": output.stat().st_size,
                "sha256": sha256_bytes(output.read_bytes()),
                "artifact_count": len(artifacts),
                "deterministic_files_byte_identical": len(byte_comparisons),
            },
            sort_keys=True,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
