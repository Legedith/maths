"""Constructive period certificates for connected simple undirected graphs."""

from __future__ import annotations

import itertools
from typing import Any

from .model import Graph


def _neighbors_and_edges(graph: Graph) -> tuple[list[list[int]], set[tuple[int, int]]]:
    neighbors: list[list[int]] = [[] for _ in range(graph.n)]
    edges: set[tuple[int, int]] = set()
    for edge in graph.edges:
        neighbors[edge.u].append(edge.v)
        neighbors[edge.v].append(edge.u)
        edges.add(edge.key)
    for row in neighbors:
        row.sort()
    return neighbors, edges


def _canonical_cycle(vertices: tuple[int, ...]) -> tuple[int, ...]:
    rotations: list[tuple[int, ...]] = []
    for sequence in (vertices, tuple(reversed(vertices))):
        for shift in range(len(vertices)):
            rotations.append(sequence[shift:] + sequence[:shift])
    return min(rotations)


def _odd_cycle(graph: Graph, edge_keys: set[tuple[int, int]]) -> tuple[int, ...]:
    candidates: set[tuple[int, ...]] = set()
    for length in range(3, graph.n + 1, 2):
        for vertices in itertools.permutations(range(graph.n), length):
            if vertices[0] != min(vertices):
                continue
            if all(
                (min(vertices[index], vertices[(index + 1) % length]), max(vertices[index], vertices[(index + 1) % length]))
                in edge_keys
                for index in range(length)
            ):
                candidates.add(_canonical_cycle(vertices))
        if candidates:
            return min(candidates)
    raise ValueError("non-bipartite graph lacks an odd-cycle certificate")


def period_with_certificate(graph: Graph) -> tuple[int, dict[str, Any]]:
    neighbors, edge_keys = _neighbors_and_edges(graph)
    colors: list[int | None] = [None] * graph.n
    colors[0] = 0
    pending = [0]
    conflict = False
    while pending:
        vertex = pending.pop(0)
        for neighbor in neighbors[vertex]:
            if colors[neighbor] is None:
                colors[neighbor] = 1 - int(colors[vertex])
                pending.append(neighbor)
            elif colors[neighbor] == colors[vertex]:
                conflict = True
    if any(color is None for color in colors):
        raise ValueError("period requires a connected graph")
    if not conflict:
        left = [vertex for vertex, color in enumerate(colors) if color == 0]
        right = [vertex for vertex, color in enumerate(colors) if color == 1]
        checks = [
            {
                "edge": [edge.u, edge.v],
                "colors": [colors[edge.u], colors[edge.v]],
                "crosses_partition": colors[edge.u] != colors[edge.v],
            }
            for edge in graph.edges
        ]
        return 2, {
            "kind": "bipartition_parity",
            "period": "2",
            "left": left,
            "right": right,
            "edge_checks": checks,
            "justification": "every step crosses the bipartition, so return times are even; traversing one edge out and back gives a length-two return",
        }
    cycle = _odd_cycle(graph, edge_keys)
    return 1, {
        "kind": "odd_cycle",
        "period": "1",
        "cycle": list(cycle) + [cycle[0]],
        "odd_length": len(cycle),
        "edge_checks": [
            [cycle[index], cycle[(index + 1) % len(cycle)]] for index in range(len(cycle))
        ],
        "justification": "the odd cycle gives an odd return and traversing one edge out and back gives an even return, whose gcd is one",
    }
