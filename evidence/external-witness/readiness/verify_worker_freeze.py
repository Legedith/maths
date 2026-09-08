from __future__ import annotations

import hashlib
import json
from datetime import datetime
from pathlib import Path


SOURCE = Path(r"D:/CodexWorkspaces/mathematics-atlas/tool-feasibility-work")
AUDIT = Path(__file__).resolve().parent
EXPECTED_MANIFEST_SHA256 = "7b1f6c24c93e3a6d5995435d2a1a8f2c9453191e4651a2d27febacff009341b8"
EXPECTED_REPORT_SHA256 = "2e904356cd2fc9b34ceb09096cd60c9513800d030c332fbe73ce6ae040d9c2f6"
EXPECTED_CONTRACT_SHA256 = "e521415fd5edac2a155b5a091c7a6e0343bab3990becc5bde77099aa25e93162"


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def load_json(relative: str) -> dict:
    return json.loads((SOURCE / relative).read_text(encoding="utf-8-sig"))


def line(relative: str, number: int) -> str:
    return (SOURCE / relative).read_text(encoding="utf-8").splitlines()[number - 1]


manifest_path = SOURCE / "logs/artifact-manifest.json"
report_path = SOURCE / "notes/feasibility-report.md"
manifest = load_json("logs/artifact-manifest.json")
report = report_path.read_text(encoding="utf-8")
contract = load_json("docs/smoke-contract.json")
z3_install = load_json("raw/z3-install.json")
sympy_install = load_json("raw/sympy-install.json")
z3_smoke = load_json("raw/z3-smoke.json")
sympy_smoke = load_json("raw/sympy-smoke.json")
runtime = load_json("raw/runtime-discovery.json")
source_manifest = load_json("raw/source-retrieval-manifest.json")
sympy_source_manifest = load_json("raw/sympy-source-retrieval.json")

manifest_results = []
for item in manifest["files"]:
    path = SOURCE / item["path"]
    actual_bytes = path.stat().st_size if path.is_file() else None
    actual_sha256 = sha256(path) if path.is_file() else None
    manifest_results.append(
        {
            "path": item["path"],
            "expected_bytes": item["bytes"],
            "actual_bytes": actual_bytes,
            "expected_sha256": item["sha256"],
            "actual_sha256": actual_sha256,
            "pass": actual_bytes == item["bytes"] and actual_sha256 == item["sha256"],
        }
    )

listed = {item["path"].replace("\\", "/") for item in manifest["files"]}
actual = set()
for path in SOURCE.rglob("*"):
    if not path.is_file():
        continue
    relative = path.relative_to(SOURCE).as_posix()
    if relative.startswith(".venv/") or relative.startswith(".uv-cache/"):
        continue
    if relative == "logs/artifact-manifest.json":
        continue
    actual.add(relative)

z3_executable = SOURCE / ".venv/bin/z3.exe"
z3_executable_result = {
    "path": ".venv/bin/z3.exe",
    "bytes": z3_executable.stat().st_size,
    "sha256": sha256(z3_executable),
}
z3_executable_result["pass"] = (
    z3_executable_result["bytes"] == 18_842_624
    and z3_executable_result["sha256"] == "c638e6b8d066a5ad6ea2712dcd5e2eff5c57eba501b98e7fa8487f7daf0e863d"
)

path_inventory = {item["name"]: item for item in runtime["path_inventory"]}
command_records = {item["id"]: item for item in runtime["command_records"]}
native_absent_names = ["z3", "sage", "lean", "lake", "elan", "loogle", "isabelle"]
native_path_absence = all(not path_inventory[name]["found_on_path"] for name in native_absent_names)
wsl_path_output = command_records["wsl_tool_paths"]["output"]
wsl_path_absence = (
    command_records["wsl_tool_paths"]["exit_code"] == 0
    and "z3=sage=lean=lake=loogle=isabelle=" in wsl_path_output
)

source_records = source_manifest["records"]
source_hash_checks = []
for item in source_records:
    source_path = SOURCE / item["local_path"]
    source_hash_checks.append(
        {
            "id": item["id"],
            "url": item["url"],
            "status": item["exit_code"],
            "sha256": sha256(source_path),
            "expected_sha256": item["sha256"],
            "pass": item["exit_code"] == 0
            and source_path.stat().st_size == item["bytes"]
            and sha256(source_path) == item["sha256"],
        }
    )
for item in sympy_source_manifest["items"]:
    source_path = SOURCE / item["path"]
    source_hash_checks.append(
        {
            "id": item["id"],
            "url": item["url"],
            "status": item["status"],
            "sha256": sha256(source_path),
            "expected_sha256": item["sha256"],
            "pass": item["status"] == "success"
            and source_path.stat().st_size == item["bytes"]
            and sha256(source_path) == item["sha256"],
        }
    )

