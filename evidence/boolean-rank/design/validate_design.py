from __future__ import annotations

import hashlib
import json
from pathlib import Path
import subprocess


ROOT = Path(__file__).resolve().parent
PROJECT = Path("D:/CodexWorkspaces/mathematics-atlas/project")


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> int:
    design = json.loads((ROOT / "integration-design.json").read_text(encoding="utf-8"))
    inventory = json.loads((ROOT / "consumer-inventory.json").read_text(encoding="utf-8"))
    atlas = json.loads((PROJECT / "data/atlas.json").read_text(encoding="utf-8"))
    checks: dict[str, bool] = {}

    snapshot = design["project_snapshot"]
    repository = Path(snapshot["repository"]).resolve()
    revision = snapshot["git_revision"]
    input_results: list[dict[str, object]] = []
    for row in design["input_pins"]:
        path = Path(row["path"]).resolve()
        expected = row["sha256"]
        current_sha256 = sha256(path) if path.is_file() else None
        verification_source = "current_file"
        reviewed_sha256 = current_sha256
        if path.is_relative_to(repository):
            relative = path.relative_to(repository).as_posix()
            verification_source = f"git:{revision}:{relative}"
            try:
                reviewed_sha256 = hashlib.sha256(
                    subprocess.check_output(
                        ["git", "show", f"{revision}:{relative}"],
                        cwd=repository,
                    )
                ).hexdigest()
            except (OSError, subprocess.CalledProcessError):
                reviewed_sha256 = None
        input_results.append(
            {
                "path": row["path"],
                "expected_sha256": expected,
                "reviewed_sha256": reviewed_sha256,
                "reviewed_snapshot_matches": reviewed_sha256 == expected,
                "verification_source": verification_source,
                "current_sha256": current_sha256,
                "current_working_tree_matches": current_sha256 == expected,
            }
        )
    checks["input_hashes"] = all(
        row["reviewed_snapshot_matches"] for row in input_results
    )
    nodes = design["nodes"]
    sources = design["source_records"]
    relations = design["relationships"]
    supporting = design["supporting_navigation_edges"]
    journeys = design["journeys"]
    node_ids = [row["id"] for row in nodes]
    source_ids = [row["id"] for row in sources]
    all_node_ids = {row["id"] for row in atlas["nodes"]} | set(node_ids)
    all_source_ids = {row["id"] for row in atlas["sources"]} | set(source_ids)

    checks["expected_counts"] = (
        len(nodes) == 7
        and len(relations) == 4
        and len(supporting) == 4
        and len(sources) == 2
        and len(journeys) == 2
        and len(atlas["nodes"]) + len(nodes) == 40
        and len(atlas["edges"]) + len(relations) + len(supporting) == 52
    )
    checks["unique_new_ids"] = (
        len(node_ids) == len(set(node_ids))
        and len(source_ids) == len(set(source_ids))
        and not (set(node_ids) & {row["id"] for row in atlas["nodes"]})
        and not (set(source_ids) & {row["id"] for row in atlas["sources"]})
    )
    all_edges = relations + supporting
    checks["edge_endpoints"] = all(
        row["from"] in all_node_ids
        and row["to"] in all_node_ids
        and row["from"] != row["to"]
        for row in all_edges
    )
    checks["evidence_sources"] = all(
        evidence["source"] in all_source_ids
        and isinstance(evidence.get("locator"), str)
        and bool(evidence["locator"].strip())
        for row in [*nodes, *all_edges]
        for evidence in row["evidence"]
    )
    checks["journey_references"] = all(
        step["node"] in all_node_ids and bool(step["prompt"].strip())
        for journey in journeys
        for step in journey["steps"]
    )
    checks["r1_to_r4_complete"] = {
        row["curation_record_id"] for row in relations
    } == {"R1", "R2", "R3", "R4"} and all(
        all(
            key in row
            for key in (
                "source_scope",
                "witness_translation",
                "local_boundary_case",
                "notation_boundaries",
            )
        )
        and all(
            isinstance(row["witness_translation"].get(key), str)
            and bool(row["witness_translation"][key].strip())
            for key in ("forward", "reverse", "result")
        )
        and row["local_boundary_case"].get("evidence_basis")
        == "atlas_local_definition_and_proof"
        for row in relations
    )
    checks["r4_nodes_explicit"] = {
        "local-boolean-rank",
        "local-biclique-cover",
    }.issubset(node_ids)
    r3 = next(row for row in relations if row["curation_record_id"] == "R3")
    checks["r3_boundaries"] = (
        "M_f[x,y]=f(x,y)" in r3["assumptions"]
        and "nonempty" in r3["source_scope"].lower()
        and "printed logarithm does not resolve" in r3["source_scope"].lower()
        and "atlas_local_definition_and_proof"
        == r3["local_boundary_case"]["evidence_basis"]
        and any("not deterministic" in text.lower() for text in r3["notation_boundaries"])
    )
    beginner = design["beginner_explanation"].lower()
    guardrail = design["recommendation"]["material_guardrail"].lower()
    checks["known_not_novel"] = (
        "established translations" in beginner
        and "not a new discovery" in beginner
        and "not evidence of real-system benefit" in guardrail
        and "novelty" in guardrail
        and design["conditional_teaching_example"]["certification"]
        == "This design did not inspect or certify the example's computation."
    )
    version_inventory = inventory["atlas_schema_version_inventory"]
    checks["consumer_version_boundary"] = (
        version_inventory["literal_runtime_check"]["path"]
        == "scripts/validate_atlas.py"
        and version_inventory["active_atlas_version_declaration"]["path"]
        == "data/atlas.json"
        and len(version_inventory["unrelated_version_1_0_records_do_not_change"]) >= 10
    )
    checks["functional_not_visual_scope"] = any(
        "no claim" in text.lower() and "visual qa" in text.lower()
        for text in inventory["functional_layout_checks"]
    ) and "requires_visual_review" not in (ROOT / "integration-design.json").read_text(
        encoding="utf-8"
    )

    result = {
        "schema_version": "boolean-rank-integration-design-validation-v1",
        "checks": checks,
        "passed": all(checks.values()),
        "counts": {
            "checks": len(checks),
            "passed": sum(checks.values()),
            "failed": sum(not value for value in checks.values()),
        },
        "input_verification": {
            "project_revision": revision,
            "records": input_results,
            "working_tree_drift_count": sum(
                not row["current_working_tree_matches"] for row in input_results
            ),
            "boundary": "Project inputs are certified against the recorded Git revision. Current-file mismatches are retained as later working-tree drift and are not certified by this design validation.",
        },
        "scope": "Internal consistency and pinned-input integrity only; no implementation, source re-review, example certification or application benchmark.",
    }
    output = ROOT / "design-validation.json"
    output.write_text(
        json.dumps(result, ensure_ascii=True, sort_keys=True, indent=2) + "\n",
        encoding="utf-8",
    )
    print(json.dumps(result, ensure_ascii=True, sort_keys=True, indent=2))
    return 0 if result["passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
