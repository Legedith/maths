"""Exact batch reuse under unordered two-terminal graph symmetry."""

from __future__ import annotations

from collections import OrderedDict
from dataclasses import dataclass
from fractions import Fraction
from itertools import combinations, permutations
from typing import cast

from .analysis import analyze_graph
from .validation import validate_payload


CanonicalKey = tuple[int, int]


@dataclass(frozen=True, slots=True)
class _CanonicalForm:
    """Canonical key and one deterministic caller-to-canonical bijection."""

    key: CanonicalKey
    caller_to_canonical: tuple[int, ...]
    canonical_edges: tuple[tuple[int, int], ...]
    source_maps_to_zero: bool
    tie_count: int
    candidate_count: int


_EDGE_ORDERS: dict[int, tuple[tuple[int, int], ...]] = {
    n: tuple(combinations(range(n), 2)) for n in range(2, 7)
}
_EDGE_INDICES: dict[int, dict[tuple[int, int], int]] = {
    n: {edge: index for index, edge in enumerate(order)}
    for n, order in _EDGE_ORDERS.items()
}


def _edge_mask(
    n: int,
    edges: tuple[tuple[int, int], ...],
    caller_to_canonical: tuple[int, ...],
) -> int:
    """Encode relabelled edges in lexicographic undirected-edge order."""
    indices = _EDGE_INDICES[n]
    mask = 0
    for left, right in edges:
        mapped = tuple(sorted((caller_to_canonical[left], caller_to_canonical[right])))
        mask |= 1 << indices[cast(tuple[int, int], mapped)]
    return mask


def _canonicalize_validated(
    n: int,
    edges: tuple[tuple[int, int], ...],
    source: int,
    target: int,
) -> _CanonicalForm:
    """Enumerate exactly 2*(n-2)! terminal-respecting relabellings."""
    nonterminals = tuple(
        vertex for vertex in range(n) if vertex != source and vertex != target
    )
    best_mask: int | None = None
    best_mapping: tuple[int, ...] | None = None
    tie_count = 0
    candidate_count = 0

    for zero_terminal, one_terminal in ((source, target), (target, source)):
        for canonical_nonterminals in permutations(nonterminals):
            mapping = [-1] * n
            mapping[zero_terminal] = 0
            mapping[one_terminal] = 1
            for canonical_vertex, caller_vertex in enumerate(
                canonical_nonterminals, start=2
            ):
                mapping[caller_vertex] = canonical_vertex
            frozen_mapping = tuple(mapping)
            mask = _edge_mask(n, edges, frozen_mapping)
            candidate_count += 1
            if best_mask is None or mask < best_mask:
                best_mask = mask
                best_mapping = frozen_mapping
                tie_count = 1
            elif mask == best_mask:
                tie_count += 1
                if best_mapping is None or frozen_mapping < best_mapping:
                    best_mapping = frozen_mapping

    if best_mask is None or best_mapping is None:  # impossible for n >= 2
        raise AssertionError("canonicalization generated no relabellings")
    canonical_edges = tuple(
        edge
        for index, edge in enumerate(_EDGE_ORDERS[n])
        if best_mask & (1 << index)
    )
    return _CanonicalForm(
        key=(n, best_mask),
        caller_to_canonical=best_mapping,
        canonical_edges=canonical_edges,
        source_maps_to_zero=best_mapping[source] == 0,
        tie_count=tie_count,
        candidate_count=candidate_count,
    )


