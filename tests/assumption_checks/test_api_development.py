from __future__ import annotations

from atlas_checks import ALGORITHM_VERSION, check_transfer
from atlas_checks.quantities import QUANTITY_NAMES

from .helpers import assumption, b, binary, entry, make_payload, q, qty, unary


def test_weighted_commute_counterexample_has_exact_trace() -> None:
    payload = make_payload(
        edges=[
            {"u": 0, "v": 1, "conductance": 2},
            {"u": 1, "v": 2, "conductance": 1},
        ],
        source=0,
        target=2,
        assumptions=[assumption("connected-domain", qty("connected"))],
        claim=binary(
            "eq",
            qty("commute"),
            binary("mul", binary("mul", q(2), qty("edge_count")), qty("resistance")),
        ),
    )
    result = check_transfer(payload)
    assert result["verdict"] == "counterexample"
    assert result["algorithm_version"] == ALGORITHM_VERSION
    assert result["quantities"]["commute"]["value"] == "9"
    assert result["quantities"]["resistance"]["value"] == "3/2"
    assert result["claim_evaluation"]["value"] is False
    assert result["claim_evaluation"]["trace"]["left"]["value"] == "9"


def test_weighted_commute_uses_graph_volume_and_direction() -> None:
    payload = make_payload(
        edges=[
            {"u": 0, "v": 1, "conductance": "2"},
            {"u": 1, "v": 2, "conductance": "1"},
        ],
        source=0,
        target=2,
        claim=binary(
            "and",
            binary(
                "eq",
                qty("commute"),
                binary("mul", qty("total_conductance"), qty("resistance")),
            ),
            binary("ne", qty("hit_forward"), qty("hit_backward")),
        ),
    )
    result = check_transfer(payload)
    assert result["verdict"] == "no_counterexample_in_instance"
    assert result["quantities"]["total_conductance"]["value"] == "6"
    assert result["quantities"]["total_conductance"]["definition"] == (
        "sum_degrees=2*sum_edge_conductances (graph volume)"
    )
    assert result["quantities"]["hit_forward"]["value"] == "6"
    assert result["quantities"]["hit_backward"]["value"] == "3"
    assert "instance_scope_warning" in result


def test_weighted_tree_mass_and_edge_probability_are_independent_exact_values() -> None:
    payload = make_payload(
        edges=[
            {"u": 0, "v": 1, "conductance": 2},
            {"u": 0, "v": 2, "conductance": 1},
            {"u": 1, "v": 2, "conductance": 1},
        ],
        claim=binary(
            "and",
            binary("eq", qty("target_cofactor"), qty("tree_mass")),
            binary(
                "eq",
                qty("edge_probability"),
                binary("mul", q(2), qty("resistance")),
            ),
        ),
    )
    result = check_transfer(payload)
    assert result["verdict"] == "no_counterexample_in_instance"
    assert result["quantities"]["tree_mass"]["value"] == "5"
    assert result["quantities"]["edge_probability"]["value"] == "4/5"
    assert result["quantities"]["resistance"]["value"] == "2/5"
    assert result["quantities"]["tree_mass"]["method"] == "independent_exhaustive_tree_enumeration"
    assert result["quantities"]["resistance"]["method"] == "independent_electrical_solve"


def test_row_transition_and_random_walk_laplacian_convention() -> None:
    payload = make_payload(
        edges=[
            {"u": 0, "v": 1, "conductance": 2},
            {"u": 1, "v": 2, "conductance": 1},
        ],
        source=0,
        target=2,
        claim=binary(
            "and",
            binary("eq", entry(qty("transition_matrix"), 1, 0), q("2/3")),
            binary("eq", entry(qty("laplacian_rw"), 1, 2), q("-1/3")),
        ),
    )
    result = check_transfer(payload)
    assert result["verdict"] == "no_counterexample_in_instance"
    assert result["quantities"]["transition_matrix"]["value"] == [
        ["0", "1", "0"],
        ["2/3", "0", "1/3"],
        ["0", "1", "0"],
    ]
    assert result["quantities"]["laplacian_rw"]["value"] == [
        ["1", "-1", "0"],
        ["-2/3", "1", "-1/3"],
        ["0", "-1", "1"],
    ]


