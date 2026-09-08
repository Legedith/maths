"""Assemble a scoped library bundle for an independent final claim review."""
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TARGET = ROOT / ".codex/evidence/runs/concept-library-v1/bundle.json"
bundle = json.loads(TARGET.read_text(encoding="utf-8-sig"))
assert all(c["status"] == "pending" for c in bundle["checks"]), "Do not overwrite an approved bundle."
paths: dict[str, tuple[str, str]] = {}


def add(path: str, kind: str | None = None) -> None:
    item = ROOT / path
    assert item.is_file(), path
    if kind is None:
        kind = "code" if item.suffix in {".py", ".ts", ".tsx", ".mjs", ".css"} else "log" if item.suffix in {".log", ".txt", ".jsonl"} or "/logs/" in path or "canonical-logs/" in path else "report"
    producer = "/root/sol_symmetry_audit" if "/library-independent/" in path or "/independent/" in path or "backbone-audit-work/" in path else "retained-import-worker" if "backbone-import-work/" in path else "root-integration"
    paths[path] = (kind, producer)


add("docs/concept-library-contract.md", "spec")
freeze = json.loads((ROOT / "evidence/mathgloss/library-integration-freeze.json").read_bytes())
file_hashes = freeze.get("file_sha256")
assert file_hashes, freeze.keys()
for path, digest in file_hashes.items():
    assert hashlib.sha256((ROOT / path).read_bytes()).hexdigest() == digest, path
    add(path)
for folder in ["evidence/mathgloss", "data/mathgloss"]:
    for item in sorted((ROOT / folder).rglob("*")):
        if item.is_file() and "__pycache__" not in item.parts:
            add(item.relative_to(ROOT).as_posix())
add("docs/concept-library-contract.md", "spec")
add("evidence/mathgloss/retained/backbone-import-work/docs/import-contract.md", "spec")
add("data/mathgloss/source/database.csv", "source")
add("data/mathgloss/MATHGLOSS-LICENSE", "source")
add("evidence/mathgloss/retained/backbone-audit-work/source-audit.json", "source")
for path in ["docs/concept-library-verification.md", "scripts/build_library_evidence.py"]:
    add(path)
for prefix in ["concept-library-", "mathgloss-", "library-integrated-python-tests"]:
    for item in sorted((ROOT / "logs").glob(prefix + "*")):
        if item.is_file():
            add(item.relative_to(ROOT).as_posix(), "log")

artifacts = []
ids = {}
for index, (path, (kind, producer)) in enumerate(paths.items(), 1):
    key = f"A{index:03d}"
    ids[path] = key
    artifacts.append({"id": key, "kind": kind, "path": path, "sha256": hashlib.sha256((ROOT / path).read_bytes()).hexdigest(), "producer": producer})


def support(path: str, locator: str, expected=None):
    value = {"artifact_id": ids[path], "locator": locator}
    if expected is not None:
        value["expected"] = expected
    return value


