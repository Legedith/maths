from __future__ import annotations

import hashlib
import json
from pathlib import Path


ROOT = Path(r"D:/CodexWorkspaces/mathematics-atlas")
PROJECT = ROOT / "project"
AUDIT = ROOT / "library-audit-work"
OUT = AUDIT / "final-library-audit.json"
FREEZE_SHA = "68bd8c6f8ff2dfaa1c1b26b1d4c030025ae1a6d84004767c8b537939f09ef316"


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def artifact(path: Path, kind: str, note: str) -> dict[str, object]:
    data = path.read_bytes()
    return {
        "path": str(path.relative_to(ROOT)).replace("\\", "/"),
        "kind": kind,
        "bytes": len(data),
        "sha256": hashlib.sha256(data).hexdigest(),
        "note": note,
    }


freeze_path = PROJECT / "evidence/mathgloss/library-integration-freeze.json"
assert sha(freeze_path) == FREEZE_SHA
freeze = json.loads(freeze_path.read_text(encoding="utf-8"))
for relative, expected in freeze["file_sha256"].items():
    assert sha(PROJECT / relative) == expected, relative

navigation = json.loads((AUDIT / "navigation-check.json").read_text(encoding="utf-8"))
route = json.loads((AUDIT / "route-check.json").read_text(encoding="utf-8"))
webmcp = json.loads((AUDIT / "webmcp-contract-check.json").read_text(encoding="utf-8"))
static = json.loads((AUDIT / "static-integration-check.json").read_text(encoding="utf-8"))
for name, report in [
    ("navigation", navigation),
    ("route", route),
    ("webmcp", webmcp),
    ("static", static),
]:
    assert report["status"] == "pass", name

node_log = json.loads((AUDIT / "11-author-node-check-rerun.json").read_text(encoding="utf-8"))
portable_log = json.loads((AUDIT / "09-portable-reproduction.json").read_text(encoding="utf-8"))
assert node_log["exit_code"] == 0
assert portable_log["exit_code"] == 0
assert navigation["source_record_urls_checked"] == 4814
assert navigation["catalog_records"] == 4814
assert navigation["catalog_links"] == 7217
assert route["frozen_files_checked_before_and_after"] == 24
assert route["state_mutation_detected"] is False

policy_differences = navigation["precommitted_policy_differences"]
assert [item["id"] for item in policy_differences] == [
    "multi-hit-label-fragment",
    "filtered-bct",
    "abelian-group-small-pages",
]

artifacts = [
    artifact(PROJECT / "docs/concept-library-contract.md", "spec", "Prospective integration contract."),
    artifact(freeze_path, "manifest", "Root-frozen 24-file integration target."),
    artifact(AUDIT / "independent-cases.json", "evaluator-contract", "Cases selected before implementation inspection."),
    artifact(AUDIT / "01-freeze-independent-cases.json", "evaluator-log", "Raw case-freeze command record."),
    artifact(AUDIT / "navigation-check.json", "test", "Independent documented-policy search/filter/pagination check."),
    artifact(AUDIT / "17-navigation-check-final.json", "test-log", "Raw final navigation command record."),
    artifact(AUDIT / "route-check.json", "test", "Independent exact route boundary check."),
    artifact(AUDIT / "08-route-check-attempt05.json", "test-log", "Raw passing route command after retained loader setup failures."),
    artifact(AUDIT / "static-integration-check.json", "evaluator", "Exact integration, page delta and retained-log check."),
    artifact(AUDIT / "16-static-integration-check-pass.json", "evaluator-log", "Raw passing static evaluator command."),
    artifact(AUDIT / "webmcp-contract-check.json", "test", "Independent tool schema/action/code and observation alignment check."),
    artifact(AUDIT / "10-webmcp-contract-check.json", "test-log", "Raw WebMCP contract test command."),
    artifact(AUDIT / "09-portable-reproduction.json", "reproduction-log", "Exact copied explicit-input adapter reproduction."),
    artifact(AUDIT / "11-author-node-check-rerun.json", "test-log", "Independent rerun of frozen project navigation script."),
    artifact(PROJECT / "evidence/mathgloss/library-webmcp-observations.json", "observation", "Root-observed focused browser/tool state; values independently source-checked."),
    artifact(PROJECT / "data/mathgloss/candidate-index.json", "data", "Integrated byte-exact independently audited candidate index."),
    artifact(PROJECT / "data/mathgloss/source/database.csv", "source", "Pinned source CSV retained for portable reproduction."),
    artifact(PROJECT / "components/concept-library.tsx", "code", "Visible library state, disclosure and source/resource links."),
    artifact(PROJECT / "lib/concept-library.ts", "code", "Validated lexical search and pagination core."),
    artifact(PROJECT / "app/api/concept-library/route.ts", "code", "GET-only, no-store bounded API route."),
]

