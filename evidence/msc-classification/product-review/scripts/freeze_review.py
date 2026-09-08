"""Freeze the exact independent checker and reviewed project artifacts before execution."""
from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import json
from pathlib import Path


def file_record(root: Path, relative: str) -> dict[str, object]:
    path = root / relative
    raw = path.read_bytes()
    return {"path": relative.replace("\\", "/"), "bytes": len(raw), "sha256": hashlib.sha256(raw).hexdigest()}


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--project-root", type=Path, required=True)
    parser.add_argument("--author-work", type=Path, required=True)
    parser.add_argument("--review-root", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    if args.output.exists():
        raise FileExistsError(f"Refusing to overwrite: {args.output}")
    project_root = args.project_root.resolve()
    author_work = args.author_work.resolve()
    review_root = args.review_root.resolve()
    upstream_freeze_path = author_work / "preexecution-freeze-03.json"
    upstream_freeze = json.loads(upstream_freeze_path.read_text(encoding="utf-8-sig"))
    project_files = [file_record(project_root, row["path"]) for row in upstream_freeze["files"]]
    expected = {row["path"]: row for row in upstream_freeze["files"]}
    mismatches = [
        {"path": row["path"], "expected": expected[row["path"]], "actual": row}
        for row in project_files
        if row["sha256"] != expected[row["path"]]["sha256"] or row["bytes"] != expected[row["path"]]["bytes"]
    ]
    if mismatches:
        raise AssertionError(f"Project differs from supplied freeze: {mismatches}")
    evidence_paths = [
        "preexecution-freeze-02.json",
        "preexecution-freeze-03.json",
        "checks-02.json",
        "logs/attempt-msc-product-checks-02.json",
        "logs/attempt-msc-product-checks-02.stdout.bin",
        "logs/attempt-msc-product-checks-02.stderr.bin",
        "logs/attempt-msc-production-build-01.json",
        "logs/attempt-msc-production-build-01.stdout.bin",
        "logs/attempt-msc-production-build-01.stderr.bin",
        "logs/attempt-msc-tsc-01.json",
        "logs/attempt-msc-tsc-02.json",
        "logs/attempt-msc-lint-01.json",
        "logs/attempt-msc-lint-02.json",
    ]
    result = {
        "schema_version": "independent-msc-product-review-freeze-v1",
        "auditor": "/root/sol_atlas_audit",
        "frozen_at_utc": dt.datetime.now(dt.timezone.utc).isoformat(),
        "scope": "Frozen project product/data/test/docs/workflow files plus auditor-owned checker; project remains read-only.",
        "project_root": str(project_root),
        "upstream_freeze": file_record(author_work, "preexecution-freeze-02.json"),
        "project_files": project_files,
        "author_evidence_inputs": [file_record(author_work, path) for path in evidence_paths],
        "independent_files": [
            file_record(review_root, "scripts/audit_msc_product.py"),
            file_record(review_root, "scripts/run_logged.py"),
            file_record(review_root, "scripts/freeze_review.py"),
            file_record(review_root, "checker-correction-01.json"),
        ],
        "project_hash_mismatches": mismatches,
        "execution_pending": True,
        "visual_or_dom_review_authorized": False,
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(json.dumps({"status": "frozen", "project_files": len(project_files), "mismatches": len(mismatches), "output": str(args.output.resolve())}, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
