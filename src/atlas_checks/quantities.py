"""Lazy exact quantities with explicit definitions and undefined states."""

from __future__ import annotations

from dataclasses import dataclass
from fractions import Fraction
from typing import Any

from . import electrical, markov, trees
from .graph_math import (
    combinatorial_laplacian,
    is_connected,
    terminal_edge,
    terminals_connected,
    weighted_degrees,
)
from .linear import determinant, matrix_vector, minor, rank
from .model import Graph, rational_text
from .period import period_with_certificate
from .values import TypedValue, boolean, matrix, rational, vector


QUANTITY_NAMES = {
    "n",
    "edge_count",
    "total_conductance",
    "degrees",
    "laplacian",
    "transition_matrix",
    "laplacian_rw",
    "laplacian_rank",
    "laplacian_determinant",
    "target_cofactor",
    "nonzero_spectrum_product",
    "rw_nonzero_spectrum_product",
    "tree_mass",
    "tree_edge_mass",
    "edge_probability",
    "stationary_measure",
    "stationary_distribution",
    "resistance",
    "hit_forward",
    "hit_backward",
    "commute",
    "potentials",
    "ones",
    "connected",
    "terminals_connected",
    "terminal_is_edge",
    "period",
}


@dataclass(frozen=True, slots=True)
class QuantityResult:
    value: TypedValue | None
    method: str
    definition: str
    error_code: str | None = None
    error: str | None = None

    @property
    def defined(self) -> bool:
        return self.value is not None

    def record(self) -> dict[str, Any]:
        base: dict[str, Any] = {
            "status": "defined" if self.defined else "undefined",
            "method": self.method,
            "definition": self.definition,
        }
        if self.value is not None:
            base.update(self.value.record())
        else:
            base.update(error_code=self.error_code, error=self.error)
        return base


