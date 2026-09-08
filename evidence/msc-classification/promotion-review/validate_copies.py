from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def compare_tree(published: Path, original: Path) -> dict[str, Any]:
    rows = []
    for target in sorted(path for path in published.rglob("*") if path.is_file()):
        rel = target.relative_to(published)
        source = original / rel
        target_hash = sha256(target)
        source_hash = sha256(source) if source.is_file() else None
        rows.append({
            "path": rel.as_posix(),
            "original_exists": source.is_file(),
            "published_sha256": target_hash,
            "original_sha256": source_hash,
            "byte_identical": source_hash == target_hash,
        })
    return {
        "published_root": str(published.resolve()),
        "original_root": str(original.resolve()),
        "published_files": len(rows),
        "with_original": sum(row["original_exists"] for row in rows),
        "without_original": sum(not row["original_exists"] for row in rows),
        "byte_identical": sum(row["byte_identical"] for row in rows),
        "all_existing_originals_byte_identical": all(
            row["byte_identical"] for row in rows if row["original_exists"]
        ),
        "unmatched_published_paths": [row["path"] for row in rows if not row["original_exists"]],
        "rows": rows,
    }


def compare_pairs(pairs: list[tuple[str, Path, Path]]) -> dict[str, Any]:
    rows = []
    for role, left, right in pairs:
        left_hash = sha256(left) if left.is_file() else None
        right_hash = sha256(right) if right.is_file() else None
        rows.append({
            "role": role,
            "published": str(left.resolve()),
            "original": str(right.resolve()),
            "published_exists": left.is_file(),
            "original_exists": right.is_file(),
            "published_sha256": left_hash,
            "original_sha256": right_hash,
            "byte_identical": left_hash is not None and left_hash == right_hash,
        })
    return {"count": len(rows), "all_byte_identical": all(row["byte_identical"] for row in rows), "rows": rows}


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--workspace", type=Path, required=True)
    parser.add_argument("--project", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    workspace = args.workspace.resolve()
    project = args.project.resolve()

    trees = {
        "source_review": compare_tree(
            project / "evidence/msc-classification/source-review",
            workspace / "msc-reuse-review-work",
        ),
        "adapter_review": compare_tree(
            project / "evidence/msc-classification/adapter-review",
            workspace / "msc-import-review-work",
        ),
        "product_review": compare_tree(
            project / "evidence/msc-classification/product-review",
            workspace / "msc-product-review-work",
        ),
        "product_history": compare_tree(
            project / "evidence/msc-classification/product-history",
            workspace / "msc-product-work",
        ),
    }

    product_manifest = json.loads(
        (workspace / "msc-product-review-work/publication-manifest.json").read_text(encoding="utf-8")
    )
    product_copy_rows = []
    for entry in product_manifest["copy_records"]:
        published = project / "evidence/msc-classification/product-review" / entry["path"]
        original = workspace / "msc-product-review-work" / entry["path"]
        actual = sha256(published) if published.is_file() else None
        product_copy_rows.append({
            "path": entry["path"],
            "declared_sha256": entry["sha256"],
            "published_sha256": actual,
            "original_sha256": sha256(original) if original.is_file() else None,
            "pass": original.is_file() and actual == entry["sha256"] == sha256(original),
        })
    external_rows = []
    for entry in product_manifest["external_evidence_records"]:
        path = Path(entry["path"])
        actual = sha256(path) if path.is_file() else None
        external_rows.append({
            "role": entry["role"],
            "path": entry["path"],
            "declared_sha256": entry["sha256"],
            "actual_sha256": actual,
            "pass": actual == entry["sha256"],
        })

    direct_pairs = compare_pairs([
        (
            "final_bundle_staging_copy",
            project / ".codex/evidence/runs/msc-classification-v1/bundle.json",
            workspace / "msc-product-work/bundle-final-candidate-03.json",
        ),
        (
            "product_publication_manifest",
            project / "evidence/msc-classification/product-review/publication-manifest.json",
            workspace / "msc-product-review-work/publication-manifest.json",
        ),
        (
            "product_review_seal",
            project / "evidence/msc-classification/product-review/review-seal.json",
            workspace / "msc-product-review-work/review-seal.json",
        ),
        (
            "product_final_audit",
            project / "evidence/msc-classification/product-review/final-msc-product-audit.json",
            workspace / "msc-product-review-work/final-msc-product-audit.json",
        ),
        (
            "product_freeze_03",
            project / "evidence/msc-classification/product-history/preexecution-freeze-03.json",
            workspace / "msc-product-work/preexecution-freeze-03.json",
        ),
        (
            "subjects_author_run",
            project / "data/msc/subjects.json",
            workspace / "msc-import-work/run-03/subjects.json",
        ),
        (
            "references_author_run",
            project / "data/msc/references.json",
            workspace / "msc-import-work/run-03/references.json",
        ),
        (
            "summary_author_run",
            project / "data/msc/summary.json",
            workspace / "msc-import-work/run-03/summary.json",
        ),
        (
            "subjects_auditor_replay",
            project / "data/msc/subjects.json",
            workspace / "msc-import-review-work/replay-output/subjects.json",
        ),
        (
            "references_auditor_replay",
            project / "data/msc/references.json",
            workspace / "msc-import-review-work/replay-output/references.json",
        ),
        (
            "summary_auditor_replay",
            project / "data/msc/summary.json",
            workspace / "msc-import-review-work/replay-output/summary.json",
        ),
        (
            "portable_importer",
            project / "experiments/msc-index/import_msc.py",
            workspace / "msc-import-work/import_msc.py",
        ),
        (
            "portable_contract",
            project / "experiments/msc-index/contract-v1.md",
            workspace / "msc-import-work/contract-v1.md",
        ),
        (
            "portable_official_csv",
            project / "experiments/msc-index/inputs/raw/official.csv",
            workspace / "msc-reuse-work/raw/official.csv",
        ),
        (
            "portable_suggested_turtle",
            project / "experiments/msc-index/inputs/raw/suggestion4.ttl",
            workspace / "msc-reuse-work/raw/suggestion4.ttl",
        ),
        (
            "retained_source_license",
            project / "data/msc/LICENSE-CC-BY-NC-SA-4.0.md",
            workspace / "msc-reuse-work/raw/upstream-license.md",
        ),
    ])

    freeze_path = project / "evidence/msc-classification/product-history/preexecution-freeze-03.json"
    freeze = json.loads(freeze_path.read_text(encoding="utf-8"))
    freeze_rows = []
    for entry in freeze["files"]:
        path = project / entry["path"]
        actual = sha256(path) if path.is_file() else None
        freeze_rows.append({
            "path": entry["path"],
            "expected_sha256": entry["sha256"],
            "actual_sha256": actual,
            "pass": actual == entry["sha256"],
        })
    freeze_validation = {
        "freeze_path": str(freeze_path.resolve()),
        "freeze_sha256": sha256(freeze_path),
        "file_count": len(freeze_rows),
        "all_current_files_match": all(row["pass"] for row in freeze_rows),
        "rows": freeze_rows,
    }

    result = {
        "schema_version": "msc-promotion-copy-validation-v1",
        "reviewer": "/root/sol_symmetry_worker",
        "role": "independent release evidence reviewer; not an author of source inspection, adapter, product, tests, or bundle",
        "trees": trees,
        "product_publication_manifest": {
            "copy_record_count": len(product_copy_rows),
            "all_copy_records_match_published_and_original": all(row["pass"] for row in product_copy_rows),
            "external_record_count": len(external_rows),
            "all_external_records_match": all(row["pass"] for row in external_rows),
            "copy_records": product_copy_rows,
            "external_records": external_rows,
        },
        "direct_pairs": direct_pairs,
        "current_product_against_freeze_03": freeze_validation,
    }
    result["all_checks_pass"] = (
        all(tree["all_existing_originals_byte_identical"] for tree in trees.values())
        and result["product_publication_manifest"]["all_copy_records_match_published_and_original"]
        and result["product_publication_manifest"]["all_external_records_match"]
        and direct_pairs["all_byte_identical"]
        and freeze_validation["all_current_files_match"]
    )
    args.output.write_text(json.dumps(result, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(json.dumps({
        "output": str(args.output.resolve()),
        "output_sha256": sha256(args.output),
        "all_checks_pass": result["all_checks_pass"],
        "trees": {name: {key: tree[key] for key in ("published_files", "with_original", "without_original", "byte_identical", "all_existing_originals_byte_identical", "unmatched_published_paths")} for name, tree in trees.items()},
        "product_manifest": {
            "copy_records": len(product_copy_rows),
            "copy_records_pass": sum(row["pass"] for row in product_copy_rows),
            "external_records": len(external_rows),
            "external_records_pass": sum(row["pass"] for row in external_rows),
        },
        "direct_pairs": {
            "count": direct_pairs["count"],
            "pass": sum(row["byte_identical"] for row in direct_pairs["rows"]),
        },
        "freeze_03": {
            "count": freeze_validation["file_count"],
            "pass": sum(row["pass"] for row in freeze_rows),
        },
    }, indent=2))


if __name__ == "__main__":
    main()