report = {
    "schema_version": "chain-of-evidence-independent-verification-v1",
    "auditor": {
        "identity": "/root/sol_symmetry_audit",
        "role": "independent Sol Max verifier",
        "independent_from_integration_author": True,
    },
    "subject": "MathGloss concept and resource library integration",
    "overall_status": "pass_scoped",
    "frozen_target": {
        "integration_freeze_sha256": FREEZE_SHA,
        "files": len(freeze["file_sha256"]),
        "contract_sha256": "a55985517bafb4909af576d2245d7898c98f101482e36d66b1841b8168879f3d",
        "candidate_index_sha256": "282ed1fd858595b782c856fbd2c96964a0b6ff3850fedf21105ca9bbb7edb4da",
        "importer_audit_sha256": "260a9424c45d5c2725d2bae7630c6bef9f8ac8b0de0f39224814d179559b3b46",
    },
    "checks": [
        {
            "id": "reproduction",
            "status": "pass",
            "notes": (
                "An exact copied portable adapter and the unchanged audited importer reproduced the license, candidate index, complete ledger and summary at all four audited hashes. The frozen Node navigation check reran successfully, and independent route/navigation/WebMCP harnesses exited successfully."
            ),
            "evidence_paths": [
                "library-audit-work/09-portable-reproduction.json",
                "library-audit-work/11-author-node-check-rerun.json",
                "library-audit-work/17-navigation-check-final.json",
                "library-audit-work/08-route-check-attempt05.json",
                "library-audit-work/10-webmcp-contract-check.json",
            ],
        },
        {
            "id": "specification_compliance",
            "status": "pass",
            "notes": (
                "The public library documents and implements NFKC/lowercase/punctuation-separated all-fragment matching, exact-label/prefix ranking with source-order ties, source filtering, a fixed 20-record page bound, totals and no-drop navigation. UI cards show exact recorded names/links, MathGloss attribution, unreviewed status and pinned record links; the search-miss caveat is visible. Invalid route/tool inputs are bounded. Form and WebMCP use the same runSearch state transition."
            ),
            "evidence_paths": [
                "project/docs/concept-library-contract.md",
                "project/docs/concept-library.md",
                "library-audit-work/navigation-check.json",
                "library-audit-work/route-check.json",
                "library-audit-work/webmcp-contract-check.json",
                "library-audit-work/static-integration-check.json",
            ],
        },
        {
            "id": "source_verification",
            "status": "pass",
            "notes": (
                "Integrated CSV, candidate index, summary, ledger, license and importer modules are byte-identical to the independently audited artifacts. Counts are 4,814 records and 7,217 retained links. Every integrated record traversed pagination without loss, all seven source totals matched the oracle, all 4,814 generated source-record URLs matched physical locators, and Q1028209 retains U+2013 with no U+FFFD."
            ),
            "evidence_paths": [
                "library-audit-work/static-integration-check.json",
                "library-audit-work/navigation-check.json",
                "project/evidence/mathgloss/independent/final-importer-audit.json",
                "project/data/mathgloss/candidate-index.json",
            ],
        },
        {
            "id": "implementation_alignment",
            "status": "pass",
            "notes": (
                "All 24 frozen files match the integration manifest. Exact route execution covered valid, Unicode, filtered, miss and beyond-last pages plus 15 malformed/ambiguous/oversized requests; responses were bounded and no-store, and frozen files stayed unchanged. The original page is text-exact after removing the single new /library link block. Retained typecheck/lint/build logs pass after the documented evidence-archive exclusion; product app/components/lib/scripts remain checked."
            ),
            "evidence_paths": [
                "project/evidence/mathgloss/library-integration-freeze.json",
                "library-audit-work/route-check.json",
                "library-audit-work/static-integration-check.json",
                "project/evidence/research-search/audited-page-before-library.tsx.snapshot",
            ],
        },
    ],
    "verified_counts": {
        "frozen_files": 24,
        "catalog_records": 4814,
        "catalog_links": 7217,
        "all_catalog_pages": 241,
        "all_catalog_unique_records": 4814,
        "nlab_records": 4505,
        "nlab_pages": 226,
        "source_record_urls_checked": 4814,
        "resource_totals": navigation["resource_totals"],
        "valid_route_cases": len(route["valid_cases"]),
        "invalid_route_cases": len(route["invalid_cases"]),
        "maximum_observed_error_bytes": route["response_boundary"]["maximum_observed_error_bytes"],
    },
    "prospective_case_adjudication": {
        "status": "transparent_policy_variance_no_contract_failure",
        "case_manifest_sha256": "108c67ef95d33892a805be1a6a55a9349988b372a2c783a3703f7548548f3ea5",
        "explanation": (
            "The query/filter inputs were frozen before implementation inspection. Their provisional oracle used contiguous Unicode-casefolded substring matching across all resource aliases, while the prospective product contract only required a documented lexical policy. The already-frozen product docs use NFKC lowercase all-fragment matching and restrict alias matching to the selected source. Three stored expectations therefore differ: abelian group returns 13 rather than 12 because 'Abelian 2-group' satisfies both fragments; BCT category theory returns 3 rather than 4 because an alias from another resource is excluded; the abelian pagination case repeats the first difference. These variances are retained rather than erased. Independent reimplementation of the frozen documented policy matched every target result and order."
        ),
        "differences": policy_differences,
    },
    "privacy_and_state": {
        "api_export": "GET only",
        "cache_control": "no-store on success and error",
        "external_search_or_resource_fetch": False,
        "persistent_browser_or_server_state_found": False,
        "same_origin_get_limit": (
            "Query text is carried in the same-origin request URL and may be present in ordinary same-origin access logs. No stronger secrecy claim is certified."
        ),
        "webmcp_annotation": (
            "readOnlyHint false is consistent with the intentional visible client-state update; untrustedContentHint true is appropriate for imported labels and links. The API/data remain read-only."
        ),
    },
    "limitations": [
        "This certifies exact integration, deterministic lexical navigation, bounded API behavior and scoped tool/state alignment for one pinned MathGloss snapshot. It does not certify concept identity, equivalence, resource quality, availability, learner level, theorem support, linked content, rights in linked prose, impact, novelty or completeness as a map of mathematics.",
        "The focused browser/WebMCP observations were produced by the root integrator. This reviewer independently verified their hash, source values and frozen-code alignment, but did not perform a second visual browser run or broad visual QA.",
        "The retained build/typecheck/lint command records are root-produced. This reviewer independently ran the exact frozen navigation script plus stronger pure search, route, portable-import and WebMCP contract harnesses.",
        "The evidence/** typecheck/lint exclusion is an archive boundary. It does not certify historical harnesses under current project lint rules; their own retained execution records support claims that cite them.",
        "GET no-store prevents response caching but does not remove query text from the same-origin request URL or possible access logs.",
    ],
    "artifacts": artifacts,
}

OUT.write_text(json.dumps(report, ensure_ascii=True, indent=2, sort_keys=True) + "\n", encoding="utf-8", newline="\n")
print(json.dumps({"status": report["overall_status"], "path": str(OUT), "sha256": sha(OUT)}, sort_keys=True))
