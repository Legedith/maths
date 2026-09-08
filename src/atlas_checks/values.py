"""Typed exact values and JSON serialization."""

from __future__ import annotations

from dataclasses import dataclass
from fractions import Fraction
from typing import Any

from .model import rational_text


@dataclass(frozen=True, slots=True)
class TypedValue:
    type: str
    data: Any

    @property
    def shape(self) -> list[int]:
        if self.type in {"rational", "boolean"}:
            return []
        if self.type == "rational_vector":
            return [len(self.data)]
        if self.type == "rational_matrix":
            return [len(self.data), len(self.data[0]) if self.data else 0]
        raise ValueError(f"unknown value type {self.type}")

    def json_value(self) -> Any:
        if self.type == "rational":
            return rational_text(self.data)
        if self.type == "boolean":
            return self.data
        if self.type == "rational_vector":
            return [rational_text(value) for value in self.data]
        if self.type == "rational_matrix":
            return [[rational_text(value) for value in row] for row in self.data]
        raise ValueError(f"unknown value type {self.type}")

    def record(self) -> dict[str, Any]:
        return {"type": self.type, "shape": self.shape, "value": self.json_value()}


def rational(value: Fraction | int) -> TypedValue:
    return TypedValue("rational", Fraction(value))


def boolean(value: bool) -> TypedValue:
    return TypedValue("boolean", bool(value))


def vector(values: list[Fraction] | tuple[Fraction, ...]) -> TypedValue:
    return TypedValue("rational_vector", tuple(values))


def matrix(values: list[list[Fraction]]) -> TypedValue:
    return TypedValue("rational_matrix", tuple(tuple(row) for row in values))
