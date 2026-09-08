from __future__ import annotations

import argparse
from fractions import Fraction
from itertools import combinations
import hashlib
import json
from pathlib import Path


EXPECTED_ENCODING_SHA256 = "96346c871b570aff57557ef201e7335bea4fb1ac55fe0e5a54ed6a149afa13d5"


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def q(value: object) -> Fraction:
    return Fraction(str(value))


def text(value: Fraction) -> str:
    return str(value.numerator) if value.denominator == 1 else f"{value.numerator}/{value.denominator}"


def matrix_text(matrix: list[list[Fraction]]) -> list[list[str]]:
    return [[text(value) for value in row] for row in matrix]


def laplacian(vertices: list[int], edges: list[list[object]]) -> list[list[Fraction]]:
    n = len(vertices)
    result = [[Fraction(0) for _ in range(n)] for _ in range(n)]
    for u, v, weight_text in edges:
        weight = q(weight_text)
        if weight <= 0 or u == v:
            raise ValueError("invalid frozen edge")
        result[u][u] += weight
        result[v][v] += weight
        result[u][v] -= weight
        result[v][u] -= weight
    return result


def transpose(columns: list[list[object]]) -> list[list[Fraction]]:
    return [[q(columns[column][row]) for column in range(len(columns))] for row in range(len(columns[0]))]


def multiply(left: list[list[Fraction]], right: list[list[Fraction]]) -> list[list[Fraction]]:
    return [
        [sum((left[i][k] * right[k][j] for k in range(len(right))), Fraction(0)) for j in range(len(right[0]))]
        for i in range(len(left))
    ]


def determinant(matrix: list[list[Fraction]]) -> Fraction:
    work = [row[:] for row in matrix]
    n = len(work)
    sign = 1
    value = Fraction(1)
    for column in range(n):
        pivot = next((row for row in range(column, n) if work[row][column] != 0), None)
        if pivot is None:
            return Fraction(0)
        if pivot != column:
            work[column], work[pivot] = work[pivot], work[column]
            sign *= -1
        pivot_value = work[column][column]
        value *= pivot_value
        for row in range(column + 1, n):
            factor = work[row][column] / pivot_value
            for j in range(column + 1, n):
                work[row][j] -= factor * work[column][j]
        for row in range(column + 1, n):
            work[row][column] = Fraction(0)
    return value * sign


def minor(matrix: list[list[Fraction]], removed: int) -> list[list[Fraction]]:
    return [
        [value for j, value in enumerate(row) if j != removed]
        for i, row in enumerate(matrix)
        if i != removed
    ]


def solve(matrix: list[list[Fraction]], rhs: list[Fraction]) -> list[Fraction]:
    work = [row[:] + [rhs[index]] for index, row in enumerate(matrix)]
    n = len(work)
    for column in range(n):
        pivot = next((row for row in range(column, n) if work[row][column] != 0), None)
        if pivot is None:
            raise ValueError("singular system")
        work[column], work[pivot] = work[pivot], work[column]
        scale = work[column][column]
        work[column] = [value / scale for value in work[column]]
        for row in range(n):
            if row == column:
                continue
            factor = work[row][column]
            work[row] = [work[row][j] - factor * work[column][j] for j in range(n + 1)]
    return [work[i][-1] for i in range(n)]


