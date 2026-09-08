"""Strict version-1 input and expression validation."""

from __future__ import annotations

import re
from dataclasses import dataclass
from fractions import Fraction
from typing import Any

from .model import Assumption, CheckInput, Edge, Graph, Provenance, rational_text


MAX_AST_DEPTH = 20
MAX_AST_NODES = 300
_TOP_FIELDS = {"id", "graph", "source", "target", "provenance", "assumptions", "claim"}
_GRAPH_FIELDS = {"n", "edges"}
_EDGE_FIELDS = {"u", "v", "conductance"}
_PROVENANCE_FIELDS = {
    "kind",
    "source_url",
    "source_locator",
    "annotation_id",
    "annotator",
    "interpretation",
}
_ASSUMPTION_FIELDS = {"id", "expression"}
_BINARY_OPS = {"add", "sub", "mul", "div", "eq", "ne", "lt", "le", "and", "or"}
_UNARY_OPS = {"neg", "not", "sum", "product"}
_RATIONAL_PATTERN = re.compile(r"^([+-]?\d+)(?:/([+]?\d+))?$")


@dataclass(frozen=True, slots=True)
class InputValidationError(ValueError):
    code: str
    path: str
    message: str

    def __str__(self) -> str:
        return f"{self.path}: {self.message}"

    def record(self) -> dict[str, str]:
        return {"code": self.code, "path": self.path, "message": self.message}


def _fail(code: str, path: str, message: str) -> None:
    raise InputValidationError(code, path, message)


def _is_int(value: object) -> bool:
    return isinstance(value, int) and not isinstance(value, bool)


def _object(value: object, path: str, fields: set[str]) -> dict[str, Any]:
    if not isinstance(value, dict):
        _fail("wrong_type", path, "must be an object")
    supplied = set(value)
    missing = fields - supplied
    extra = supplied - fields
    if missing:
        _fail("missing_field", path, f"missing fields: {', '.join(sorted(missing))}")
    if extra:
        _fail("unsupported_field", path, f"unsupported fields: {', '.join(sorted(map(str, extra)))}")
    return value


def _nonempty_string(value: object, path: str) -> str:
    if not isinstance(value, str) or not value.strip():
        _fail("wrong_type", path, "must be a nonempty string")
    return value


def _parse_rational(
    value: object,
    path: str,
    *,
    positive: bool,
    digit_limit: int | None,
) -> Fraction:
    numerator_text: str
    denominator_text: str
    if _is_int(value):
        numerator_text = str(value)
        denominator_text = "1"
    elif isinstance(value, str):
        match = _RATIONAL_PATTERN.fullmatch(value.strip())
        if match is None:
            _fail("invalid_rational", path, "must be an integer string or p/q with a nonnegative denominator token")
        numerator_text = match.group(1)
        denominator_text = (match.group(2) or "1").lstrip("+")
    else:
        _fail("wrong_type", path, "must be an integer or rational string, not a boolean or float")

    numerator_digits = numerator_text.lstrip("+-")
    denominator_digits = denominator_text.lstrip("+")
    if digit_limit is not None and (
        len(numerator_digits) > digit_limit or len(denominator_digits) > digit_limit
    ):
        _fail("rational_too_large", path, f"numerator and denominator are limited to {digit_limit} digits")
    try:
        denominator = int(denominator_text)
        numerator = int(numerator_text)
    except ValueError:
        _fail("rational_too_large", path, "rational token exceeds the runtime integer conversion limit")
    if denominator <= 0:
        _fail("invalid_rational", path, "denominator must be positive")
    result = Fraction(numerator, denominator)
    if positive and result <= 0:
        _fail("invalid_conductance", path, "conductance must be strictly positive")
    return result


def _validate_expression(raw: object, path: str, count: list[int]) -> dict[str, Any]:
    def visit(node: object, node_path: str, depth: int) -> dict[str, Any]:
        if depth > MAX_AST_DEPTH:
            _fail("ast_depth_limit", node_path, f"AST depth exceeds {MAX_AST_DEPTH}")
        count[0] += 1
        if count[0] > MAX_AST_NODES:
            _fail("ast_node_limit", path, f"total AST node count exceeds {MAX_AST_NODES}")
        if not isinstance(node, dict):
            _fail("wrong_type", node_path, "expression must be an object")
        kind = node.get("kind")
        if not isinstance(kind, str):
            _fail("wrong_type", f"{node_path}.kind", "must be a string")

        if kind == "rational":
            obj = _object(node, node_path, {"kind", "value"})
            value = _parse_rational(obj["value"], f"{node_path}.value", positive=False, digit_limit=None)
            return {"kind": "rational", "value": rational_text(value)}
        if kind == "boolean":
            obj = _object(node, node_path, {"kind", "value"})
            if not isinstance(obj["value"], bool):
                _fail("wrong_type", f"{node_path}.value", "must be a boolean")
            return {"kind": "boolean", "value": obj["value"]}
        if kind == "quantity":
            obj = _object(node, node_path, {"kind", "name"})
            if not isinstance(obj["name"], str):
                _fail("wrong_type", f"{node_path}.name", "must be a string")
            return {"kind": "quantity", "name": obj["name"]}
        if kind == "binary":
            obj = _object(node, node_path, {"kind", "op", "left", "right"})
            if not isinstance(obj["op"], str) or obj["op"] not in _BINARY_OPS:
                _fail("unsupported_operator", f"{node_path}.op", "unsupported binary operator")
            return {
                "kind": "binary",
                "op": obj["op"],
                "left": visit(obj["left"], f"{node_path}.left", depth + 1),
                "right": visit(obj["right"], f"{node_path}.right", depth + 1),
            }
        if kind == "unary":
            obj = _object(node, node_path, {"kind", "op", "arg"})
            if not isinstance(obj["op"], str) or obj["op"] not in _UNARY_OPS:
                _fail("unsupported_operator", f"{node_path}.op", "unsupported unary operator")
            return {
                "kind": "unary",
                "op": obj["op"],
                "arg": visit(obj["arg"], f"{node_path}.arg", depth + 1),
            }
        if kind == "entry":
            obj = _object(node, node_path, {"kind", "arg", "indices"})
            indices = obj["indices"]
            if not isinstance(indices, list) or len(indices) not in (1, 2):
                _fail("invalid_indices", f"{node_path}.indices", "must contain one or two indices")
            normalized_indices: list[int] = []
            for index, value in enumerate(indices):
                if not _is_int(value) or value < 0:
                    _fail(
                        "invalid_index",
                        f"{node_path}.indices[{index}]",
                        "must be a nonnegative integer, not a boolean",
                    )
                normalized_indices.append(value)
            return {
                "kind": "entry",
                "arg": visit(obj["arg"], f"{node_path}.arg", depth + 1),
                "indices": normalized_indices,
            }
        _fail("unsupported_expression", f"{node_path}.kind", f"unsupported expression kind: {kind!r}")

    return visit(raw, path, 1)


