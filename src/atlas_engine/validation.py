"""Strict validation for the version-1 graph input domain."""

from typing import Any


class InputValidationError(ValueError):
    """Raised when a payload lies outside the frozen engine domain."""


def _is_integer(value: object) -> bool:
    return isinstance(value, int) and not isinstance(value, bool)


def _connected(n: int, edges: tuple[tuple[int, int], ...]) -> bool:
    adjacency = [[] for _ in range(n)]
    for left, right in edges:
        adjacency[left].append(right)
        adjacency[right].append(left)
    seen = {0}
    stack = [0]
    while stack:
        vertex = stack.pop()
        for neighbor in adjacency[vertex]:
            if neighbor not in seen:
                seen.add(neighbor)
                stack.append(neighbor)
    return len(seen) == n


def validate_payload(payload: object) -> tuple[int, tuple[tuple[int, int], ...], int, int]:
    """Validate and normalize a JSON-compatible graph payload."""
    if not isinstance(payload, dict):
        raise InputValidationError("payload must be an object")
    required = {"n", "edges", "source", "target"}
    supplied = set(payload)
    missing = required - supplied
    extra = supplied - required
    if missing:
        raise InputValidationError(f"missing fields: {', '.join(sorted(missing))}")
    if extra:
        raise InputValidationError(f"unsupported fields: {', '.join(sorted(str(item) for item in extra))}")

    n: Any = payload["n"]
    if not _is_integer(n) or not 2 <= n <= 6:
        raise InputValidationError("n must be an integer from 2 through 6")
    raw_edges: Any = payload["edges"]
    if not isinstance(raw_edges, list):
        raise InputValidationError("edges must be an array")

    normalized: list[tuple[int, int]] = []
    seen_edges: set[tuple[int, int]] = set()
    for index, edge in enumerate(raw_edges):
        if not isinstance(edge, list) or len(edge) != 2:
            raise InputValidationError(f"edge {index} must be a two-element array")
        left, right = edge
        if not _is_integer(left) or not _is_integer(right):
            raise InputValidationError(f"edge {index} vertices must be integers, not booleans or floats")
        if not 0 <= left < n or not 0 <= right < n:
            raise InputValidationError(f"edge {index} contains a vertex outside 0..{n - 1}")
        if left == right:
            raise InputValidationError(f"edge {index} is a self-loop")
        canonical = (min(left, right), max(left, right))
        if canonical in seen_edges:
            raise InputValidationError(f"edge {index} duplicates an undirected edge")
        seen_edges.add(canonical)
        normalized.append(canonical)

    source: Any = payload["source"]
    target: Any = payload["target"]
    if not _is_integer(source) or not 0 <= source < n:
        raise InputValidationError(f"source must be an integer in 0..{n - 1}")
    if not _is_integer(target) or not 0 <= target < n:
        raise InputValidationError(f"target must be an integer in 0..{n - 1}")
    if source == target:
        raise InputValidationError("source and target must be distinct")

    edges = tuple(sorted(normalized))
    if not _connected(n, edges):
        raise InputValidationError("graph must be connected")
    return n, edges, source, target

