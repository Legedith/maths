"""Validated immutable records used by the structured checker."""

from __future__ import annotations

from dataclasses import dataclass
from fractions import Fraction
from typing import Any


def rational_text(value: Fraction) -> str:
    """Return a canonical exact JSON representation."""
    if value.denominator == 1:
        return str(value.numerator)
    return f"{value.numerator}/{value.denominator}"


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
