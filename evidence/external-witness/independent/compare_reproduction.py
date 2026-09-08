from __future__ import annotations

import hashlib
import json
from pathlib import Path


AUDIT = Path(__file__).resolve().parent
WORKER = AUDIT.parent / "external-witness-work"
AUTHOR = WORKER / "run-01"
REPRO = AUDIT / "reproduction/run-reproduction"
EXPECTED_PREEXECUTION_SHA256 = "11359bdd37807ae1cf5b42697007503d56ae54d77a6452c4fa2ff83f9f5a6cfc"
EXPECTED_RESULT_FREEZE_SHA256 = "51ce2155fc96b993a141a5d2b40a632f46fee39bd9cc8406362285acf3168215"


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8-sig"))


preexecution = load(WORKER / "preexecution-freeze-attempt02.json")
result_freeze = load(WORKER / "result-freeze.json")
copy_checks = []
for item in preexecution["files"]:
    copied = AUDIT / "reproduction" / item["path"]
    copy_checks.append(
        {
            "path": item["path"],
            "bytes": copied.stat().st_size,
            "sha256": sha256(copied),
            "pass": copied.stat().st_size == item["bytes"] and sha256(copied) == item["sha256"],
        }
    )

result_freeze_checks = []
for item in result_freeze["files"]:
    path = WORKER / item["path"]
    result_freeze_checks.append(
        {
            "path": item["path"],
            "bytes": path.stat().st_size,
            "sha256": sha256(path),
            "pass": path.stat().st_size == item["bytes"] and sha256(path) == item["sha256"],
        }
    )

author_first = load(AUTHOR / "results/case-23150070.json")
repro_first = load(REPRO / "results/case-23150070.json")
author_second = load(AUTHOR / "results/case-23832572.json")
repro_second = load(REPRO / "results/case-23832572.json")
author_summary = load(AUTHOR / "results/result-summary.json")
repro_summary = load(REPRO / "results/result-summary.json")
author_command = load(AUTHOR / "command.json")
repro_command = load(REPRO / "command.json")

first_fields = [
    "theorem_id",
    "laplacian",
    "charpoly_det_tI_minus_L",
    "eigenvalue_multiplicities",
    "eigenvalues_with_multiplicity",
    "source_expression",
    "summary_expression",
    "principal_cofactors",
    "tree_total",
    "basis_columns",
    "basis_determinant",
    "basis_eigenvalues",
    "basis_residual",
    "source_control_matches",
    "summary_disagrees",
    "basis_certificate_holds",
]
second_fields = [
    "theorem_id",
    "laplacian",
    "spanning_trees",
    "tau",
    "tau_e",
    "ordinary_count",
    "ordinary_count_e",
    "cofactors",
    "cofactors_match_tau",
    "source_expression",
    "summary_expression",
]
summary_fields = [
    "known_case_count",
    "author_expected_checks_pass",
    "exact_checks",
    "scope",
    "encoding_sha256",
    "versions",
]

