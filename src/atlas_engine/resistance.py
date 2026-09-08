"""Exact unit-current Laplacian computation of effective resistance."""

from fractions import Fraction

from .linear import solve_linear


def laplacian_matrix(n: int, edges: tuple[tuple[int, int], ...]) -> list[list[int]]:
    matrix = [[0 for _ in range(n)] for _ in range(n)]
    for left, right in edges:
        matrix[left][left] += 1
        matrix[right][right] += 1
        matrix[left][right] -= 1
        matrix[right][left] -= 1
    return matrix


def resistance_and_potentials(
    laplacian: list[list[int]], source: int, target: int
) -> tuple[Fraction, list[Fraction]]:
    """Ground target, inject one ampere at source, and solve the reduced system."""
    n = len(laplacian)
    free_vertices = [vertex for vertex in range(n) if vertex != target]
    coefficients = [
        [Fraction(laplacian[row][column]) for column in free_vertices]
        for row in free_vertices
    ]
    constants = [Fraction(1 if row == source else 0) for row in free_vertices]
    solved = solve_linear(coefficients, constants)
    potentials = [Fraction(0) for _ in range(n)]
    for vertex, value in zip(free_vertices, solved, strict=True):
        potentials[vertex] = value
    return potentials[source], potentials

