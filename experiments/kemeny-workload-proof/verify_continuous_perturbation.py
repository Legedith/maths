from __future__ import annotations

import argparse
import hashlib
import json
import platform
from fractions import Fraction as F
from itertools import combinations, product
from pathlib import Path

STAGE = Path(__file__).resolve().parent
GRAPHS = ((3, 3, 3), (3, 3, 4), (3, 4, 5), (4, 4, 6))
THETAS = (F(0), F(1, 10), F(1, 2))
LEFT, RIGHT = F(-1, 10), F(1, 10)


def inverse(a):
    n = len(a)
    rows = [list(a[i]) + [F(i == j) for j in range(n)] for i in range(n)]
    for j in range(n):
        pivot = next(i for i in range(j, n) if rows[i][j])
        rows[j], rows[pivot] = rows[pivot], rows[j]
        scale = rows[j][j]
        rows[j] = [v / scale for v in rows[j]]
        for i in range(n):
            if i != j and rows[i][j]:
                scale = rows[i][j]
                rows[i] = [x - scale * y for x, y in zip(rows[i], rows[j])]
    return [row[n:] for row in rows]


def dot(v, w):
    return sum((x * y for x, y in zip(v, w)), F(0))


def contrast_action(matrix, edge):
    i, j = edge
    return [row[i] - row[j] for row in matrix]


def perturb_stats(matrix, edge, theta):
    z = contrast_action(matrix, edge)
    r = z[edge[0]] - z[edge[1]]
    s = dot(z, z) + len(matrix) * theta * z[-1] ** 2
    assert 0 < r <= 1  # The existing edge still has unit conductance here.
    assert s > 0
    return r, s


def scaled_trace(matrix, theta):
    return sum((matrix[i][i] for i in range(len(matrix))), F(0)) + len(matrix) * theta * matrix[-1][-1]


def minimum_quadratic(coefficients):
    a, b, c = coefficients
    arguments = [LEFT, RIGHT]
    if c > 0 and LEFT < -b / (2 * c) < RIGHT:
        arguments.append(-b / (2 * c))
    values = [(a + b * x + c * x * x, x) for x in arguments]
    value, argument = min(values)
    return value, argument, arguments


def graph_data(parts):
    a, b, c = parts
    n = a + b + c + 1
    groups = [0] * a + [1] * b + [2] * c + [3]
    h = n - 1
    edges = [ij for ij in combinations(range(n), 2) if groups[ij[0]] != groups[ij[1]] and ij != (0, h)]
    edge_set = set(edges)
    missing = [ij for ij in combinations(range(n), 2) if ij not in edge_set]
    lap = [[F(0) for _ in range(n)] for _ in range(n)]
    for i, j in edges:
        lap[i][i] += 1
        lap[j][j] += 1
        lap[i][j] -= 1
        lap[j][i] -= 1
    grounded = inverse([row[:-1] for row in lap[:-1]])
    extended = [row + [F(0)] for row in grounded] + [[F(0)] * n]
    means = [sum(row, F(0)) / n for row in extended]
    grand = sum(means, F(0)) / n
    matrix = [[extended[i][j] - means[i] - means[j] + grand for j in range(n)] for i in range(n)]
    assert all(sum(row, F(0)) == 0 for row in matrix)
    assert all(sum((lap[i][k] * matrix[k][j] for k in range(n)), F(0)) == F(i == j) - F(1, n) for i in range(n) for j in range(n))
    candidates = {}
    for edge in missing:
        z = contrast_action(matrix, edge)
        r = z[edge[0]] - z[edge[1]]
        candidates[edge] = [[matrix[i][j] - z[i] * z[j] / (1 + r) for j in range(n)] for i in range(n)]
    representatives = {
        'u-B': (0, a), 'u-C': (0, a + b),
        'Aother-B': (1, a), 'Aother-C': (1, a + b),
        'B-C': (a, a + b), 'h-Aother': (1, h),
        'h-B': (a, h), 'h-C': (a + b, h),
    }
    assert all(edge in edge_set for edge in representatives.values())
    return n, len(edges), missing, candidates, representatives