source_locator_checks = {
    "z3_pip_install_line_228": "pip install z3-solver" in line("raw/sources/z3-README.md", 228),
    "z3_venv_line_244": "virtual environment" in line("raw/sources/z3-README.md", 244),
    "z3_venv_binary_line_257": "Z3 and the Python bindings" in line("raw/sources/z3-README.md", 257),
    "sympy_eigenvals_index_line_9065": "MatrixBase.eigenvals" in line("raw/sources/sympy-matrices.html", 9065),
    "sympy_rational_line_1104": "Rational" in line("raw/sources/sympy-gotchas.html", 1104),
    "sage_conda_line_290": "conda-forge" in line("raw/sources/sage-install.html", 290),
    "sage_windows_wsl_line_351": "Windows Subsystem for Linux" in line("raw/sources/sage-install.html", 351),
    "lean_elan_line_3419": "elan" in line("raw/sources/lean-install.html", 3419),
    "lean_mathlib_download_line_3488": "Mathlib" in line("raw/sources/lean-install.html", 3488),
    "loogle_build_line_34": "lake build" in line("raw/sources/loogle-README.md", 34),
    "loogle_index_line_40": "builds the search index" in line("raw/sources/loogle-README.md", 40),
    "isabelle_executable_line_121": "Isabelle2025-1.exe" in line("raw/sources/isabelle-install.html", 121),
    "isabelle_bundle_line_128": "contains everything required" in line("raw/sources/isabelle-install.html", 128),
    "isabelle_size_line_9": "1070580582 bytes" in line("raw/sources/isabelle-dist-index.html", 9),
}

z3_pypi = load_json("raw/sources/z3-pypi-5.1.0.0.json")
z3_pypi_check = (
    z3_pypi["info"]["name"] == "z3-solver"
    and z3_pypi["info"]["version"] == "5.1.0.0"
    and any(item["filename"] == "z3_solver-5.1.0.0-py3-none-win_amd64.whl" for item in z3_pypi["urls"])
)

z3_install_records = {item["id"]: item for item in z3_install["records"]}
install_checks = {
    "z3_isolated_paths": z3_install["uv_cache_dir"] == ".uv-cache" and z3_install["venv"] == ".venv",
    "z3_install_pass": z3_install["all_steps_pass"] is True,
    "z3_freeze_exact": z3_install_records["freeze_venv"]["output"].strip().endswith("z3-solver==5.1.0.0"),
    "sympy_isolated_paths": sympy_install["environment"]["staging_only"] is True
    and "tool-feasibility-work\\.venv" in sympy_install["environment"]["python"]
    and "tool-feasibility-work\\.uv-cache" in sympy_install["environment"]["UV_CACHE_DIR"],
    "sympy_install_pass": sympy_install["install_exit_code"] == 0 and sympy_install["freeze_exit_code"] == 0,
    "sympy_freeze_exact": all(
        pin in sympy_install["freeze_output"]
        for pin in ("mpmath==1.3.0", "sympy==1.14.0", "z3-solver==5.1.0.0")
    ),
}

worker_smoke_checks = {
    "z3_all_pass": z3_smoke["all_pass"] is True,
    "z3_versions": z3_smoke["python_version"] == "3.12.11"
    and z3_smoke["z3_solver_distribution_version"] == "5.1.0.0"
    and z3_smoke["z3_library_version"] == "5.1.0",
    "z3_sat": z3_smoke["cases"][0]["actual"] == "sat"
    and z3_smoke["cases"][0]["model_values"] == {"x": "1/3", "y": "1/2"},
    "z3_unsat": z3_smoke["cases"][1]["actual"] == "unsat",
    "sympy_contract_hash": sympy_smoke["contract_sha256"] == EXPECTED_CONTRACT_SHA256,
    "sympy_all_pass": sympy_smoke["all_pass"] is True,
    "sympy_values": sympy_smoke["observed"]
    == {
        "determinant": "5/36",
        "eigenvalue_multiplicities": {"5/6": 1, "1/6": 1},
        "inverse": [["18/5", "-12/5"], ["-12/5", "18/5"]],
    },
}

contract_times = {
    "z3_contract_frozen_at_utc": contract["frozen_at_utc"],
    "sympy_case_frozen_at_utc": contract["sympy_addendum_frozen_at_utc"],
    "sympy_install_authorized_at_utc": contract["sympy_installation_clarification"]["recorded_at_utc"],
    "sympy_install_started_at_utc": sympy_install["started_at_utc"],
    "sympy_smoke_started_at_utc": sympy_smoke["started_at_utc"],
}
contract_chronology_pass = (
    datetime.fromisoformat(contract_times["sympy_case_frozen_at_utc"].replace("Z", "+00:00"))
    < datetime.fromisoformat(contract_times["sympy_install_authorized_at_utc"].replace("Z", "+00:00"))
    < datetime.fromisoformat(contract_times["sympy_install_started_at_utc"].replace("Z", "+00:00"))
    < datetime.fromisoformat(contract_times["sympy_smoke_started_at_utc"].replace("Z", "+00:00"))
)