def test_spectrum_products_are_coefficients_only_in_connected_case() -> None:
    payload = make_payload(
        source=0,
        target=2,
        claim=binary(
            "and",
            binary("eq", qty("nonzero_spectrum_product"), binary("mul", qty("n"), qty("tree_mass"))),
            binary("eq", qty("rw_nonzero_spectrum_product"), q(2)),
        ),
    )
    result = check_transfer(payload)
    assert result["verdict"] == "no_counterexample_in_instance"
    assert result["quantities"]["nonzero_spectrum_product"]["value"] == "3"
    assert result["quantities"]["rw_nonzero_spectrum_product"]["value"] == "2"


def test_disconnected_same_component_keeps_local_resistance_and_hitting_defined() -> None:
    edges = [
        {"u": 0, "v": 1, "conductance": 2},
        {"u": 2, "v": 3, "conductance": 1},
    ]
    payload = make_payload(
        n=4,
        edges=edges,
        source=0,
        target=1,
        claim=binary(
            "and",
            binary("eq", qty("resistance"), q("1/2")),
            binary("eq", qty("hit_forward"), q(1)),
        ),
    )
    result = check_transfer(payload)
    assert result["verdict"] == "no_counterexample_in_instance"

    stationary = check_transfer(
        make_payload(
            n=4,
            edges=edges,
            source=0,
            target=1,
            claim=binary("eq", unary("sum", qty("stationary_distribution")), q(1)),
        )
    )
    assert stationary["verdict"] == "no_counterexample_in_instance"
    assert stationary["quantities"]["stationary_distribution"]["value"] == [
        "1/3",
        "1/3",
        "1/6",
        "1/6",
    ]


def test_global_potentials_are_undefined_on_disconnected_graph() -> None:
    result = check_transfer(
        make_payload(
            n=4,
            edges=[
                {"u": 0, "v": 1, "conductance": 1},
                {"u": 2, "v": 3, "conductance": 1},
            ],
            source=0,
            target=1,
            claim=binary("eq", qty("potentials"), qty("ones")),
        )
    )
    assert result["verdict"] == "abstain"
    assert result["quantities"]["potentials"]["status"] == "undefined"
    assert result["quantities"]["potentials"]["error_code"] == "disconnected_graph"


def test_tree_mass_is_zero_but_edge_probability_is_undefined_when_disconnected() -> None:
    edges = [{"u": 0, "v": 1, "conductance": 1}]
    mass = check_transfer(
        make_payload(n=3, edges=edges, claim=binary("eq", qty("tree_mass"), q(0)))
    )
    assert mass["verdict"] == "no_counterexample_in_instance"
    probability = check_transfer(
        make_payload(n=3, edges=edges, claim=binary("eq", qty("edge_probability"), q(0)))
    )
    assert probability["verdict"] == "abstain"
    assert probability["quantities"]["edge_probability"]["error_code"] == "disconnected_graph"


def test_connected_terminal_nonedge_probability_is_undefined() -> None:
    result = check_transfer(
        make_payload(
            source=0,
            target=2,
            claim=binary("eq", qty("edge_probability"), q(0)),
        )
    )
    assert result["verdict"] == "abstain"
    assert result["quantities"]["edge_probability"]["error_code"] == "terminal_nonedge"


def test_false_assumption_precedes_other_undefined_assumption() -> None:
    result = check_transfer(
        make_payload(
            n=3,
            edges=[{"u": 0, "v": 1, "conductance": 1}],
            source=0,
            target=2,
            assumptions=[
                assumption("connected", qty("connected")),
                assumption("unavailable", qty("does_not_exist")),
            ],
            claim=b(True),
        )
    )
    assert result["verdict"] == "not_applicable"
    assert [row["status"] for row in result["evaluated_assumptions"]] == ["false", "abstain"]
    assert result["claim_evaluation"]["status"] == "not_evaluated"


