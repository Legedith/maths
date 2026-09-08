"""Record final artifacts and independent attestations; never invent a passing audit."""
from __future__ import annotations

from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RUN = ROOT / ".codex/evidence/runs/atlas-foundation"


def read(path: str):
    return json.loads((ROOT / path).read_text(encoding="utf-8-sig"))


def main() -> None:
    artifacts: list[dict] = []
    ids: dict[str, str] = {}

    def artifact(path: str, kind: str, producer: str = "root") -> str:
        if path in ids:
            return ids[path]
        resolved = (ROOT / path).resolve()
        if not resolved.is_relative_to(ROOT) or not resolved.is_file():
            raise ValueError(f"Missing or escaping evidence: {path}")
        identifier = f"A{len(artifacts) + 1:03d}"
        ids[path] = identifier
        artifacts.append({"id": identifier, "kind": kind, "path": path,
                          "sha256": hashlib.sha256(resolved.read_bytes()).hexdigest(),
                          "producer": producer})
        return identifier

    spec = artifact("docs/task-spec.md", "spec", "user-or-orchestrator")
    for path in ("docs/engine-contract.md", "docs/symmetry-contract.md", "docs/discovery-contract.md"):
        artifact(path, "spec", "root, frozen before the governed implementation")

    # Preserve every retained test record and source/audit note, including failures.
    for folder in ("evidence", "logs"):
        for path in sorted((ROOT / folder).rglob("*")):
            if not path.is_file() or "__pycache__" in path.parts or "primary-sources" in path.parts or "pytest-temp" in path.parts:
                continue
            relative = path.relative_to(ROOT).as_posix()
            kind = "log" if path.suffix in {".log", ".jsonl"} else "result"
            if path.suffix == ".md":
                kind = "report"
            if path.name == "prior-art-audit.md" or path.name == "theoremsearch-response.json":
                kind = "source"
            if path.suffix in {".py", ".ps1", ".ts"}:
                kind = "code"
            producer = ("sol_symmetry_audit" if relative.startswith("evidence/symmetry/independent/")
                        else "sol_atlas_audit" if relative.startswith("evidence/foundation/independent/")
                        else "sol_symmetry_audit" if relative.startswith("evidence/reuse/independent/")
                        else "retained original agent" if relative.startswith("evidence/exploration/")
                        else "worker or root; exact producer and command retained in artifact")
            artifact(relative, kind, producer)
    for folder in ("src", "lib", "app", "tests", "scripts", "components"):
        for path in sorted((ROOT / folder).rglob("*")):
            if path.is_file() and path.suffix in {".py", ".ts", ".tsx", ".css", ".ps1"} and "__pycache__" not in path.parts:
                if folder == "components" and "ui" in path.parts:
                    continue
                artifact(path.relative_to(ROOT).as_posix(), "test" if folder == "tests" else "code", "root integration and assigned implementation workers")
    for path in ("data/atlas.json", "fixtures/frozen.json", "fixtures/supplemental-six.json", "pyproject.toml", "uv.lock", "README.md", "README-engine.md", "README-symmetry.md", "docs/decision.md", "docs/reuse-decision.md", "docs/normalization-case.md"):
        artifact(path, "source" if path == "data/atlas.json" else "spec" if path.startswith("fixtures/") else "report")

    claims: list[dict] = []

    def claim(identifier: str, kind: str, statement: str, supports: list[dict]):
        claims.append({"id": identifier, "type": kind, "statement": statement, "status": "supported", "supports": supports})

    def support(path: str, pointer: str, expected):
        return {"artifact_id": ids[path], "locator": "json:" + pointer, "expected": expected}

    claim("C001", "numerical", "The curated region has 31 nodes, 40 directed relations and 7 sources; these are corpus counts, not coverage of mathematics.", [support("evidence/corpus/validation.json", "/counts/nodes", 31), support("evidence/corpus/validation.json", "/counts/edges", 40), support("evidence/corpus/validation.json", "/counts/sources", 7)])
    claim("C002", "numerical", "The baseline checks 772 records with zero failures: one selected edge on each of 771 connected labelled graphs on 2–5 vertices plus one named six-vertex cycle.", [support("evidence/baseline/summary.json", "/record_count", 772), support("evidence/baseline/summary.json", "/failure_count", 0), support("evidence/baseline/summary.json", "/exhaustive_graph_count", 771), support("evidence/baseline/summary.json", "/named_6_vertex_fixture_count", 1)])
    claim("C003", "numerical", "The browser engine agrees on all public outputs for 772 baseline records and 3 separately identified supplemental records.", [support("evidence/browser-engine/summary.json", "/passed", True), support("evidence/browser-engine/summary.json", "/record_count", 772), support("evidence/browser-engine/summary.json", "/supplemental_record_count", 3)])
    claim("C004", "numerical", "Eight curated lexical retrieval sanity cases and 961 ordered navigation pairs passed; this is not a semantic-recall or novelty benchmark.", [support("evidence/corpus/search-and-paths.json", "/passed", True), support("evidence/corpus/search-and-paths.json", "/retrieval_sanity_cases", 8), support("evidence/corpus/search-and-paths.json", "/navigation_pairs", 961)])
    correctness = "evidence/symmetry/independent/verifier-correctness-attempt-02/summary.json"
    benchmark = "evidence/symmetry/independent/verifier-benchmark-attempt-01/summary.json"
    claim("C005", "numerical", "Independent symmetry reproduction compared 15,192 full result dictionaries with zero failures in the frozen finite domain.", [support(correctness, "/ordered_pair_record_count", 15192), support(correctness, "/failure_count", 0)])
    # Exact JSON field names are checked, not inferred from a prose ratio.
    claim("C006", "numerical", "The independent 21-round frozen-workload benchmark recorded median direct time 0.2803868 s and symmetry time 0.1129344 s. These are machine- and workload-specific measurements.", [support(benchmark, "/direct_median_seconds", 0.2803868), support(benchmark, "/symmetry_median_seconds", 0.1129344), support(benchmark, "/equal_round_count", 21), support(benchmark, "/paired_round_count", 21), support(benchmark, "/passed", True)])
    claim("C007", "numerical", "The annotated normalized-probability reading predicts commute 1 for K2, while exact computation and the original unnormalized-measure formula give 2.", [support("evidence/reuse/normalization-witness.json", "/candidate_prediction", "1"), support("evidence/reuse/normalization-witness.json", "/actual_commute", "2"), support("evidence/reuse/normalization-witness.json", "/original_formula_prediction", "2")])
    claim("C008", "methodological", "Electrical and Markov quantities use separately constructed exact systems sharing a generic rational solver; tree enumeration uses subset connectivity. Cross-language agreement alone is not an independent proof.", [{"artifact_id": ids["src/atlas_engine/analysis.py"], "locator": "contains:def analyze_graph"}, {"artifact_id": ids["src/atlas_engine/trees.py"], "locator": "contains:combinations"}])
    claim("C009", "citation", "Canonical-form-indexed graph evaluation reuse has direct prior art; this optimization is not claimed as a globally new algorithm.", [{"artifact_id": ids["evidence/symmetry/independent/prior-art-audit.md"], "locator": "contains:10.1162/evco.2007.15.2.199"}])
    claim("C010", "conclusion", "This region supplies tested finite computations and one independently checked summary normalization mismatch. It does not establish a new mathematical theorem, a general automatic assumption detector, or complete mathematical coverage.", [{"claim_id": "C001"}, {"claim_id": "C002"}, {"claim_id": "C005"}, {"claim_id": "C007"}, {"claim_id": "C009"}])

    audit_paths = ["evidence/foundation/independent/final-audit.json", "evidence/symmetry/independent/final-audit.json"]
    checks = []
    for identifier in ("reproduction", "specification_compliance", "source_verification", "implementation_alignment"):
        attestations = []
        evidence_ids = [ids[p] for p in audit_paths]
        for path in audit_paths:
            records = read(path)["checks"]
            record = next(c for c in records if c["id"] == identifier)
            if record["status"] != "pass":
                raise ValueError(f"Independent audit has not passed {identifier}: {path}")
            attestations.append(record)
            for reference in record.get("supporting_paths", record.get("evidence", [])):
                candidate = reference if reference in ids else (Path(path).parent / reference).as_posix()
                if candidate in ids:
                    evidence_ids.append(ids[candidate])
        checks.append({"id": identifier, "status": "pass", "auditor": "sol_atlas_audit; sol_symmetry_audit (separate scoped independent attestations)", "evidence": list(dict.fromkeys(evidence_ids)), "note": " | ".join(str(a.get("note", a.get("notes", "See independent report for exact scope."))) for a in attestations)})
    bundle = {"schema_version": "1.0", "run_id": "atlas-foundation", "objective": "Deliver the source-grounded Laplacian atlas milestone, bounded symmetry optimization and reviewed reuse example while preserving the full active mathematical mapping and discovery objective.", "created_at": datetime.now(timezone.utc).isoformat(), "task_spec_artifact_id": spec, "evaluator_command": "uv run --frozen python -m atlas_engine evaluate --output-dir evidence/baseline; uv run --frozen python scripts/run_symmetry_correctness.py --output-dir evidence/symmetry/local-correctness; uv run --frozen python scripts/run_symmetry_benchmark.py --output-dir evidence/symmetry/local-benchmark", "artifacts": artifacts, "claims": claims, "checks": checks, "limitations": ["Finite curated region, not all mathematics; no claim of globally novel mathematics or algorithms.", "No current corpus entry has been checked in a pinned Lean environment.", "The external-summary semantic annotation is manual; its exact separating witness is automated. No error-prevalence estimate or evaluated automatic semantic parser.", "Search sanity cases are curated rediscovery checks, not held-out semantic or novelty evaluation.", "Original branch response events, roles and timing are retained and independently checked; encrypted original prompt bodies prevent checking textual prompt identity.", "Wall-clock benchmark benefit applies to the frozen repeated finite workload; cold or larger graphs can be slower.", "Focused WebMCP checks do not establish broad visual, responsive or accessibility QA."]}
    RUN.mkdir(parents=True, exist_ok=True)
    (RUN / "bundle.json").write_text(json.dumps(bundle, indent=2, ensure_ascii=False) + "\n", encoding="utf-8", newline="\n")
    print(json.dumps({"artifacts": len(artifacts), "claims": len(claims), "checks": len(checks)}))


if __name__ == "__main__":
    main()