report_checks = {
    "corrected_report_hash": sha256(report_path) == EXPECTED_REPORT_SHA256,
    "ascii_only": all(ord(character) < 128 for character in report),
    "cap_failure_disclosed": "exceeded the requested 15-minute cap" in report and "No cap-compliance claim is made" in report,
    "z3_executable_disclosed": ".venv/bin/z3.exe" in report and z3_executable_result["sha256"] in report,
    "absence_scoped": "inspected native PATH" in report and "installed Ubuntu-20.04 WSL PATH" in report,
    "unsupported_setup_estimates_removed": "Estimated human setup burden" not in report
    and "roughly 1-3 hours" not in report
    and "about 5-10 minutes" not in report,
    "scope_limit_disclosed": "do not validate a study encoding" in report and "mathematical novelty" in report,
}

failed_seal_checks = {
    "prior_report": sha256(SOURCE / "logs/failed-seals/feasibility-report-failed-seal-eaaad427.md")
    == "eaaad427babd5746e31bd48d9d2ce39a0484d0b973fbb92bc062b14601e023e8",
    "prior_manifest": sha256(SOURCE / "logs/failed-seals/artifact-manifest-failed-seal-95a193e1.json")
    == "95a193e1054597db091423f4d255bcd0e5cb8b50cc20b0757ef9a773665c58a6",
    "intermediate_manifest": sha256(SOURCE / "logs/failed-seals/artifact-manifest-correction-attempt-01-291d3c3d.json")
    == "291d3c3da574b03827d42380816f21a66a866a78571caade5c295bcda1e2b0be",
    "correction_record": sha256(SOURCE / "logs/feasibility-report-correction.json")
    == "d583cf1fb7b8f77777f753839092bef6ed68cf240552b30323c46b6a3fd07736",
}

checks = {
    "manifest_sha256": sha256(manifest_path) == EXPECTED_MANIFEST_SHA256,
    "manifest_file_count": manifest["file_count"] == 33 == len(manifest["files"]),
    "manifest_artifacts": all(item["pass"] for item in manifest_results),
    "manifest_complete_within_exclusions": listed == actual,
    "contract_sha256": sha256(SOURCE / "docs/smoke-contract.json") == EXPECTED_CONTRACT_SHA256,
    "contract_chronology": contract_chronology_pass,
    "worker_install_records": all(install_checks.values()),
    "worker_smoke_records": all(worker_smoke_checks.values()),
    "source_retrieval_hashes": all(item["pass"] for item in source_hash_checks),
    "source_locators": all(source_locator_checks.values()),
    "z3_pypi_metadata": z3_pypi_check,
    "scoped_runtime_absence": native_path_absence
    and wsl_path_absence
    and runtime["elan"]["root_exists"] is False
    and runtime["program_files_matches"] == [],
    "z3_package_executable": z3_executable_result["pass"],
    "corrected_report": all(report_checks.values()),
    "failed_seals_preserved": all(failed_seal_checks.values()),
}

result = {
    "schema_version": "independent-tool-freeze-check-v1",
    "auditor": "/root/sol_symmetry_audit",
    "subject": "corrected bounded tool-feasibility worker freeze",
    "inputs": {
        "manifest": {
            "path": "tool-feasibility-work/logs/artifact-manifest.json",
            "sha256": sha256(manifest_path),
        },
        "report": {
            "path": "tool-feasibility-work/notes/feasibility-report.md",
            "sha256": sha256(report_path),
        },
        "contract": {
            "path": "tool-feasibility-work/docs/smoke-contract.json",
            "sha256": sha256(SOURCE / "docs/smoke-contract.json"),
        },
    },
    "checks": checks,
    "all_non_cap_checks_pass": all(checks.values()),
    "time_cap": {
        "status": "fail",
        "requested_seconds": 900,
        "author_reported_execution_and_discovery_seconds": 1031.075,
        "author_reported_overrun_seconds": 131.075,
        "note": "The exact span is author-reported; the corrected final seal is later packaging. No cap-compliance claim is certified.",
    },
    "manifest_details": {
        "listed_files": len(listed),
        "actual_nonexcluded_files": len(actual),
        "missing_from_disk": sorted(listed - actual),
        "unlisted_nonexcluded": sorted(actual - listed),
        "file_results": manifest_results,
    },
    "contract_chronology": contract_times,
    "install_checks": install_checks,
    "worker_smoke_checks": worker_smoke_checks,
    "runtime_absence_scope": {
        "native_path_names_checked": native_absent_names,
        "native_path_absence": native_path_absence,
        "wsl_distribution_named": "Ubuntu-20.04",
        "wsl_command_output": wsl_path_output,
        "wsl_path_absence": wsl_path_absence,
        "elan_root_exists": runtime["elan"]["root_exists"],
        "program_files_matches": runtime["program_files_matches"],
        "scope_limit": runtime["scope_limit"],
    },
    "z3_package_executable": z3_executable_result,
    "source_hash_checks": source_hash_checks,
    "source_locator_checks": source_locator_checks,
    "report_checks": report_checks,
    "failed_seal_checks": failed_seal_checks,
}

(AUDIT / "worker-freeze-check.json").write_text(
    json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
    encoding="utf-8",
    newline="\n",
)
print(json.dumps({"all_non_cap_checks_pass": result["all_non_cap_checks_pass"], "time_cap": "fail"}, sort_keys=True))
raise SystemExit(0 if result["all_non_cap_checks_pass"] else 1)