def test_ambiguous_interpretation_abstains_without_computation() -> None:
    result = check_transfer(
        make_payload(
            interpretation="ambiguous",
            assumptions=[assumption("connected", qty("connected"))],
            claim=binary("eq", qty("tree_mass"), q(1)),
        )
    )
    assert result["verdict"] == "abstain"
    assert result["quantities"] == {}
    assert result["evaluated_assumptions"][0]["status"] == "not_evaluated"


def test_strict_boolean_operation_propagates_undefined() -> None:
    result = check_transfer(
        make_payload(claim=binary("and", b(False), qty("unknown_quantity_name")))
    )
    assert result["verdict"] == "abstain"
    trace = result["claim_evaluation"]["trace"]
    assert trace["left"]["value"] is False
    assert trace["right"]["status"] == "abstain"


def test_runtime_failures_abstain_instead_of_fabricating_values() -> None:
    cases = [
        (binary("div", q(1), q(0)), "division_by_zero"),
        (entry(qty("degrees"), 99), "index_out_of_range"),
        (binary("add", b(True), q(1)), "operand_type_error"),
        (q(1), "nonboolean_result"),
    ]
    for claim, code in cases:
        result = check_transfer(make_payload(claim=claim, check_id=f"runtime-{code}"))
        assert result["verdict"] == "abstain"
        assert code in {error["code"] for error in result["errors"]}


def test_period_certificates_are_constructive() -> None:
    cycle = check_transfer(
        make_payload(
            n=4,
            edges=[
                {"u": 0, "v": 1, "conductance": 1},
                {"u": 1, "v": 2, "conductance": 1},
                {"u": 2, "v": 3, "conductance": 1},
                {"u": 3, "v": 0, "conductance": 1},
            ],
            source=0,
            target=2,
            claim=binary("eq", qty("period"), q(2)),
        )
    )
    assert cycle["verdict"] == "no_counterexample_in_instance"
    assert cycle["certificates"]["period"]["kind"] == "bipartition_parity"
    assert all(row["crosses_partition"] for row in cycle["certificates"]["period"]["edge_checks"])

    triangle = check_transfer(
        make_payload(
            edges=[
                {"u": 0, "v": 1, "conductance": 1},
                {"u": 0, "v": 2, "conductance": 1},
                {"u": 1, "v": 2, "conductance": 1},
            ],
            claim=binary("eq", qty("period"), q(1)),
        )
    )
    assert triangle["verdict"] == "no_counterexample_in_instance"
    assert triangle["certificates"]["period"]["kind"] == "odd_cycle"
    assert triangle["certificates"]["period"]["odd_length"] == 3
    assert triangle["certificates"]["period"]["cycle"][0] == triangle["certificates"]["period"]["cycle"][-1]

    triangle_with_tail = check_transfer(
        make_payload(
            n=4,
            edges=[
                {"u": 0, "v": 1, "conductance": 1},
                {"u": 0, "v": 2, "conductance": 1},
                {"u": 1, "v": 2, "conductance": 1},
                {"u": 1, "v": 3, "conductance": 1},
            ],
            claim=binary("eq", qty("period"), q(1)),
        )
    )
    assert triangle_with_tail["verdict"] == "no_counterexample_in_instance"
    assert triangle_with_tail["certificates"]["period"]["odd_length"] == 3


def test_gauge_certificate_checks_constant_shift() -> None:
    result = check_transfer(
        make_payload(
            edges=[
                {"u": 0, "v": 1, "conductance": 1},
                {"u": 0, "v": 2, "conductance": 1},
                {"u": 1, "v": 2, "conductance": 1},
            ],
            claim=binary("eq", entry(qty("potentials"), 1), q(0)),
        )
    )
    assert result["verdict"] == "no_counterexample_in_instance"
    certificate = result["certificates"]["gauge"]
    assert certificate["laplacian_times_ones"] == ["0", "0", "0"]
    assert certificate["rank"] == 2
    assert certificate["nullity"] == 1
    assert certificate["shift_preserves_equation"] is True