def validate_payload(raw: object) -> CheckInput:
    payload = _object(raw, "$", _TOP_FIELDS)
    check_id = _nonempty_string(payload["id"], "$.id")

    graph_raw = _object(payload["graph"], "$.graph", _GRAPH_FIELDS)
    n = graph_raw["n"]
    if not _is_int(n) or not 2 <= n <= 6:
        _fail("invalid_n", "$.graph.n", "must be a non-boolean integer from 2 through 6")
    raw_edges = graph_raw["edges"]
    if not isinstance(raw_edges, list):
        _fail("wrong_type", "$.graph.edges", "must be an array")
    edges: list[Edge] = []
    seen: set[tuple[int, int]] = set()
    for index, raw_edge in enumerate(raw_edges):
        edge_path = f"$.graph.edges[{index}]"
        edge_obj = _object(raw_edge, edge_path, _EDGE_FIELDS)
        u, v = edge_obj["u"], edge_obj["v"]
        if not _is_int(u) or not _is_int(v):
            _fail("invalid_vertex", edge_path, "u and v must be non-boolean integers")
        if not 0 <= u < n or not 0 <= v < n:
            _fail("invalid_vertex", edge_path, f"vertices must lie in 0..{n - 1}")
        if u == v:
            _fail("self_loop", edge_path, "self-loops are not admitted")
        key = min(u, v), max(u, v)
        if key in seen:
            _fail("duplicate_edge", edge_path, "duplicates an undirected edge")
        seen.add(key)
        conductance = _parse_rational(
            edge_obj["conductance"],
            f"{edge_path}.conductance",
            positive=True,
            digit_limit=12,
        )
        edges.append(Edge(key[0], key[1], conductance))
    edges.sort(key=lambda edge: edge.key)

    source, target = payload["source"], payload["target"]
    if not _is_int(source) or not 0 <= source < n:
        _fail("invalid_terminal", "$.source", f"must be a non-boolean integer in 0..{n - 1}")
    if not _is_int(target) or not 0 <= target < n:
        _fail("invalid_terminal", "$.target", f"must be a non-boolean integer in 0..{n - 1}")
    if source == target:
        _fail("invalid_terminal", "$.target", "source and target must be distinct")

    provenance_raw = _object(payload["provenance"], "$.provenance", _PROVENANCE_FIELDS)
    provenance_values = {
        field: _nonempty_string(provenance_raw[field], f"$.provenance.{field}")
        for field in _PROVENANCE_FIELDS
    }
    if provenance_values["kind"] not in {"source_annotation", "synthetic"}:
        _fail("invalid_provenance_kind", "$.provenance.kind", "must be source_annotation or synthetic")
    if provenance_values["interpretation"] not in {"explicit", "ambiguous", "unsupported"}:
        _fail(
            "invalid_interpretation",
            "$.provenance.interpretation",
            "must be explicit, ambiguous, or unsupported",
        )
    provenance = Provenance(**provenance_values)

    raw_assumptions = payload["assumptions"]
    if not isinstance(raw_assumptions, list):
        _fail("wrong_type", "$.assumptions", "must be an array")
    assumptions: list[Assumption] = []
    assumption_ids: set[str] = set()
    ast_count = [0]
    for index, raw_assumption in enumerate(raw_assumptions):
        assumption_path = f"$.assumptions[{index}]"
        assumption_obj = _object(raw_assumption, assumption_path, _ASSUMPTION_FIELDS)
        assumption_id = _nonempty_string(assumption_obj["id"], f"{assumption_path}.id")
        if assumption_id in assumption_ids:
            _fail("duplicate_assumption_id", f"{assumption_path}.id", "assumption IDs must be unique")
        assumption_ids.add(assumption_id)
        assumptions.append(
            Assumption(
                assumption_id,
                _validate_expression(
                    assumption_obj["expression"],
                    f"{assumption_path}.expression",
                    ast_count,
                ),
            )
        )
    claim = _validate_expression(payload["claim"], "$.claim", ast_count)
    return CheckInput(
        id=check_id,
        graph=Graph(n=n, edges=tuple(edges), source=source, target=target),
        provenance=provenance,
        assumptions=tuple(assumptions),
        claim=claim,
    )
