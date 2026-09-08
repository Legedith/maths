"""Nonexecuting typed evaluator for the frozen bounded expression AST."""

from __future__ import annotations

from dataclasses import dataclass
from fractions import Fraction
from typing import Any

from .quantities import QuantityStore
from .values import TypedValue, boolean, rational


@dataclass(frozen=True, slots=True)
class Evaluation:
    value: TypedValue | None
    trace: dict[str, Any]
    errors: tuple[dict[str, str], ...] = ()

    @property
    def defined(self) -> bool:
        return self.value is not None


def _error(code: str, path: str, message: str, trace: dict[str, Any]) -> Evaluation:
    record = {"code": code, "path": path, "message": message}
    trace.update(status="abstain", errors=[record])
    return Evaluation(None, trace, (record,))


def _with_children_error(trace: dict[str, Any], outcomes: list[Evaluation]) -> Evaluation:
    errors = tuple(error for outcome in outcomes for error in outcome.errors)
    trace.update(status="abstain", errors=list(errors))
    return Evaluation(None, trace, errors)


def _success(value: TypedValue, trace: dict[str, Any]) -> Evaluation:
    trace.update(status="defined", **value.record())
    return Evaluation(value, trace)


class ExpressionEvaluator:
    def __init__(self, quantities: QuantityStore):
        self.quantities = quantities

    def evaluate(self, expression: dict[str, Any], path: str) -> Evaluation:
        kind = expression["kind"]
        if kind == "rational":
            return _success(rational(Fraction(expression["value"])), {"path": path, "kind": kind})
        if kind == "boolean":
            return _success(boolean(expression["value"]), {"path": path, "kind": kind})
        if kind == "quantity":
            name = expression["name"]
            result = self.quantities.get(name)
            trace = {"path": path, "kind": kind, "name": name, "quantity": result.record()}
            if result.value is None:
                return _error(
                    result.error_code or "undefined_quantity",
                    path,
                    result.error or "quantity is undefined",
                    trace,
                )
            return _success(result.value, trace)
        if kind == "binary":
            return self._binary(expression, path)
        if kind == "unary":
            return self._unary(expression, path)
        if kind == "entry":
            return self._entry(expression, path)
        raise AssertionError("validated expression kind was not handled")

    def _binary(self, expression: dict[str, Any], path: str) -> Evaluation:
        op = expression["op"]
        left = self.evaluate(expression["left"], f"{path}.left")
        right = self.evaluate(expression["right"], f"{path}.right")
        trace = {
            "path": path,
            "kind": "binary",
            "op": op,
            "left": left.trace,
            "right": right.trace,
        }
        if not left.defined or not right.defined:
            return _with_children_error(trace, [left, right])
        assert left.value is not None and right.value is not None

        if op in {"add", "sub", "mul", "div", "lt", "le"}:
            if left.value.type != "rational" or right.value.type != "rational":
                return _error(
                    "operand_type_error",
                    path,
                    f"{op} requires two rational scalars",
                    trace,
                )
            a, b = left.value.data, right.value.data
            if op == "add":
                return _success(rational(a + b), trace)
            if op == "sub":
                return _success(rational(a - b), trace)
            if op == "mul":
                return _success(rational(a * b), trace)
            if op == "div":
                if b == 0:
                    return _error("division_by_zero", path, "division by zero", trace)
                return _success(rational(a / b), trace)
            if op == "lt":
                return _success(boolean(a < b), trace)
            return _success(boolean(a <= b), trace)

        if op in {"and", "or"}:
            if left.value.type != "boolean" or right.value.type != "boolean":
                return _error(
                    "operand_type_error",
                    path,
                    f"{op} requires two booleans",
                    trace,
                )
            if op == "and":
                return _success(boolean(left.value.data and right.value.data), trace)
            return _success(boolean(left.value.data or right.value.data), trace)

        if op in {"eq", "ne"}:
            if left.value.type != right.value.type or left.value.shape != right.value.shape:
                return _error(
                    "operand_type_error",
                    path,
                    "equality requires operands of the same type and shape",
                    trace,
                )
            equal = left.value.data == right.value.data
            return _success(boolean(equal if op == "eq" else not equal), trace)
        raise AssertionError("validated binary operator was not handled")

    def _unary(self, expression: dict[str, Any], path: str) -> Evaluation:
        op = expression["op"]
        arg = self.evaluate(expression["arg"], f"{path}.arg")
        trace = {"path": path, "kind": "unary", "op": op, "arg": arg.trace}
        if not arg.defined:
            return _with_children_error(trace, [arg])
        assert arg.value is not None
        if op == "neg":
            if arg.value.type != "rational":
                return _error("operand_type_error", path, "neg requires a rational scalar", trace)
            return _success(rational(-arg.value.data), trace)
        if op == "not":
            if arg.value.type != "boolean":
                return _error("operand_type_error", path, "not requires a boolean", trace)
            return _success(boolean(not arg.value.data), trace)
        if op in {"sum", "product"}:
            if arg.value.type != "rational_vector":
                return _error(
                    "operand_type_error",
                    path,
                    f"{op} requires a rational vector",
                    trace,
                )
            if op == "sum":
                value = sum(arg.value.data, Fraction(0))
            else:
                value = Fraction(1)
                for entry in arg.value.data:
                    value *= entry
            return _success(rational(value), trace)
        raise AssertionError("validated unary operator was not handled")

    def _entry(self, expression: dict[str, Any], path: str) -> Evaluation:
        arg = self.evaluate(expression["arg"], f"{path}.arg")
        indices = expression["indices"]
        trace = {"path": path, "kind": "entry", "indices": indices, "arg": arg.trace}
        if not arg.defined:
            return _with_children_error(trace, [arg])
        assert arg.value is not None
        if arg.value.type == "rational_vector" and len(indices) == 1:
            index = indices[0]
            if index >= len(arg.value.data):
                return _error("index_out_of_range", path, "vector index is out of range", trace)
            return _success(rational(arg.value.data[index]), trace)
        if arg.value.type == "rational_matrix" and len(indices) == 2:
            row, column = indices
            if row >= len(arg.value.data) or column >= len(arg.value.data[0]):
                return _error("index_out_of_range", path, "matrix index is out of range", trace)
            return _success(rational(arg.value.data[row][column]), trace)
        return _error(
            "operand_type_error",
            path,
            "entry requires one index for a rational vector or two for a rational matrix",
            trace,
        )
