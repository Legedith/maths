from __future__ import annotations

import hashlib
import importlib.metadata
import json
import platform
import sys
from datetime import datetime, timezone
from pathlib import Path

import sympy
import z3


ROOT = Path(__file__).resolve().parent
CONTRACT = ROOT / "smoke-contract.json"
EXPECTED_CONTRACT_SHA256 = "e521415fd5edac2a155b5a091c7a6e0343bab3990becc5bde77099aa25e93162"


def rational(text: str) -> sympy.Rational:
    numerator, denominator = text.split("/", maxsplit=1)
    return sympy.Rational(int(numerator), int(denominator))


contract_bytes = CONTRACT.read_bytes()
contract_sha256 = hashlib.sha256(contract_bytes).hexdigest()
contract = json.loads(contract_bytes)

x, y = z3.Reals("x y")
sat_solver = z3.Solver()
sat_solver.add(x == z3.Q(1, 3), y == z3.Q(1, 2), x + y == z3.Q(5, 6))
sat_result = sat_solver.check()
sat_model = sat_solver.model() if sat_result == z3.sat else None
sat_values = (
    {
        "x": str(sat_model.eval(x, model_completion=True)),
        "y": str(sat_model.eval(y, model_completion=True)),
    }
    if sat_model is not None
    else None
)

ux, uy = z3.Reals("ux uy")
unsat_solver = z3.Solver()
unsat_solver.add(ux == z3.Q(1, 3), uy == z3.Q(1, 2), ux + uy == 1)
unsat_result = unsat_solver.check()

matrix_case = contract["sympy"]["case"]
matrix = sympy.Matrix([[rational(value) for value in row] for row in matrix_case["matrix"]])
determinant = str(matrix.det())
eigenvalues = {str(value): int(multiplicity) for value, multiplicity in matrix.eigenvals().items()}
inverse = [[str(value) for value in row] for row in matrix.inv().tolist()]

checks = {
    "contract_sha256": contract_sha256 == EXPECTED_CONTRACT_SHA256,
    "z3_distribution_version": importlib.metadata.version("z3-solver") == "5.1.0.0",
    "z3_library_version": z3.get_version_string() == "5.1.0",
    "z3_sat_result": str(sat_result) == contract["z3"]["cases"][0]["expected"],
    "z3_sat_model": sat_values == contract["z3"]["cases"][0]["required_model_values"],
    "z3_unsat_result": str(unsat_result) == contract["z3"]["cases"][1]["expected"],
    "sympy_distribution_version": importlib.metadata.version("sympy") == "1.14.0",
    "sympy_determinant": determinant == matrix_case["expected_determinant"],
    "sympy_eigenvalues": eigenvalues == matrix_case["expected_eigenvalue_multiplicities"],
    "sympy_inverse": inverse == matrix_case["expected_inverse"],
}

result = {
    "schema_version": "independent-tool-smoke-v1",
    "auditor": "/root/sol_symmetry_audit",
    "recorded_at_utc": datetime.now(timezone.utc).isoformat(),
    "scope": "Independent replay of the sealed generic exact-rational fixtures only; no study claim or study encoding.",
    "command": ".venv/Scripts/python.exe independent_smoke.py",
    "contract": {
        "path": "smoke-contract.json",
        "sha256": contract_sha256,
    },
    "environment": {
        "python_executable": sys.executable,
        "python_version": platform.python_version(),
        "z3_solver_distribution_version": importlib.metadata.version("z3-solver"),
        "z3_library_version": z3.get_version_string(),
        "sympy_distribution_version": importlib.metadata.version("sympy"),
        "mpmath_distribution_version": importlib.metadata.version("mpmath"),
    },
    "observed": {
        "z3": {
            "sat": str(sat_result),
            "sat_model_values": sat_values,
            "unsat": str(unsat_result),
        },
        "sympy": {
            "determinant": determinant,
            "eigenvalue_multiplicities": eigenvalues,
            "inverse": inverse,
        },
    },
    "checks": checks,
    "all_pass": all(checks.values()),
}

output = ROOT / "independent-smoke.json"
output.write_text(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8", newline="\n")
print(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True))
raise SystemExit(0 if result["all_pass"] else 1)
