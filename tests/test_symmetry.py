import json
from fractions import Fraction
from math import factorial
from pathlib import Path

import pytest

import atlas_engine.symmetry as symmetry_module
from atlas_engine import InputValidationError, SymmetryBatchAnalyzer, analyze_graph
from atlas_engine.symmetry import _canonicalize_validated
from atlas_engine.validation import validate_payload


FIXTURE_PATH = (
    Path(__file__).resolve().parents[1] / "fixtures" / "frozen.json"
)
FIXTURES = json.loads(FIXTURE_PATH.read_text(encoding="utf-8"))


@pytest.mark.parametrize("fixture", FIXTURES["valid"], ids=lambda item: item["id"])
def test_all_public_fields_match_direct_analyzer_for_frozen_valid_fixture(fixture):
    analyzer = SymmetryBatchAnalyzer()
    optimized = analyzer.analyze(fixture["input"])
    direct = analyze_graph(fixture["input"])
    assert optimized == direct
    for key, expected in fixture["expected"].items():
        assert optimized[key] == expected


@pytest.mark.parametrize("fixture", FIXTURES["invalid"], ids=lambda item: item["id"])
def test_frozen_invalid_fixture_is_rejected_before_cache_lookup(fixture):
    analyzer = SymmetryBatchAnalyzer()
    analyzer.analyze(
        {"n": 2, "edges": [[0, 1]], "source": 0, "target": 1}
    )
    before = analyzer.diagnostics()
    with pytest.raises(InputValidationError) as direct_error:
        analyze_graph(fixture["input"])
    with pytest.raises(InputValidationError) as optimized_error:
        analyzer.analyze(fixture["input"])
    assert str(optimized_error.value) == str(direct_error.value)
    assert analyzer.diagnostics() == before


def test_reversed_terminals_swap_hitting_times_and_apply_r_minus_potential():
    edges = [[0, 1], [1, 2]]
    analyzer = SymmetryBatchAnalyzer()
    forward = analyzer.analyze(
        {"n": 3, "edges": edges, "source": 0, "target": 1}
    )
    backward = analyzer.analyze(
        {"n": 3, "edges": edges, "source": 1, "target": 0}
    )
    assert forward == analyze_graph(
        {"n": 3, "edges": edges, "source": 0, "target": 1}
    )
    assert backward == analyze_graph(
        {"n": 3, "edges": edges, "source": 1, "target": 0}
    )
    assert forward["hit_forward"] != forward["hit_backward"]
    assert backward["hit_forward"] == forward["hit_backward"]
    assert backward["hit_backward"] == forward["hit_forward"]
    resistance = Fraction(forward["resistance"])
    assert all(
        Fraction(forward_value) + Fraction(backward_value) == resistance
        for forward_value, backward_value in zip(
            forward["potentials"], backward["potentials"], strict=True
        )
    )
    assert analyzer.diagnostics()["hits"] == 1


def test_isomorphic_relabelling_reuses_one_key_and_restores_caller_labels():
    first = {
        "n": 5,
        "edges": [[0, 1], [1, 2], [2, 3], [3, 4], [1, 4]],
        "source": 0,
        "target": 3,
    }
    old_to_new = {0: 4, 1: 2, 2: 0, 3: 1, 4: 3}
    second = {
        "n": 5,
        "edges": [
            [old_to_new[right], old_to_new[left]]
            for left, right in reversed(first["edges"])
        ],
        "source": old_to_new[first["source"]],
        "target": old_to_new[first["target"]],
    }
    analyzer = SymmetryBatchAnalyzer()
    assert analyzer.analyze(first) == analyze_graph(first)
    assert analyzer.analyze(second) == analyze_graph(second)
    assert analyzer.diagnostics() == {
        "capacity": 256,
        "size": 1,
        "hits": 1,
        "misses": 1,
        "core_calls": 1,
        "evictions": 0,
    }


def test_nonedge_nullability_and_checks_match_exactly():
    payload = {
        "n": 4,
        "edges": [[0, 1], [1, 2], [2, 3]],
        "source": 0,
        "target": 3,
    }
    result = SymmetryBatchAnalyzer().analyze(payload)
    assert result == analyze_graph(payload)
    assert result["tree_edge_count"] is None
    assert result["edge_probability"] is None
    assert "edge_probability_equals_resistance" not in result["checks"]


