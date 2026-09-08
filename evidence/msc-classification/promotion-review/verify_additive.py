from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--prior", type=Path, required=True)
    parser.add_argument("--candidate", type=Path, required=True)
    parser.add_argument("--project", type=Path, required=True)
    parser.add_argument("--review-source", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    prior = json.loads(args.prior.read_text(encoding="utf-8"))
    candidate = json.loads(args.candidate.read_text(encoding="utf-8"))
    project = args.project.resolve()
    review_source = args.review_source.resolve()

    prior_count = len(prior["artifacts"])
    added = candidate["artifacts"][prior_count:]
    added_checks = []
    for entry in added:
        path = project / entry["path"]
        actual = digest(path) if path.is_file() else None
        added_checks.append({
            "id": entry["id"],
            "path": entry["path"],
            "exists": path.is_file(),
            "expected_sha256": entry["sha256"],
            "actual_sha256": actual,
            "pass": actual == entry["sha256"],
        })

    review_prefix = "evidence/msc-classification/promotion-review/"
    review_rows = [row for row in added_checks if row["path"].startswith(review_prefix)]
    review_copy_checks = []
    for row in review_rows:
        rel = row["path"].removeprefix(review_prefix)
        source = review_source / rel
        review_copy_checks.append({
            "path": rel,
            "source_exists": source.is_file(),
            "source_sha256": digest(source) if source.is_file() else None,
            "candidate_sha256": row["actual_sha256"],
            "byte_identical": source.is_file() and digest(source) == row["actual_sha256"],
        })

    other_top_level_keys = sorted(set(prior) | set(candidate) - {"artifacts"})
    top_level = {key: prior.get(key) == candidate.get(key) for key in other_top_level_keys if key != "artifacts"}
    result = {
        "schema_version": "msc-promotion-additive-check-v1",
        "prior": {"path": str(args.prior.resolve()), "sha256": digest(args.prior), "artifacts": prior_count},
        "candidate": {"path": str(args.candidate.resolve()), "sha256": digest(args.candidate), "artifacts": len(candidate["artifacts"])},
        "candidate_matches_project_bundle": digest(args.candidate) == digest(project / ".codex/evidence/runs/msc-classification-v1/bundle.json"),
        "prior_artifact_records_preserved_as_prefix": candidate["artifacts"][:prior_count] == prior["artifacts"],
        "all_nonartifact_top_level_values_unchanged": all(top_level.values()),
        "top_level_value_checks": top_level,
        "added_artifacts": {
            "count": len(added),
            "ids": [row["id"] for row in added],
            "all_exist_and_hash_match": all(row["pass"] for row in added_checks),
            "promotion_review_count": len(review_rows),
            "assembly_history_count": sum(row["path"].startswith("evidence/msc-classification/assembly/") for row in added_checks),
            "copy_receipt_count": sum(row["path"] == "evidence/msc-classification/publication-copy-03.json" for row in added_checks),
            "paths_with_unexpected_scope": [
                row["path"] for row in added_checks
                if not (
                    row["path"].startswith(review_prefix)
                    or row["path"].startswith("evidence/msc-classification/assembly/")
                    or row["path"] == "evidence/msc-classification/publication-copy-03.json"
                )
            ],
            "rows": added_checks,
        },
        "promotion_review_copies": {
            "count": len(review_copy_checks),
            "all_byte_identical": all(row["byte_identical"] for row in review_copy_checks),
            "rows": review_copy_checks,
        },
    }
    result["all_pass"] = all([
        result["candidate_matches_project_bundle"],
        result["prior_artifact_records_preserved_as_prefix"],
        result["all_nonartifact_top_level_values_unchanged"],
        result["added_artifacts"]["count"] == 37,
        result["added_artifacts"]["ids"] == [f"A{i}" for i in range(266, 303)],
        result["added_artifacts"]["all_exist_and_hash_match"],
        result["added_artifacts"]["promotion_review_count"] == 27,
        result["added_artifacts"]["assembly_history_count"] == 9,
        result["added_artifacts"]["copy_receipt_count"] == 1,
        not result["added_artifacts"]["paths_with_unexpected_scope"],
        result["promotion_review_copies"]["all_byte_identical"],
    ])
    args.output.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({
        "output": str(args.output.resolve()),
        "output_sha256": digest(args.output),
        "candidate_sha256": result["candidate"]["sha256"],
        "prior_artifacts_preserved": result["prior_artifact_records_preserved_as_prefix"],
        "nonartifact_values_unchanged": result["all_nonartifact_top_level_values_unchanged"],
        "added": {
            "total": result["added_artifacts"]["count"],
            "review": result["added_artifacts"]["promotion_review_count"],
            "assembly": result["added_artifacts"]["assembly_history_count"],
            "receipt": result["added_artifacts"]["copy_receipt_count"],
        },
        "all_pass": result["all_pass"],
    }, indent=2))


if __name__ == "__main__":
    main()
