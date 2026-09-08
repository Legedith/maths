"""Independent exhaustive weighted spanning-tree enumeration."""

from __future__ import annotations

import itertools
from fractions import Fraction

from .model import Graph


def weighted_tree_masses(graph: Graph) -> tuple[Fraction, Fraction | None]:
    """Return total mass and selected-terminal-edge mass when that edge exists."""
    selected_key = min(graph.source, graph.target), max(graph.source, graph.target)
    selected_exists = any(edge.key == selected_key for edge in graph.edges)
    total = Fraction(0)
    selected_total = Fraction(0)
    for subset in itertools.combinations(graph.edges, graph.n - 1):
        parent = list(range(graph.n))

        def find(vertex: int) -> int:
            while parent[vertex] != vertex:
                parent[vertex] = parent[parent[vertex]]
                vertex = parent[vertex]
            return vertex

        mass = Fraction(1)
        cyclic = False
        keys: set[tuple[int, int]] = set()
        for edge in subset:
            left, right = find(edge.u), find(edge.v)
            if left == right:
                cyclic = True
                break
            parent[left] = right
            mass *= edge.conductance
            keys.add(edge.key)
        if cyclic or len({find(vertex) for vertex in range(graph.n)}) != 1:
            continue
        total += mass
        if selected_exists and selected_key in keys:
            selected_total += mass
    return total, selected_total if selected_exists else None
