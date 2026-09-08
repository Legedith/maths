"""Assemble the scoped checker evidence; semantic promotion needs its auditor."""
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TARGET = ROOT / ".codex/evidence/runs/assumption-checks-v1/bundle.json"
BASE = "evidence/assumption-checks/independent/"
bundle = json.loads(TARGET.read_text(encoding="utf-8-sig"))
paths: dict[str, tuple[str, str]] = {}

def add(path: str, kind: str | None = None, producer: str | None = None) -> None:
    item = ROOT / path
    assert item.is_file(), path
    if kind is None:
        kind = "code" if item.suffix in {".py", ".ts", ".tsx"} else "log" if item.suffix in {".log", ".txt", ".jsonl"} else "report"
    paths[path] = (kind, producer or ("independent-verifier-sol-atlas-audit" if path.startswith(BASE) else "root-integration"))

specs = ["docs/assumption-check-contract.md", "docs/assumption-check-interface.md", "docs/assumption-check-clarifications.md", "docs/assumption-check-clarification-2.md", "fixtures/retrieval-study-v1.json"]
for path in specs: add(path, "spec", "root-frozen-specification")
for item in sorted((ROOT / BASE).rglob("*")):
    if item.is_file() and "__pycache__" not in item.parts:
        add(item.relative_to(ROOT).as_posix())
for relative in ["source-locators.json", "publication/source-matrix.json"]:
    add(BASE + relative, "source", "independent-primary-source-reading")
freeze = json.loads((ROOT / "evidence/assumption-checks/worker/root-patch-freeze-v1.0.2.json").read_text(encoding="utf-8"))
for path, digest in freeze["file_sha256"].items():
    assert hashlib.sha256((ROOT/path).read_bytes()).hexdigest() == digest
    add(path, "test" if path.startswith("tests/") else None)
publication = json.loads((ROOT/BASE/"publication/publication-manifest.json").read_text(encoding="utf-8"))
for record in publication["groups"]["project_evidence_references_in_place"]:
    # Remap the recorded historical project prefix for portable assembly.
    relative = record["source_path"].replace("\\", "/").split("/project/", 1)[1]
    assert hashlib.sha256((ROOT/relative).read_bytes()).hexdigest() == record["sha256"]
    add(relative, "spec" if relative in specs else None)
for folder in ["evidence/assumption-checks/root-reproduction", "evidence/assumption-checks/teaching", "fixtures/assumption-checks/teaching"]:
    for item in sorted((ROOT/folder).rglob("*")):
        if item.is_file(): add(item.relative_to(ROOT).as_posix())
for path in ["docs/assumption-check-progress.md", "docs/assumption-teaching-examples.md", "evidence/assumption-checks/independent-transfer.json", "logs/assumption-public-reproduction.command.json", "logs/assumption-public-reproduction.console.log", "logs/library-integrated-python-tests.command.json", "logs/library-integrated-python-tests.console.log", "scripts/build_assumption_evidence.py"]:
    add(path)

artifacts = []
ids = {}
for index, (path, (kind, producer)) in enumerate(paths.items(), 1):
    key = f"A{index:03d}"
    ids[path] = key
    artifacts.append({"id": key, "kind": kind, "path": path, "sha256": hashlib.sha256((ROOT/path).read_bytes()).hexdigest(), "producer": producer})

def support(path: str, locator: str, expected=None):
    result = {"artifact_id": ids[path], "locator": locator}
    if expected is not None: result["expected"] = expected
    return result