stable_checks = {
    "first_numeric_record": all(author_first[field] == repro_first[field] for field in first_fields),
    "second_numeric_record": all(author_second[field] == repro_second[field] for field in second_fields),
    "summary_query": author_second["summary_query"]["status"] == repro_second["summary_query"]["status"] == "sat"
    and author_second["summary_query"]["voltages"] == repro_second["summary_query"]["voltages"]
    == ["2/5", "0", "1/5"]
    and author_second["summary_query"]["timeout_ms"] == repro_second["summary_query"]["timeout_ms"] == 5000,
    "source_query": author_second["source_query"] == repro_second["source_query"]
    == {"status": "unsat", "timeout_ms": 5000},
    "sympy_replay": author_second["sympy_replay"] == repro_second["sympy_replay"],
    "result_summary": all(author_summary[field] == repro_summary[field] for field in summary_fields),
    "smt2_summary_negation": (AUTHOR / "results/triangle-summary-negation.smt2").read_bytes()
    == (REPRO / "results/triangle-summary-negation.smt2").read_bytes(),
    "smt2_source_negation": (AUTHOR / "results/triangle-source-negation.smt2").read_bytes()
    == (REPRO / "results/triangle-source-negation.smt2").read_bytes(),
    "stdout": (AUTHOR / "stdout.log").read_bytes() == (REPRO / "stdout.log").read_bytes(),
    "stderr_empty": (AUTHOR / "stderr.log").read_bytes() == (REPRO / "stderr.log").read_bytes() == b"",
    "command_outcome": author_command["exit_code"] == repro_command["exit_code"] == 0
    and author_command["timed_out"] is repro_command["timed_out"] is False
    and author_command["timeout_seconds"] == repro_command["timeout_seconds"] == 60,
    "child_argv_shape": author_command["argv"][2] == repro_command["argv"][2] == "--calculate"
    and author_command["argv"][3] == repro_command["argv"][3] == "--output-dir"
    and author_command["argv"][4].endswith("results")
    and repro_command["argv"][4].endswith("results"),
}

direct_author = load(AUDIT / "direct-certificate.json")
direct_repro = load(AUDIT / "direct-certificate-reproduction.json")
direct_checks = {
    "author_result_certificate": direct_author["all_pass"] is True,
    "reproduction_result_certificate": direct_repro["all_pass"] is True,
    "case_23150070_direct_values": direct_author["case_23150070"]["direct"]
    == direct_repro["case_23150070"]["direct"],
    "case_23832572_direct_values": direct_author["case_23832572"]["direct"]
    == direct_repro["case_23832572"]["direct"],
}

byte_comparison = {}
for author_path in sorted(path for path in AUTHOR.rglob("*") if path.is_file()):
    relative = author_path.relative_to(AUTHOR).as_posix()
    reproduction_path = REPRO / relative
    byte_comparison[relative] = reproduction_path.is_file() and author_path.read_bytes() == reproduction_path.read_bytes()
noncommand_files_byte_equal = all(
    matches for relative, matches in byte_comparison.items() if relative != "command.json"
)

checks = {
    "preexecution_freeze_sha256": sha256(WORKER / "preexecution-freeze-attempt02.json")
    == EXPECTED_PREEXECUTION_SHA256,
    "result_freeze_sha256": sha256(WORKER / "result-freeze.json") == EXPECTED_RESULT_FREEZE_SHA256,
    "copied_inputs": all(item["pass"] for item in copy_checks),
    "author_result_freeze": all(item["pass"] for item in result_freeze_checks),
    "stable_records": all(stable_checks.values()),
    "direct_certificates": all(direct_checks.values()),
    "all_noncommand_files_byte_equal": noncommand_files_byte_equal,
}

result = {
    "schema_version": "external-witness-copied-reproduction-comparison-v1",
    "auditor": "/root/sol_symmetry_audit",
    "comparison_policy": "Compare mathematical values, statuses, exact-check maps, package versions, SMT assertions, and process outcomes; do not compare timestamps, elapsed durations, absolute paths, or output-directory names.",
    "inputs": {
        "preexecution_freeze_sha256": sha256(WORKER / "preexecution-freeze-attempt02.json"),
        "result_freeze_sha256": sha256(WORKER / "result-freeze.json"),
        "author_run": str(AUTHOR),
        "reproduction_run": str(REPRO),
    },
    "checks": checks,
    "stable_checks": stable_checks,
    "direct_checks": direct_checks,
    "byte_comparison": byte_comparison,
    "copied_input_checks": copy_checks,
    "author_result_freeze_checks": result_freeze_checks,
    "all_pass": all(checks.values()),
}

(AUDIT / "reproduction-compare.json").write_text(
    json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
    encoding="utf-8",
    newline="\n",
)
print(json.dumps({"all_pass": result["all_pass"]}, sort_keys=True))
raise SystemExit(0 if result["all_pass"] else 1)
