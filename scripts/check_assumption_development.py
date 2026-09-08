#!/usr/bin/env python3
"""Development-only exhaustive cross-checks over all simple graphs through n=5."""

from __future__ import annotations

import argparse
import itertools
import json
from fractions import Fraction
from pathlib import Path
from typing import Any

from atlas_checks.graph_math import combinatorial_laplacian, components, is_connected, weighted_degrees
from atlas_checks.linear import matrix_vector
from atlas_checks.markov import canonical_stationary_distribution, transition_matrix
from atlas_checks.model import Edge, Graph, rational_text
from atlas_checks.quantities import QuantityStore


def value(store: QuantityStore, name: str):
    result = store.get(name)
    if result.value is None:
        raise AssertionError(f"{name} unexpectedly undefined: {result.error_code}: {result.error}")
    return result.value.data


def undefined(store: QuantityStore, name: str, code: str) -> None:
    result = store.get(name)
    if result.value is not None or result.error_code != code:
        raise AssertionError(f"{name}: expected undefined {code}, got {result.record()}")


def graph_from_mask(n: int, mask: int) -> Graph:
    possible = list(itertools.combinations(range(n), 2))
    edges = tuple(
        Edge(u, v, Fraction(1))
        for bit, (u, v) in enumerate(possible)
        if mask & (1 << bit)
    )
    return Graph(n=n, edges=edges, source=0, target=1)


def with_terminals(graph: Graph, source: int, target: int) -> Graph:
    return Graph(n=graph.n, edges=graph.edges, source=source, target=target)


def check_graph(graph: Graph) -> int:
    checks = 0
    store = QuantityStore(graph)
    component_count = len(components(graph))
    assert value(store, "laplacian_rank") == graph.n - component_count
    checks += 1
    tree_mass = value(store, "tree_mass")
    assert value(store, "target_cofactor") == tree_mass
    checks += 1
    connected = is_connected(graph)
    if connected:
        assert value(store, "nonzero_spectrum_product") == graph.n * tree_mass
        checks += 1
    else:
        undefined(store, "nonzero_spectrum_product", "disconnected_graph")
        checks += 1

    degrees = weighted_degrees(graph)
    if all(degrees):
        transition = transition_matrix(graph)
        assert all(sum(row, Fraction(0)) == 1 for row in transition)
        stationary = canonical_stationary_distribution(graph)
        evolved = [
            sum((stationary[row] * transition[row][column] for row in range(graph.n)), Fraction(0))
            for column in range(graph.n)
        ]
        assert evolved == stationary
        checks += 2
    else:
        undefined(store, "transition_matrix", "isolated_vertex")
        undefined(store, "stationary_distribution", "isolated_vertex")
        checks += 2

    if connected:
        period_value = value(store, "period")
        certificate = store.certificates()["period"]
        edge_keys = {edge.key for edge in graph.edges}
        if period_value == 2:
            assert certificate["kind"] == "bipartition_parity"
            assert all(item["crosses_partition"] for item in certificate["edge_checks"])
        else:
            assert period_value == 1 and certificate["kind"] == "odd_cycle"
            cycle = certificate["cycle"]
            assert certificate["odd_length"] % 2 == 1 and cycle[0] == cycle[-1]
            assert all(
                (min(left, right), max(left, right)) in edge_keys
                for left, right in zip(cycle[:-1], cycle[1:], strict=True)
            )
        checks += 1

    for source in range(graph.n):
        for target in range(graph.n):
            if source == target:
                continue
            pair_graph = with_terminals(graph, source, target)
            pair_store = QuantityStore(pair_graph)
            same_component = target in next(component for component in components(pair_graph) if source in component)
            if not same_component:
                undefined(pair_store, "resistance", "terminals_disconnected")
                undefined(pair_store, "hit_forward", "terminals_disconnected")
                undefined(pair_store, "hit_backward", "terminals_disconnected")
                checks += 3
                continue
            resistance = value(pair_store, "resistance")
            forward = value(pair_store, "hit_forward")
            backward = value(pair_store, "hit_backward")
            assert resistance > 0 and forward > 0 and backward > 0
            checks += 3
            if connected:
                assert forward + backward == value(pair_store, "total_conductance") * resistance
                potentials = list(value(pair_store, "potentials"))
                laplacian = combinatorial_laplacian(pair_graph)
                current = [
                    Fraction(1) if vertex == source else Fraction(-1) if vertex == target else Fraction(0)
                    for vertex in range(graph.n)
                ]
                assert potentials[target] == 0
                assert matrix_vector(laplacian, potentials) == current
                checks += 3
                selected = next((edge for edge in graph.edges if edge.key == (min(source, target), max(source, target))), None)
                if selected is not None:
                    assert value(pair_store, "edge_probability") == selected.conductance * resistance
                    checks += 1
                else:
                    undefined(pair_store, "edge_probability", "terminal_nonedge")
                    checks += 1
    return checks


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--max-n", type=int, default=5)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--summary", type=Path, required=True)
    args = parser.parse_args()
    if not 2 <= args.max_n <= 5:
        raise SystemExit("--max-n must lie in 2..5 for the development run")

    records: list[dict[str, Any]] = []
    total_checks = 0
    failures = 0
    for n in range(2, args.max_n + 1):
        possible_edges = n * (n - 1) // 2
        for mask in range(1 << possible_edges):
            graph = graph_from_mask(n, mask)
            try:
                checks = check_graph(graph)
                record = {
                    "n": n,
                    "mask": mask,
                    "edge_count": len(graph.edges),
                    "status": "pass",
                    "checks": checks,
                }
                total_checks += checks
            except Exception as exc:
                failures += 1
                record = {
                    "n": n,
                    "mask": mask,
                    "edges": [[edge.u, edge.v, rational_text(edge.conductance)] for edge in graph.edges],
                    "status": "fail",
                    "error_type": type(exc).__name__,
                    "error": str(exc),
                }
            records.append(record)

    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text("".join(json.dumps(record, sort_keys=True) + "\n" for record in records), encoding="utf-8")
    by_n = {
        str(n): {
            "graphs": sum(record["n"] == n for record in records),
            "passed": sum(record["n"] == n and record["status"] == "pass" for record in records),
            "failed": sum(record["n"] == n and record["status"] == "fail" for record in records),
            "checks": sum(record.get("checks", 0) for record in records if record["n"] == n),
        }
        for n in range(2, args.max_n + 1)
    }
    summary = {
        "scope": "development_only_all_labeled_simple_unweighted_graphs",
        "max_n": args.max_n,
        "graphs": len(records),
        "checks": total_checks,
        "failures": failures,
        "by_n": by_n,
        "limitations": "This is implementation development evidence, not independent evaluation or universal theorem evidence.",
    }
    args.summary.write_text(json.dumps(summary, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(summary, sort_keys=True))
    return 0 if failures == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