final = BASE + "final-audit.json"
summary = "evidence/assumption-checks/root-reproduction/comparison-summary.json"
matrix = BASE + "publication/source-matrix.json"
claims = [
    {"id": "C001", "type": "methodological", "statement": "The checker evaluates explicitly supplied structured claims and assumptions over exact finite weighted graph quantities. It records supplied provenance without fetching sources or interpreting natural language.", "status": "supported", "supports": [support("src/atlas_checks/api.py", "contains:def check_transfer"), support("docs/assumption-check-contract.md", "contains:Natural-language interpretation is outside this implementation"), support(final, "json:/limitations/1")]},
    {"id": "C002", "type": "citation", "statement": "The cited graph sources distinguish the row-walk and symmetric normalized Laplacians and distinguish stationarity from convergence; these distinctions govern the checker conventions.", "status": "supported", "supports": [support(matrix, "json:/foundation_sources/0/id", "rw-laplacian-name-and-formula"), support(matrix, "json:/foundation_sources/2/id", "symmetric-normalized-distinction"), support(matrix, "json:/foundation_sources/3/id", "stationary-is-not-convergence")]},
    {"id": "C003", "type": "numerical", "statement": "The final frozen checker and the portable integrated rerun match all 80 prospective structured oracle cases with zero failures; this is a finite diagnostic result.", "status": "supported", "supports": [support(summary, "json:/case_count", 80), support(summary, "json:/pass_count", 80), support(summary, "json:/failure_count", 0), support(final, "json:/assertions/portable_run_is_same_output_bytes", True)]},
    {"id": "C004", "type": "methodological", "statement": "Supplemental representation failures and evaluator mistakes remain retained separately from the prospective suite. The final output formatter was independently checked against a Decimal oracle without changing the process-wide integer conversion limit.", "status": "supported", "supports": [support("src/atlas_checks/model.py", "contains:def _integer_text"), support(BASE + "raw/v1.0.2-exact-output-attempt02/large-output-v1.0.2-independent-verification.json", "json:/all_checks_pass", True), support(final, "json:/historical_failures_and_invalid_attempts")]},
    {"id": "C005", "type": "numerical", "statement": "Two frozen source-only AI reviews covered 24 purposively retrieved results and agreed on 21. Source adjudication retained 12 supported, 9 refuted and 3 insufficient labels; these descriptive counts do not estimate population error rates.", "status": "supported", "supports": [support(final, "json:/retrieval_study/fixed_results", 24), support(final, "json:/retrieval_study/reviewer_agreement", 21), support(final, "json:/retrieval_study/adjudicated_labels_descriptive_only", {"supported": 12, "refuted": 9, "insufficient": 3}), support(BASE + "retrieval-review-adjudication-corrections.json", "json:/scope_limit")]},
    {"id": "C006", "type": "numerical", "statement": "The retrieval-derived check covers 6 evaluable theorem IDs, 2 syntax-mappable but abstaining IDs and 16 excluded IDs. Its 9 instance fixtures yield 7 no-counterexample results and 2 abstentions, adding zero source-refutation detections.", "status": "supported", "supports": [support(final, "json:/retrieval_study/structured_accounting", {"evaluable_theorem_ids": 6, "fixed_retrieval_rows": 24, "fully_ineligible_theorem_ids": 16, "structured_fixture_count": 9, "syntax_mappable_but_abstaining_theorem_ids": 2, "syntax_mappable_theorem_ids": 8}), support(final, "json:/retrieval_study/structured_fixture_verdicts", {"abstain": 2, "no_counterexample_in_instance": 7}), support(final, "json:/retrieval_study/incremental_source_refutation_detections", 0)]},
    {"id": "C007", "type": "numerical", "statement": "Three separately authored teaching records were independently checked for their retained version 1.0.1 numerical and assumption behavior; they are not held-out retrieval cases.", "status": "supported", "supports": [support(BASE + "raw/teaching-examples-v1.0.1-verification.json", "json:/record_count", 3), support(BASE + "raw/teaching-examples-v1.0.1-verification.json", "json:/all_expected_checks_pass", True), support("docs/assumption-teaching-examples.md", "contains:retained 1.0.1 runs")]},
    {"id": "C008", "type": "conclusion", "statement": "This phase establishes a scoped diagnostic implementation and exposes coverage limits. It does not demonstrate added source-refutation detection, researcher-time benefit, new mathematics or completion of the broader map; compare existing mathematics tools before extending the custom grammar.", "status": "supported", "supports": [{"claim_id": "C001"}, {"claim_id": "C003"}, {"claim_id": "C005"}, {"claim_id": "C006"}]},
]
bundle.update({"task_spec_artifact_id": ids[specs[0]], "evaluator_command": "uv run --frozen python evidence/assumption-checks/independent/publication/heldout-v1/run_public_suite.py --project-root . --output-dir work/assumption-reproduction", "artifacts": artifacts, "claims": claims})
audit = json.loads((ROOT/final).read_text(encoding="utf-8"))
bundle["checks"] = [{"id": check["id"], "status": "pending", "auditor": check["auditor"], "evidence": [ids[final]], "note": "Frozen implementation audit passed; pending independent review of this integrated claim bundle. " + check["note"]} for check in audit["checks"]]
bundle["limitations"] = audit["limitations"] + ["The separate concept-library integration is outside this checker bundle.", "Historical frozen README wording about pending review is superseded by the linked progress page and final audit, without changing the frozen bytes."]
TARGET.write_text(json.dumps(bundle, indent=2) + "\n", encoding="utf-8", newline="\n")
print(json.dumps({"artifacts": len(artifacts), "claims": len(claims), "status": "pending_integrated_claim_review", "sha256": hashlib.sha256(TARGET.read_bytes()).hexdigest()}))
