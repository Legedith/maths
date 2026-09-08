"""Independent first-step equations for simple-random-walk hitting times."""

from fractions import Fraction

from .linear import solve_linear


def _adjacency(n: int, edges: tuple[tuple[int, int], ...]) -> list[list[int]]:
    neighbors = [[] for _ in range(n)]
    for left, right in edges:
        neighbors[left].append(right)
        neighbors[right].append(left)
    return neighbors


def hitting_time(
    n: int, edges: tuple[tuple[int, int], ...], start: int, destination: int
) -> Fraction:
    """Solve h(v)=1+average(h(neighbor)) with h(destination)=0."""
    neighbors = _adjacency(n, edges)
    transient = [vertex for vertex in range(n) if vertex != destination]
    position = {vertex: index for index, vertex in enumerate(transient)}
    coefficients = [[Fraction(0) for _ in transient] for _ in transient]
    constants = [Fraction(1) for _ in transient]
    for vertex in transient:
        row = position[vertex]
        coefficients[row][row] = 1
        probability = Fraction(1, len(neighbors[vertex]))
        for neighbor in neighbors[vertex]:
            if neighbor != destination:
                coefficients[row][position[neighbor]] -= probability
    return solve_linear(coefficients, constants)[position[start]]

