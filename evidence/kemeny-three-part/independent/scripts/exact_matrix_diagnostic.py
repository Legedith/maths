"""Finite exact graph diagnostics for the independently audited sign theorem.

These examples check the source formula against direct rational matrices.  They
are diagnostics only; the universal proof is the polynomial certificate audit.
"""

from __future__ import annotations

import argparse
from fractions import Fraction
from itertools import combinations
import json
from pathlib import Path


def invert(matrix: list[list[Fraction]]) -> list[list[Fraction]]:
    n = len(matrix)
    augmented = [
        row[:] + [Fraction(int(i == j)) for j in range(n)]
        for i, row in enumerate(matrix)
    ]
    for column in range(n):
        pivot = next((row for row in range(column, n) if augmented[row][column]), None)
        if pivot is None:
            raise ArithmeticError("singular matrix")
        augmented[column], augmented[pivot] = augmented[pivot], augmented[column]
        pivot_value = augmented[column][column]
        augmented[column] = [value / pivot_value for value in augmented[column]]
        for row in range(n):
            if row == column:
                continue
            factor = augmented[row][column]
            if factor:
                augmented[row] = [
                    value - factor * pivot_entry
                    for value, pivot_entry in zip(augmented[row], augmented[column], strict=True)
                ]
    return [row[n:] for row in augmented]


def complete_multipartite_adjacency(sizes: tuple[int, ...]) -> tuple[list[list[int]], list[list[int]]]:
    parts: list[list[int]] = []
    cursor = 0
    for size in sizes:
        parts.append(list(range(cursor, cursor + size)))
        cursor += size
    labels = [0] * cursor
    for part_index, vertices in enumerate(parts):
        for vertex in vertices:
            labels[vertex] = part_index
    adjacency = [
        [int(i != j and labels[i] != labels[j]) for j in range(cursor)]
        for i in range(cursor)
    ]
    return adjacency, parts


def kemeny(adjacency: list[list[int]]) -> Fraction:
    n = len(adjacency)
    degrees = [sum(row) for row in adjacency]
    volume = sum(degrees)
    transition = [
        [Fraction(adjacency[i][j], degrees[i]) for j in range(n)]
        for i in range(n)
    ]
    stationary = [Fraction(degree, volume) for degree in degrees]
    fundamental = [
        [Fraction(int(i == j)) - transition[i][j] + stationary[j] for j in range(n)]
        for i in range(n)
    ]
    inverse = invert(fundamental)
    return sum(inverse[i][i] for i in range(n)) - 1


def source_delta(selected: int, other_one: int, other_two: int, p: int) -> Fraction:
    q = [selected, other_one, other_two] + [1] * p
    n = sum(q)
    alpha = [n - part for part in q]
    gamma = sum(part * part_alpha for part, part_alpha in zip(q, alpha, strict=True))
    x = selected
    a1 = alpha[0]
    source_sum = sum(
        q[j]
        * alpha[j]
        * (
            Fraction(alpha[j], n)
            + Fraction(x - 2, 2)
            + Fraction((n - 2) * (gamma - x * a1), 2 * n * a1)
        )
        for j in range(1, len(q))
    )
    brace = (
        -Fraction(gamma, 2 * a1)
        + Fraction(Fraction((x - 2) * gamma, 2) + source_sum, gamma)
        + Fraction(gamma - a1, a1 * (a1 + 2))
    )
    return Fraction(2, gamma + 2) * brace


def encode(value: Fraction) -> str:
    return f"{value.numerator}/{value.denominator}"


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()

    cases = ((3, 3, 3, 1), (3, 3, 5, 2), (3, 4, 5, 1), (4, 4, 6, 3))
    results = []
    comparisons_checked = 0
    for a, b, c, p in cases:
        non_singletons = (a, b, c)
        sizes = non_singletons + (1,) * p
        adjacency, parts = complete_multipartite_adjacency(sizes)
        before = kemeny(adjacency)
        minimum = min(non_singletons)
        per_part = []
        for part_index, size in enumerate(non_singletons):
            if size != minimum:
                continue
            other_sizes = [non_singletons[index] for index in range(3) if index != part_index]
            expected = source_delta(size, other_sizes[0], other_sizes[1], p)
            edge_results = []
            for left, right in combinations(parts[part_index], 2):
                changed = [row[:] for row in adjacency]
                changed[left][right] = changed[right][left] = 1
                observed = kemeny(changed) - before
                if observed != expected:
                    raise AssertionError(
                        f"matrix/source mismatch for {(a,b,c,p)}, part {part_index}, edge {(left,right)}: "
                        f"{observed} != {expected}"
                    )
                if observed >= 0:
                    raise AssertionError("minimum-part diagnostic is not strictly negative")
                edge_results.append({"edge": [left, right], "delta": encode(observed)})
                comparisons_checked += 1
            if len({row["delta"] for row in edge_results}) != 1:
                raise AssertionError("within-part edge orbit produced unequal values")
            per_part.append(
                {
                    "part_index": part_index,
                    "part_size": size,
                    "source_delta": encode(expected),
                    "all_within_part_edges": edge_results,
                }
            )
        if len({item["source_delta"] for item in per_part}) != 1:
            raise AssertionError("tied minimum parts produced unequal source values")
        results.append(
            {
                "a_b_c_p": [a, b, c, p],
                "base_kemeny": encode(before),
                "minimum_size": minimum,
                "minimum_part_count": len(per_part),
                "minimum_parts": per_part,
            }
        )

    report = {
        "schema_version": "independent-exact-matrix-diagnostic-v1",
        "status": "PASS",
        "method": "Fraction trace((I-P+1*pi)^-1)-1 versus Theorem 3.2.3",
        "scope": "finite diagnostics only; not evidence for the universal quantifier",
        "cases": len(results),
        "edge_comparisons": comparisons_checked,
        "results": results,
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(report, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
