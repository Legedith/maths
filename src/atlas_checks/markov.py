"""Markov quantities built independently from weighted first-step equations."""

from __future__ import annotations

from fractions import Fraction

from .linear import Matrix, identity, solve
from .model import Graph


def _weighted_neighbors(graph: Graph) -> list[list[tuple[int, Fraction]]]:
    neighbors: list[list[tuple[int, Fraction]]] = [[] for _ in range(graph.n)]
    for edge in graph.edges:
        neighbors[edge.u].append((edge.v, edge.conductance))
        neighbors[edge.v].append((edge.u, edge.conductance))
    return neighbors


def markov_degrees(graph: Graph) -> list[Fraction]:
    return [sum((weight for _, weight in row), Fraction(0)) for row in _weighted_neighbors(graph)]


def transition_matrix(graph: Graph) -> Matrix:
    neighbors = _weighted_neighbors(graph)
    degrees = [sum((weight for _, weight in row), Fraction(0)) for row in neighbors]
    if any(degree == 0 for degree in degrees):
        raise ValueError("transition matrix is undefined with an isolated vertex")
    matrix = [[Fraction(0) for _ in range(graph.n)] for _ in range(graph.n)]
    for vertex, row in enumerate(neighbors):
        for neighbor, weight in row:
            matrix[vertex][neighbor] = weight / degrees[vertex]
    return matrix


def random_walk_laplacian(graph: Graph) -> Matrix:
    transition = transition_matrix(graph)
    unit = identity(graph.n)
    return [[unit[row][column] - transition[row][column] for column in range(graph.n)] for row in range(graph.n)]


def canonical_stationary_distribution(graph: Graph) -> list[Fraction]:
    degrees = markov_degrees(graph)
    if any(degree == 0 for degree in degrees):
        raise ValueError("stationary distribution is undefined with an isolated vertex")
    volume = sum(degrees, Fraction(0))
    return [degree / volume for degree in degrees]


def _component(neighbors: list[list[tuple[int, Fraction]]], start: int) -> tuple[int, ...]:
    reached = {start}
    pending = [start]
    while pending:
        vertex = pending.pop()
        for neighbor, _ in neighbors[vertex]:
            if neighbor not in reached:
                reached.add(neighbor)
                pending.append(neighbor)
    return tuple(sorted(reached))


def hitting_time(graph: Graph, start: int, target: int) -> Fraction:
    """Solve h(x)=1+sum_y P(x,y)h(y), independently of electrical quantities."""
    neighbors = _weighted_neighbors(graph)
    vertices = _component(neighbors, start)
    if target not in vertices:
        raise ValueError("target is unreachable")
    transient = [vertex for vertex in vertices if vertex != target]
    position = {vertex: index for index, vertex in enumerate(transient)}
    coefficients = [[Fraction(0) for _ in transient] for _ in transient]
    constants = [Fraction(1) for _ in transient]
    for vertex in transient:
        row = position[vertex]
        degree = sum((weight for _, weight in neighbors[vertex]), Fraction(0))
        coefficients[row][row] = 1
        for neighbor, weight in neighbors[vertex]:
            if neighbor != target:
                coefficients[row][position[neighbor]] -= weight / degree
    return solve(coefficients, constants)[position[start]]
