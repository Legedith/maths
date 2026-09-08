"""Electrical solve constructed directly from edge conductances."""

from __future__ import annotations

from fractions import Fraction

from .linear import solve
from .model import Graph


def _electrical_component(graph: Graph, start: int) -> tuple[int, ...]:
    neighbors: list[list[int]] = [[] for _ in range(graph.n)]
    for edge in graph.edges:
        neighbors[edge.u].append(edge.v)
        neighbors[edge.v].append(edge.u)
    reached = {start}
    pending = [start]
    while pending:
        vertex = pending.pop()
        for neighbor in neighbors[vertex]:
            if neighbor not in reached:
                reached.add(neighbor)
                pending.append(neighbor)
    return tuple(sorted(reached))


def resistance_and_component_potentials(graph: Graph) -> tuple[Fraction, dict[int, Fraction]]:
    """Ground target and solve unit-current equations on its terminal component."""
    vertices = _electrical_component(graph, graph.source)
    if graph.target not in vertices:
        raise ValueError("terminals are disconnected")
    position = {vertex: index for index, vertex in enumerate(vertices)}
    size = len(vertices)
    laplacian = [[Fraction(0) for _ in range(size)] for _ in range(size)]
    for edge in graph.edges:
        if edge.u not in position or edge.v not in position:
            continue
        u, v = position[edge.u], position[edge.v]
        laplacian[u][u] += edge.conductance
        laplacian[v][v] += edge.conductance
        laplacian[u][v] -= edge.conductance
        laplacian[v][u] -= edge.conductance

    target_position = position[graph.target]
    free = [index for index in range(size) if index != target_position]
    coefficients = [[laplacian[row][column] for column in free] for row in free]
    constants = [Fraction(1) if vertices[row] == graph.source else Fraction(0) for row in free]
    solution = solve(coefficients, constants)
    potentials = {vertex: Fraction(0) for vertex in vertices}
    for row, value in zip(free, solution, strict=True):
        potentials[vertices[row]] = value
    return potentials[graph.source] - potentials[graph.target], potentials


def global_grounded_potentials(graph: Graph) -> list[Fraction]:
    resistance, component = resistance_and_component_potentials(graph)
    del resistance
    if len(component) != graph.n:
        raise ValueError("global potentials require a connected graph")
    return [component[vertex] for vertex in range(graph.n)]
