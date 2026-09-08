from __future__ import annotations

import hashlib
import json
from pathlib import Path


ROOT = Path(r"D:/CodexWorkspaces/mathematics-atlas")
PROJECT = ROOT / "project"
IMPORT = ROOT / "backbone-import-work"
AUDIT = ROOT / "library-audit-work"
FREEZE = PROJECT / "evidence/mathgloss/library-integration-freeze.json"
OUT = AUDIT / "static-integration-check.json"
EXPECTED_FREEZE_SHA = "68bd8c6f8ff2dfaa1c1b26b1d4c030025ae1a6d84004767c8b537939f09ef316"


def sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def item(path: Path) -> dict[str, object]:
    data = path.read_bytes()
    return {"path": str(path), "bytes": len(data), "sha256": sha(data)}


freeze_raw = FREEZE.read_bytes()
assert sha(freeze_raw) == EXPECTED_FREEZE_SHA
freeze = json.loads(freeze_raw.decode("utf-8", errors="strict"))
manifest_results = []
for relative, expected in freeze["file_sha256"].items():
    path = PROJECT / relative
    actual = sha(path.read_bytes())
    assert actual == expected, (relative, expected, actual)
    manifest_results.append({"path": relative, "sha256": actual})

exact_pairs = [
    (
        PROJECT / "data/mathgloss/candidate-index.json",
        IMPORT / "outputs/full-run-final-01/candidate-index.json",
    ),
    (
        PROJECT / "data/mathgloss/summary.json",
        IMPORT / "outputs/full-run-final-01/summary.json",
    ),
    (
        PROJECT / "data/mathgloss/MATHGLOSS-LICENSE",
        IMPORT / "outputs/full-run-final-01/MATHGLOSS-LICENSE",
    ),
    (
        PROJECT / "data/mathgloss/source/database.csv",
        ROOT / "backbone-reuse-work/raw/mathgloss/data/database.csv",
    ),
    (
        PROJECT / "evidence/mathgloss/import-ledger.jsonl",
        IMPORT / "outputs/full-run-final-01/import-ledger.jsonl",
    ),
    (
        PROJECT / "src/mathgloss_import/core.py",
        IMPORT / "implementation/src/mathgloss_import/core.py",
    ),
    (
        PROJECT / "src/mathgloss_import/__init__.py",
        IMPORT / "implementation/src/mathgloss_import/__init__.py",
    ),
]
exact_copy_results = []
for integrated, audited in exact_pairs:
    integrated_bytes = integrated.read_bytes()
    audited_bytes = audited.read_bytes()
    assert integrated_bytes == audited_bytes, (integrated, audited)
    exact_copy_results.append(
        {
            "integrated": str(integrated.relative_to(ROOT)).replace("\\", "/"),
            "audited_basis": str(audited.relative_to(ROOT)).replace("\\", "/"),
            "bytes": len(integrated_bytes),
            "sha256": sha(integrated_bytes),
        }
    )

assert sha((PROJECT / "evidence/mathgloss/independent/final-importer-audit.json").read_bytes()) == freeze["importer_audit_sha256"]

expected_bundle = {
    "MATHGLOSS-LICENSE": "5dc6b930900926814fc7bb9ff45dfcceae3aa33780eb010c83e6df58493594e7",
    "candidate-index.json": "282ed1fd858595b782c856fbd2c96964a0b6ff3850fedf21105ca9bbb7edb4da",
    "import-ledger.jsonl": "14d8e9cc972a83ac4267d4b168d9510f74c65abbae509e7149012ba653c4ad61",
    "summary.json": "0102f6fca4237d80d3e4e167c476f118d5cfaff41b5b325882bc784eecfa6e58",
}
portable_results = []
for name, expected in expected_bundle.items():
    reproduced = (AUDIT / "portable-reproduction" / name).read_bytes()
    audited = (IMPORT / "outputs/full-run-final-01" / name).read_bytes()
    assert sha(reproduced) == expected
    assert reproduced == audited
    portable_results.append({"name": name, "bytes": len(reproduced), "sha256": expected})
portable_log = json.loads((AUDIT / "09-portable-reproduction.json").read_text(encoding="utf-8"))
assert portable_log["exit_code"] == 0

snapshot_path = PROJECT / "evidence/research-search/audited-page-before-library.tsx.snapshot"
page_path = PROJECT / "app/page.tsx"
snapshot = snapshot_path.read_text(encoding="utf-8")
page = page_path.read_text(encoding="utf-8")
insertion = """            <Link
              href="/library"
              className="mt-3 inline-flex items-center gap-1 text-sm text-blue-700 underline underline-offset-4"
            >
              Browse concept resources <ArrowRight size={14} />
            </Link>
"""
assert page.count(insertion) == 1
assert page.replace(insertion, "", 1) == snapshot

component = (PROJECT / "components/concept-library.tsx").read_text(encoding="utf-8")
docs = (PROJECT / "docs/concept-library.md").read_text(encoding="utf-8")
docs_flat = " ".join(docs.split())
route = (PROJECT / "app/api/concept-library/route.ts").read_text(encoding="utf-8")
for phrase in [
    "These mappings come from",
    "have not been individually verified here",
    "a missing search result does not mean an idea is undiscovered",
    "Mapping proposed by MathGloss · unreviewed",
    "Source record ↗",
    "the recorded source revision",
]:
    assert phrase in component, phrase
