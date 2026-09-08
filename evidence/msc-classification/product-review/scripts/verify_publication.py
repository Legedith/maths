"""Verify all files and hashes in the independent MSC publication manifest and seal."""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--review-root", type=Path, required=True)
    args = parser.parse_args()
    root = args.review_root.resolve()
    manifest = json.loads((root / "publication-manifest.json").read_text(encoding="utf-8"))
    seal = json.loads((root / "review-seal.json").read_text(encoding="utf-8"))
    records = manifest["copy_records"]
    paths = [item["path"] for item in records]
    checks = {
        "manifest_schema": manifest["schema_version"] == "independent-msc-product-publication-manifest-v1",
        "recommendation": manifest["recommendation"] == "PASS_FOR_SCOPED_SUBJECT_BROWSER_PRODUCT",
        "copy_paths_unique": len(paths) == len(set(paths)),
        "copy_flags": all(item["copy"] is True for item in records),
        "copy_files_exist": all((root / item["path"]).is_file() for item in records),
        "copy_sizes_match": all((root / item["path"]).stat().st_size == item["bytes"] for item in records),
        "copy_hashes_match": all(sha256(root / item["path"]) == item["sha256"] for item in records),
        "external_flags": all(item["copy"] is False for item in manifest["external_evidence_records"]),
        "seal_schema": seal["schema_version"] == "independent-msc-product-review-seal-v1",
        "seal_hashes_match": all(
            (root / item["path"]).stat().st_size == item["bytes"] and sha256(root / item["path"]) == item["sha256"]
            for item in seal["sealed_files"].values()
        ),
    }
    result = {
        "schema_version": "independent-msc-product-publication-verification-v1",
        "checks": checks,
        "all_pass": all(checks.values()),
        "copy_records": len(records),
        "external_evidence_records": len(manifest["external_evidence_records"]),
        "manifest_sha256": sha256(root / "publication-manifest.json"),
        "seal_sha256": sha256(root / "review-seal.json"),
    }
    print(json.dumps(result, sort_keys=True))
    return 0 if result["all_pass"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