def test_normalization_sorts_edges_and_reduces_rationals() -> None:
    result = check_transfer(
        make_payload(
            edges=[
                {"u": 2, "v": 1, "conductance": " 006/008 "},
                {"u": 1, "v": 0, "conductance": "+2/4"},
            ],
            claim=b(True),
        )
    )
    assert result["verdict"] == "no_counterexample_in_instance"
    assert result["normalized_input"]["graph"]["edges"] == [
        {"u": 0, "v": 1, "conductance": "1/2"},
        {"u": 1, "v": 2, "conductance": "3/4"},
    ]
    assert len(result["normalized_input_sha256"]) == 64


def test_expression_language_operations_and_shape_equality() -> None:
    true_claims = [
        binary("eq", binary("add", q("1/3"), q("2/3")), q(1)),
        binary("eq", binary("sub", q(1), q("1/3")), q("2/3")),
        binary("eq", binary("mul", q("2/3"), q("3/4")), q("1/2")),
        binary("eq", binary("div", q("2/3"), q("4/5")), q("5/6")),
        binary("eq", unary("neg", q("-2/3")), q("2/3")),
        binary("lt", q("1/3"), q("1/2")),
        binary("le", q("1/2"), q("1/2")),
        binary("or", b(False), unary("not", b(False))),
        binary("eq", unary("sum", qty("degrees")), qty("total_conductance")),
        binary("eq", unary("product", qty("ones")), q(1)),
        binary("eq", qty("laplacian"), qty("laplacian")),
        binary("eq", qty("stationary_measure"), qty("degrees")),
        binary("eq", entry(qty("laplacian"), 0, 0), q(1)),
    ]
    for index, claim in enumerate(true_claims):
        result = check_transfer(make_payload(claim=claim, check_id=f"expression-{index}"))
        assert result["verdict"] == "no_counterexample_in_instance"

    mismatch = check_transfer(
        make_payload(claim=binary("eq", qty("degrees"), qty("laplacian")))
    )
    assert mismatch["verdict"] == "abstain"
    assert mismatch["errors"][0]["code"] == "operand_type_error"


def test_provenance_strings_are_preserved_and_not_verified() -> None:
    payload = make_payload()
    payload["provenance"]["kind"] = "source_annotation"
    payload["provenance"]["source_locator"] = "  theorem 3, supplied spacing  "
    result = check_transfer(payload)
    assert result["verdict"] == "no_counterexample_in_instance"
    assert result["provenance"]["source_locator"] == "  theorem 3, supplied spacing  "


def test_six_vertex_rational_weight_case_is_exact() -> None:
    result = check_transfer(
        make_payload(
            n=6,
            edges=[
                {"u": 0, "v": 1, "conductance": "1/2"},
                {"u": 1, "v": 2, "conductance": "2/3"},
                {"u": 2, "v": 3, "conductance": "3/4"},
                {"u": 3, "v": 4, "conductance": "4/5"},
                {"u": 4, "v": 5, "conductance": "5/6"},
                {"u": 5, "v": 0, "conductance": "6/7"},
            ],
            source=0,
            target=1,
            claim=binary(
                "and",
                binary("eq", qty("target_cofactor"), qty("tree_mass")),
                binary(
                    "eq",
                    qty("commute"),
                    binary("mul", qty("total_conductance"), qty("resistance")),
                ),
            ),
        )
    )
    assert result["verdict"] == "no_counterexample_in_instance"
    assert "/" in result["quantities"]["tree_mass"]["value"]


def test_every_frozen_quantity_name_is_exposed_on_an_applicable_graph() -> None:
    edges = [
        {"u": 0, "v": 1, "conductance": "2/3"},
        {"u": 0, "v": 2, "conductance": "3/5"},
        {"u": 1, "v": 2, "conductance": "5/7"},
    ]
    for name in sorted(QUANTITY_NAMES):
        result = check_transfer(
            make_payload(
                edges=edges,
                claim=binary("eq", qty(name), qty(name)),
                check_id=f"quantity-{name}",
            )
        )
        assert result["verdict"] == "no_counterexample_in_instance", (name, result)
        assert result["quantities"][name]["status"] == "defined"