for phrase in [
    "4,814 concept records",
    "7,217 links",
    "Unicode NFKC normalization",
    "Pages contain at most 20",
    "No query is sent to an",
    "does not establish their individual reuse terms",
    "does not copy or certify the linked pages",
    "proves identity",
    "not a complete map of mathematics",
]:
    assert phrase in docs_flat, phrase
assert "href={record.identity_candidate.uri}" in component
assert "href={link.url}" in component
assert "href={conceptSourceUrl(record)}" in component
assert component.count('rel="noopener noreferrer"') >= 3
assert "/api/concept-library?${params.toString()}" in component
assert "fetch(" not in route
assert all(token not in component for token in ["localStorage", "sessionStorage", "document.cookie", "sendBeacon"])

candidate_raw = (PROJECT / "data/mathgloss/candidate-index.json").read_bytes()
candidate_text = candidate_raw.decode("utf-8", errors="strict")
assert "\ufffd" not in candidate_text
candidate = json.loads(candidate_text)
record = next(r for r in candidate["records"] if r["identity_candidate"]["qid"] == "Q1028209")
assert record["label_as_recorded"] == "Deutsch\u2013Jozsa algorithm"
assert ord(record["label_as_recorded"][7]) == 0x2013
assert candidate["catalog_status"] == "unreviewed_external_link_catalogue"
assert all(
    r["mapping_status"] == "unreviewed"
    and r["identity_candidate"]["status"] == "unreviewed"
    and r["asserted_by"] == "MathGloss"
    for r in candidate["records"]
)

log_expectations = {
    "concept-library-navigation-attempt-01.command.json": 0,
    "concept-library-typecheck.command.json": 0,
    "concept-library-lint-attempt-01.command.json": 1,
    "concept-library-lint-attempt-02.command.json": 0,
    "concept-library-build.command.json": 0,
    "concept-library-format.command.json": 0,
    "concept-library-navigation-format.command.json": 0,
}
log_results = []
for name, expected_exit in log_expectations.items():
    path = PROJECT / "logs" / name
    value = json.loads(path.read_text(encoding="utf-8-sig"))
    assert value["exit_code"] == expected_exit, name
    console = PROJECT / value["console_log"]
    assert console.is_file(), console
    log_results.append(
        {
            "name": name,
            "exit_code": value["exit_code"],
            "command": value["command_argv"],
            "command_sha256": sha(path.read_bytes()),
            "console_sha256": sha(console.read_bytes()),
        }
    )
lint_failure = (PROJECT / "logs/concept-library-lint-attempt-01.console.log").read_text(encoding="utf-8-sig")
assert "evidence/research-search/independent" in lint_failure
assert "app/api/concept-library/route.ts" in lint_failure
assert '"exclude": ["node_modules", "evidence/**"]' in (PROJECT / "tsconfig.json").read_text(encoding="utf-8")
assert '"evidence/**"' in (PROJECT / ".oxlintrc.json").read_text(encoding="utf-8")

report = {
    "schema_version": "concept-library-independent-static-integration-check-v1",
    "status": "pass",
    "freeze_sha256": EXPECTED_FREEZE_SHA,
    "manifest_files_verified": len(manifest_results),
    "manifest_results": manifest_results,
    "exact_audited_copy_results": exact_copy_results,
    "portable_reproduction": portable_results,
    "prior_page_delta": {
        "snapshot_sha256": sha(snapshot_path.read_bytes()),
        "current_page_sha256": sha(page_path.read_bytes()),
        "only_change": "one /library Browse concept resources Link block",
        "reverse_delta_matches_snapshot_text_exactly": True,
    },
    "data": {
        "records": len(candidate["records"]),
        "links": sum(len(r["links"]) for r in candidate["records"]),
        "catalog_status": candidate["catalog_status"],
        "unicode_q1028209": record["label_as_recorded"],
        "unicode_codepoints": [f"U+{ord(c):04X}" for c in record["label_as_recorded"]],
        "replacement_character_present": "\ufffd" in candidate_text,
    },
    "ui_disclosure_and_links": {
        "mathgloss_source_visible": True,
        "unreviewed_visible_per_card": True,
        "search_miss_caveat_visible": True,
        "pinned_revision_visible": True,
        "qid_resource_and_source_record_links_rendered": True,
        "outbound_rel_noopener_noreferrer": True,
    },
    "root_command_history": log_results,
    "archive_exclusion_assessment": (
        "The retained first lint failure mixed historical evidence harnesses with product code and occurred before the data files were present. "
        "The frozen config excludes evidence/** only; app/components/lib/scripts remain included. This is a scoped archive boundary, not evidence that those historical harnesses pass current type-aware lint."
    ),
    "privacy_limit": (
        "The search stays inside the same-origin static catalog and the API is no-store. Because it is a GET API, query text remains in the same-origin request URL and may be present in ordinary server access logs."
    ),
    "limitations": [
        "This checks exact integration, presentation boundaries and retained build logs; it does not inspect outbound page content or rights.",
        "No semantic identity, equivalence, resource quality, learner level, theorem support, impact, novelty or whole-map claim is certified.",
    ],
}
OUT.write_text(json.dumps(report, ensure_ascii=True, indent=2, sort_keys=True) + "\n", encoding="utf-8", newline="\n")
print(json.dumps({"status": "pass", "output": str(OUT), "sha256": sha(OUT.read_bytes())}, sort_keys=True))
