"""Exhaustive spanning-tree oracle based only on subsets and connectivity."""

from itertools import combinations


def _is_connected(n: int, chosen: tuple[tuple[int, int], ...]) -> bool:
    neighbors = [[] for _ in range(n)]
    for left, right in chosen:
        neighbors[left].append(right)
        neighbors[right].append(left)
    seen = {0}
    pending = [0]
    while pending:
        vertex = pending.pop()
        for neighbor in neighbors[vertex]:
            if neighbor not in seen:
                seen.add(neighbor)
                pending.append(neighbor)
    return len(seen) == n


def spanning_tree_counts(
    n: int,
    edges: tuple[tuple[int, int], ...],
    selected_edge: tuple[int, int] | None,
) -> tuple[int, int | None]:
    """Enumerate all n-1 edge subsets; connectivity alone identifies trees."""
    total = 0
    containing = 0
    for subset in combinations(edges, n - 1):
        if _is_connected(n, subset):
            total += 1
            if selected_edge is not None and selected_edge in subset:
                containing += 1
    return total, containing if selected_edge is not None else None