def _transport_result(
    canonical: dict[str, object],
    n: int,
    edges: tuple[tuple[int, int], ...],
    source: int,
    target: int,
    form: _CanonicalForm,
) -> dict[str, object]:
    """Build a fresh caller-labelled result from a private canonical result."""
    mapping = form.caller_to_canonical
    canonical_laplacian = cast(list[list[int]], canonical["laplacian"])
    laplacian = [
        [canonical_laplacian[mapping[row]][mapping[column]] for column in range(n)]
        for row in range(n)
    ]

    canonical_potentials = cast(list[str], canonical["potentials"])
    resistance_text = cast(str, canonical["resistance"])
    resistance = Fraction(resistance_text)
    if form.source_maps_to_zero:
        potentials = [canonical_potentials[mapping[vertex]] for vertex in range(n)]
        hit_forward = cast(str, canonical["hit_forward"])
        hit_backward = cast(str, canonical["hit_backward"])
    else:
        potentials = [
            str(resistance - Fraction(canonical_potentials[mapping[vertex]]))
            for vertex in range(n)
        ]
        hit_forward = cast(str, canonical["hit_backward"])
        hit_backward = cast(str, canonical["hit_forward"])

    commute_text = cast(str, canonical["commute"])
    spanning_tree_count = cast(int, canonical["spanning_tree_count"])
    edge_probability = cast(str | None, canonical["edge_probability"])
    checks: dict[str, bool] = {
        "laplacian_row_sums_zero": all(sum(row) == 0 for row in laplacian),
        "commute_equals_2m_resistance": (
            Fraction(commute_text) == 2 * len(edges) * resistance
        ),
        "spanning_tree_count_positive": spanning_tree_count > 0,
    }
    if edge_probability is not None:
        checks["edge_probability_equals_resistance"] = (
            Fraction(edge_probability) == resistance
        )
    if not all(checks.values()):
        raise ArithmeticError("an exact cross-check failed after symmetry transport")

    return {
        "n": n,
        "edges": [list(edge) for edge in edges],
        "source": source,
        "target": target,
        "laplacian": laplacian,
        "potentials": potentials,
        "resistance": resistance_text,
        "hit_forward": hit_forward,
        "hit_backward": hit_backward,
        "commute": commute_text,
        "spanning_tree_count": spanning_tree_count,
        "tree_edge_count": canonical["tree_edge_count"],
        "edge_probability": edge_probability,
        "checks": checks,
    }


class SymmetryBatchAnalyzer:
    """Instance-local bounded LRU cache of exact canonical core results.

    A least-recently-used policy bounds memory while retaining representatives
    that recur in nearby batch work. ``clear`` empties the cache and resets all
    diagnostics. Invalid payloads do not change cache state or diagnostics.
    """

    def __init__(self, capacity: int = 256) -> None:
        if isinstance(capacity, bool) or not isinstance(capacity, int) or capacity < 1:
            raise ValueError("capacity must be a positive integer")
        self._capacity = capacity
        self._cache: OrderedDict[CanonicalKey, dict[str, object]] = OrderedDict()
        self._hits = 0
        self._misses = 0
        self._core_calls = 0
        self._evictions = 0

    @property
    def capacity(self) -> int:
        return self._capacity

    @property
    def cache_size(self) -> int:
        return len(self._cache)

    @property
    def hits(self) -> int:
        return self._hits

    @property
    def misses(self) -> int:
        return self._misses

    @property
    def core_calls(self) -> int:
        return self._core_calls

    @property
    def evictions(self) -> int:
        return self._evictions

    def diagnostics(self) -> dict[str, int]:
        """Return a detached JSON-compatible snapshot of cache statistics."""
        return {
            "capacity": self._capacity,
            "size": len(self._cache),
            "hits": self._hits,
            "misses": self._misses,
            "core_calls": self._core_calls,
            "evictions": self._evictions,
        }

    def clear(self) -> None:
        """Remove all entries and reset hit, miss, core-call, and eviction counts."""
        self._cache.clear()
        self._hits = 0
        self._misses = 0
        self._core_calls = 0
        self._evictions = 0

    def analyze(self, payload: object) -> dict[str, object]:
        """Validate, reuse an exact canonical result, and restore caller labels."""
        n, edges, source, target = validate_payload(payload)
        form = _canonicalize_validated(n, edges, source, target)

        canonical = self._cache.get(form.key)
        if canonical is None:
            self._misses += 1
            self._core_calls += 1
            canonical = analyze_graph(
                {
                    "n": n,
                    "edges": [list(edge) for edge in form.canonical_edges],
                    "source": 0,
                    "target": 1,
                }
            )
            self._cache[form.key] = canonical
            if len(self._cache) > self._capacity:
                self._cache.popitem(last=False)
                self._evictions += 1
        else:
            self._hits += 1
            self._cache.move_to_end(form.key)

        return _transport_result(canonical, n, edges, source, target, form)
