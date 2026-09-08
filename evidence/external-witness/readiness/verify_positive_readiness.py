from __future__ import annotations

import hashlib
import json
from pathlib import Path


AUDIT = Path(__file__).resolve().parent
WORKER = AUDIT.parent / "tool-feasibility-work"
EXPECTED_CONTRACT_SHA256 = "e521415fd5edac2a155b5a091c7a6e0343bab3990becc5bde77099aa25e93162"


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8-sig"))


def source_line(relative: str, number: int) -> str:
    return (WORKER / relative).read_text(encoding="utf-8").splitlines()[number - 1]


setup = load(AUDIT / "independent-env-setup.json")
smoke = load(AUDIT / "independent-smoke.json")
worker_z3_install = load(WORKER / "raw/z3-install.json")
worker_z3_smoke = load(WORKER / "raw/z3-smoke.json")
worker_sympy_install = load(WORKER / "raw/sympy-install.json")
worker_sympy_smoke = load(WORKER / "raw/sympy-smoke.json")
z3_metadata = load(WORKER / "raw/sources/z3-pypi-5.1.0.0.json")

setup_records = {item["id"]: item for item in setup["records"]}
checks = {
    "contract_copy_exact": sha256(AUDIT / "smoke-contract.json") == EXPECTED_CONTRACT_SHA256
    and sha256(WORKER / "docs/smoke-contract.json") == EXPECTED_CONTRACT_SHA256,
    "audit_setup_pass": setup["all_pass"] is True,
    "audit_uses_shared_d_cache": setup["uv_cache_dir"] == "D:\\CodexWorkspaces\\mathematics-atlas\\uv-cache",
    "audit_uses_isolated_venv": setup["isolated_venv"] == ".venv"
    and "tool-readiness-audit-work" in setup["audit_root"],
    "audit_exact_install_command": setup_records["install_pins"]["command"].endswith(
        "z3-solver==5.1.0.0 sympy==1.14.0"
    ),
    "audit_exact_freeze": setup_records["freeze"]["output"].splitlines()
    == ["mpmath==1.3.0", "sympy==1.14.0", "z3-solver==5.1.0.0"],
    "audit_smoke_all_ten": smoke["all_pass"] is True
    and len(smoke["checks"]) == 10
    and all(smoke["checks"].values()),
    "audit_z3_values": smoke["observed"]["z3"]
    == {"sat": "sat", "sat_model_values": {"x": "1/3", "y": "1/2"}, "unsat": "unsat"},
    "audit_sympy_values": smoke["observed"]["sympy"]
    == {
        "determinant": "5/36",
        "eigenvalue_multiplicities": {"1/6": 1, "5/6": 1},
        "inverse": [["18/5", "-12/5"], ["-12/5", "18/5"]],
    },
    "worker_positive_z3_alignment": worker_z3_install["all_steps_pass"] is True
    and worker_z3_smoke["all_pass"] is True
    and worker_z3_smoke["z3_solver_distribution_version"] == "5.1.0.0"
    and worker_z3_smoke["z3_library_version"] == "5.1.0",
    "worker_positive_sympy_alignment": worker_sympy_install["install_exit_code"] == 0
    and worker_sympy_install["freeze_exit_code"] == 0
    and worker_sympy_smoke["all_pass"] is True
    and worker_sympy_smoke["contract_sha256"] == EXPECTED_CONTRACT_SHA256,
    "z3_primary_source": "pip install z3-solver" in source_line("raw/sources/z3-README.md", 228)
    and "virtual environment" in source_line("raw/sources/z3-README.md", 244)
    and "Z3 and the Python bindings" in source_line("raw/sources/z3-README.md", 257),
    "z3_release_metadata": z3_metadata["info"]["name"] == "z3-solver"
    and z3_metadata["info"]["version"] == "5.1.0.0"
    and any(item["filename"] == "z3_solver-5.1.0.0-py3-none-win_amd64.whl" for item in z3_metadata["urls"]),
    "sympy_primary_source": "MatrixBase.eigenvals" in source_line("raw/sources/sympy-matrices.html", 9065)
    and "Rational" in source_line("raw/sources/sympy-gotchas.html", 1104),
}

result = {
    "schema_version": "independent-positive-tool-readiness-v1",
    "auditor": "/root/sol_symmetry_audit",
    "scope": "Positive local readiness of the exact Z3 and SymPy Python APIs for the sealed generic fixtures only.",
    "inputs": {
        "contract_sha256": EXPECTED_CONTRACT_SHA256,
        "independent_setup_sha256": sha256(AUDIT / "independent-env-setup.json"),
        "independent_smoke_sha256": sha256(AUDIT / "independent-smoke.json"),
        "worker_z3_install_sha256": sha256(WORKER / "raw/z3-install.json"),
        "worker_z3_smoke_sha256": sha256(WORKER / "raw/z3-smoke.json"),
        "worker_sympy_install_sha256": sha256(WORKER / "raw/sympy-install.json"),
        "worker_sympy_smoke_sha256": sha256(WORKER / "raw/sympy-smoke.json"),
    },
    "checks": checks,
    "all_positive_checks_pass": all(checks.values()),
    "certified": {
        "z3_python_api": {
            "status": "ready_in_isolated_audit_environment",
            "python": "3.12.11",
            "z3_solver_distribution": "5.1.0.0",
            "z3_library": "5.1.0",
        },
        "sympy_python_api": {
            "status": "ready_in_isolated_audit_environment",
            "python": "3.12.11",
            "sympy": "1.14.0",
            "mpmath": "1.3.0",
        },
    },
    "not_certified": [
        "Any native, WSL, Program Files, user-toolchain, container, or machine-wide absence conclusion.",
        "The broader author feasibility report or either of its two sealed versions.",
        "Compliance with the requested 15-minute cap; the author reports an overrun.",
        "Any human setup-time estimate.",
        "The bundled z3 command-line executable; this audit executed the Python API only.",
        "Any study encoding, theorem, natural-language interpretation, solver performance, productivity, impact, or novelty claim.",
    ],
    "historical_findings": [
        {
            "seal_sha256": "eaaad427babd5746e31bd48d9d2ce39a0484d0b973fbb92bc062b14601e023e8",
            "finding": "The first report incorrectly claimed absence of a staging Z3 executable; .venv/bin/z3.exe was present.",
        },
        {
            "seal_sha256": "2e904356cd2fc9b34ceb09096cd60c9513800d030c332fbe73ce6ae040d9c2f6",
            "finding": "The corrected report attributed Ubuntu-20.04 WSL PATH absence to elan although the recorded WSL lookup omitted elan.",
        },
        {
            "finding": "A console rendering concern was rechecked against the preserved bytes: the first report contained six U+2013 characters and zero U+FFFD characters, so no byte-level replacement-character defect is asserted.",
        },
    ],
    "time_cap": {
        "status": "fail",
        "requested_seconds": 900,
        "author_reported_execution_and_discovery_seconds": 1031.075,
        "author_reported_overrun_seconds": 131.075,
        "note": "The later sealing/correction work is separate; no cap-compliance claim is made.",
    },
}

(AUDIT / "positive-readiness-check.json").write_text(
    json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
    encoding="utf-8",
    newline="\n",
)
print(json.dumps({"all_positive_checks_pass": result["all_positive_checks_pass"], "time_cap": "fail"}, sort_keys=True))
raise SystemExit(0 if result["all_positive_checks_pass"] else 1)
