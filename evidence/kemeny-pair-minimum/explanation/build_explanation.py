from __future__ import annotations

import argparse
import hashlib
import itertools
import json
import os
from pathlib import Path
from typing import Any


SOURCE_PINS = {
    "result-manifest.json": {
        "bytes": 5978,
        "sha256": "78b4121cc83d7e06bed7470f70c1cbb365ba1d24543595f7620b9e15e0524a9d",
    },
    "run-01/summary.json": {
        "bytes": 181512,
        "sha256": "14367bd2c8c9539206754f65b2da7b17baa5430cde97c33a070ddfc35ffc37f4",
    },
    "run-01/witnesses.json": {
        "bytes": 1573,
        "sha256": "11667e046a4fff70fff23b5e7f501a7941def67c8067edd9034f56555a40b13f",
    },
}

EXPECTED_WITNESS_ID = {
    "n": 6,
    "source_file": "graph6c.g6",
    "source_graph6": "E?zW",
    "source_line": 10,
    "pair_index_global": 504,
}
EXPECTED_BASE_EDGES = [
    [1, 5],
    [1, 6],
    [2, 5],
    [2, 6],
    [3, 5],
    [4, 6],
    [5, 6],
]
EXPECTED_ADDED_EDGES = [[1, 2], [3, 4]]
EXPECTED_KEMENY = {
    "base": {"denominator": 28, "numerator": 135},
    "joint": {"denominator": 252, "numerator": 1229},
    "single_e": {"denominator": 16, "numerator": 77},
    "single_f": {"denominator": 28, "numerator": 135},
}
EXPECTED_DELTAS = {
    "joint_minus_base": {"denominator": 18, "numerator": 1},
    "single_e_minus_base": {"denominator": 112, "numerator": -1},
    "single_f_minus_base": {"denominator": 1, "numerator": 0},
}
EXPECTED_PER_ORDER = [
    {"n": 2, "representative_count": 1, "pair_count": 0, "witness_count": 0},
    {"n": 3, "representative_count": 2, "pair_count": 0, "witness_count": 0},
    {"n": 4, "representative_count": 6, "pair_count": 8, "witness_count": 0},
    {"n": 5, "representative_count": 21, "pair_count": 139, "witness_count": 0},
    {"n": 6, "representative_count": 112, "pair_count": 2243, "witness_count": 1},
]
EXPECTED_LABELLED_COUNTS = [
    {"n": 2, "connected_labelled_count": 1},
    {"n": 3, "connected_labelled_count": 4},
    {"n": 4, "connected_labelled_count": 38},
    {"n": 5, "connected_labelled_count": 728},
    {"n": 6, "connected_labelled_count": 26704},
]


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def load_pinned_json(author_dir: Path, relative_path: str) -> tuple[dict[str, Any], dict[str, Any]]:
    path = author_dir / relative_path
    raw = path.read_bytes()
    pin = SOURCE_PINS[relative_path]
    actual = {"bytes": len(raw), "sha256": sha256_bytes(raw)}
    if actual != pin:
        raise ValueError(f"source pin mismatch for {relative_path}: {actual!r}")
    return json.loads(raw), actual


def edge_set(edges: list[list[int]]) -> set[tuple[int, int]]:
    normalized: set[tuple[int, int]] = set()
    for edge in edges:
        if not isinstance(edge, list) or len(edge) != 2:
            raise ValueError(f"invalid edge record: {edge!r}")
        u, v = edge
        if not isinstance(u, int) or isinstance(u, bool) or not isinstance(v, int) or isinstance(v, bool):
            raise ValueError(f"noninteger endpoint: {edge!r}")
        if not 1 <= u < v <= 6:
            raise ValueError(f"edge is not normalized on vertices 1..6: {edge!r}")
        normalized.add((u, v))
    if len(normalized) != len(edges):
        raise ValueError("duplicate base edge")
    return normalized


def relative_display_path(output_parent: Path, source: Path) -> str:
    return Path(os.path.relpath(source, output_parent)).as_posix()


