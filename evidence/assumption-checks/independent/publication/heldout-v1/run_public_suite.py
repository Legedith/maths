from __future__ import annotations

import argparse
import copy
import hashlib
import json
import platform
import subprocess
import sys
import traceback
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


EXPECTED_FREEZE_MANIFEST_SHA256 = "50fd6ed3f43f8bdd30e325b249e605cd2bbde33db2336cf0142eba9a1ec5505d"
EXPECTED_SUITE_SHA256 = "ddf50219b87547a9cae547d936a7afba76380f11c4cda7c5fbb473635a01d9ee"
EXPECTED_ALGORITHM_VERSION = "atlas-checks/1.0.2"


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Reproduce the public 80-case structured-transfer evaluation against a project checkout."
    )
    parser.add_argument("--project-root", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--suite-dir", type=Path, default=Path(__file__).resolve().parent)
    args = parser.parse_args()
    project = args.project_root.resolve()
    output_dir = args.output_dir.resolve()
    suite_dir = args.suite_dir.resolve()
    output_dir.mkdir(parents=True, exist_ok=True)

    run_path = output_dir / "run.jsonl"
    summary_path = output_dir / "run-summary.json"
    console_path = output_dir / "run-console.txt"
    comparison_detail_path = output_dir / "comparison-detail.json"
    comparison_summary_path = output_dir / "comparison-summary.json"
    comparison_console_path = output_dir / "comparison-console.txt"
    for path in (run_path, summary_path, console_path, comparison_detail_path, comparison_summary_path, comparison_console_path):
        if path.exists():
            raise RuntimeError(f"refusing to overwrite {path}")

    release_manifest_path = suite_dir / "release-manifest.json"
    release_manifest = json.loads(release_manifest_path.read_text(encoding="utf-8"))
    release_checks = {}
    for name, record in release_manifest["files"].items():
        path = suite_dir / name
        release_checks[name] = {
            "bytes_match": path.stat().st_size == record["bytes"],
            "sha256_match": sha256(path) == record["sha256"],
        }
    if not all(all(item.values()) for item in release_checks.values()):
        raise RuntimeError("public suite release file hash/size mismatch")
    suite_path = suite_dir / "suite.json"
    cases_path = suite_dir / "cases.json"
    oracle_path = suite_dir / "oracle.json"
    if sha256(suite_path) != EXPECTED_SUITE_SHA256:
        raise RuntimeError("historical plaintext suite hash mismatch")
    cases_document = json.loads(cases_path.read_text(encoding="utf-8"))
    cases = cases_document["cases"]
    if cases_document.get("suite_id") != "structured-transfer-heldout-v1" or len(cases) != 80:
        raise RuntimeError("unexpected public suite identity or case count")

    freeze_path = project / "evidence" / "assumption-checks" / "worker" / "root-patch-freeze-v1.0.2.json"
    if sha256(freeze_path) != EXPECTED_FREEZE_MANIFEST_SHA256:
        raise RuntimeError("1.0.2 freeze manifest hash mismatch")
    freeze = json.loads(freeze_path.read_text(encoding="utf-8"))
    frozen_checks = []
    for relative, expected in freeze["file_sha256"].items():
        actual = sha256(project / relative)
        frozen_checks.append({"path": relative, "expected": expected, "actual": actual, "matches": actual == expected})
    if len(frozen_checks) != 19 or not all(item["matches"] for item in frozen_checks):
        raise RuntimeError("frozen project file mismatch")

    sys.path.insert(0, str(project / "src"))
    from atlas_checks import ALGORITHM_VERSION, check_transfer  # noqa: PLC0415

    if ALGORITHM_VERSION != EXPECTED_ALGORITHM_VERSION:
        raise RuntimeError(f"unexpected algorithm version {ALGORITHM_VERSION!r}")
    started_at = utc_now()
    exception_count = 0
    verdicts: Counter[str] = Counter()
    with run_path.open("x", encoding="utf-8", newline="\n") as stream:
        for sequence, case in enumerate(cases, start=1):
            record: dict[str, Any] = {
                "sequence": sequence,
                "case_id": case["case_id"],
                "partition": case["partition"],
                "pair": case["pair"],
                "theme": case["theme"],
                "implementation_output": None,
                "exception": None,
            }
            try:
                result = check_transfer(copy.deepcopy(case["input"]))
                record["implementation_output"] = result
                verdicts[str(result.get("verdict"))] += 1
            except BaseException as exc:
                exception_count += 1
                record["exception"] = {
                    "class": type(exc).__name__,
                    "message": str(exc),
                    "traceback": traceback.format_exc(),
                }
            stream.write(json.dumps(record, sort_keys=True, separators=(",", ":"), ensure_ascii=True) + "\n")
            stream.flush()

    completed_at = utc_now()
    summary = {
        "schema_version": "1.0",
        "run_kind": "portable_public_reproduction",
        "auditor": "/root/sol_atlas_audit",
        "started_at": started_at,
        "completed_at": completed_at,
        "algorithm_version": ALGORITHM_VERSION,
        "python": platform.python_version(),
        "project_root": str(project),
        "freeze_manifest_sha256": sha256(freeze_path),
        "verified_frozen_file_count": len(frozen_checks),
        "suite_id": cases_document["suite_id"],
        "suite_plaintext_sha256": sha256(suite_path),
        "cases_sha256": sha256(cases_path),
        "oracle_sha256": sha256(oracle_path),
        "case_count": len(cases),
        "implementation_exception_count": exception_count,
        "observed_verdict_histogram": dict(sorted(verdicts.items())),
        "run_jsonl": str(run_path),
        "run_jsonl_sha256": sha256(run_path),
        "comparison_status": "not_performed_until_after_this_run_was_fully_retained",
        "implementation_modified": False,
    }
    summary_path.write_text(json.dumps(summary, indent=2, sort_keys=True, ensure_ascii=True) + "\n", encoding="utf-8", newline="\n")
    console_path.write_text(
        "\n".join([
            "Portable public structured-transfer evaluation",
            f"started_at={started_at}",
            f"completed_at={completed_at}",
            f"algorithm_version={ALGORITHM_VERSION}",
            f"verified_frozen_files={len(frozen_checks)}",
            f"cases={len(cases)}",
            f"implementation_exception_count={exception_count}",
            f"run_jsonl_sha256={sha256(run_path)}",
            "comparison_status=run retained; invoking comparator next",
        ]) + "\n",
        encoding="utf-8",
        newline="\n",
    )

    comparator = suite_dir / "compare_public_suite.py"
    command = [
        sys.executable,
        str(comparator),
        "--cases", str(cases_path),
        "--oracle", str(oracle_path),
        "--run-jsonl", str(run_path),
        "--detail-output", str(comparison_detail_path),
        "--summary-output", str(comparison_summary_path),
    ]
    completed = subprocess.run(command, capture_output=True, text=True, encoding="utf-8", errors="backslashreplace", check=False)
    comparison_console_path.write_text(
        json.dumps({"command": command, "exit_code": completed.returncode, "stdout": completed.stdout, "stderr": completed.stderr}, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
        newline="\n",
    )
    compact = {
        "run_jsonl_sha256": sha256(run_path),
        "implementation_exception_count": exception_count,
        "comparison_exit_code": completed.returncode,
        "comparison_summary_sha256": sha256(comparison_summary_path) if comparison_summary_path.exists() else None,
        "output_dir": str(output_dir),
    }
    print(json.dumps(compact, sort_keys=True))
    return completed.returncode


if __name__ == "__main__":
    raise SystemExit(main())
