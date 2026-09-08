from __future__ import annotations

import argparse
import copy
import hashlib
import json
from pathlib import Path
import subprocess
import sys
from typing import Any, Callable


EXPECTED_FREEZE_SHA256 = "391aa34b932aa37c4ccb45e2b9ee589ba3eaec38540c15f9d43b9581c420f7f6"
EXPECTED_CONTRACT_SHA256 = "a302711e12faa6526456d92a42707f94c55ff421c7afabe58f925133c071dcda"
EXPECTED_RECORD_SHA256 = "0ba1c19b75b0b37fcd29214d3ad5565aca747481aba779084e23367b0a110fd2"
EXPECTED_REVIEW_SHA256 = "13bff50ecbd050f359a7948996197e9b09a12c5a5305fedb4aa40804cefcbad0"

NEW_IDS = {
    "nodes": {
        "boolean-relation-matrix",
        "boolean-rank",
        "one-support-rectangle-cover",
        "fixed-bipartition-biclique-cover",
        "nondeterministic-communication-s2",
        "local-boolean-rank",
        "local-biclique-cover",
    },
    "edges": {
        "boolean-rank-r1",
        "boolean-rank-r2",
        "boolean-rank-r3",
        "boolean-rank-r4",
        "boolean-matrix-cover-definition",
        "rectangle-cover-local-objective",
        "biclique-cover-local-objective",
        "biadjacency-versus-adjacency",
    },
    "sources": {"javadi-local-clique", "karchmer-few-witnesses"},
    "journeys": {"boolean-table-to-certificate", "total-cover-to-local-load"},
    "opportunities": set(),
}


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def joined(value: Any) -> str:
    if isinstance(value, str):
        return value
    if isinstance(value, dict):
        return " ".join(joined(item) for item in value.values())
    if isinstance(value, list):
        return " ".join(joined(item) for item in value)
    return str(value)


