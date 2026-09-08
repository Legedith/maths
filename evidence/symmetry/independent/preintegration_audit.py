"""Independent pre-integration audit for unordered-terminal transport.

This is verifier-only code.  It deliberately does not import or reproduce the
candidate cache implementation.  It enumerates the frozen domain boundary,
constructs the mathematical transport directly from the unchanged analyzer,
and checks spanning-tree outputs with a determinant oracle.
"""

from __future__ import annotations

import argparse
import hashlib
import itertools
import json
import sys
from collections import Counter
from fractions import Fraction
from pathlib import Path


PROJECT = Path("D:/CodexWorkspaces/mathematics-atlas/project")
sys.path.insert(0, str(PROJECT / "src"))

from atlas_engine import analyze_graph  # noqa: E402


def connected(n: int, edges: tuple[tuple[int, int], ...]) -> bool:
    adjacency = [[] for _ in range(n)]
    for left, right in edges:
        adjacency[left].append(right)
        adjacency[right].append(left)
    seen = {0}
    pending = [0]
    while pending:
        vertex = pending.pop()
        for neighbor in adjacency[vertex]:
            if neighbor not in seen:
                seen.add(neighbor)
                pending.append(neighbor)
    return len(seen) == n


def connected_graphs(n: int):
    possible = tuple(itertools.combinations(range(n), 2))
    for mask in range(1 << len(possible)):
        edges = tuple(edge for bit, edge in enumerate(possible) if mask & (1 << bit))
        if connected(n, edges):
            yield edges


def mapped_edges(
    edges: tuple[tuple[int, int], ...], mapping: tuple[int, ...]
) -> tuple[tuple[int, int], ...]:
    return tuple(
        sorted((min(mapping[u], mapping[v]), max(mapping[u], mapping[v])) for u, v in edges)
    )


def edge_mask(n: int, edges: tuple[tuple[int, int], ...]) -> int:
    positions = {edge: bit for bit, edge in enumerate(itertools.combinations(range(n), 2))}
    return sum(1 << positions[edge] for edge in edges)


def edges_from_mask(n: int, mask: int) -> tuple[tuple[int, int], ...]:
    return tuple(
        edge
        for bit, edge in enumerate(itertools.combinations(range(n), 2))
        if mask & (1 << bit)
    )


def minimizers(
    n: int,
    edges: tuple[tuple[int, int], ...],
    source: int,
    target: int,
) -> tuple[int, list[tuple[int, ...]]]:
    remaining = tuple(v for v in range(n) if v not in (source, target))
    best_mask: int | None = None
    best: list[tuple[int, ...]] = []
    for source_image, target_image in ((0, 1), (1, 0)):
        for rest_order in itertools.permutations(remaining):
            mapping = [-1] * n
            mapping[source] = source_image
            mapping[target] = target_image
            for image, vertex in enumerate(rest_order, start=2):
                mapping[vertex] = image
            frozen = tuple(mapping)
            mask = edge_mask(n, mapped_edges(edges, frozen))
            if best_mask is None or mask < best_mask:
                best_mask = mask
                best = [frozen]
            elif mask == best_mask:
                best.append(frozen)
    assert best_mask is not None
    return best_mask, best


def payload(n: int, edges: tuple[tuple[int, int], ...], source: int, target: int):
    return {
        "n": n,
        "edges": [list(edge) for edge in edges],
        "source": source,
        "target": target,
    }


def transport(
    canonical: dict[str, object],
    original_edges: tuple[tuple[int, int], ...],
    source: int,
    target: int,
    mapping: tuple[int, ...],
) -> dict[str, object]:
    n = int(canonical["n"])
    reverse = mapping[source] == 1
    resistance = Fraction(str(canonical["resistance"]))
    canonical_potentials = [Fraction(str(value)) for value in canonical["potentials"]]
    if reverse:
        potentials = [resistance - canonical_potentials[mapping[v]] for v in range(n)]
        hit_forward = canonical["hit_backward"]
        hit_backward = canonical["hit_forward"]
    else:
        potentials = [canonical_potentials[mapping[v]] for v in range(n)]
        hit_forward = canonical["hit_forward"]
        hit_backward = canonical["hit_backward"]
    canonical_laplacian = canonical["laplacian"]
    return {
        "n": n,
        "edges": [list(edge) for edge in original_edges],
        "source": source,
        "target": target,
        "laplacian": [
            [canonical_laplacian[mapping[i]][mapping[j]] for j in range(n)]
            for i in range(n)
        ],
        "potentials": [str(value) for value in potentials],
        "resistance": canonical["resistance"],
        "hit_forward": hit_forward,
        "hit_backward": hit_backward,
        "commute": canonical["commute"],
        "spanning_tree_count": canonical["spanning_tree_count"],
        "tree_edge_count": canonical["tree_edge_count"],
        "edge_probability": canonical["edge_probability"],
        "checks": dict(canonical["checks"]),
    }


