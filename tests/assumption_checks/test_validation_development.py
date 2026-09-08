from __future__ import annotations

import pytest

from atlas_checks import check_transfer

from .helpers import assumption, b, binary, make_payload, qty, unary


def error_code(payload: object) -> str:
    result = check_transfer(payload)
    assert result["verdict"] == "invalid_input"
    assert result["normalized_input"] is None
    return result["errors"][0]["code"]


@pytest.mark.parametrize(
    ("mutate", "expected"),
    [
        (lambda p: p.update(id=""), "wrong_type"),
        (lambda p: p.update(id=4), "wrong_type"),
        (lambda p: p["graph"].update(n=True), "invalid_n"),
        (lambda p: p["graph"].update(n=3.0), "invalid_n"),
        (lambda p: p.update(source=False), "invalid_terminal"),
        (lambda p: p.update(target=0), "invalid_terminal"),
        (lambda p: p.update(extra=True), "unsupported_field"),
        (lambda p: p["graph"].update(directed=False), "unsupported_field"),
        (lambda p: p["graph"]["edges"][0].update(label="x"), "unsupported_field"),
        (lambda p: p["graph"]["edges"][0].update(v=0), "self_loop"),
        (
            lambda p: p["graph"]["edges"].append({"u": 1, "v": 0, "conductance": 2}),
            "duplicate_edge",
        ),
        (lambda p: p["graph"]["edges"][0].update(conductance=True), "wrong_type"),
        (lambda p: p["graph"]["edges"][0].update(conductance=0.5), "wrong_type"),
        (lambda p: p["graph"]["edges"][0].update(conductance=0), "invalid_conductance"),
        (lambda p: p["graph"]["edges"][0].update(conductance="-1"), "invalid_conductance"),
        (lambda p: p["graph"]["edges"][0].update(conductance="1/0"), "invalid_rational"),
        (lambda p: p["graph"]["edges"][0].update(conductance="1/-2"), "invalid_rational"),
        (
            lambda p: p["graph"]["edges"][0].update(conductance=1234567890123),
            "rational_too_large",
        ),
        (
            lambda p: p["graph"]["edges"][0].update(conductance="1/0000000000001"),
            "rational_too_large",
        ),
        (lambda p: p["provenance"].update(annotator=" "), "wrong_type"),
        (lambda p: p["provenance"].update(kind="paper"), "invalid_provenance_kind"),
        (lambda p: p["provenance"].update(interpretation="guessed"), "invalid_interpretation"),
    ],
)
def test_structural_graph_and_record_errors(mutate, expected: str) -> None:
    payload = make_payload()
    mutate(payload)
    assert error_code(payload) == expected


def test_duplicate_assumption_ids_are_invalid() -> None:
    payload = make_payload(
        assumptions=[assumption("domain", b(True)), assumption("domain", b(False))]
    )
    assert error_code(payload) == "duplicate_assumption_id"


@pytest.mark.parametrize(
    ("claim", "expected"),
    [
        ({"kind": "mystery"}, "unsupported_expression"),
        ({"kind": "binary", "op": "pow", "left": b(True), "right": b(True)}, "unsupported_operator"),
        ({"kind": "boolean", "value": True, "extra": 1}, "unsupported_field"),
        ({"kind": "entry", "arg": qty("degrees"), "indices": [-1]}, "invalid_index"),
        ({"kind": "entry", "arg": qty("degrees"), "indices": [True]}, "invalid_index"),
        ({"kind": "entry", "arg": qty("degrees"), "indices": []}, "invalid_indices"),
    ],
)
def test_ast_structural_errors_are_invalid(claim, expected: str) -> None:
    assert error_code(make_payload(claim=claim)) == expected


def test_structural_invalidity_precedes_ambiguous_interpretation() -> None:
    payload = make_payload(interpretation="ambiguous", claim={"kind": "mystery"})
    assert error_code(payload) == "unsupported_expression"


def _not_chain(nodes: int):
    expression = b(True)
    for _ in range(nodes - 1):
        expression = unary("not", expression)
    return expression


def test_ast_depth_twenty_is_valid_and_twenty_one_is_invalid() -> None:
    valid = check_transfer(make_payload(claim=_not_chain(20)))
    assert valid["verdict"] in {"counterexample", "no_counterexample_in_instance"}
    assert error_code(make_payload(claim=_not_chain(21))) == "ast_depth_limit"


def test_ast_node_cap_is_total_across_assumptions_and_claim() -> None:
    assumptions = [assumption(f"a-{index}", b(True)) for index in range(300)]
    assert error_code(make_payload(assumptions=assumptions, claim=b(True))) == "ast_node_limit"


def test_false_boolean_literal_is_valid() -> None:
    result = check_transfer(make_payload(claim=b(False)))
    assert result["verdict"] == "counterexample"


def test_unknown_quantity_is_runtime_abstention() -> None:
    result = check_transfer(make_payload(claim=qty("not_in_vocabulary")))
    assert result["verdict"] == "abstain"
    assert result["errors"][0]["code"] == "unknown_quantity"


def test_pathologically_large_rational_token_is_rejected_structurally() -> None:
    result = check_transfer(make_payload(claim={"kind": "rational", "value": "1" * 5000}))
    assert result["verdict"] == "invalid_input"
    assert result["errors"][0]["code"] == "rational_too_large"
