from __future__ import annotations

import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parent
PROJECT = ROOT.parent / "project"


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def artifact(path: str, kind: str, note: str) -> dict[str, object]:
    absolute = ROOT / path
    if not absolute.is_file():
        raise FileNotFoundError(absolute)
    return {
        "path": path,
        "kind": kind,
        "bytes": absolute.stat().st_size,
        "sha256": sha256(absolute),
        "note": note,
    }


publication_files = [
    artifact(
        "final-library-audit.json",
        "independent-verification",
        "Final scoped verdict with four explicit gate statuses and limitations.",
    ),
    artifact(
        "18-write-final-library-audit.json",
        "command-log",
        "Raw successful command record that constructed the final audit report.",
    ),
    artifact(
        "independent-cases.json",
        "evaluator-contract",
        "Prospective cases frozen before implementation inspection; includes provisional oracle outputs.",
    ),
    artifact(
        "01-freeze-independent-cases.json",
        "command-log",
        "Raw successful command record for freezing the independent cases.",
    ),
    artifact(
        "navigation-check.json",
        "test",
        "Final independent documented-policy fidelity, search, filter, ordering and pagination result.",
    ),
    artifact(
        "17-navigation-check-final.json",
        "test-log",
        "Raw successful final navigation command record.",
    ),
    artifact(
        "route-check.json",
        "test",
        "Final independent route boundary and no-store result.",
    ),
    artifact(
        "08-route-check-attempt05.json",
        "test-log",
        "Raw successful route command after retained harness-loader setup failures.",
    ),
    artifact(
        "09-portable-reproduction.json",
        "reproduction-log",
        "Raw exact explicit-input importer reproduction with output hashes; copied outputs are intentionally omitted.",
    ),
    artifact(
        "webmcp-contract-check.json",
        "test",
        "Independent tool schema, validation, action wiring and root-observation alignment result.",
    ),
    artifact(
        "10-webmcp-contract-check.json",
        "test-log",
        "Raw successful WebMCP contract command record.",
    ),
    artifact(
        "11-author-node-check-rerun.json",
        "reproduction-log",
        "Independent rerun record for the frozen project navigation checker.",
    ),
    artifact(
        "static-integration-check.json",
        "test",
        "Final independent frozen-hash, byte-fidelity, page-delta and disclosure alignment result.",
    ),
    artifact(
        "16-static-integration-check-pass.json",
        "test-log",
        "Raw successful static integration command record.",
    ),
    artifact(
        "02-navigation-check.json",
        "retained-failure-log",
        "Initial navigation failure that exposed the provisional-oracle versus documented-policy variance; retained without rewriting history.",
    ),
    artifact(
        "04-route-check.json",
        "retained-failure-log",
        "First route harness loader/setup failure; target code was not implicated.",
    ),
    artifact(
        "05-route-check-attempt02.json",
        "retained-failure-log",
        "Second route harness loader/setup failure; target code was not implicated.",
    ),
    artifact(
        "06-route-check-attempt03.json",
        "retained-failure-log",
        "Third route harness loader/setup failure; target code was not implicated.",
    ),
    artifact(
        "07-route-check-attempt04.json",
        "retained-failure-log",
        "Fourth route harness loader/setup failure; target code was not implicated.",
    ),
    artifact(
        "12-static-integration-check.json",
        "retained-failure-log",
        "First static-checker false start caused by an evaluator phrase assertion.",
    ),
    artifact(
        "13-static-integration-check-attempt02.json",
        "retained-failure-log",
        "Second static-checker false start caused by an evaluator phrase assertion.",
    ),
    artifact(
        "14-static-integration-check-attempt03.json",
        "retained-failure-log",
        "Third static-checker false start caused by an evaluator phrase assertion.",
    ),
    artifact(
        "15-static-integration-check-attempt04.json",
        "retained-failure-log",
        "Fourth static-checker false start caused by an evaluator phrase assertion.",
    ),
    artifact(
        "freeze_library_cases.py",
        "evaluator-code",
        "Prospective-case generator.",
    ),
    artifact(
        "check_library_integration.mjs",
        "evaluator-code",
        "Independent navigation and exact data-fidelity checker.",
    ),
    artifact(
        "library-alias-loader.mjs",
        "evaluator-support-code",
        "Read-only Node loader used to execute frozen TypeScript modules in isolation.",
    ),
    artifact(
        "check_library_route.mjs",
        "evaluator-code",
        "Independent exact route boundary checker.",
    ),
    artifact(
        "check_library_webmcp.mjs",
        "evaluator-code",
        "Independent WebMCP schema/action/state contract checker.",
    ),
    artifact(
        "check_library_static.py",
        "evaluator-code",
        "Independent frozen-file, integration and disclosure checker.",
    ),
    artifact(
        "write_final_library_audit.py",
        "report-code",
        "Deterministic final-audit report constructor.",
    ),
    artifact(
        "write_publication_manifest.py",
        "manifest-code",
        "Deterministic publication-manifest constructor.",
    ),
]

