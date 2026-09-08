"""Narrow documentation and CI alignment check for the frozen MSC product files."""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--project-root", type=Path, required=True)
    parser.add_argument("--freeze", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    if args.output.exists():
        raise FileExistsError(f"Refusing to overwrite: {args.output}")
    root = args.project_root.resolve()
    freeze = json.loads(args.freeze.read_text(encoding="utf-8-sig"))
    expected = {row["path"]: row for row in freeze["files"]}
    reviewed = [
        "README.md",
        "docs/coverage.md",
        "docs/reuse-decision.md",
        "docs/subject-browser.md",
        ".github/workflows/verify.yml",
        ".github/workflows/reproduce-subject-classification.yml",
    ]
    checks: list[dict[str, object]] = []

    def check(name: str, condition: bool, note: str) -> None:
        checks.append({"name": name, "passed": bool(condition), "note": note})

    for relative in reviewed:
        path = root / relative
        check(
            f"frozen hash {relative}",
            path.stat().st_size == expected[relative]["bytes"] and sha256(path) == expected[relative]["sha256"],
            expected[relative]["sha256"],
        )

    readme = (root / "README.md").read_text(encoding="utf-8")
    coverage = (root / "docs/coverage.md").read_text(encoding="utf-8")
    reuse = (root / "docs/reuse-decision.md").read_text(encoding="utf-8")
    subject_doc = (root / "docs/subject-browser.md").read_text(encoding="utf-8")
    verify = (root / ".github/workflows/verify.yml").read_text(encoding="utf-8")
    reproduce = (root / ".github/workflows/reproduce-subject-classification.yml").read_text(encoding="utf-8")
    importer = (root / "experiments/msc-index/import_msc.py").read_text(encoding="utf-8")
    wrapper = (root / "experiments/msc-index/run_logged.py").read_text(encoding="utf-8")

    count_phrase = "6,603"
    reference_phrase = "3,083"
    check("README states bounded classification counts", count_phrase in readme and reference_phrase in readme, "Subject and source-reference counts are labelled as classification records.")
    check("coverage keeps imported layers distinct", "Neither import automatically establishes a mathematical identity" in coverage and "not summed into a universal coverage percentage" in coverage, "No proof or universal-coverage promotion.")
    check("reuse decision keeps subject navigation scoped", "This is classification navigation" in reuse and "no automatic equivalence or prerequisite claim" in reuse, "The MSC import is not promoted to a mathematical crosswalk.")
    check("subject guide gives exact count and condition scope", "All 415 conditional references retain their scope records" in subject_doc and "62-member collection" in subject_doc, "Condition-bearing and collection records remain explicit.")
    check("subject guide distinguishes detail and list payloads", "Detail responses retain source locators and exact RDF identifiers; paginated lists contain subject summaries." in subject_doc, "Reviewer-requested precision correction is present.")
    check("subject guide disclaims proof and completeness", "does not establish prerequisites, equivalences, proofs" in subject_doc and "completeness of mathematical knowledge" in subject_doc, "No formal-proof or coverage overclaim.")
    check("README reproduction includes product check", "node scripts/check-subjects.ts" in readme, "Documented project check exists.")
    check("main verification workflow includes product check", "- run: node scripts/check-subjects.ts" in verify, "Existing verification job runs the catalogue checker.")
    check("reproduction workflow invokes frozen uv importer", "uv run --project experiments/msc-index --frozen python" in reproduce and "experiments/msc-index/import_msc.py" in reproduce, "Command uses the packaged uv project and retained inputs.")
    check("reproduction workflow compares all outputs", all(f"cmp data/msc/{name}.json work/msc-ci/index/{name}.json" in reproduce for name in ("subjects", "references", "summary")), "All three generated artifacts are byte-compared.")
    check("reproduction workflow runs navigation check", "node scripts/check-subjects.ts --output work/msc-ci/product-checks.json" in reproduce, "The product checker runs without requiring a live server.")
    check("workflow wrapper flag matches implementation", "--log-dir work/msc-ci/logs" in reproduce and 'parser.add_argument("--log-dir"' in wrapper, "CI uses the wrapper's implemented flag.")
    check("workflow importer flags match implementation", all(flag in importer for flag in ('"--source-root"', '"--output-dir"')) and "--source-root experiments/msc-index/inputs --output-dir work/msc-ci/index" in reproduce, "CI uses implemented importer options.")
    check("workflow retains evidence on failure", "if: always()" in reproduce and "retention-days: 30" in reproduce, "The CI output directory is uploaded for passing and failing runs.")

    status = "pass" if all(row["passed"] for row in checks) else "fail"
    result = {
        "schema_version": "independent-msc-docs-ci-review-v1",
        "auditor": "/root/sol_atlas_audit",
        "status": status,
        "scope": "Frozen subject-browser counts, boundary wording, documented commands and CI command/flag alignment; workflow was inspected, not executed on GitHub.",
        "freeze": {"path": str(args.freeze.resolve()), "sha256": sha256(args.freeze)},
        "reviewed_files": [{"path": path, "sha256": sha256(root / path)} for path in reviewed],
        "checks": checks,
        "failed": sum(not row["passed"] for row in checks),
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(json.dumps({"status": status, "checks": len(checks), "failed": result["failed"], "output": str(args.output.resolve()), "output_sha256": sha256(args.output)}, sort_keys=True))
    return 0 if status == "pass" else 1


if __name__ == "__main__":
    raise SystemExit(main())
