"""Exact replay of two disclosed examples using existing mathematics packages."""
import argparse
from datetime import datetime, timezone
import hashlib
from importlib.metadata import version
import json
from pathlib import Path
import platform
import subprocess
import sys
import time


def stamp():
    return datetime.now(timezone.utc).isoformat()


def save(path, value):
    path.write_text(json.dumps(value, indent=2) + "\n", encoding="utf-8", newline="\n")


def calculate(output):
    import sympy as sp
    import z3

    encoding_path = Path(__file__).with_name("encoding.json")
    encoding = json.loads(encoding_path.read_text(encoding="utf-8"))
    first, second = encoding["cases"]

    def laplacian(case):
        matrix = sp.zeros(len(case["vertices"]))
        for u, v, text in case["conductance_edges"]:
            weight = sp.Rational(text)
            assert weight > 0 and u != v
            matrix[u, u] += weight
            matrix[v, v] += weight
            matrix[u, v] -= weight
            matrix[v, u] -= weight
        return matrix

    def matrix_text(matrix):
        assert not matrix.has(sp.Float)
        return [[str(matrix[i, j]) for j in range(matrix.cols)] for i in range(matrix.rows)]

    # The sorted list retains every multiplicity. Remove exactly one zero.
    L = laplacian(first)
    t = sp.Symbol("t")
    eigenvalues = L.eigenvals()
    expanded = sorted(value for value, count in eigenvalues.items() for _ in range(count))
    indexed = expanded.copy()
    indexed.remove(sp.Integer(0))
    source_value = sp.prod(indexed) / L.rows
    summary_value = sp.prod(value for value in expanded if value != 0) / L.rows
    cofactors = [L.minor_submatrix(i, i).det() for i in range(L.rows)]
    basis = sp.Matrix.hstack(*(sp.Matrix(v) for v in first["certificate_columns"]))
    spectrum = [sp.Rational(v) for v in first["certificate_eigenvalues"]]
    residual = L * basis - basis * sp.diag(*spectrum)
    result_first = {
        "theorem_id": first["theorem_id"], "laplacian": matrix_text(L),
        "charpoly_det_tI_minus_L": str(L.charpoly(t).as_expr()),
        "eigenvalue_multiplicities": {str(k): int(v) for k, v in eigenvalues.items()},
        "eigenvalues_with_multiplicity": [str(x) for x in expanded],
        "source_expression": str(source_value), "summary_expression": str(summary_value),
        "principal_cofactors": [str(x) for x in cofactors], "tree_total": "0",
        "tree_total_reason": "Two disjoint edges have no connected spanning subgraph on four vertices.",
        "basis_columns": first["certificate_columns"], "basis_determinant": str(basis.det()),
        "basis_eigenvalues": [str(v) for v in spectrum], "basis_residual": matrix_text(residual),
        "source_control_matches": source_value == 0 and all(x == 0 for x in cofactors),
        "summary_disagrees": summary_value != 0,
        "basis_certificate_holds": basis.det() != 0 and residual == sp.zeros(4),
    }
    save(output / "case-23150070.json", result_first)

    L2 = laplacian(second)
    weights = [sp.Rational(edge[2]) for edge in second["conductance_edges"]]
    trees = [{"edge_indices": indices, "weight": sp.prod(weights[i] for i in indices), "contains_e": 0 in indices} for indices in second["tree_edge_indices"]]
    tau = sum(tree["weight"] for tree in trees)
    tau_e = sum(tree["weight"] for tree in trees if tree["contains_e"])
    count = len(trees)
    count_e = sum(tree["contains_e"] for tree in trees)
    source_resistance = tau_e / (tau * weights[0])
    summary_resistance = sp.Rational(count_e, count) / weights[0]
    v = z3.Reals("v0 v1 v2")
    injection = [1, -1, 0]

    def rational(value):
        return z3.RealVal(str(value))

    constraints = [sum(rational(L2[i, j]) * v[j] for j in range(3)) == injection[i] for i in range(3)]
    constraints += [v[1] == 0]
    constraints += [rational(w) > 0 for w in weights]
    constraints += [rational(tau) > 0, rational(count) > 0, rational(tau * weights[0]) != 0, rational(count * weights[0]) != 0]

    def query(name, rhs):
        solver = z3.Solver()
        solver.set(timeout=encoding["solver_timeout_ms"])
        solver.add(*constraints, v[0] - v[1] != rational(rhs))
        (output / (name + ".smt2")).write_text(solver.to_smt2(), encoding="utf-8", newline="\n")
        status = solver.check()
        record = {"status": str(status), "timeout_ms": encoding["solver_timeout_ms"]}
        if status == z3.sat:
            model = solver.model()
            record["model_sexpr"] = model.sexpr()
            record["voltages"] = [str(model.eval(x).as_fraction()) for x in v]
        elif status == z3.unknown:
            record["reason_unknown"] = solver.reason_unknown()
        save(output / (name + ".json"), record)
        return record

    summary_query = query("triangle-summary-negation", summary_resistance)
    source_query = query("triangle-source-negation", source_resistance)
    replay = None
    if summary_query["status"] == "sat":
        model_voltage = sp.Matrix([sp.Rational(s) for s in summary_query["voltages"]])
        independent_voltage = L2.extract([0, 2], [0, 2]).inv() * sp.Matrix([1, 0])
        resistance = model_voltage[0] - model_voltage[1]
        replay = {
            "model_voltage": matrix_text(model_voltage), "current": matrix_text(L2 * model_voltage),
            "independent_grounded_voltage": matrix_text(independent_voltage),
            "node_equations_hold": L2 * model_voltage == sp.Matrix(injection) and model_voltage[1] == 0,
            "independent_solution_matches": model_voltage[0] == independent_voltage[0] and model_voltage[2] == independent_voltage[1],
            "resistance": str(resistance), "source_control_matches": resistance == source_resistance,
            "summary_disagrees": resistance != summary_resistance,
        }
    cofactors2 = [L2.minor_submatrix(i, i).det() for i in range(3)]
    result_second = {
        "theorem_id": second["theorem_id"], "laplacian": matrix_text(L2),
        "spanning_trees": [{**tree, "weight": str(tree["weight"])} for tree in trees],
        "tau": str(tau), "tau_e": str(tau_e), "ordinary_count": count, "ordinary_count_e": count_e,
        "cofactors": [str(x) for x in cofactors2], "cofactors_match_tau": all(x == tau for x in cofactors2),
        "source_expression": str(source_resistance), "summary_expression": str(summary_resistance),
        "summary_query": summary_query, "source_query": source_query, "sympy_replay": replay,
    }
    save(output / "case-23832572.json", result_second)
    actual_first = {"source_expression": result_first["source_expression"], "summary_expression": result_first["summary_expression"], "tree_total": result_first["tree_total"], "cofactors": result_first["principal_cofactors"]}
    actual_second = {"summary_query": summary_query["status"], "source_control_query": source_query["status"], "voltages": summary_query.get("voltages"), "tau": result_second["tau"], "tau_e": result_second["tau_e"], "resistance": replay["resistance"] if replay else None, "summary_expression": result_second["summary_expression"]}
    exact_checks = {}
    for case, actual in [(first, actual_first), (second, actual_second)]:
        for name, expected in case["expected"].items():
            observed = actual.get(name)
            exact_checks[f"case-{case['theorem_id']}/{name}"] = {"expected": expected, "actual": observed, "pass": observed == expected}
    passed = (all(check["pass"] for check in exact_checks.values()) and result_first["source_control_matches"] and result_first["summary_disagrees"] and result_first["basis_certificate_holds"] and result_second["cofactors_match_tau"] and summary_query["status"] == "sat" and source_query["status"] == "unsat" and replay is not None and all(replay[k] for k in ["node_equations_hold", "independent_solution_matches", "source_control_matches", "summary_disagrees"]))
    save(output / "result-summary.json", {"known_case_count": 2, "author_expected_checks_pass": bool(passed), "exact_checks": exact_checks, "independent_gate": "pending", "scope": encoding["scope"], "encoding_sha256": hashlib.sha256(encoding_path.read_bytes()).hexdigest(), "versions": {"python": platform.python_version(), "z3-solver": version("z3-solver"), "sympy": version("sympy"), "mpmath": version("mpmath")}})
    print(json.dumps({"known_case_count": 2, "author_expected_checks_pass": bool(passed)}))
    return 0 if passed else 1


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--calculate", action="store_true")
    args = parser.parse_args()
    if args.calculate:
        args.output_dir.mkdir()
        return calculate(args.output_dir)
    args.output_dir.mkdir()
    argv = [sys.executable, str(Path(__file__).resolve()), "--calculate", "--output-dir", str(args.output_dir / "results")]
    started = stamp()
    timer = time.perf_counter()
    try:
        process = subprocess.run(argv, capture_output=True, timeout=60)
        stdout, stderr, exit_code, timed_out = process.stdout, process.stderr, process.returncode, False
    except subprocess.TimeoutExpired as exc:
        stdout, stderr, exit_code, timed_out = exc.stdout or b"", exc.stderr or b"", 124, True
    (args.output_dir / "stdout.log").write_bytes(stdout)
    (args.output_dir / "stderr.log").write_bytes(stderr)
    save(args.output_dir / "command.json", {"argv": argv, "cwd": str(Path.cwd()), "started_at": started, "ended_at": stamp(), "elapsed_seconds": time.perf_counter() - timer, "timeout_seconds": 60, "timed_out": timed_out, "exit_code": exit_code})
    print(stdout.decode("utf-8", errors="replace"), end="")
    if stderr:
        print(stderr.decode("utf-8", errors="replace"), file=sys.stderr, end="")
    return exit_code


if __name__ == "__main__":
    raise SystemExit(main())