class QuantityStore:
    """Compute named quantities only when referenced, retaining exact provenance."""

    def __init__(self, graph: Graph):
        self.graph = graph
        self._cache: dict[str, QuantityResult] = {}
        self._tree_cache: tuple[Fraction, Fraction | None] | None = None
        self._electrical_cache: tuple[Fraction, dict[int, Fraction]] | None = None
        self._hitting_cache: tuple[Fraction, Fraction] | None = None
        self._period_certificate: dict[str, Any] | None = None

    @staticmethod
    def _defined(value: TypedValue, method: str, definition: str) -> QuantityResult:
        return QuantityResult(value=value, method=method, definition=definition)

    @staticmethod
    def _undefined(code: str, message: str, method: str, definition: str) -> QuantityResult:
        return QuantityResult(
            value=None,
            method=method,
            definition=definition,
            error_code=code,
            error=message,
        )

    def get(self, name: str) -> QuantityResult:
        if name not in QUANTITY_NAMES:
            return self._undefined(
                "unknown_quantity",
                f"unknown quantity {name!r}",
                "none",
                "not part of the frozen quantity vocabulary",
            )
        if name not in self._cache:
            method = getattr(self, f"_quantity_{name}")
            self._cache[name] = method()
        return self._cache[name]

    def accessed_records(self) -> dict[str, Any]:
        return {name: self._cache[name].record() for name in sorted(self._cache)}

    def _laplacian(self):
        return combinatorial_laplacian(self.graph)

    def _trees(self):
        if self._tree_cache is None:
            self._tree_cache = trees.weighted_tree_masses(self.graph)
        return self._tree_cache

    def _electrical(self):
        if self._electrical_cache is None:
            self._electrical_cache = electrical.resistance_and_component_potentials(self.graph)
        return self._electrical_cache

    def _hitting(self):
        if self._hitting_cache is None:
            self._hitting_cache = (
                markov.hitting_time(self.graph, self.graph.source, self.graph.target),
                markov.hitting_time(self.graph, self.graph.target, self.graph.source),
            )
        return self._hitting_cache

    def _quantity_n(self):
        return self._defined(rational(self.graph.n), "input", "number of vertices")

    def _quantity_edge_count(self):
        return self._defined(rational(len(self.graph.edges)), "input", "number of undirected edges")

    def _quantity_total_conductance(self):
        value = sum(weighted_degrees(self.graph), Fraction(0))
        return self._defined(
            rational(value),
            "exact_degree_sum",
            "sum_degrees=2*sum_edge_conductances (graph volume)",
        )

    def _quantity_degrees(self):
        return self._defined(
            vector(weighted_degrees(self.graph)),
            "exact_incidence_sum",
            "weighted degree at each vertex",
        )

    def _quantity_laplacian(self):
        return self._defined(
            matrix(self._laplacian()),
            "exact_combinatorial_construction",
            "L=D-A with conductances in A",
        )

    def _quantity_transition_matrix(self):
        try:
            value = markov.transition_matrix(self.graph)
        except ValueError as exc:
            return self._undefined(
                "isolated_vertex",
                str(exc),
                "independent_markov_construction",
                "row-stochastic P=D^-1 A",
            )
        return self._defined(
            matrix(value),
            "independent_markov_construction",
            "row-stochastic P=D^-1 A; row distributions evolve as mu P",
        )

    def _quantity_laplacian_rw(self):
        try:
            value = markov.random_walk_laplacian(self.graph)
        except ValueError as exc:
            return self._undefined(
                "isolated_vertex",
                str(exc),
                "independent_markov_construction",
                "L_rw=I-P=D^-1 L for row-stochastic P",
            )
        return self._defined(
            matrix(value),
            "independent_markov_construction",
            "L_rw=I-P=D^-1 L for row-stochastic P",
        )

    def _quantity_laplacian_rank(self):
        return self._defined(
            rational(rank(self._laplacian())),
            "exact_gaussian_elimination",
            "rank of the combinatorial Laplacian",
        )

    def _quantity_laplacian_determinant(self):
        return self._defined(
            rational(determinant(self._laplacian())),
            "exact_gaussian_elimination",
            "determinant of the combinatorial Laplacian",
        )

    def _quantity_target_cofactor(self):
        value = determinant(minor(self._laplacian(), self.graph.target, self.graph.target))
        return self._defined(
            rational(value),
            "exact_gaussian_elimination",
            "determinant after deleting the target row and column of L",
        )

    def _quantity_nonzero_spectrum_product(self):
        if not is_connected(self.graph):
            return self._undefined(
                "disconnected_graph",
                "nonzero_spectrum_product is exposed only when L has nullity one",
                "principal_minor_coefficient",
                "sum of all principal (n-1)-minors of L on a connected graph",
            )
        laplacian = self._laplacian()
        value = sum(
            (determinant(minor(laplacian, vertex, vertex)) for vertex in range(self.graph.n)),
            Fraction(0),
        )
        return self._defined(
            rational(value),
            "principal_minor_coefficient",
            "sum of all principal (n-1)-minors of L on a connected graph",
        )

    def _quantity_rw_nonzero_spectrum_product(self):
        if not is_connected(self.graph):
            return self._undefined(
                "disconnected_graph",
                "rw_nonzero_spectrum_product is exposed only on a connected graph",
                "principal_minor_coefficient",
                "sum of principal (n-1)-minors of L_rw on a connected graph",
            )
        random_walk_laplacian = markov.random_walk_laplacian(self.graph)
        value = sum(
            (
                determinant(minor(random_walk_laplacian, vertex, vertex))
                for vertex in range(self.graph.n)
            ),
            Fraction(0),
        )
        return self._defined(
            rational(value),
            "principal_minor_coefficient",
            "sum of principal (n-1)-minors of L_rw on a connected graph",
        )

    def _quantity_tree_mass(self):
        return self._defined(
            rational(self._trees()[0]),
            "independent_exhaustive_tree_enumeration",
            "sum over spanning trees of products of edge conductances; zero if none",
        )

    def _quantity_tree_edge_mass(self):
        if not is_connected(self.graph):
            return self._undefined(
                "disconnected_graph",
                "tree_edge_mass requires a connected graph",
                "independent_exhaustive_tree_enumeration",
                "weighted mass of spanning trees containing the selected terminal edge",
            )
        if terminal_edge(self.graph) is None:
            return self._undefined(
                "terminal_nonedge",
                "tree_edge_mass requires the terminal pair to be an existing edge",
                "independent_exhaustive_tree_enumeration",
                "weighted mass of spanning trees containing the selected terminal edge",
            )
        value = self._trees()[1]
        assert value is not None
        return self._defined(
            rational(value),
            "independent_exhaustive_tree_enumeration",
            "weighted mass of spanning trees containing the selected terminal edge",
        )

    def _quantity_edge_probability(self):
        edge_mass = self._quantity_tree_edge_mass()
        if not edge_mass.defined:
            return self._undefined(
                edge_mass.error_code or "undefined_quantity",
                edge_mass.error or "edge_probability is undefined",
                "independent_exhaustive_tree_enumeration",
                "tree_edge_mass/tree_mass for an existing terminal edge in a connected graph",
            )
        total_mass = self._trees()[0]
        assert edge_mass.value is not None
        return self._defined(
            rational(edge_mass.value.data / total_mass),
            "independent_exhaustive_tree_enumeration",
            "tree_edge_mass/tree_mass for an existing terminal edge in a connected graph",
        )

    def _quantity_stationary_measure(self):
        return self._defined(
            vector(markov.markov_degrees(self.graph)),
            "independent_markov_construction",
            "unnormalized weighted-degree measure",
        )

    def _quantity_stationary_distribution(self):
        try:
            value = markov.canonical_stationary_distribution(self.graph)
        except ValueError as exc:
            return self._undefined(
                "isolated_vertex",
                str(exc),
                "independent_markov_construction",
                "canonical degree-normalized stationary vector; no uniqueness or limit claim",
            )
        return self._defined(
            vector(value),
            "independent_markov_construction",
            "canonical degree-normalized stationary vector; no uniqueness or limit claim",
        )

    def _quantity_resistance(self):
        if not terminals_connected(self.graph):
            return self._undefined(
                "terminals_disconnected",
                "effective resistance is undefined between different components",
                "independent_electrical_solve",
                "unit-current voltage difference with target grounded",
            )
        return self._defined(
            rational(self._electrical()[0]),
            "independent_electrical_solve",
            "unit-current voltage difference with target grounded",
        )

    def _quantity_hit_forward(self):
        if not terminals_connected(self.graph):
            return self._undefined(
                "terminals_disconnected",
                "forward hitting time is undefined because target is unreachable",
                "independent_markov_first_step_system",
                "E_source[tau_target]",
            )
        return self._defined(
            rational(self._hitting()[0]),
            "independent_markov_first_step_system",
            "E_source[tau_target]",
        )

    def _quantity_hit_backward(self):
        if not terminals_connected(self.graph):
            return self._undefined(
                "terminals_disconnected",
                "backward hitting time is undefined because source is unreachable from target",
                "independent_markov_first_step_system",
                "E_target[tau_source]",
            )
        return self._defined(
            rational(self._hitting()[1]),
            "independent_markov_first_step_system",
            "E_target[tau_source]",
        )

    def _quantity_commute(self):
        if not terminals_connected(self.graph):
            return self._undefined(
                "terminals_disconnected",
                "commute time is undefined between different components",
                "sum_of_independent_hitting_solves",
                "E_source[tau_target]+E_target[tau_source]",
            )
        forward, backward = self._hitting()
        return self._defined(
            rational(forward + backward),
            "sum_of_independent_hitting_solves",
            "E_source[tau_target]+E_target[tau_source]",
        )

    def _quantity_potentials(self):
        if not is_connected(self.graph):
            return self._undefined(
                "disconnected_graph",
                "global potentials require a connected graph",
                "independent_electrical_solve",
                "Lv=e_source-e_target with v_target=0",
            )
        return self._defined(
            vector(electrical.global_grounded_potentials(self.graph)),
            "independent_electrical_solve",
            "Lv=e_source-e_target with v_target=0",
        )

    def _quantity_ones(self):
        return self._defined(
            vector([Fraction(1) for _ in range(self.graph.n)]),
            "exact_construction",
            "all-ones vector used for the Laplacian nullspace witness",
        )

    def _quantity_connected(self):
        return self._defined(boolean(is_connected(self.graph)), "graph_search", "all vertices form one component")

    def _quantity_terminals_connected(self):
        return self._defined(
            boolean(terminals_connected(self.graph)),
            "graph_search",
            "source and target lie in the same component",
        )

    def _quantity_terminal_is_edge(self):
        return self._defined(
            boolean(terminal_edge(self.graph) is not None),
            "edge_lookup",
            "the unordered source-target pair is an existing edge",
        )

    def _quantity_period(self):
        if not is_connected(self.graph):
            return self._undefined(
                "disconnected_graph",
                "period is exposed only for a connected graph",
                "constructive_graph_certificate",
                "period 2 by bipartition parity or period 1 by an explicit odd cycle",
            )
        value, certificate = period_with_certificate(self.graph)
        self._period_certificate = certificate
        return self._defined(
            rational(value),
            "constructive_graph_certificate",
            "period 2 by bipartition parity or period 1 by an explicit odd cycle",
        )

    def certificates(self) -> dict[str, Any]:
        gauge_names = {"ones", "laplacian", "laplacian_rank", "laplacian_determinant", "potentials"}
        if gauge_names.intersection(self._cache):
            laplacian = self._laplacian()
            ones = [Fraction(1) for _ in range(self.graph.n)]
            zeros = matrix_vector(laplacian, ones)
            laplacian_rank = rank(laplacian)
            gauge: dict[str, Any] = {
                "status": "defined",
                "kind": "laplacian_nullspace",
                "ones": ["1" for _ in range(self.graph.n)],
                "laplacian_times_ones": [rational_text(value) for value in zeros],
                "rank": laplacian_rank,
                "nullity": self.graph.n - laplacian_rank,
            }
            potentials_record = self._cache.get("potentials")
            if potentials_record is not None and potentials_record.defined:
                potentials = electrical.global_grounded_potentials(self.graph)
                shifted = [value + 1 for value in potentials]
                current = [
                    Fraction(1)
                    if vertex == self.graph.source
                    else Fraction(-1)
                    if vertex == self.graph.target
                    else Fraction(0)
                    for vertex in range(self.graph.n)
                ]
                original_current = matrix_vector(laplacian, potentials)
                shifted_current = matrix_vector(laplacian, shifted)
                gauge.update(
                    grounded_target=self.graph.target,
                    potentials=[rational_text(value) for value in potentials],
                    shifted_by_ones=[rational_text(value) for value in shifted],
                    required_current=[rational_text(value) for value in current],
                    original_current=[rational_text(value) for value in original_current],
                    shifted_current=[rational_text(value) for value in shifted_current],
                    shift_preserves_equation=original_current == current and shifted_current == current,
                )
        else:
            gauge = {"status": "not_evaluated", "reason": "no gauge-related quantity was referenced"}

        if "period" not in self._cache:
            period_certificate: dict[str, Any] = {
                "status": "not_evaluated",
                "reason": "period was not referenced",
            }
        elif self._cache["period"].defined:
            if self._period_certificate is None:
                _, self._period_certificate = period_with_certificate(self.graph)
            period_certificate = {"status": "defined", **self._period_certificate}
        else:
            period_certificate = {
                "status": "undefined",
                "error_code": self._cache["period"].error_code,
                "error": self._cache["period"].error,
            }
        return {"gauge": gauge, "period": period_certificate}
