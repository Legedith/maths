"""Exact output must remain serializable beyond the input digit bound."""
from decimal import Decimal, localcontext
from fractions import Fraction
import json
import sys

import pytest

from atlas_checks import check_transfer
from atlas_checks.model import rational_text
from .helpers import make_payload


@pytest.mark.parametrize("value", [
    Fraction(0), Fraction(1), Fraction(-1), Fraction(10 ** 9),
    Fraction(-(10 ** 9)), Fraction(10 ** 18 + 1, 10 ** 9 + 7),
    Fraction(10 ** 5000 + 1), Fraction(-(10 ** 5000 + 1), 10 ** 5001 + 3),
], ids=["zero", "one", "negative", "chunk-boundary", "negative-boundary", "zero-padding", "huge-positive", "huge-rational"])
def test_exact_decimal_chunks_match_independent_decimal_parser(value: Fraction) -> None:
    digit_limit = sys.get_int_max_str_digits()
    text = rational_text(value)
    pieces = text.split("/")
    assert Decimal(pieces[0]) == Decimal(value.numerator)
    assert Decimal(pieces[1] if len(pieces) == 2 else "1") == Decimal(value.denominator)
    assert text == "0" or not text.lstrip("-").startswith("0")
    assert sys.get_int_max_str_digits() == digit_limit


def test_admitted_large_expression_returns_exact_serializable_trace() -> None:
    def product(count: int) -> dict:
        if count == 1:
            return {"kind": "quantity", "name": "tree_mass"}
        left = count // 2
        return {"kind": "binary", "op": "mul", "left": product(left), "right": product(count-left)}
    payload = make_payload(claim={"kind": "binary", "op": "lt", "left": {"kind": "rational", "value": 0}, "right": product(140)})
    payload["graph"] = {"n": 6, "edges": [{"u": 0, "v": v, "conductance": 999999999999} for v in range(1, 6)]}
    payload["source"], payload["target"] = 0, 1
    limit = sys.get_int_max_str_digits()
    result = check_transfer(payload)
    assert result["verdict"] == "no_counterexample_in_instance"
    value = result["claim_evaluation"]["trace"]["right"]["value"]
    assert len(value) == 8400
    with localcontext() as context:
        context.prec = 8401
        assert Decimal(value) == Decimal(999999999999) ** 700
    assert json.loads(json.dumps(result))["claim_evaluation"]["value"] is True
    assert sys.get_int_max_str_digits() == limit
