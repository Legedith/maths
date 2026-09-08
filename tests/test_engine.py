import json
from fractions import Fraction
from pathlib import Path

import pytest

from atlas_engine import InputValidationError, analyze_graph
from atlas_engine.linear import solve_linear


FIXTURES = json.loads(
    (Path(__file__).parents[1] / "fixtures" / "frozen.json").read_text(encoding="utf-8")
)


@pytest.mark.parametrize("fixture", FIXTURES["valid"], ids=lambda item: item["id"])
def test_frozen_valid_fixtures(fixture):
    result = analyze_graph(fixture["input"])
    for key, expected in fixture["expected"].items():
        assert result[key] == expected
    assert all(result["checks"].values())


@pytest.mark.parametrize("fixture", FIXTURES["invalid"], ids=lambda item: item["id"])
def test_frozen_invalid_fixtures(fixture):
    with pytest.raises(InputValidationError):
        analyze_graph(fixture["input"])


def test_nonedge_is_explicitly_not_applicable():
    result = analyze_graph(
        {"n": 3, "edges": [[0, 1], [1, 2]], "source": 0, "target": 2}
    )
    assert result["resistance"] == "2"
    assert result["tree_edge_count"] is None
    assert result["edge_probability"] is None
    assert "edge_probability_equals_resistance" not in result["checks"]


def test_output_is_canonical_and_json_compatible():
    result = analyze_graph(
        {"n": 3, "edges": [[2, 0], [1, 0], [2, 1]], "source": 1, "target": 0}
    )
    assert result["edges"] == [[0, 1], [0, 2], [1, 2]]
    assert result["potentials"] == ["0", "2/3", "1/3"]
    assert result["hit_forward"] == "2"
    assert result["hit_backward"] == "2"
    assert result["commute"] == "4"
    assert result["tree_edge_count"] == 2
    json.dumps(result)


@pytest.mark.parametrize(
    "payload",
    [
        None,
        [],
        {"n": 2, "edges": [[0, 1]], "source": 0},
        {"n": True, "edges": [[0, 1]], "source": 0, "target": 1},
        {"n": 2.0, "edges": [[0, 1]], "source": 0, "target": 1},
        {"n": 2, "edges": ((0, 1),), "source": 0, "target": 1},
        {"n": 2, "edges": [[0, 1]], "source": False, "target": 1},
        {"n": 2, "edges": [[0, 1]], "source": 0, "target": 1, "x": 1},
        {"n": 3, "edges": [[0, 3], [0, 1]], "source": 0, "target": 1},
    ],
)
def test_additional_strict_boundaries(payload):
    with pytest.raises(InputValidationError):
        analyze_graph(payload)


def test_exact_solver_pivots_and_rejects_singular_system():
    assert solve_linear(
        [[Fraction(0), Fraction(1)], [Fraction(2), Fraction(3)]],
        [Fraction(4), Fraction(5)],
    ) == [Fraction(-7, 2), Fraction(4)]
    with pytest.raises(ValueError, match="singular"):
        solve_linear(
            [[Fraction(1), Fraction(2)], [Fraction(2), Fraction(4)]],
            [Fraction(3), Fraction(6)],
        )