def spanning_trees(vertices: list[int], edges: list[list[object]]) -> list[dict[str, object]]:
    n = len(vertices)
    trees: list[dict[str, object]] = []
    for indices in combinations(range(len(edges)), n - 1):
        parent = list(range(n))

        def find(node: int) -> int:
            while parent[node] != node:
                parent[node] = parent[parent[node]]
                node = parent[node]
            return node

        acyclic = True
        for index in indices:
            u, v, _ = edges[index]
            ru, rv = find(u), find(v)
            if ru == rv:
                acyclic = False
                break
            parent[ru] = rv
        connected = acyclic and len({find(vertex) for vertex in vertices}) == 1
        if connected:
            weight = Fraction(1)
            for index in indices:
                weight *= q(edges[index][2])
            trees.append({"edge_indices": list(indices), "weight": text(weight), "contains_e": 0 in indices})
    return trees


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--encoding", type=Path, required=True)
    parser.add_argument("--results", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()

    encoding_hash = sha256(args.encoding)
    encoding = json.loads(args.encoding.read_text(encoding="utf-8"))
    first, second = encoding["cases"]
    observed_first = json.loads((args.results / "case-23150070.json").read_text(encoding="utf-8"))
    observed_second = json.loads((args.results / "case-23832572.json").read_text(encoding="utf-8"))

    l1 = laplacian(first["vertices"], first["conductance_edges"])
    basis = transpose(first["certificate_columns"])
    diagonal = [[Fraction(0) for _ in range(4)] for _ in range(4)]
    for i, eigenvalue in enumerate(first["certificate_eigenvalues"]):
        diagonal[i][i] = q(eigenvalue)
    lb = multiply(l1, basis)
    bd = multiply(basis, diagonal)
    basis_det = determinant(basis)
    cofactors1 = [determinant(minor(l1, index)) for index in range(4)]
    trees1 = spanning_trees(first["vertices"], first["conductance_edges"])
    spectrum = [q(value) for value in first["certificate_eigenvalues"]]
    one_zero_removed = spectrum[:]
    one_zero_removed.remove(Fraction(0))
    source_expression1 = Fraction(1, 4)
    for value in one_zero_removed:
        source_expression1 *= value
    summary_expression1 = Fraction(1, 4)
    for value in spectrum:
        if value != 0:
            summary_expression1 *= value

    direct_first = {
        "laplacian": matrix_text(l1),
        "basis": matrix_text(basis),
        "basis_determinant": text(basis_det),
        "lb": matrix_text(lb),
        "bd": matrix_text(bd),
        "lb_equals_bd": lb == bd,
        "cofactors": [text(value) for value in cofactors1],
        "spanning_trees": trees1,
        "tree_total": len(trees1),
        "source_expression": text(source_expression1),
        "summary_expression": text(summary_expression1),
    }
    checks_first = {
        "encoding_hash": encoding_hash == EXPECTED_ENCODING_SHA256,
        "basis_invertible": basis_det != 0,
        "lb_equals_bd": lb == bd,
        "spectrum_exact": [text(value) for value in spectrum] == ["0", "0", "2", "2"],
        "all_cofactors_zero": cofactors1 == [Fraction(0)] * 4,
        "no_spanning_tree": trees1 == [],
        "source_expression_zero": source_expression1 == 0,
        "summary_expression_one": summary_expression1 == 1,
        "author_laplacian": observed_first["laplacian"] == direct_first["laplacian"],
        "author_basis_determinant": observed_first["basis_determinant"] == direct_first["basis_determinant"],
        "author_basis_residual": observed_first["basis_residual"] == [["0"] * 4 for _ in range(4)],
        "author_cofactors": observed_first["principal_cofactors"] == direct_first["cofactors"],
        "author_expressions": observed_first["source_expression"] == direct_first["source_expression"]
        and observed_first["summary_expression"] == direct_first["summary_expression"]
        and observed_first["tree_total"] == "0",
    }

    l2 = laplacian(second["vertices"], second["conductance_edges"])
    trees2 = spanning_trees(second["vertices"], second["conductance_edges"])
    tau = sum((q(tree["weight"]) for tree in trees2), Fraction(0))
    tau_e = sum((q(tree["weight"]) for tree in trees2 if tree["contains_e"]), Fraction(0))
    count = len(trees2)
    count_e = sum(1 for tree in trees2 if tree["contains_e"])
    grounded_indices = [0, 2]
    grounded = [[l2[i][j] for j in grounded_indices] for i in grounded_indices]
    grounded_solution = solve(grounded, [Fraction(1), Fraction(0)])
    voltage = [grounded_solution[0], Fraction(0), grounded_solution[1]]
    current = [sum((l2[i][j] * voltage[j] for j in range(3)), Fraction(0)) for i in range(3)]
    resistance = voltage[0] - voltage[1]
    w01 = q(second["conductance_edges"][0][2])
    source_expression2 = tau_e / (tau * w01)
    summary_expression2 = Fraction(count_e, count) / w01
    cofactors2 = [determinant(minor(l2, index)) for index in range(3)]

    direct_second = {
        "laplacian": matrix_text(l2),
        "spanning_trees": trees2,
        "tau": text(tau),
        "tau_e": text(tau_e),
        "ordinary_count": count,
        "ordinary_count_e": count_e,
        "grounded_matrix": matrix_text(grounded),
        "grounded_determinant": text(determinant(grounded)),
        "voltages": [text(value) for value in voltage],
        "current": [text(value) for value in current],
        "resistance": text(resistance),
        "source_expression": text(source_expression2),
        "summary_expression": text(summary_expression2),
        "cofactors": [text(value) for value in cofactors2],
    }
    author_replay = observed_second["sympy_replay"]
    checks_second = {
        "tree_list": trees2
        == [
            {"edge_indices": [0, 1], "weight": "2", "contains_e": True},
            {"edge_indices": [0, 2], "weight": "2", "contains_e": True},
            {"edge_indices": [1, 2], "weight": "1", "contains_e": False},
        ],
        "weighted_totals": tau == 5 and tau_e == 4,
        "ordinary_counts": count == 3 and count_e == 2,
        "grounded_invertible": determinant(grounded) == 5,
        "voltages_exact": voltage == [Fraction(2, 5), Fraction(0), Fraction(1, 5)],
        "current_exact": current == [Fraction(1), Fraction(-1), Fraction(0)],
        "resistance_exact": resistance == Fraction(2, 5),
        "source_expression_matches": source_expression2 == resistance,
        "summary_expression_disagrees": summary_expression2 == Fraction(1, 3) and summary_expression2 != resistance,
        "cofactors_match_tau": cofactors2 == [tau] * 3,
        "author_laplacian": observed_second["laplacian"] == direct_second["laplacian"],
        "author_tree_list": observed_second["spanning_trees"] == direct_second["spanning_trees"],
        "author_totals": observed_second["tau"] == direct_second["tau"]
        and observed_second["tau_e"] == direct_second["tau_e"]
        and observed_second["ordinary_count"] == count
        and observed_second["ordinary_count_e"] == count_e,
        "author_cofactors": observed_second["cofactors"] == direct_second["cofactors"],
        "author_expressions": observed_second["source_expression"] == direct_second["source_expression"]
        and observed_second["summary_expression"] == direct_second["summary_expression"],
        "author_summary_query": observed_second["summary_query"]["status"] == "sat"
        and observed_second["summary_query"]["voltages"] == direct_second["voltages"],
        "author_source_query": observed_second["source_query"]["status"] == "unsat",
        "author_replay": author_replay is not None
        and author_replay["resistance"] == direct_second["resistance"]
        and author_replay["node_equations_hold"] is True
        and author_replay["source_control_matches"] is True
        and author_replay["summary_disagrees"] is True,
    }

    result = {
        "schema_version": "direct-exact-certificate-v1",
        "auditor": "/root/sol_symmetry_audit",
        "method": "Python standard-library Fraction arithmetic, direct Gaussian elimination, determinant elimination, matrix multiplication, and exhaustive edge-subset enumeration; no SymPy or Z3 import.",
        "encoding": {"path": str(args.encoding), "sha256": encoding_hash},
        "results": str(args.results),
        "case_23150070": {"direct": direct_first, "checks": checks_first, "all_pass": all(checks_first.values())},
        "case_23832572": {"direct": direct_second, "checks": checks_second, "all_pass": all(checks_second.values())},
    }
    result["all_pass"] = result["case_23150070"]["all_pass"] and result["case_23832572"]["all_pass"]
    args.output.write_text(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8", newline="\n")
    print(json.dumps({"all_pass": result["all_pass"]}, sort_keys=True))
    return 0 if result["all_pass"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