def has_all(value: Any, *needles: str) -> bool:
    text = joined(value).lower()
    return all(needle.lower() in text for needle in needles)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--project-root", type=Path, required=True)
    parser.add_argument("--freeze-manifest", type=Path, required=True)
    parser.add_argument("--admitted-records", type=Path, required=True)
    parser.add_argument("--correction-review", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    args = parser.parse_args()

    project = args.project_root.resolve()
    output = args.output_dir.resolve()
    if output.exists():
        raise SystemExit("Use a fresh --output-dir")
    output.mkdir(parents=True)

    checks: list[dict[str, Any]] = []

    def check(name: str, condition: bool, detail: Any = None) -> None:
        checks.append({"name": name, "passed": bool(condition), "detail": detail})

    freeze = load(args.freeze_manifest)
    check(
        "freeze manifest identity",
        sha256(args.freeze_manifest) == EXPECTED_FREEZE_SHA256
        and freeze.get("schema_version") == "boolean-rank-implementation-freeze-v2",
        {"sha256": sha256(args.freeze_manifest), "records": len(freeze.get("files", []))},
    )
    freeze_rows = []
    for record in freeze["files"]:
        path = project / record["path"]
        actual_hash = sha256(path) if path.is_file() else None
        actual_bytes = path.stat().st_size if path.is_file() else None
        freeze_rows.append(
            {
                "path": record["path"],
                "expected_sha256": record["sha256"],
                "actual_sha256": actual_hash,
                "expected_bytes": record["bytes"],
                "actual_bytes": actual_bytes,
                "passed": actual_hash == record["sha256"] and actual_bytes == record["bytes"],
            }
        )
    check(
        "all 49 frozen project artifacts match",
        len(freeze_rows) == 49 and all(row["passed"] for row in freeze_rows),
        {"records": len(freeze_rows), "failures": [row for row in freeze_rows if not row["passed"]]},
    )
    (output / "freeze-hash-verification.json").write_text(
        json.dumps({"records": freeze_rows}, sort_keys=True, indent=2) + "\n",
        encoding="utf-8",
    )

    contract = project / "docs/boolean-rank-contract.md"
    admitted = load(args.admitted_records)
    correction = load(args.correction_review)
    retained_admitted = project / "evidence/boolean-rank/source-review/corrected-records-v1.json"
    retained_review = project / "evidence/boolean-rank/source-review/correction-review.json"
    check(
        "contract and admitted inputs have pinned identities",
        sha256(contract) == EXPECTED_CONTRACT_SHA256
        and sha256(args.admitted_records) == EXPECTED_RECORD_SHA256
        and sha256(args.correction_review) == EXPECTED_REVIEW_SHA256
        and retained_admitted.read_bytes() == args.admitted_records.read_bytes()
        and retained_review.read_bytes() == args.correction_review.read_bytes(),
        {
            "contract": sha256(contract),
            "admitted": sha256(args.admitted_records),
            "correction_review": sha256(args.correction_review),
        },
    )
    decisions = {row["id"]: row for row in correction["bridge_decisions"]}
    check(
        "upstream independent semantic review admits exactly R1-R4",
        correction.get("overall_recommendation") == "PASS"
        and set(decisions) == {"R1", "R2", "R3", "R4"}
        and all(row.get("decision") == "ADMIT" for row in decisions.values()),
        "This product audit reuses the upstream source review; hash identity alone is not a new source-entailment proof.",
    )

    atlas = load(project / "data/atlas.json")
    baseline = json.loads(
        subprocess.check_output(
            ["git", "show", f"{freeze['base_commit']}:data/atlas.json"],
            cwd=project,
            text=True,
            encoding="utf-8",
        )
    )
    check(
        "schema and collection counts",
        atlas.get("schema_version") == "1.1"
        and {key: len(atlas[key]) for key in ("nodes", "edges", "sources", "journeys", "opportunities")}
        == {"nodes": 40, "edges": 52, "sources": 11, "journeys": 6, "opportunities": 6}
        and len(atlas.get("examples", [])) == 7,
        {key: len(atlas[key]) for key in ("nodes", "edges", "sources", "journeys", "opportunities", "examples")},
    )
    preservation_failures = []
    addition_results = {}
    for category in NEW_IDS:
        old_by_id = {row["id"]: row for row in baseline[category]}
        new_by_id = {row["id"]: row for row in atlas[category]}
        for identifier, expected in old_by_id.items():
            if new_by_id.get(identifier) != expected:
                preservation_failures.append(f"{category}:{identifier}")
        actual_additions = set(new_by_id) - set(old_by_id)
        addition_results[category] = {
            "expected": sorted(NEW_IDS[category]),
            "actual": sorted(actual_additions),
            "passed": actual_additions == NEW_IDS[category],
        }
    check(
        "all pre-existing records remain value-identical",
        not preservation_failures
        and atlas["examples"] == baseline["examples"]
        and atlas["title"] == baseline["title"]
        and atlas["domains"] == baseline["domains"],
        {"changed_old_records": preservation_failures, "examples_equal": atlas["examples"] == baseline["examples"]},
    )
    check(
        "exact 7/8/2/2 additions and no opportunity addition",
        all(row["passed"] for row in addition_results.values()),
        addition_results,
    )

    nodes = {row["id"]: row for row in atlas["nodes"]}
    edges = {row["id"]: row for row in atlas["edges"]}
    sources = {row["id"]: row for row in atlas["sources"]}
    journeys = {row["id"]: row for row in atlas["journeys"]}

    source_expected = {
        "javadi-local-clique": {
            "url": "https://arxiv.org/pdf/1210.6965v1",
            "year": 2012,
            "locator": "Introduction, printed pp. 2-3",
        },
        "karchmer-few-witnesses": {
            "url": "https://www.math.ias.edu/~avi/PUBLICATIONS/MYPAPERS/SAKS/KCOVER/JOURNAL/kcover.pdf",
            "year": 2003,
            "locator": "Sections 2.1-2.3, printed pp. 3-5; Proposition 3 and proof",
        },
    }
    check(
        "new sources preserve primary URLs, locators, dates and local-convention limits",
        all(
            all(sources[sid].get(key) == value for key, value in expected.items())
            for sid, expected in source_expected.items()
        )
        and "zero-support conventions are separate local definitions" in sources["javadi-local-clique"]["note"]
        and has_all(sources["karchmer-few-witnesses"]["note"], "nonzero-support", "Atlas zero case", "superscript notation", "local"),
        source_expected,
    )

    node_obligations = {
        "boolean-relation-matrix": ["finite nonempty labeled", "0 or 1", "not automatically the full symmetric adjacency"],
        "boolean-rank": ["boolean or-and", "dimension k may be zero", "empty disjunction"],
        "one-support-rectangle-cover": ["no zero cell", "overlap", "not a one-witness restriction", "empty family"],
        "fixed-bipartition-biclique-cover": ["fixed labeled nonempty sides", "biadjacency matrix", "not the full symmetric adjacency", "empty family"],
        "nondeterministic-communication-s2": ["maximum leaf depth", "not deterministic", "m_f[x,y]=f(x,y)", "all-zero totalization is an atlas convention"],
        "local-boolean-rank": ["per row or column", "does not count", "matrix cell", "load zero"],
        "local-biclique-cover": ["per vertex", "individual edge", "load zero"],
    }
    node_results = {
        identifier: {
            "passed": identifier in nodes
            and nodes[identifier].get("status") == "sourced"
            and has_all(nodes[identifier], *needles),
            "obligations": needles,
        }
        for identifier, needles in node_obligations.items()
    }
    check(
        "seven concepts retain definitions, domain assumptions and nearby-parameter boundaries",
        all(row["passed"] for row in node_results.values()),
        node_results,
    )

    admitted_by_id = {row["id"]: row for row in admitted["relationships"]}
    relation_map = {f"boolean-rank-r{i}": f"R{i}" for i in range(1, 5)}
    common_relation_results = {}
    for edge_id, record_id in relation_map.items():
        edge = edges[edge_id]
        curation = edge.get("curation_record", {})
        common_relation_results[edge_id] = {
            "passed": edge.get("status") == "established"
            and curation
            == {
                "id": record_id,
                "artifact": "evidence/boolean-rank/source-review/corrected-records-v1.json",
                "artifact_sha256": EXPECTED_RECORD_SHA256,
                "independent_review": "evidence/boolean-rank/source-review/correction-review.json",
                "independent_review_sha256": EXPECTED_REVIEW_SHA256,
            }
            and edge.get("local_boundary_case", {}).get("evidence_basis")
            == "atlas_local_definition_and_proof"
            and all(
                isinstance(edge.get(field), expected_type)
                for field, expected_type in (
                    ("source_scope", str),
                    ("witness_translation", dict),
                    ("local_boundary_case", dict),
                    ("notation_boundaries", list),
                )
            ),
            "admitted_record_present": record_id in admitted_by_id,
        }
    check(
        "R1-R4 each retain typed source, witness, zero-case, notation and curation fields",
        all(row["passed"] and row["admitted_record_present"] for row in common_relation_results.values()),
        common_relation_results,
    )

    r1 = edges["boolean-rank-r1"]
    check(
        "R1 uses both witness inequalities rather than false exact k preservation",
        r1["from"] == "boolean-rank"
        and r1["to"] == "one-support-rectangle-cover"
        and has_all(r1["statement"], "r_B(A)=rc_1(A)")
        and has_all(r1["witness_translation"]["forward"], "factor index", "contains no zero", "covers every 1-cell", "omit empty factors")
        and has_all(r1["witness_translation"]["reverse"], "indicator", "reconstructs A")
        and has_all(r1["witness_translation"]["result"], "at most k", "exactly t", "two inequalities", "minima equal")
        and has_all(r1["local_boundary_case"], "all-zero", "k=0", "empty disjunction", "empty rectangle", "=0")
        and has_all(r1, "unrestricted", "not S2 kappa_1"),
        r1["witness_translation"],
    )

    r2 = edges["boolean-rank-r2"]
    check(
        "R2 fixes the labeled bipartition and preserves cell-edge cover cardinality",
        r2["from"] == "one-support-rectangle-cover"
        and r2["to"] == "fixed-bipartition-biclique-cover"
        and has_all(r2["assumptions"], "fixed labeled nonempty sides", "x-by-y biadjacency", "respect the fixed sides")
        and has_all(r2["witness_translation"], "s x t", "biclique", "one-to-one", "cover cardinality")
        and has_all(r2["notation_boundaries"], "not the full symmetric adjacency", "may not be changed")
        and has_all(r2["local_boundary_case"], "edgeless", "empty", "=0"),
        {"assumptions": r2["assumptions"], "witness_translation": r2["witness_translation"]},
    )

    r3 = edges["boolean-rank-r3"]
    check(
        "R3 preserves the exact S2 protocol, nonzero domain and reverse leaf bound",
        r3["from"] == "one-support-rectangle-cover"
        and r3["to"] == "nondeterministic-communication-s2"
        and has_all(r3["assumptions"], "m_f[x,y]=f(x,y)", "maximum-leaf-depth", "at least one 1-input")
        and has_all(r3["source_scope"], "proposition 3", "nonempty-1-support", "does not resolve rc_1=0")
        and has_all(r3["witness_translation"]["forward"], "t>=1", "first party", "row-compatible", "ceil(log_2 t)", "second party", "column")
        and has_all(r3["witness_translation"]["reverse"], "accepting leaves", "all-one rectangles", "2^h")
        and has_all(r3["witness_translation"]["result"], "two inequalities", "nonempty 1-support", "s2 protocol")
        and has_all(r3["statement"], "for nonzero f", "max(1,rc_1(m_f))"),
        {"statement": r3["statement"], "source_scope": r3["source_scope"], "witness_translation": r3["witness_translation"]},
    )
    check(
        "R3 separates the Atlas zero totalization and nearby notation",
        has_all(r3["local_boundary_case"], "all-zero", "empty cover", "depth-zero constant-reject", "sound and complete", "max(1,0)", "=0")
        and has_all(r3["notation_boundaries"], "Atlas notation for S2 n(f)", "not S2 n_1(f)", "unrestricted kappa", "not kappa_1", "not deterministic communication", "complement-side definition"),
        {"zero": r3["local_boundary_case"], "notation": r3["notation_boundaries"]},
    )

    r4 = edges["boolean-rank-r4"]
    check(
        "R4 preserves participant incidence and rejects cell-edge multiplicity",
        r4["from"] == "local-boolean-rank"
        and r4["to"] == "local-biclique-cover"
        and has_all(r4["assumptions"], "row or column", "per vertex", "neither", "per-cell", "per-edge")
        and has_all(r4["witness_translation"], "corresponding graph vertex", "vertex incidence", "row or column incidence", "same maximum incidence")
        and has_all(r4["notation_boundaries"], "maximum participation", "not the number of rectangles covering an individual 1-cell")
        and has_all(r4["local_boundary_case"], "nonempty", "load zero", "maximum", "defined", "=0"),
        {"assumptions": r4["assumptions"], "witness_translation": r4["witness_translation"]},
    )

    supporting_expected = {
        "boolean-matrix-cover-definition": ("boolean-relation-matrix", "one-support-rectangle-cover", "defines_parameter"),
        "rectangle-cover-local-objective": ("one-support-rectangle-cover", "local-boolean-rank", "changes_objective"),
        "biclique-cover-local-objective": ("fixed-bipartition-biclique-cover", "local-biclique-cover", "changes_objective"),
        "biadjacency-versus-adjacency": ("boolean-relation-matrix", "adjacency-matrix", "distinguishes_representation"),
    }
    check(
        "supporting edges are definitions or an explicit representation boundary",
        all(
            (edges[eid]["from"], edges[eid]["to"], edges[eid]["type"]) == expected
            for eid, expected in supporting_expected.items()
        )
        and has_all(edges["biadjacency-versus-adjacency"], "may be rectangular", "square symmetric", "no equality"),
        supporting_expected,
    )
    check(
        "two learning journeys retain the intended node sequences and scope prompts",
        [step["node"] for step in journeys["boolean-table-to-certificate"]["steps"]]
        == [
            "boolean-relation-matrix",
            "one-support-rectangle-cover",
            "boolean-rank",
            "fixed-bipartition-biclique-cover",
            "nondeterministic-communication-s2",
        ]
        and [step["node"] for step in journeys["total-cover-to-local-load"]["steps"]]
        == ["one-support-rectangle-cover", "local-boolean-rank", "local-biclique-cover"]
        and has_all(journeys["boolean-table-to-certificate"], "overlap", "fixed", "s2 model", "deterministic", "privacy", "latency", "deployed")
        and has_all(journeys["total-cover-to-local-load"], "busiest row or column", "not the busiest cell", "vertex participation"),
        {key: [step["node"] for step in journeys[key]["steps"]] for key in NEW_IDS["journeys"]},
    )

    adjacency: dict[str, set[str]] = {identifier: set() for identifier in nodes}
    for edge in atlas["edges"]:
        adjacency[edge["from"]].add(edge["to"])
        adjacency[edge["to"]].add(edge["from"])
    connected_pairs = 0
    for start in nodes:
        seen = {start}
        queue = [start]
        for current in queue:
            for neighbor in adjacency[current]:
                if neighbor not in seen:
                    seen.add(neighbor)
                    queue.append(neighbor)
        connected_pairs += len(seen)
    check(
        "independent undirected traversal reaches all 1,600 ordered pairs",
        connected_pairs == 1600,
        {"ordered_pairs": connected_pairs},
    )

    projection = load(project / "evidence/boolean-rank/integration-projection.json")
    projected = {
        **{row["id"]: row for row in projection["relationships"]},
        **{
            row["id"]: row
            for category in ("nodes", "edges", "sources", "journeys")
            for row in projection["additions"][category]
        },
    }
    actual_added = {
        **{identifier: nodes[identifier] for identifier in NEW_IDS["nodes"]},
        **{identifier: edges[identifier] for identifier in NEW_IDS["edges"]},
        **{identifier: sources[identifier] for identifier in NEW_IDS["sources"]},
        **{identifier: journeys[identifier] for identifier in NEW_IDS["journeys"]},
    }
    check(
        "author projection is byte-value aligned with actual additions",
        projected == actual_added,
        "This identity is provenance only; semantic checks above do not rely solely on the author projection.",
    )

    bridge_doc = (project / "docs/boolean-rank-bridge.md").read_text(encoding="utf-8")
    coverage_doc = (project / "docs/coverage.md").read_text(encoding="utf-8")
    reuse_doc = (project / "docs/reuse-decision.md").read_text(encoding="utf-8")
    readme = (project / "README.md").read_text(encoding="utf-8")
    docs_joined = "\n".join((bridge_doc, coverage_doc, reuse_doc, readme)).lower()
    check(
        "documentation states counts, review boundary and no novelty or impact",
        has_all(bridge_doc, "at most k", "nonempty 1-support", "not n_1(f)", "all-zero", "known relationships", "does not establish", "real-world benefit")
        and has_all(coverage_doc, "40 concepts", "52 directed relations", "finite mathematical content")
        and has_all(reuse_doc, "four independently admitted known translations", "does not establish that benefit")
        and has_all(readme, "seven concepts", "eight added relations", "40 concepts", "52 relations", "11 sources", "six journeys")
        and "\ufffd" not in docs_joined,
        "Documentation is reviewed as frozen pending the product audit; a later status-only publication update is outside this freeze.",
    )
    user_visible = [
        "README.md",
        "app/page.tsx",
        "components/atlas-map.tsx",
        "data/atlas.json",
        "docs/boolean-rank-bridge.md",
        "docs/coverage.md",
        "docs/data-model.md",
        "docs/reuse-decision.md",
    ]
    bad_unicode = [path for path in user_visible if "\ufffd" in (project / path).read_text(encoding="utf-8")]
    crlf = [
        path
        for path in ("README.md", "data/atlas.json", "evidence/boolean-rank/integration-projection.json")
        if b"\r\n" in (project / path).read_bytes()
    ]
    check(
        "frozen learner text is valid UTF-8 and corrected files use LF",
        not bad_unicode and not crlf,
        {"replacement_character_files": bad_unicode, "crlf_files": crlf},
    )

    validator = project / "scripts/validate_atlas.py"
    r3_index = next(index for index, row in enumerate(atlas["edges"]) if row["id"] == "boolean-rank-r3")

    def edge3(data: dict[str, Any]) -> dict[str, Any]:
        return data["edges"][r3_index]

    mutations: dict[str, Callable[[dict[str, Any]], None]] = {
        "old-schema": lambda data: data.__setitem__("schema_version", "1.0"),
        "boolean-coordinate": lambda data: data["nodes"][0].__setitem__("x", True),
        "nan-coordinate": lambda data: data["nodes"][0].__setitem__("x", float("nan")),
        "missing-source-scope": lambda data: edge3(data).pop("source_scope"),
        "blank-forward-witness": lambda data: edge3(data)["witness_translation"].__setitem__("forward", " "),
        "missing-zero-evidence-basis": lambda data: edge3(data)["local_boundary_case"].pop("evidence_basis"),
        "source-attributed-zero": lambda data: edge3(data)["local_boundary_case"].__setitem__("evidence_basis", "cited_source"),
        "empty-zero-conventions": lambda data: edge3(data)["local_boundary_case"].__setitem__("adopted_conventions", []),
        "empty-notation": lambda data: edge3(data).__setitem__("notation_boundaries", []),
        "wrong-curation-id": lambda data: edge3(data)["curation_record"].__setitem__("id", "R1"),
        "stale-curation-hash": lambda data: edge3(data)["curation_record"].__setitem__("artifact_sha256", "0" * 64),
        "absolute-curation-path": lambda data: edge3(data)["curation_record"].__setitem__("artifact", "D:/outside.json"),
        "traversal-curation-path": lambda data: edge3(data)["curation_record"].__setitem__("artifact", "../outside.json"),
        "directory-curation-path": lambda data: edge3(data)["curation_record"].__setitem__("artifact", "evidence/boolean-rank"),
        "malformed-edge-id": lambda data: edge3(data).__setitem__("id", []),
    }
    mutation_results = []
    mutation_root = output / "malformed"
    for name, mutate in mutations.items():
        case_dir = mutation_root / name
        case_dir.mkdir(parents=True)
        value = copy.deepcopy(atlas)
        mutate(value)
        corpus_path = case_dir / "corpus.json"
        report_path = case_dir / "report.json"
        corpus_path.write_text(json.dumps(value, ensure_ascii=True, sort_keys=True) + "\n", encoding="utf-8")
        command = [sys.executable, str(validator), str(corpus_path), "--output", str(report_path)]
        completed = subprocess.run(command, cwd=project, capture_output=True)
        (case_dir / "stdout.bin").write_bytes(completed.stdout)
        (case_dir / "stderr.bin").write_bytes(completed.stderr)
        (case_dir / "command.json").write_text(
            json.dumps({"argv": command, "cwd": str(project), "returncode": completed.returncode}, sort_keys=True, indent=2) + "\n",
            encoding="utf-8",
        )
        report = load(report_path) if report_path.is_file() else None
        passed = (
            completed.returncode == 1
            and isinstance(report, dict)
            and report.get("passed") is False
            and bool(report.get("errors"))
            and b"Traceback" not in completed.stderr
        )
        mutation_results.append(
            {
                "id": name,
                "passed": passed,
                "returncode": completed.returncode,
                "errors": report.get("errors") if isinstance(report, dict) else None,
                "stdout_sha256": hashlib.sha256(completed.stdout).hexdigest(),
                "stderr_sha256": hashlib.sha256(completed.stderr).hexdigest(),
            }
        )
    check(
        "15 fresh malformed semantic and provenance cases fail structurally without traceback",
        len(mutation_results) == 15 and all(row["passed"] for row in mutation_results),
        mutation_results,
    )

    failed = [row for row in checks if not row["passed"]]
    report = {
        "schema_version": "boolean-rank-independent-data-check-v1",
        "auditor": {
            "identity": "/root/sol_atlas_audit",
            "role": "independent product auditor and earlier integration-design author",
            "implementation_author": False,
        },
        "inputs": {
            "freeze_manifest": {"path": str(args.freeze_manifest), "sha256": sha256(args.freeze_manifest)},
            "contract": {"path": str(contract), "sha256": sha256(contract)},
            "admitted_records": {"path": str(args.admitted_records), "sha256": sha256(args.admitted_records)},
            "correction_review": {"path": str(args.correction_review), "sha256": sha256(args.correction_review)},
        },
        "passed": not failed,
        "counts": {"checks": len(checks), "passed": len(checks) - len(failed), "failed": len(failed), "malformed_cases": len(mutation_results)},
        "checks": checks,
        "scope": "Frozen data, admitted-record projection, provenance, baseline preservation, docs, independent navigation, and malformed validator behavior. It does not newly prove the source papers, visually assess a browser, certify the teaching example, or measure practical impact or novelty.",
    }
    (output / "independent-data-check.json").write_text(
        json.dumps(report, ensure_ascii=True, sort_keys=True, indent=2) + "\n",
        encoding="utf-8",
    )
    print(json.dumps({"passed": report["passed"], **report["counts"]}, sort_keys=True))
    return 0 if report["passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
