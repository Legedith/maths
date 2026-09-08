"""Exact graph structure and combinatorial Laplacian utilities."""

from __future__ import annotations

from fractions import Fraction

from .linear import Matrix
from .model import Graph


def weighted_degrees(graph: Graph) -> list[Fraction]:
    result = [Fraction(0) for _ in range(graph.n)]
    for edge in graph.edges:
        result[edge.u] += edge.conductance
        result[edge.v] += edge.conductance
    return result


def adjacency(graph: Graph) -> list[list[int]]:
    result: list[list[int]] = [[] for _ in range(graph.n)]
    for edge in graph.edges:
        result[edge.u].append(edge.v)
        result[edge.v].append(edge.u)
    for neighbors in result:
        neighbors.sort()
    return result


def component_from(graph: Graph, start: int) -> tuple[int, ...]:
    neighbors = adjacency(graph)
    reached = {start}
    pending = [start]
    while pending:
        vertex = pending.pop()
        for neighbor in neighbors[vertex]:
            if neighbor not in reached:
                reached.add(neighbor)
                pending.append(neighbor)
    return tuple(sorted(reached))


def components(graph: Graph) -> tuple[tuple[int, ...], ...]:
    remaining = set(range(graph.n))
    result: list[tuple[int, ...]] = []
    while remaining:
        component = component_from(graph, min(remaining))
        result.append(component)
        remaining.difference_update(component)
    return tuple(result)


def is_connected(graph: Graph) -> bool:
    return len(component_from(graph, 0)) == graph.n


def terminals_connected(graph: Graph) -> bool:
    return graph.target in component_from(graph, graph.source)


def terminal_edge(graph: Graph):
    key = min(graph.source, graph.target), max(graph.source, graph.target)
    return next((edge for edge in graph.edges if edge.key == key), None)


def combinatorial_laplacian(graph: Graph) -> Matrix:
    matrix = [[Fraction(0) for _ in range(graph.n)] for _ in range(graph.n)]
    for edge in graph.edges:
        matrix[edge.u][edge.u] += edge.conductance
        matrix[edge.v][edge.v] += edge.conductance
        matrix[edge.u][edge.v] -= edge.conductance
        matrix[edge.v][edge.u] -= edge.conductance
    return matrix
