from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path, PurePosixPath


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def read_json(path: Path) -> object:
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, value: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(
        (json.dumps(value, ensure_ascii=True, sort_keys=True, indent=2) + "\n").encode(
            "utf-8"
        )
    )


def safe_relative(value: str) -> bool:
    path = PurePosixPath(value)
    return bool(value) and not path.is_absolute() and ".." not in path.parts


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--project-root", type=Path, required=True)
    parser.add_argument("--freeze", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    project = args.project_root.resolve()
    freeze_path = args.freeze.resolve()
    freeze = read_json(freeze_path)
    assert isinstance(freeze, dict)
    checks: list[dict[str, object]] = []

    def check(name: str, condition: bool, detail: object) -> None:
        checks.append({"name": name, "passed": bool(condition), "detail": detail})

    input_failures = []
    for record in freeze["inputs"]:
        path = Path(record["path"])
        actual = sha256(path)
        if actual != record["sha256"]:
            input_failures.append(
                {"path": str(path), "expected": record["sha256"], "actual": actual}
            )
    check("all frozen delta-review inputs match", not input_failures, input_failures)

    assembly_path = Path(freeze["named_inputs"]["release_assembly"])
    bundle_path = Path(freeze["named_inputs"]["assembled_bundle"])
    original_bundle_path = Path(freeze["named_inputs"]["original_bundle"])
    implementation_freeze_path = Path(freeze["named_inputs"]["implementation_freeze"])
    audit_path = Path(freeze["named_inputs"]["independent_audit"])
    publication_manifest_path = Path(
        freeze["named_inputs"]["independent_publication_manifest"]
    )
    assembly = read_json(assembly_path)
    bundle = read_json(bundle_path)
    original_bundle = read_json(original_bundle_path)
    implementation_freeze = read_json(implementation_freeze_path)
    audit = read_json(audit_path)
    publication_manifest = read_json(publication_manifest_path)
    assert all(
        isinstance(item, dict)
        for item in (
            assembly,
            bundle,
            original_bundle,
            implementation_freeze,
            audit,
            publication_manifest,
        )
    )

    target_failures = []
    for target in assembly["review_targets"]:
        path = project / target["path"]
        actual = sha256(path)
        if actual != target["sha256"] or path.stat().st_size != target["bytes"]:
            target_failures.append(
                {
                    "path": target["path"],
                    "expected_sha256": target["sha256"],
                    "actual_sha256": actual,
                    "expected_bytes": target["bytes"],
                    "actual_bytes": path.stat().st_size,
                }
            )
    check(
        "all four release-assembly review targets match",
        not target_failures and len(assembly["review_targets"]) == 4,
        {"target_count": len(assembly["review_targets"]), "failures": target_failures},
    )

    frozen_deltas = []
    for record in implementation_freeze["files"]:
        path = project / record["path"]
        actual = sha256(path)
        if actual != record["sha256"]:
            frozen_deltas.append(
                {
                    "path": record["path"],
                    "before_sha256": record["sha256"],
                    "after_sha256": actual,
                }
            )
    check(
        "exactly one frozen file changed and it is the declared bridge documentation delta",
        frozen_deltas == assembly["frozen_file_delta"]
        and assembly["unchanged_frozen_files"] == 48,
        {"actual": frozen_deltas, "declared": assembly["frozen_file_delta"]},
    )

    original_claims = original_bundle["claims"]
    current_claims = bundle["claims"]
    check(
        "C001-C007 remain byte-value identical",
        current_claims == original_claims
        and [claim["id"] for claim in current_claims]
        == assembly["unchanged_claim_ids"],
        {
            "ids": [claim["id"] for claim in current_claims],
            "equal_to_bundle_draft": current_claims == original_claims,
        },
    )

    report_checks = {record["id"]: record for record in audit["four_checks"]}
    bundle_checks = {record["id"]: record for record in bundle["checks"]}
    check_failures = []
    for check_id, report_check in report_checks.items():
        bundled = bundle_checks.get(check_id)
        if not bundled or bundled["status"] != "pass":
            check_failures.append({"id": check_id, "reason": "missing or non-pass"})
            continue
        if bundled["auditor"] != report_check["auditor"] or bundled["note"] != report_check["note"]:
            check_failures.append({"id": check_id, "reason": "auditor or note differs"})
    check(
        "bundle carries all four sealed gate decisions without changing notes",
        not check_failures and set(bundle_checks) == set(report_checks),
        check_failures,
    )

    artifact_ids: set[str] = set()
    artifact_paths: set[str] = set()
    artifact_failures = []
    for artifact in bundle["artifacts"]:
        if artifact["id"] in artifact_ids:
            artifact_failures.append({"id": artifact["id"], "error": "duplicate ID"})
        artifact_ids.add(artifact["id"])
        if artifact["path"] in artifact_paths:
            artifact_failures.append(
                {"path": artifact["path"], "error": "duplicate path"}
            )
        artifact_paths.add(artifact["path"])
        if not safe_relative(artifact["path"]):
            artifact_failures.append(
                {"path": artifact["path"], "error": "unsafe path"}
            )
            continue
        path = project / artifact["path"]
        if not path.is_file():
            artifact_failures.append(
                {"path": artifact["path"], "error": "missing file"}
            )
        elif sha256(path) != artifact["sha256"]:
            artifact_failures.append(
                {
                    "path": artifact["path"],
                    "error": "hash mismatch",
                    "actual": sha256(path),
                    "expected": artifact["sha256"],
                }
            )
    check(
        "all assembled bundle artifacts have unique safe paths and matching bytes",
        not artifact_failures and len(bundle["artifacts"]) == 259,
        {"artifact_count": len(bundle["artifacts"]), "failures": artifact_failures},
    )

    independent_root = project / "evidence" / "boolean-rank" / "independent"
    copied_failures = []
    for record in publication_manifest["records"]:
        path = independent_root / record["path"]
        if not path.is_file() or sha256(path) != record["sha256"]:
            copied_failures.append(record["path"])
    check(
        "all 144 selected independent publication records copied byte-identically",
        len(publication_manifest["records"]) == 144 and not copied_failures,
        {
            "record_count": len(publication_manifest["records"]),
            "failures": copied_failures,
            "manifest_sha256": sha256(publication_manifest_path),
        },
    )

    note = (project / "docs" / "boolean-rank-verification.md").read_text(
        encoding="utf-8"
    )
    bridge = (project / "docs" / "boolean-rank-bridge.md").read_text(
        encoding="utf-8"
    )
    normalized_note = " ".join(note.split())
    documentation_conditions = {
        "scoped_integration": "accepted the scoped integration" in note,
        "role_disclosed": "integration-design advice, but did not" in note,
        "source_gate_limited": "not treated as a proof of source entailment" in normalized_note,
        "no_visual_claim": "visual or\nresponsive quality" in note,
        "no_impact_claim": "measured real-world benefit" in note,
        "bridge_pass_link": "[scoped independent product review](boolean-rank-verification.md)" in bridge,
        "bridge_no_new_source_proof": "does not constitute a new primary-source proof" in bridge,
        "old_product_pending_removed": "product integration still requires its own independent final review" not in bridge,
    }
    check(
        "verification note and bridge status replacement preserve the sealed scope",
        all(documentation_conditions.values()),
        documentation_conditions,
    )

    workflow = (project / ".github" / "workflows" / "verify.yml").read_text(
        encoding="utf-8"
    )
    workflow_conditions = {
        "audited_checker": "node scripts/check-boolean-rank.mjs --output work/boolean-rank-ci/functional.json" in workflow,
        "logged_runner": "experiments/msc-index/run_logged.py" in workflow,
        "uv_frozen": "uv run --project experiments/msc-index --frozen python" in workflow,
        "bounded_timeout": "--attempt-id boolean-rank-ci --timeout-seconds 300" in workflow,
        "raw_folder_uploaded": "path: work/boolean-rank-ci/" in workflow,
        "pinned_upload": "actions/upload-artifact@ea165f8d65b6e75b540449e92b4886f43607fa02" in workflow,
    }
    check(
        "workflow delta schedules the audited checker and raw folder with pinned actions",
        all(workflow_conditions.values()),
        workflow_conditions,
    )

    expected_pending_limitation = (
        "The independent product audit passed for the frozen implementation. The "
        "documentation, CI and evidence-assembly delta is pending its separate "
        "acknowledgment; publication remains withheld until then."
    )
    check(
        "current bundle truthfully keeps additive review pending",
        bundle["limitations"][0] == expected_pending_limitation,
        bundle["limitations"][0],
    )

    passed = all(record["passed"] for record in checks)
    output = {
        "schema_version": "boolean-rank-release-delta-independent-check-v1",
        "auditor": "/root/sol_atlas_audit",
        "passed": passed,
        "check_count": len(checks),
        "checks": checks,
        "scope": (
            "Exact additive documentation, CI-command and evidence-assembly review only. "
            "No repeated runtime, browser, mathematical-source, production-build, hosted-CI "
            "or deployment verification."
        ),
    }
    write_json(args.output.resolve(), output)
    print(json.dumps(output, ensure_ascii=True, sort_keys=True, indent=2))
    return 0 if passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