def bareiss_determinant(matrix: list[list[int]]) -> int:
    """Exact fraction-free determinant, independent of the project solver."""
    n = len(matrix)
    if n == 0:
        return 1
    work = [row[:] for row in matrix]
    sign = 1
    denominator = 1
    for k in range(n - 1):
        if work[k][k] == 0:
            pivot = next((r for r in range(k + 1, n) if work[r][k]), None)
            if pivot is None:
                return 0
            work[k], work[pivot] = work[pivot], work[k]
            sign *= -1
        pivot_value = work[k][k]
        for i in range(k + 1, n):
            for j in range(k + 1, n):
                work[i][j] = (
                    work[i][j] * pivot_value - work[i][k] * work[k][j]
                ) // denominator
        denominator = pivot_value
        for i in range(k + 1, n):
            work[i][k] = 0
    return sign * work[-1][-1]


def tree_count_matrix(n: int, edges: tuple[tuple[int, int], ...]) -> int:
    laplacian = [[0] * n for _ in range(n)]
    for left, right in edges:
        laplacian[left][left] += 1
        laplacian[right][right] += 1
        laplacian[left][right] -= 1
        laplacian[right][left] -= 1
    return bareiss_determinant([row[:-1] for row in laplacian[:-1]])


def contracted_tree_count(
    n: int, edges: tuple[tuple[int, int], ...], selected: tuple[int, int]
) -> int:
    """Count trees containing selected via the matrix-tree theorem on G/e.

    Parallel edges created by contraction are retained as multiplicities.
    """
    left, right = selected
    representatives = [left if vertex == right else vertex for vertex in range(n)]
    surviving = sorted(set(representatives))
    relabel = {vertex: index for index, vertex in enumerate(surviving)}
    multiedges: list[tuple[int, int]] = []
    for u, v in edges:
        if (u, v) == selected:
            continue
        a = relabel[representatives[u]]
        b = relabel[representatives[v]]
        if a != b:
            multiedges.append((min(a, b), max(a, b)))
    return tree_count_matrix(n - 1, tuple(multiedges))


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def audit() -> dict[str, object]:
    graph_counts = Counter()
    pair_counts = Counter()
    edge_pair_counts = Counter()
    nonedge_pair_counts = Counter()
    tie_histogram = Counter()
    endpoint_swapping_tie_instances = 0
    cache: dict[tuple[int, int], dict[str, object]] = {}
    edge_class_keys: set[tuple[int, int]] = set()
    nonedge_class_keys: set[tuple[int, int]] = set()
    frozen_benchmark_keys: set[tuple[int, int]] = set()
    exact_mismatches: list[dict[str, object]] = []
    tie_mismatches: list[dict[str, object]] = []
    tree_mismatches: list[dict[str, object]] = []
    nonedge_mismatches: list[dict[str, object]] = []
    asymmetric_hit_example: dict[str, object] | None = None
    key_instance_counts = Counter()

    for n in range(2, 6):
        for graph_index, edges in enumerate(connected_graphs(n)):
            graph_counts[n] += 1
            matrix_tree_count = tree_count_matrix(n, edges)
            direct_graph_tree_count: int | None = None
            benchmark_source, benchmark_target = edges[0]
            benchmark_mask, _ = minimizers(
                n, edges, benchmark_source, benchmark_target
            )
            frozen_benchmark_keys.add((n, benchmark_mask))
            for source in range(n):
                for target in range(n):
                    if source == target:
                        continue
                    pair_counts[n] += 1
                    terminal_edge = (min(source, target), max(source, target))
                    is_edge = terminal_edge in edges
                    if is_edge:
                        edge_pair_counts[n] += 1
                    else:
                        nonedge_pair_counts[n] += 1

                    mask, maps = minimizers(n, edges, source, target)
                    mapping = maps[0]
                    key = (n, mask)
                    (edge_class_keys if is_edge else nonedge_class_keys).add(key)
                    key_instance_counts[key] += 1
                    tie_histogram[len(maps)] += 1
                    if {m[source] for m in maps} == {0, 1}:
                        endpoint_swapping_tie_instances += 1

                    canonical = cache.get(key)
                    if canonical is None:
                        canonical_edges = edges_from_mask(n, mask)
                        canonical = analyze_graph(payload(n, canonical_edges, 0, 1))
                        cache[key] = canonical
                    direct = analyze_graph(payload(n, edges, source, target))
                    expected = transport(canonical, edges, source, target, mapping)
                    if direct != expected and len(exact_mismatches) < 20:
                        differing = sorted(k for k in direct if direct[k] != expected[k])
                        exact_mismatches.append(
                            {
                                "n": n,
                                "graph_index": graph_index,
                                "source": source,
                                "target": target,
                                "key": list(key),
                                "differing_fields": differing,
                            }
                        )

                    tie_outputs = {
                        json.dumps(transport(canonical, edges, source, target, other), sort_keys=True)
                        for other in maps
                    }
                    if len(tie_outputs) != 1 and len(tie_mismatches) < 20:
                        tie_mismatches.append(
                            {
                                "n": n,
                                "graph_index": graph_index,
                                "source": source,
                                "target": target,
                                "key": list(key),
                                "minimizer_count": len(maps),
                            }
                        )

                    if direct_graph_tree_count is None:
                        direct_graph_tree_count = int(direct["spanning_tree_count"])
                        if direct_graph_tree_count != matrix_tree_count:
                            tree_mismatches.append(
                                {
                                    "n": n,
                                    "graph_index": graph_index,
                                    "kind": "total",
                                    "analyzer": direct_graph_tree_count,
                                    "determinant": matrix_tree_count,
                                }
                            )
                    if is_edge:
                        contracted = contracted_tree_count(n, edges, terminal_edge)
                        if direct["tree_edge_count"] != contracted:
                            tree_mismatches.append(
                                {
                                    "n": n,
                                    "graph_index": graph_index,
                                    "edge": list(terminal_edge),
                                    "kind": "selected",
                                    "analyzer": direct["tree_edge_count"],
                                    "contraction_determinant": contracted,
                                }
                            )
                    elif not (
                        direct["tree_edge_count"] is None
                        and direct["edge_probability"] is None
                        and "edge_probability_equals_resistance" not in direct["checks"]
                    ):
                        nonedge_mismatches.append(
                            {
                                "n": n,
                                "graph_index": graph_index,
                                "source": source,
                                "target": target,
                            }
                        )

                    if (
                        asymmetric_hit_example is None
                        and direct["hit_forward"] != direct["hit_backward"]
                    ):
                        asymmetric_hit_example = {
                            "input": payload(n, edges, source, target),
                            "hit_forward": direct["hit_forward"],
                            "hit_backward": direct["hit_backward"],
                        }

    source_files = [
        PROJECT / "docs" / "discovery-contract.md",
        PROJECT / "docs" / "symmetry-contract.md",
        PROJECT / "src" / "atlas_engine" / "analysis.py",
        PROJECT / "src" / "atlas_engine" / "resistance.py",
        PROJECT / "src" / "atlas_engine" / "markov.py",
        PROJECT / "src" / "atlas_engine" / "trees.py",
        Path(__file__),
    ]
    return {
        "status": "pass"
        if not (exact_mismatches or tie_mismatches or tree_mismatches or nonedge_mismatches)
        else "fail",
        "graph_counts": {str(k): graph_counts[k] for k in sorted(graph_counts)},
        "graph_count_total": sum(graph_counts.values()),
        "ordered_pair_counts": {str(k): pair_counts[k] for k in sorted(pair_counts)},
        "ordered_pair_count_total": sum(pair_counts.values()),
        "ordered_existing_pair_counts": {
            str(k): edge_pair_counts[k] for k in sorted(edge_pair_counts)
        },
        "ordered_existing_pair_count_total": sum(edge_pair_counts.values()),
        "ordered_nonedge_pair_counts": {
            str(k): nonedge_pair_counts[k] for k in sorted(nonedge_pair_counts)
        },
        "ordered_nonedge_pair_count_total": sum(nonedge_pair_counts.values()),
        "unordered_terminal_canonical_class_count": len(cache),
        "unordered_terminal_edge_class_count": len(edge_class_keys),
        "unordered_terminal_nonedge_class_count": len(nonedge_class_keys),
        "frozen_771_benchmark_canonical_class_count": len(frozen_benchmark_keys),
        "canonical_key_multiplicity": {
            "minimum": min(key_instance_counts.values()),
            "maximum": max(key_instance_counts.values()),
            "sum": sum(key_instance_counts.values()),
        },
        "minimizer_count_histogram": {
            str(k): tie_histogram[k] for k in sorted(tie_histogram)
        },
        "endpoint_swapping_tie_instance_count": endpoint_swapping_tie_instances,
        "exact_transport_mismatches": exact_mismatches,
        "tie_transport_mismatches": tie_mismatches,
        "tree_oracle_mismatches": tree_mismatches[:20],
        "tree_oracle_mismatch_count": len(tree_mismatches),
        "nonedge_applicability_mismatches": nonedge_mismatches[:20],
        "nonedge_applicability_mismatch_count": len(nonedge_mismatches),
        "asymmetric_directional_hitting_time_example": asymmetric_hit_example,
        "voltage_reversal_counterexample": {
            "input": {"n": 2, "edges": [[0, 1]], "source": 1, "target": 0},
            "canonical_potential": ["1", "0"],
            "correct_R_minus_p_under_identity_map": ["0", "1"],
            "incorrect_negation_under_identity_map": ["-1", "0"],
        },
        "sha256": {str(path): sha256(path) for path in source_files},
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