summary = "data/mathgloss/summary.json"
audit = "evidence/mathgloss/library-independent/final-library-audit.json"
importer = "evidence/mathgloss/independent/final-importer-audit.json"
source = "evidence/mathgloss/retained/backbone-audit-work/source-audit.json"
claims = [
    {"id": "C001", "type": "numerical", "statement": "The pinned metadata import contains 4,814 concept records and 7,217 retained resource links. Independent import and integration reviews verify source fidelity; the proposed identities and mappings remain unreviewed.", "status": "supported", "supports": [support(summary, "json:/counts/candidate_records", 4814), support(summary, "json:/counts/retained_link_pairs", 7217), support(summary, "json:/catalog_status", "unreviewed_external_link_catalogue"), support(importer, "json:/overall_status", "pass_scoped"), support(audit, "json:/overall_status", "pass_scoped")]},
    {"id": "C002", "type": "citation", "statement": "The imported source is MathGloss data/database.csv at revision b8f659605486f80f2816515f525af2c395c711fa. Its exact repository license notice is retained; the import copies metadata and links, and does not establish rights in outbound content.", "status": "supported", "supports": [support(source, "json:/mathgloss_snapshot/head", "b8f659605486f80f2816515f525af2c395c711fa"), support("data/mathgloss/MATHGLOSS-LICENSE", "contains:Permission is hereby granted"), support(summary, "json:/source/csv_path", "data/database.csv"), support(importer, "json:/checks/2/notes")]},
    {"id": "C003", "type": "methodological", "statement": "The library uses documented NFKC all-fragment lexical matching, resource filtering and bounded deterministic pagination. Independent navigation covers all 241 catalog pages without record loss. Three differences from the auditor's provisional matching expectations are retained and adjudicated against the frozen documented policy.", "status": "supported", "supports": [support("lib/concept-library.ts", "contains:normalize"), support("docs/concept-library.md", "contains:then requires every query fragment to occur"), support(audit, "json:/verified_counts/all_catalog_pages", 241), support(audit, "json:/verified_counts/all_catalog_unique_records", 4814), support(audit, "json:/prospective_case_adjudication/status", "transparent_policy_variance_no_contract_failure")]},
    {"id": "C004", "type": "numerical", "statement": "The independent route audit covers five valid and fifteen invalid requests with bounded no-store responses. Library search makes no external search request; query text remains in the same-origin GET URL and may appear in access logs.", "status": "supported", "supports": [support(audit, "json:/verified_counts/valid_route_cases", 5), support(audit, "json:/verified_counts/invalid_route_cases", 15), support(audit, "json:/privacy_and_state/cache_control", "no-store on success and error"), support(audit, "json:/privacy_and_state/external_search_or_resource_fetch", False), support(audit, "json:/privacy_and_state/same_origin_get_limit")]},
    {"id": "C005", "type": "methodological", "statement": "The library form and WebMCP action share the same search state transition. Focused root-observed browser results were independently checked against frozen code; this does not represent a second visual-browser run or broad visual QA.", "status": "supported", "supports": [support("components/concept-library.tsx", "contains:runSearch"), support("evidence/mathgloss/library-webmcp-observations.json", "json:/tool", "search_learning_resources"), support(audit, "json:/limitations/1")]},
    {"id": "C006", "type": "conclusion", "statement": "This reuse expands searchable resource coverage with source provenance. The finite fidelity and navigation checks do not establish concept equivalence, theorem truth, learner suitability, practical impact, novelty or completion of the mathematics map.", "status": "supported", "supports": [{"claim_id": "C001"}, {"claim_id": "C002"}, {"claim_id": "C003"}, {"claim_id": "C004"}, {"claim_id": "C005"}]},
]
report = json.loads((ROOT / audit).read_bytes())
typed_paths = {
    "reproduction": "logs/mathgloss-portable-reproduction-verified.console.log",
    "specification_compliance": "docs/concept-library-contract.md",
    "source_verification": source,
    "implementation_alignment": "lib/concept-library.ts",
}
bundle.update(task_spec_artifact_id=ids["docs/concept-library-contract.md"], evaluator_command="uv run --frozen python scripts/import_mathgloss.py --source-csv data/mathgloss/source/database.csv --source-license data/mathgloss/MATHGLOSS-LICENSE --output-dir work/mathgloss-reproduction; node scripts/check-concept-library.ts", artifacts=artifacts, claims=claims)
bundle["checks"] = [{"id": check["id"], "status": "pending", "auditor": report["auditor"]["identity"], "evidence": [ids[audit], ids[importer], ids[typed_paths[check["id"]]]], "note": "Implementation review passed; independent final claim review is pending. " + check["notes"]} for check in report["checks"]]
bundle["limitations"] = report["limitations"] + ["Frozen implementation documentation retains its historical pending-review wording; docs/concept-library-verification.md records the additive review result.", "The independently reviewed checker and historical foundation have separate bundles; this bundle does not recertify them."]
TARGET.write_text(json.dumps(bundle, indent=2) + "\n", encoding="utf-8", newline="\n")
print(json.dumps({"artifact_count": len(artifacts), "claim_count": len(claims), "sha256": hashlib.sha256(TARGET.read_bytes()).hexdigest(), "status": "pending_independent_claim_review"}))