def test_returned_nested_mutation_cannot_reach_cached_result():
    payload = {
        "n": 4,
        "edges": [[0, 1], [1, 2], [2, 3], [0, 3]],
        "source": 0,
        "target": 2,
    }
    expected = analyze_graph(payload)
    analyzer = SymmetryBatchAnalyzer()
    exposed = analyzer.analyze(payload)
    exposed["edges"][0][0] = 99
    exposed["laplacian"][0][0] = 99
    exposed["potentials"][0] = "999"
    exposed["checks"]["laplacian_row_sums_zero"] = False
    assert analyzer.analyze(payload) == expected
    assert analyzer.diagnostics()["hits"] == 1


def test_reversed_edge_endpoints_and_input_order_are_one_cache_entry():
    canonical_input = {
        "n": 4,
        "edges": [[0, 1], [0, 3], [1, 2], [2, 3]],
        "source": 0,
        "target": 1,
    }
    scrambled_input = {
        "n": 4,
        "edges": [[3, 2], [2, 1], [3, 0], [1, 0]],
        "source": 0,
        "target": 1,
    }
    analyzer = SymmetryBatchAnalyzer()
    assert analyzer.analyze(scrambled_input) == analyze_graph(scrambled_input)
    assert analyzer.analyze(canonical_input) == analyze_graph(canonical_input)
    assert analyzer.diagnostics()["size"] == 1
    assert analyzer.diagnostics()["hits"] == 1


def test_automorphism_ties_enumerate_full_contract_and_are_output_safe():
    payload = {
        "n": 4,
        "edges": [[0, 1], [0, 2], [0, 3], [1, 2], [1, 3], [2, 3]],
        "source": 0,
        "target": 1,
    }
    n, edges, source, target = validate_payload(payload)
    form = _canonicalize_validated(n, edges, source, target)
    assert form.candidate_count == 2 * factorial(n - 2)
    assert form.tie_count == form.candidate_count
    assert SymmetryBatchAnalyzer().analyze(payload) == analyze_graph(payload)


def test_lru_eviction_clear_and_instance_isolation_have_explicit_diagnostics():
    one = {"n": 2, "edges": [[0, 1]], "source": 0, "target": 1}
    two = {"n": 3, "edges": [[0, 1], [1, 2]], "source": 0, "target": 1}
    three = {
        "n": 3,
        "edges": [[0, 1], [0, 2], [1, 2]],
        "source": 0,
        "target": 1,
    }
    left = SymmetryBatchAnalyzer(capacity=2)
    right = SymmetryBatchAnalyzer(capacity=2)
    left.analyze(one)
    left.analyze(two)
    left.analyze(one)  # one becomes most recently used
    left.analyze(three)  # evicts two
    left.analyze(two)  # misses and evicts one
    assert left.diagnostics() == {
        "capacity": 2,
        "size": 2,
        "hits": 1,
        "misses": 4,
        "core_calls": 4,
        "evictions": 2,
    }
    assert right.diagnostics() == {
        "capacity": 2,
        "size": 0,
        "hits": 0,
        "misses": 0,
        "core_calls": 0,
        "evictions": 0,
    }
    right.analyze(one)
    assert left.diagnostics()["core_calls"] == 4
    assert right.diagnostics()["core_calls"] == 1
    left.clear()
    assert left.diagnostics() == {
        "capacity": 2,
        "size": 0,
        "hits": 0,
        "misses": 0,
        "core_calls": 0,
        "evictions": 0,
    }


@pytest.mark.parametrize("capacity", [0, -1, True, 1.5, "2", None])
def test_cache_capacity_must_be_a_positive_nonboolean_integer(capacity):
    with pytest.raises(ValueError, match="positive integer"):
        SymmetryBatchAnalyzer(capacity=capacity)


def test_core_exception_is_counted_but_never_inserted(monkeypatch):
    payload = {"n": 2, "edges": [[0, 1]], "source": 0, "target": 1}
    analyzer = SymmetryBatchAnalyzer()
    original = symmetry_module.analyze_graph

    def fail_once(_payload):
        raise RuntimeError("synthetic core failure")

    monkeypatch.setattr(symmetry_module, "analyze_graph", fail_once)
    with pytest.raises(RuntimeError, match="synthetic core failure"):
        analyzer.analyze(payload)
    assert analyzer.diagnostics() == {
        "capacity": 256,
        "size": 0,
        "hits": 0,
        "misses": 1,
        "core_calls": 1,
        "evictions": 0,
    }

    monkeypatch.setattr(symmetry_module, "analyze_graph", original)
    assert analyzer.analyze(payload) == original(payload)
    assert analyzer.diagnostics()["size"] == 1
    assert analyzer.diagnostics()["misses"] == 2
    assert analyzer.diagnostics()["core_calls"] == 2
