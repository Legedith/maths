"""Independent all-terminal audit for the five frozen six-vertex families."""

from __future__ import annotations

import argparse
import hashlib
import json
from collections import Counter
from pathlib import Path

from preintegration_audit import (
    PROJECT,
    analyze_graph,
    contracted_tree_count,
    edges_from_mask,
    minimizers,
    payload,
    transport,
    tree_count_matrix,
)


FAMILIES: dict[str, tuple[tuple[int, int], ...]] = {
    "path_p6": tuple((v, v + 1) for v in range(5)),
    "cycle_c6": tuple(sorted((*((v, v + 1) for v in range(5)), (0, 5)))),
    "star_k1_5": tuple((0, v) for v in range(1, 6)),
    "complete_k6": tuple((u, v) for u in range(6) for v in range(u + 1, 6)),
    "two_triangles_bridge": (
        (0, 1),
        (0, 2),
        (1, 2),
        (2, 3),
        (3, 4),
        (3, 5),
        (4, 5),
    ),
}


def audit() -> dict[str, object]:
    canonical_cache: dict[tuple[int, int], dict[str, object]] = {}
    per_family: dict[str, object] = {}
    mismatches: list[dict[str, object]] = []
    total_pairs = 0
    total_edges = 0
    total_nonedges = 0
    total_swapping_ties = 0
    tie_histogram = Counter()

    for family, edges in FAMILIES.items():
        family_keys: set[tuple[int, int]] = set()
        family_edge_keys: set[tuple[int, int]] = set()
        family_nonedge_keys: set[tuple[int, int]] = set()
        family_pairs = 0
        family_edge_pairs = 0
        family_nonedge_pairs = 0
        family_swapping_ties = 0
        expected_tree_count = tree_count_matrix(6, edges)
        for source in range(6):
            for target in range(6):
                if source == target:
                    continue
                total_pairs += 1
                family_pairs += 1
                terminal = (min(source, target), max(source, target))
                is_edge = terminal in edges
                if is_edge:
                    total_edges += 1
                    family_edge_pairs += 1
                else:
                    total_nonedges += 1
                    family_nonedge_pairs += 1

                mask, maps = minimizers(6, edges, source, target)
                key = (6, mask)
                family_keys.add(key)
                (family_edge_keys if is_edge else family_nonedge_keys).add(key)
                tie_histogram[len(maps)] += 1
                if {mapping[source] for mapping in maps} == {0, 1}:
                    total_swapping_ties += 1
                    family_swapping_ties += 1

                canonical = canonical_cache.get(key)
                if canonical is None:
                    canonical = analyze_graph(payload(6, edges_from_mask(6, mask), 0, 1))
                    canonical_cache[key] = canonical
                direct = analyze_graph(payload(6, edges, source, target))
                expected = transport(canonical, edges, source, target, maps[0])
                if direct != expected:
                    mismatches.append(
                        {
                            "family": family,
                            "source": source,
                            "target": target,
                            "kind": "transport",
                            "fields": sorted(k for k in direct if direct[k] != expected[k]),
                        }
                    )
                tie_outputs = {
                    json.dumps(transport(canonical, edges, source, target, mapping), sort_keys=True)
                    for mapping in maps
                }
                if len(tie_outputs) != 1:
                    mismatches.append(
                        {
                            "family": family,
                            "source": source,
                            "target": target,
                            "kind": "tie",
                            "minimizer_count": len(maps),
                        }
                    )
                if direct["spanning_tree_count"] != expected_tree_count:
                    mismatches.append(
                        {
                            "family": family,
                            "source": source,
                            "target": target,
                            "kind": "total_tree",
                            "expected": expected_tree_count,
                            "actual": direct["spanning_tree_count"],
                        }
                    )
                if is_edge:
                    expected_selected = contracted_tree_count(6, edges, terminal)
                    if direct["tree_edge_count"] != expected_selected:
                        mismatches.append(
                            {
                                "family": family,
                                "source": source,
                                "target": target,
                                "kind": "selected_tree",
                                "expected": expected_selected,
                                "actual": direct["tree_edge_count"],
                            }
                        )
                elif not (
                    direct["tree_edge_count"] is None
                    and direct["edge_probability"] is None
                    and "edge_probability_equals_resistance" not in direct["checks"]
                ):
                    mismatches.append(
                        {
                            "family": family,
                            "source": source,
                            "target": target,
                            "kind": "nonedge_applicability",
                        }
                    )

        per_family[family] = {
            "ordered_pair_count": family_pairs,
            "ordered_edge_pair_count": family_edge_pairs,
            "ordered_nonedge_pair_count": family_nonedge_pairs,
            "canonical_class_count": len(family_keys),
            "edge_class_count": len(family_edge_keys),
            "nonedge_class_count": len(family_nonedge_keys),
            "endpoint_swapping_tie_count": family_swapping_ties,
            "matrix_tree_count": expected_tree_count,
        }

    script_path = Path(__file__)
    return {
        "status": "pass" if not mismatches else "fail",
        "family_count": len(FAMILIES),
        "ordered_pair_count": total_pairs,
        "ordered_edge_pair_count": total_edges,
        "ordered_nonedge_pair_count": total_nonedges,
        "canonical_class_count_across_families": len(canonical_cache),
        "endpoint_swapping_tie_count": total_swapping_ties,
        "minimizer_count_histogram": {
            str(k): tie_histogram[k] for k in sorted(tie_histogram)
        },
        "families": per_family,
        "mismatch_count": len(mismatches),
        "mismatches": mismatches[:20],
        "sha256": {
            str(script_path): hashlib.sha256(script_path.read_bytes()).hexdigest(),
            str(PROJECT / "src" / "atlas_engine" / "analysis.py"): hashlib.sha256(
                (PROJECT / "src" / "atlas_engine" / "analysis.py").read_bytes()
            ).hexdigest(),
        },
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    result = audit()
    args.output.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(result, sort_keys=True))
    return 0 if result["status"] == "pass" else 1


if __name__ == "__main__":
    raise SystemExit(main())