def rational_text(value: dict[str, int]) -> str:
    numerator = value["numerator"]
    denominator = value["denominator"]
    return str(numerator) if denominator == 1 else f"{numerator}/{denominator}"


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Create a deterministic explanation from sealed author outputs without graph evaluation."
    )
    parser.add_argument("--author-dir", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    args = parser.parse_args()

    author_dir = args.author_dir.resolve()
    output = args.output.resolve()
    if output.exists():
        raise FileExistsError(f"refusing to overwrite {output}")

    result_manifest, manifest_actual = load_pinned_json(author_dir, "result-manifest.json")
    summary, summary_actual = load_pinned_json(author_dir, "run-01/summary.json")
    witness_file, witness_actual = load_pinned_json(author_dir, "run-01/witnesses.json")

    manifest_artifacts = {item["path"]: item for item in result_manifest["artifacts"]}
    for source_name in ("run-01/summary.json", "run-01/witnesses.json"):
        if manifest_artifacts.get(source_name) != {"path": source_name, **SOURCE_PINS[source_name]}:
            raise ValueError(f"author result manifest does not carry the pinned record for {source_name}")
    if result_manifest["status"] != "author_outputs_sealed_pending_independent_evaluator":
        raise ValueError("unexpected author manifest status")

    if witness_file["status"] != "author_only_pending_independent_evaluation":
        raise ValueError("unexpected witness-file status")
    if witness_file["witness_count"] != 1 or len(witness_file["witnesses"]) != 1:
        raise ValueError("expected exactly one sealed author witness")
    witness = witness_file["witnesses"][0]
    for key, value in EXPECTED_WITNESS_ID.items():
        if witness[key] != value:
            raise ValueError(f"unexpected witness identity field {key}")
    if witness["base_edges"] != EXPECTED_BASE_EDGES:
        raise ValueError("unexpected base-edge list")
    if witness["added_edges"] != EXPECTED_ADDED_EDGES:
        raise ValueError("unexpected added-edge list")
    if witness["kemeny"] != EXPECTED_KEMENY:
        raise ValueError("unexpected exact Kemeny values")
    if witness["deltas"] != EXPECTED_DELTAS:
        raise ValueError("unexpected exact deltas")
    if witness["signs"] != {
        "joint_minus_base": "positive",
        "single_e_minus_base": "negative",
        "single_f_minus_base": "zero",
    }:
        raise ValueError("unexpected delta signs")
    if witness["equality_flags"] != {
        "joint_equals_base": False,
        "single_e_equals_base": False,
        "single_f_equals_base": True,
    }:
        raise ValueError("unexpected equality flags")
    if witness["qualifies"] is not True:
        raise ValueError("author witness is not marked qualifying")

    base = edge_set(witness["base_edges"])
    core_vertices = [1, 2, 5, 6]
    complete_core = set(itertools.combinations(core_vertices, 2))
    missing_core_edge = (1, 2)
    diamond_edges = complete_core - {missing_core_edge}
    pendant_edges = {(3, 5), (4, 6)}
    if base != diamond_edges | pendant_edges:
        raise ValueError("base graph does not equal the stated diamond-plus-two-leaves decomposition")
    for leaf, neighbor in ((3, 5), (4, 6)):
        incident = {v if u == leaf else u for u, v in base if u == leaf or v == leaf}
        if incident != {neighbor}:
            raise ValueError(f"vertex {leaf} is not a leaf at vertex {neighbor}")

    if summary["candidate_minimum_order"] != 6:
        raise ValueError("unexpected candidate minimum order")
    if summary["candidate_minimum_basis"] != "author witness plus complete author exclusion of lower orders":
        raise ValueError("unexpected candidate minimum basis")
    if summary["census"]["representative_count"] != 142:
        raise ValueError("unexpected representative total")
    if summary["census"]["pair_count"] != 2390:
        raise ValueError("unexpected pair total")
    if summary["census"]["witness_count_through_order_6"] != 1:
        raise ValueError("unexpected witness total")
    per_order = [
        {
            "n": row["n"],
            "representative_count": row["representative_count"],
            "pair_count": row["pair_count"],
            "witness_count": row["witness_count"],
        }
        for row in summary["census"]["per_order"]
    ]
    if per_order != EXPECTED_PER_ORDER:
        raise ValueError("unexpected per-order census totals")
    labelled_counts = [
        {"n": row["n"], "connected_labelled_count": row["connected_labelled_count"]}
        for row in summary["input_completeness"]
    ]
    if labelled_counts != EXPECTED_LABELLED_COUNTS:
        raise ValueError("unexpected connected-labelled coverage totals")
    if any(
        row["sets_equal"] is not True or row["orbits_pairwise_disjoint"] is not True
        for row in summary["input_completeness"]
    ):
        raise ValueError("author summary does not record complete, disjoint orbit coverage")
    if summary["lower_order_witness_counts"] != {"2": 0, "3": 0, "4": 0, "5": 0}:
        raise ValueError("unexpected lower-order witness counts")

    vertices = [
        {"id": 1, "label": "1", "x": 1, "y": 1, "roles": ["diamond_vertex", "endpoint_of_e"]},
        {"id": 2, "label": "2", "x": 1, "y": -1, "roles": ["diamond_vertex", "endpoint_of_e"]},
        {"id": 3, "label": "3", "x": -1, "y": 0, "roles": ["pendant_leaf", "endpoint_of_f"]},
        {"id": 4, "label": "4", "x": 3, "y": 0, "roles": ["pendant_leaf", "endpoint_of_f"]},
        {"id": 5, "label": "5", "x": 0, "y": 0, "roles": ["diamond_vertex", "leaf_attachment"]},
        {"id": 6, "label": "6", "x": 2, "y": 0, "roles": ["diamond_vertex", "leaf_attachment"]},
    ]
    base_edge_records = [
        {"id": f"b{index:02d}", "source": edge[0], "target": edge[1], "kind": "base"}
        for index, edge in enumerate(witness["base_edges"], start=1)
    ]
    addition_records = [
        {
            "id": "e",
            "source": witness["added_edges"][0][0],
            "target": witness["added_edges"][0][1],
            "kind": "candidate_addition",
            "singleton_effect": "strict_decrease",
            "singleton_delta": witness["deltas"]["single_e_minus_base"],
        },
        {
            "id": "f",
            "source": witness["added_edges"][1][0],
            "target": witness["added_edges"][1][1],
            "kind": "candidate_addition",
            "singleton_effect": "exactly_neutral",
            "singleton_delta": witness["deltas"]["single_f_minus_base"],
        },
    ]

    source_paths = {
        relative_path: relative_display_path(output.parent, author_dir / relative_path)
        for relative_path in SOURCE_PINS
    }
    output_record: dict[str, Any] = {
        "schema_version": "kemeny-witness-explanation-v1",
        "status": "candidate_pending_final_audit",
        "provenance": {
            "method": "deterministic serialization and edge-set decomposition only; no graph quantity was evaluated",
            "author_seal": {
                "status": result_manifest["status"],
                "code_freeze_sha256": result_manifest["code_freeze_sha256"],
                "input_freeze_sha256": result_manifest["input_freeze_sha256"],
                "canonical_attempt": result_manifest["canonical_attempt"],
                "canonical_return_code": result_manifest["canonical_return_code"],
                "canonical_timeout": result_manifest["canonical_timeout"],
            },
            "sources": [
                {
                    "role": "author_result_seal",
                    "path": source_paths["result-manifest.json"],
                    **manifest_actual,
                    "selectors": [
                        "$.status",
                        "$.code_freeze_sha256",
                        "$.input_freeze_sha256",
                        "$.artifacts[?(@.path=='run-01/summary.json')]",
                        "$.artifacts[?(@.path=='run-01/witnesses.json')]",
                    ],
                },
                {
                    "role": "finite_census_summary",
                    "path": source_paths["run-01/summary.json"],
                    **summary_actual,
                    "selectors": [
                        "$.candidate_minimum_basis",
                        "$.candidate_minimum_order",
                        "$.census.per_order",
                        "$.census.representative_count",
                        "$.census.pair_count",
                        "$.input_completeness",
                        "$.lower_order_witness_counts",
                    ],
                },
                {
                    "role": "sole_author_witness",
                    "path": source_paths["run-01/witnesses.json"],
                    **witness_actual,
                    "selectors": [
                        "$.definition",
                        "$.status",
                        "$.witness_count",
                        "$.witnesses[0]",
                    ],
                },
            ],
        },
        "candidate": {
            "identity": {key: witness[key] for key in EXPECTED_WITNESS_ID},
            "predicate": {
                "single_e": "delta_e <= 0",
                "single_f": "delta_f <= 0",
                "joint": "delta_joint > 0",
                "qualifies_in_author_output": witness["qualifies"],
            },
            "base_graph": {
                "vertex_count": witness["n"],
                "edge_count": len(witness["base_edges"]),
                "vertices": list(range(1, witness["n"] + 1)),
                "edges": witness["base_edges"],
                "structure": {
                    "kind": "diamond_with_two_pendant_leaves",
                    "diamond": {
                        "vertices": core_vertices,
                        "description": "K4 minus edge {1,2}",
                        "present_edges": [list(edge) for edge in sorted(diamond_edges)],
                        "missing_edge": list(missing_core_edge),
                    },
                    "pendant_leaves": [
                        {"leaf": 3, "neighbor": 5, "edge": [3, 5]},
                        {"leaf": 4, "neighbor": 6, "edge": [4, 6]},
                    ],
                    "edge_set_check": "exact_match",
                },
            },
            "added_edges": {"e": witness["added_edges"][0], "f": witness["added_edges"][1]},
            "exact_values": {
                "kemeny": witness["kemeny"],
                "deltas": witness["deltas"],
                "signs": witness["signs"],
                "equality_flags": witness["equality_flags"],
            },
            "material_neutral_singleton": {
                "edge": "f",
                "delta": witness["deltas"]["single_f_minus_base"],
                "kemeny_equals_base": witness["equality_flags"]["single_f_equals_base"],
                "why_material": "The frozen single-edge condition is nonincrease (<= 0), so exact equality is admissible.",
            },
        },
        "graph_drawing": {
            "format": "explicit_vertex_edge_records",
            "coordinate_system": {
                "units": "arbitrary",
                "x_axis": "right",
                "y_axis": "up",
            },
            "vertices": vertices,
            "base_edges": base_edge_records,
            "candidate_additions": addition_records,
            "display_instruction": "Render base edges as solid and candidate additions e and f as distinct dashed edges.",
        },
        "finite_census_minimum_logic": {
            "scope": summary["definition"]["graph_class"],
            "orders": summary["census"]["orders"],
            "per_order": per_order,
            "connected_labelled_coverage": labelled_counts,
            "orbit_coverage_checks_recorded_by_author": {
                "sets_equal_for_each_order": True,
                "orbits_pairwise_disjoint_for_each_order": True,
            },
            "total_representatives": summary["census"]["representative_count"],
            "total_unordered_nonedge_pairs": summary["census"]["pair_count"],
            "total_witnesses_through_order_6": summary["census"]["witness_count_through_order_6"],
            "lower_order_witness_counts": summary["lower_order_witness_counts"],
            "candidate_minimum_order": summary["candidate_minimum_order"],
            "logic": "The sealed author census records zero qualifying pairs at orders 2 through 5 and one at order 6 after enumerating every unordered pair of distinct nonedges for every listed connected representative. Within that finite census, the displayed order-6 record is therefore the candidate minimum. Independent final audit is still pending.",
        },
        "strictness_boundary": {
            "frozen_predicate": "both singleton deltas <= 0 and the joint delta > 0",
            "alternative_predicate": "both singleton deltas < 0 and the joint delta > 0",
            "candidate_under_frozen_predicate": True,
            "candidate_under_alternative_predicate": False,
            "reason": "The f singleton delta is exactly 0.",
            "claim_boundary": "No existence, minimum-order, or theorem claim is made here for the alternative strict-singleton predicate.",
        },
        "reader_explanation": {
            "short": (
                "Start with a seven-edge graph whose vertices {1,2,5,6} form a diamond "
                "(K4 without {1,2}), with leaf 3 attached to 5 and leaf 4 attached to 6. "
                "The candidate additions are e={1,2} and f={3,4}."
            ),
            "exact_effects": [
                f"The base Kemeny value is {rational_text(witness['kemeny']['base'])}.",
                (
                    f"Adding e alone gives {rational_text(witness['kemeny']['single_e'])}, "
                    f"a change of {rational_text(witness['deltas']['single_e_minus_base'])}."
                ),
                (
                    f"Adding f alone leaves the value at {rational_text(witness['kemeny']['single_f'])}, "
                    f"an exact change of {rational_text(witness['deltas']['single_f_minus_base'])}."
                ),
                (
                    f"Adding both gives {rational_text(witness['kemeny']['joint'])}, "
                    f"a change of +{rational_text(witness['deltas']['joint_minus_base'])}."
                ),
            ],
            "interpretation": "The author output marks this record qualifying because each singleton is nonincreasing while the joint addition is strictly increasing; the exactly neutral f singleton is part of that conclusion.",
            "minimum_scope": "The minimum statement is limited to the sealed finite census through six vertices and remains a candidate pending independent final audit.",
        },
        "limitations": [
            "This explanation is derived from author-produced sealed outputs and is not an independent reproduction or certification.",
            "No graph quantity was recomputed in this postprocessing step.",
            "Publication-level novelty is unresolved; this record makes no novelty claim.",
            "The finite-census minimum does not extend beyond six vertices or to a different qualifying predicate.",
        ],
    }

    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(
        json.dumps(output_record, ensure_ascii=False, sort_keys=True, separators=(",", ":")) + "\n",
        encoding="utf-8",
        newline="\n",
    )
    print(f"wrote={output}")
    print(f"bytes={output.stat().st_size}")
    print(f"sha256={sha256_bytes(output.read_bytes())}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
