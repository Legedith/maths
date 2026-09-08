"""Validated immutable records used by the structured checker."""

from __future__ import annotations

from dataclasses import dataclass
from fractions import Fraction
from typing import Any


def _integer_text(value: int) -> str:
    """Format exact output without Python's limit on long decimal conversions."""
    base = 10 ** 9
    if -base < value < base:
        return str(value)
    sign = "-" if value < 0 else ""
    remaining = abs(value)
    chunks: list[int] = []
    while remaining:
        remaining, remainder = divmod(remaining, base)
        chunks.append(remainder)
    # Each remainder is less than base: only at most nine-digit values use
    # Python's decimal formatter. Zero padding restores their place values.
    return sign + str(chunks[-1]) + "".join(f"{chunk:09d}" for chunk in reversed(chunks[:-1]))


def rational_text(value: Fraction) -> str:
    """Return a canonical exact JSON representation."""
    if value.denominator == 1:
        return _integer_text(value.numerator)
    return _integer_text(value.numerator) + "/" + _integer_text(value.denominator)


@dataclass(frozen=True, slots=True)
class Edge:
    u: int
    v: int
    conductance: Fraction

    @property
    def key(self) -> tuple[int, int]:
        return self.u, self.v

    def normalized(self) -> dict[str, Any]:
        return {"u": self.u, "v": self.v, "conductance": rational_text(self.conductance)}


@dataclass(frozen=True, slots=True)
class Graph:
    n: int
    edges: tuple[Edge, ...]
    source: int
    target: int


@dataclass(frozen=True, slots=True)
class Provenance:
    kind: str
    source_url: str
    source_locator: str
    annotation_id: str
    annotator: str
    interpretation: str

    def normalized(self) -> dict[str, str]:
        return {
            "kind": self.kind,
            "source_url": self.source_url,
            "source_locator": self.source_locator,
            "annotation_id": self.annotation_id,
            "annotator": self.annotator,
            "interpretation": self.interpretation,
        }


@dataclass(frozen=True, slots=True)
class Assumption:
    id: str
    expression: dict[str, Any]


@dataclass(frozen=True, slots=True)
class CheckInput:
    id: str
    graph: Graph
    provenance: Provenance
    assumptions: tuple[Assumption, ...]
    claim: dict[str, Any]

    def normalized(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "graph": {
                "n": self.graph.n,
                "edges": [edge.normalized() for edge in self.graph.edges],
            },
            "source": self.graph.source,
            "target": self.graph.target,
            "provenance": self.provenance.normalized(),
            "assumptions": [
                {"id": assumption.id, "expression": assumption.expression}
                for assumption in self.assumptions
            ],
            "claim": self.claim,
        }