def serial(value):
    if isinstance(value, F):
        return str(value)
    if isinstance(value, dict):
        return {str(key): serial(v) for key, v in value.items()}
    if isinstance(value, (tuple, list)):
        return [serial(v) for v in value]
    return value


def main():
    parser = argparse.ArgumentParser(description='Verify the frozen continuous one-edge perturbation certificate.')
    parser.add_argument('--output', type=Path, required=True, help='Fresh JSON output path; existing files are refused.')
    args = parser.parse_args()
    records = []
    comparison_count = 0
    interior_minima = 0
    failing = []
    for parts in GRAPHS:
        n, m, missing, matrices, representatives = graph_data(parts)
        for theta in THETAS:
            nominal = {edge: scaled_trace(matrix, theta) for edge, matrix in matrices.items()}
            optimum = min(nominal.values())
            old_set = [edge for edge in missing if nominal[edge] == optimum]
            outsiders = [edge for edge in missing if edge not in old_set]
            assert old_set and outsiders
            for name, old_edge in representatives.items():
                stats = {edge: perturb_stats(matrix, old_edge, theta) for edge, matrix in matrices.items()}
                comparisons = []
                for incumbent, outsider in product(old_set, outsiders):
                    ti, tj = nominal[incumbent], nominal[outsider]
                    ri, si = stats[incumbent]
                    rj, sj = stats[outsider]
                    difference = tj - ti
                    coefficients = (
                        difference,
                        difference * (rj + ri) - sj + si,
                        difference * rj * ri - sj * ri + si * rj,
                    )
                    minimum, at, checked = minimum_quadratic(coefficients)
                    # Exact residual checks are diagnostics for the derived identity.
                    # The generic cross-product proof is recorded separately.
                    for delta in (LEFT, F(0), RIGHT):
                        assert 1 + delta * ri > 0 and 1 + delta * rj > 0
                        direct = tj - delta * sj / (1 + delta * rj) - ti + delta * si / (1 + delta * ri)
                        polynomial = sum((coefficient * delta ** power for power, coefficient in enumerate(coefficients)), F(0))
                        assert direct * (1 + delta * ri) * (1 + delta * rj) == polynomial
                    entry = {
                        'incumbent': incumbent, 'outsider': outsider,
                        'incumbent_T_r_s': (ti, ri, si),
                        'outsider_T_r_s': (tj, rj, sj),
                        'coefficients': coefficients, 'minimum': minimum,
                        'minimum_at': at, 'checked_arguments': checked,
                        'strictly_positive': minimum > 0,
                    }
                    comparisons.append(entry)
                    comparison_count += 1
                    interior_minima += len(checked) == 3
                    if minimum <= 0:
                        failing.append({'parts': parts, 'theta': theta, 'old_edge': old_edge, **entry})
                records.append({
                    'parts': parts, 'n': n, 'm': m, 'theta': theta,
                    'old_edge_type': name, 'old_edge': old_edge,
                    'all_missing_edges': missing, 'nominal_optimal_set': old_set,
                    'comparisons': comparisons,
                })
    result = {
        'scope': 'Four fixed graphs, three workloads, every existing-edge type individually changed throughout delta in[-1/10,1/10]. Every nominal optimal candidate versus every nominal nonoptimal candidate.',
        'status': 'PASS' if not failing else 'STRONG_SEPARATION_REJECTED',
        'graph_count': len(GRAPHS), 'continuous_contexts': len(records),
        'comparison_count': comparison_count, 'quadratics_with_interior_vertex': interior_minima,
        'interval': (LEFT, RIGHT), 'failing_comparisons': failing,
        'records': records,
        'python': platform.python_version(),
        'implementation_sha256': hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
    }
    destination = args.output
    assert not destination.exists(), 'Use a fresh attempt output, never overwrite evidence.'
    destination.write_text(json.dumps(serial(result), indent=2) + '\n', encoding='utf-8')
    print(json.dumps({key: serial(result[key]) for key in ('status', 'graph_count', 'continuous_contexts', 'comparison_count', 'quadratics_with_interior_vertex')}))


if __name__ == '__main__':
    main()
