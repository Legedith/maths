"""Public composition of the independent exact computations."""

from fractions import Fraction

from .markov import hitting_time
from .resistance import laplacian_matrix, resistance_and_potentials
from .trees import spanning_tree_counts
from .validation import validate_payload


def _rational(value: Fraction) -> str:
    return str(value)


def analyze_graph(payload: object) -> dict[str, object]:
    """Analyze one admitted graph and return a JSON-compatible exact result."""
    n, edges, source, target = validate_payload(payload)
    laplacian = laplacian_matrix(n, edges)
    resistance, potentials = resistance_and_potentials(laplacian, source, target)
    hit_forward = hitting_time(n, edges, source, target)
    hit_backward = hitting_time(n, edges, target, source)
    commute = hit_forward + hit_backward

    selected = (min(source, target), max(source, target))
    existing_edge = selected if selected in edges else None
    tree_count, selected_count = spanning_tree_counts(n, edges, existing_edge)
    edge_probability = (
        Fraction(selected_count, tree_count) if selected_count is not None else None
    )

    checks: dict[str, bool] = {
        "laplacian_row_sums_zero": all(sum(row) == 0 for row in laplacian),
        "commute_equals_2m_resistance": commute == 2 * len(edges) * resistance,
        "spanning_tree_count_positive": tree_count > 0,
    }
    if edge_probability is not None:
        checks["edge_probability_equals_resistance"] = edge_probability == resistance
    if not all(checks.values()):
        raise ArithmeticError("an exact cross-check failed")

    return {
        "n": n,
        "edges": [list(edge) for edge in edges],
        "source": source,
        "target": target,
        "laplacian": laplacian,
        "potentials": [_rational(value) for value in potentials],
        "resistance": _rational(resistance),
        "hit_forward": _rational(hit_forward),
        "hit_backward": _rational(hit_backward),
        "commute": _rational(commute),
        "spanning_tree_count": tree_count,
        "tree_edge_count": selected_count,
        "edge_probability": _rational(edge_probability) if edge_probability is not None else None,
        "checks": checks,
    }