final_report = json.loads((ROOT / "final-library-audit.json").read_text(encoding="utf-8"))
expected_checks = {
    "reproduction": "pass",
    "specification_compliance": "pass",
    "source_verification": "pass",
    "implementation_alignment": "pass",
}
actual_checks = {item["id"]: item["status"] for item in final_report["checks"]}
if final_report["overall_status"] != "pass_scoped" or actual_checks != expected_checks:
    raise RuntimeError(
        f"final report does not have the expected scoped verdict: "
        f"{final_report['overall_status']=}, {actual_checks=}"
    )

freeze_path = PROJECT / "evidence/mathgloss/library-integration-freeze.json"
freeze = json.loads(freeze_path.read_text(encoding="utf-8"))
freeze_files = freeze.get("file_sha256", {})
if len(freeze_files) != 24:
    raise RuntimeError("integration freeze does not contain exactly 24 files")
for path, expected_sha256 in freeze_files.items():
    target = PROJECT / path
    if sha256(target) != expected_sha256:
        raise RuntimeError(f"frozen target changed: {path}")

manifest = {
    "schema_version": "audit-publication-manifest-v1",
    "subject": "MathGloss concept and resource library independent audit",
    "auditor": "/root/sol_symmetry_audit",
    "overall_status": final_report["overall_status"],
    "checks": expected_checks,
    "final_report": {
        "path": "final-library-audit.json",
        "bytes": (ROOT / "final-library-audit.json").stat().st_size,
        "sha256": sha256(ROOT / "final-library-audit.json"),
    },
    "frozen_target": {
        "path": "project/evidence/mathgloss/library-integration-freeze.json",
        "sha256": sha256(freeze_path),
        "files_verified": len(freeze_files),
        "all_file_hashes_match": True,
    },
    "files": publication_files,
    "retained_failures": [
        "02-navigation-check.json",
        "04-route-check.json",
        "05-route-check-attempt02.json",
        "06-route-check-attempt03.json",
        "07-route-check-attempt04.json",
        "12-static-integration-check.json",
        "13-static-integration-check-attempt02.json",
        "14-static-integration-check-attempt03.json",
        "15-static-integration-check-attempt04.json",
    ],
    "provisional_oracle_adjudication": "final-library-audit.json#/prospective_case_adjudication",
    "excluded": [
        {
            "path": "portable-copy/",
            "reason": "Temporary exact copies of project/importer code and pinned input used for isolated execution; hashes and the evaluating scripts/logs are retained.",
        },
        {
            "path": "portable-reproduction/",
            "reason": "Generated full candidate index and ledger copies are large duplicates; exact output hashes are retained in 09-portable-reproduction.json.",
        },
        {
            "path": "19-write-publication-manifest.json",
            "reason": "The command log is created after this manifest and cannot be self-listed without circularity.",
        },
    ],
}

(ROOT / "publication-manifest.json").write_text(
    json.dumps(manifest, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
    encoding="utf-8",
    newline="\n",
)
print(
    json.dumps(
        {
            "status": "pass",
            "publication_files": len(publication_files),
            "frozen_files_verified": len(freeze_files),
            "final_report_sha256": manifest["final_report"]["sha256"],
            "publication_manifest_sha256": sha256(ROOT / "publication-manifest.json"),
        },
        sort_keys=True,
    )
)
