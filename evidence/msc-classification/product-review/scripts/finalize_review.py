"""Validate the scoped final report and build a compact publication manifest."""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def record(root: Path, relative: str, *, copy: bool = True) -> dict[str, Any]:
    path = root / relative
    return {"path": relative.replace("\\", "/"), "bytes": path.stat().st_size, "sha256": sha256(path), "copy": copy}


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--review-root", type=Path, required=True)
    parser.add_argument("--project-root", type=Path, required=True)
    parser.add_argument("--author-work", type=Path, required=True)
    parser.add_argument("--import-audit", type=Path, required=True)
    args = parser.parse_args()
    root = args.review_root.resolve()
    project = args.project_root.resolve()
    author = args.author_work.resolve()

    final = json.loads((root / "final-msc-product-audit.json").read_text(encoding="utf-8"))
    findings = json.loads((root / "findings.json").read_text(encoding="utf-8"))
    audit = json.loads((root / "results/audit-02.json").read_text(encoding="utf-8"))
    audit_first = json.loads((root / "results/audit-01.json").read_text(encoding="utf-8"))
    docs = json.loads((root / "results/docs-ci-review-01.json").read_text(encoding="utf-8"))
    freeze = json.loads((author / "preexecution-freeze-03.json").read_text(encoding="utf-8-sig"))
    author_checks = json.loads((author / "checks-02.json").read_text(encoding="utf-8"))
    build = json.loads((author / "logs/attempt-msc-production-build-01.json").read_text(encoding="utf-8"))
    tsc = json.loads((author / "logs/attempt-msc-tsc-02.json").read_text(encoding="utf-8"))
    lint = json.loads((author / "logs/attempt-msc-lint-02.json").read_text(encoding="utf-8"))
    import_audit = json.loads(args.import_audit.read_text(encoding="utf-8"))

    expected_gate_ids = {"reproduction", "specification_compliance", "source_verification", "implementation_alignment"}
    final_gates = {item["id"]: item["status"] for item in final["checks"]}
    current_mismatches = []
    for item in freeze["files"]:
        path = project / item["path"]
        if path.stat().st_size != item["bytes"] or sha256(path) != item["sha256"]:
            current_mismatches.append(item["path"])

    checks = {
        "final_gate_ids_exact": set(final_gates) == expected_gate_ids,
        "final_gate_statuses_approved": final_gates == {
            "reproduction": "PASS",
            "specification_compliance": "PASS",
            "source_verification": "PASS_SCOPED",
            "implementation_alignment": "PASS",
        },
        "final_recommendation": final["recommendation"] == "PASS_FOR_SCOPED_SUBJECT_BROWSER_PRODUCT",
        "no_unresolved_substantive_findings": findings["unresolved_substantive_findings"] == [] and final["unresolved_substantive_findings"] == [],
        "corrected_audit_passes": audit["status"] == "pass" and audit["failed_checks"] == 0 and set(audit["gates"].values()) == {"pass"},
        "first_audit_failure_preserved": audit_first["status"] == "fail" and audit_first["failed_checks"] == 1,
        "docs_ci_passes": docs["status"] == "pass" and docs["failed"] == 0,
        "current_project_matches_freeze": not current_mismatches,
        "freeze_hash_matches_report": sha256(author / "preexecution-freeze-03.json") == final["target"]["final_freeze_sha256"],
        "author_checks_pass": author_checks["status"] == "pass" and author_checks["passed"] == 55 and author_checks["failed"] == 0,
        "author_build_pass": build["returncode"] == 0 and not build["timed_out"],
        "author_typecheck_pass": tsc["returncode"] == 0 and not tsc["timed_out"],
        "author_lint_pass": lint["returncode"] == 0 and not lint["timed_out"],
        "separate_import_audit_pass": import_audit["recommendation"] == "PASS_FOR_SCOPED_DATA_ADAPTER" and sha256(args.import_audit) == "878a51115ef7a4a720a3e33b36933c3f16385dc8a47873524ef8ced226dc0ad1",
    }
    validation = {
        "schema_version": "independent-msc-product-final-validation-v1",
        "auditor": "/root/sol_atlas_audit",
        "checks": checks,
        "all_pass": all(checks.values()),
        "current_project_mismatches": current_mismatches,
    }
    validation_path = root / "final-validation.json"
    if validation_path.exists():
        raise FileExistsError(f"Refusing to overwrite: {validation_path}")
    validation_path.write_text(json.dumps(validation, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    if not validation["all_pass"]:
        print(json.dumps(validation, sort_keys=True))
        return 1

    copy_files = [
        "final-msc-product-audit.json",
        "findings.json",
        "final-validation.json",
        "reviewed-inputs.json",
        "reviewed-inputs-attempt02.json",
        "checker-correction-01.json",
        "results/audit-01.json",
        "results/audit-02.json",
        "results/docs-ci-review-01.json",
        "scripts/audit_msc_product.py",
        "scripts/check_docs_ci.py",
        "scripts/freeze_review.py",
        "scripts/finalize_review.py",
        "scripts/verify_publication.py",
        "scripts/run_logged.py",
        "logs/msc-independent-audit-01.json",
        "logs/msc-independent-audit-01.stdout.bin",
        "logs/msc-independent-audit-01.stderr.bin",
        "logs/msc-independent-audit-02.json",
        "logs/msc-independent-audit-02.stdout.bin",
        "logs/msc-independent-audit-02.stderr.bin",
        "logs/docs-ci-review-01.json",
        "logs/docs-ci-review-01.stdout.bin",
        "logs/docs-ci-review-01.stderr.bin",
        "logs/freeze-01.json",
        "logs/freeze-01.stdout.bin",
        "logs/freeze-01.stderr.bin",
        "logs/freeze-02.json",
        "logs/freeze-02.stdout.bin",
        "logs/freeze-02.stderr.bin",
        "raw-http-01/page-root.json",
        "raw-http-01/page-root.body.bin",
    ]
    selected_stems = [
        "all-subjects-page-1",
        "detail-conditional",
        "detail-collection",
        "detail-hierarchy-disagreement",
        "detail-label-difference",
        "detail-empty-leaf",
        "detail-tex-string",
        "detail-max-outgoing",
        "invalid-01",
        "invalid-04",
        "invalid-06",
        "invalid-09",
        "invalid-20",
        "invalid-21",
        "valid-query-limit",
        "valid-far-page",
        "invalid-method-post",
        "page-root",
        "page-conditional",
        "page-collection",
        "page-hierarchy",
        "page-label",
        "page-empty",
        "page-tex",
        "page-invalid",
        "page-search",
        "page-duplicate_query",
    ]
    for stem in selected_stems:
        copy_files.extend([f"raw-http-02/{stem}.json", f"raw-http-02/{stem}.body.bin"])

    external = [
        {"path": str((author / "preexecution-freeze-03.json").resolve()), "sha256": sha256(author / "preexecution-freeze-03.json"), "copy": False, "role": "final_author_freeze"},
        {"path": str((author / "checks-02.json").resolve()), "sha256": sha256(author / "checks-02.json"), "copy": False, "role": "author_product_checks"},
        {"path": str((author / "logs/attempt-msc-product-checks-02.json").resolve()), "sha256": sha256(author / "logs/attempt-msc-product-checks-02.json"), "copy": False, "role": "author_product_command"},
        {"path": str((author / "logs/attempt-msc-production-build-01.json").resolve()), "sha256": sha256(author / "logs/attempt-msc-production-build-01.json"), "copy": False, "role": "author_build_command"},
        {"path": str((author / "logs/attempt-msc-tsc-02.json").resolve()), "sha256": sha256(author / "logs/attempt-msc-tsc-02.json"), "copy": False, "role": "author_typecheck_command"},
        {"path": str((author / "logs/attempt-msc-lint-02.json").resolve()), "sha256": sha256(author / "logs/attempt-msc-lint-02.json"), "copy": False, "role": "author_lint_command"},
        {"path": str(args.import_audit.resolve()), "sha256": sha256(args.import_audit), "copy": False, "role": "separate_independent_source_import_gate"},
    ]
    manifest = {
        "schema_version": "independent-msc-product-publication-manifest-v1",
        "artifact_type": "compact_publication_manifest",
        "auditor": "/root/sol_atlas_audit",
        "recommendation": final["recommendation"],
        "copy_records": [record(root, relative) for relative in copy_files],
        "external_evidence_records": external,
        "excluded": [
            {"pattern": ".venv/**", "reason": "isolated disposable runtime"},
            {"pattern": "raw-http-01/** except page-root pair", "reason": "failed run repeated the same API evidence; only the body demonstrating the checker false negative is published"},
            {"pattern": "raw-http-02/invalid-* except selected representatives", "reason": "the typed audit retains all 21 paths, statuses and errors; repeated small bodies are omitted"},
            {"pattern": "unretained traversal bodies", "reason": "the 971-request audit retains canonical code/page/body ledgers rather than 971 duplicate response files"},
        ],
    }
    manifest_path = root / "publication-manifest.json"
    if manifest_path.exists():
        raise FileExistsError(f"Refusing to overwrite: {manifest_path}")
    manifest_path.write_text(json.dumps(manifest, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    seal = {
        "schema_version": "independent-msc-product-review-seal-v1",
        "auditor": "/root/sol_atlas_audit",
        "sealed_files": {
            relative: record(root, relative)
            for relative in (
                "final-msc-product-audit.json",
                "findings.json",
                "final-validation.json",
                "results/audit-02.json",
                "results/docs-ci-review-01.json",
                "reviewed-inputs-attempt02.json",
                "publication-manifest.json",
            )
        },
    }
    seal_path = root / "review-seal.json"
    if seal_path.exists():
        raise FileExistsError(f"Refusing to overwrite: {seal_path}")
    seal_path.write_text(json.dumps(seal, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(json.dumps({
        "status": "sealed",
        "validation_sha256": sha256(validation_path),
        "manifest_sha256": sha256(manifest_path),
        "seal_sha256": sha256(seal_path),
        "copy_records": len(manifest["copy_records"]),
    }, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
