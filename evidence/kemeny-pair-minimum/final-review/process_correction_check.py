from __future__ import annotations

import hashlib
import json
import ntpath
from datetime import datetime
from fractions import Fraction
from pathlib import Path


ROOT = Path("D:/CodexWorkspaces/mathematics-atlas")
CORRECTION = ROOT / "kemeny-study-work/process-correction"
AUTHOR = ROOT / "kemeny-author-work"
INDEPENDENT = ROOT / "kemeny-independent-work"
OUTPUT = ROOT / "kemeny-final-review-work/raw/process-correction-check.json"

EXPECTED_FREEZE_SHA256 = "387e46dd4e66e2b2f08f2b5e849f59c989817038007fa08a7ae8277f71174703"
EXPECTED_COMPARISON_SHA256 = "83163cbc70e953684bf15ddeb8dd7e112260d2872099744719326c852912ace3"
EXPECTED_WRAPPER_SHA256 = "b6f4c329387705b2adf67f7dd3f806bbcd0a5906d476f5214fe8278d5ea5bfa6"
EXPECTED_STDERR = (
    "warning: `VIRTUAL_ENV=D:\\CodexWorkspaces\\mathematics-atlas\\"
    "kemeny-independent-work\\.venv` does not match the project environment path "
    "`.venv` and will be ignored; use `--active` to target the active environment instead\n"
).encode("utf-8")
OUTPUT_NAMES = (
    "summary.json",
    "graph-values.json",
    "pairs.jsonl",
    "witnesses.json",
    "published-p7.json",
)


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def instant(value: str) -> datetime:
    return datetime.fromisoformat(value.replace("Z", "+00:00"))


def canonical_windows_path(value: str) -> str:
    return ntpath.normcase(ntpath.normpath(value.replace("/", "\\")))


def assert_semantic_argv(expected: list[str], actual: list[str]) -> list[int]:
    assert len(expected) == len(actual) == 11
    path_positions = [3, 6, 8, 10]
    for index, (left, right) in enumerate(zip(expected, actual, strict=True)):
        if index in path_positions:
            assert canonical_windows_path(left) == canonical_windows_path(right), (index, left, right)
        else:
            assert left == right, (index, left, right)
    return path_positions


def rational(record: dict[str, int]) -> Fraction:
    assert set(record) == {"numerator", "denominator"}
    return Fraction(record["numerator"], record["denominator"])


def strict_count(path: Path, flavor: str) -> tuple[int, dict[int, int]]:
    total = 0
    by_order = {n: 0 for n in range(2, 7)}
    with path.open("r", encoding="utf-8", newline="") as stream:
        for line in stream:
            assert line.endswith("\n")
            row = json.loads(line)
            if flavor == "author":
                e = rational(row["deltas"]["single_e_minus_base"])
                f = rational(row["deltas"]["single_f_minus_base"])
                both = rational(row["deltas"]["joint_minus_base"])
            else:
                e = rational(row["deltas"]["e"])
                f = rational(row["deltas"]["f"])
                both = rational(row["deltas"]["both"])
            qualifies = e < 0 and f < 0 and both > 0
            if qualifies:
                total += 1
                by_order[int(row["n"])] += 1
    return total, by_order


def main() -> None:
    freeze_path = CORRECTION / "freeze.json"
    comparison_path = CORRECTION / "comparison.json"
    assert sha256(freeze_path) == EXPECTED_FREEZE_SHA256
    assert sha256(comparison_path) == EXPECTED_COMPARISON_SHA256
    freeze = json.loads(freeze_path.read_text(encoding="utf-8"))
    comparison = json.loads(comparison_path.read_text(encoding="utf-8"))

    assert freeze["schema_version"] == "kemeny-author-wrapper-correction-freeze-v1"
    assert freeze["status"] == "frozen_before_corrective_run"
    assert freeze["approved_correction_method_by"] == "/root/sol_symmetry_audit"
    assert freeze["timeout_seconds"] == 1800
    assert freeze["output_and_log_dirs_absent_before_execution"] is True
    assert "author-owned wrapper" in freeze["deviation"]
    assert "independent auditor-owned" in freeze["correction"]
    assert freeze["claims_not_authorized"] == [
        "changed original chronology",
        "new mathematical method",
        "new candidate search",
        "publication novelty",
    ]

    pins = freeze["pins"]
    assert len(pins) == 42
    assert len({canonical_windows_path(item["path"]) for item in pins}) == len(pins)
    for pin in pins:
        path = Path(pin["path"])
        assert path.stat().st_size == pin["bytes"], path
        assert sha256(path) == pin["sha256"], path
    wrapper_pins = [item for item in pins if item["role"] == "independent_auditor_owned_wrapper"]
    assert len(wrapper_pins) == 1
    assert wrapper_pins[0]["sha256"] == EXPECTED_WRAPPER_SHA256
    assert canonical_windows_path(wrapper_pins[0]["path"]) == canonical_windows_path(str(INDEPENDENT / "run_logged.py"))

    independent_freeze_path = INDEPENDENT / "input-freeze-manifest.json"
    independent_freeze = json.loads(independent_freeze_path.read_text(encoding="utf-8"))
    sealed_wrapper = [
        item for item in independent_freeze["files"]
        if canonical_windows_path(item["path"]) == canonical_windows_path(str(INDEPENDENT / "run_logged.py"))
    ]
    assert len(sealed_wrapper) == 1
    assert sealed_wrapper[0]["role"] == "independent_owned_preexecution"
    assert sealed_wrapper[0]["sha256"] == EXPECTED_WRAPPER_SHA256
    wrapper_text = (INDEPENDENT / "run_logged.py").read_text(encoding="utf-8")
    for required_fragment in (
        "process.communicate(timeout=args.timeout_seconds)",
        "terminate_process_tree(process)",
        "stdout_path.write_bytes(stdout)",
        "stderr_path.write_bytes(stderr)",
        '"started_at_utc": started',
        '"ended_at_utc": ended',
        '"returncode": None if timed_out else process.returncode',
    ):
        assert required_fragment in wrapper_text

    attempt_path = CORRECTION / "logs/attempt-author-correction-02.json"
    attempts_path = CORRECTION / "logs/attempts.jsonl"
    attempt = json.loads(attempt_path.read_text(encoding="utf-8"))
    attempt_lines = attempts_path.read_text(encoding="utf-8").splitlines()
    assert len(attempt_lines) == 1
    assert json.loads(attempt_lines[0]) == attempt
    assert attempt["schema_version"] == "logged-command-attempt-v1"
    assert attempt["attempt_id"] == "author-correction-02"
    assert attempt["timeout_seconds"] == 1800
    assert attempt["timed_out"] is False
    assert attempt["termination"] is None
    assert attempt["returncode"] == 0
    assert canonical_windows_path(attempt["working_directory"]) == canonical_windows_path(freeze["working_directory"])
    normalized_positions = assert_semantic_argv(freeze["child_argv"], attempt["argv"])
    assert attempt["selected_environment"] == {
        "PYTHONDONTWRITEBYTECODE": "1",
        "UV_CACHE_DIR": "D:\\CodexWorkspaces\\mathematics-atlas\\uv-cache",
        "UV_PROJECT_ENVIRONMENT": None,
    }

    stdout_path = CORRECTION / "logs" / attempt["stdout"]["path"]
    stderr_path = CORRECTION / "logs" / attempt["stderr"]["path"]
    for record, path in ((attempt["stdout"], stdout_path), (attempt["stderr"], stderr_path)):
        assert path.stat().st_size == record["bytes"]
        assert sha256(path) == record["sha256"]
    assert stderr_path.read_bytes() == EXPECTED_STDERR
    stdout = json.loads(stdout_path.read_text(encoding="utf-8"))
    assert stdout == {
        "candidate_minimum_order": 6,
        "output_dir": str(CORRECTION / "author-run-02"),
        "pair_count": 2390,
        "status": "complete_author_evaluation_pending_independent_verification",
        "witness_count_through_order_6": 1,
    }

    assert instant(freeze["frozen_at_utc"]) < instant(attempt["started_at_utc"])
    assert instant(attempt["started_at_utc"]) < instant(attempt["ended_at_utc"])
    assert instant(attempt["ended_at_utc"]) < instant(comparison["checked_at_utc"])
    elapsed_seconds = (instant(attempt["ended_at_utc"]) - instant(attempt["started_at_utc"])).total_seconds()
    assert 0 < elapsed_seconds < 1800

    assert comparison["schema_version"] == "kemeny-author-wrapper-correction-comparison-v1"
    assert comparison["freeze_sha256"] == EXPECTED_FREEZE_SHA256
    assert comparison["all_frozen_pins_unchanged"] is True
    assert len(comparison["pins"]) == 42 and all(item["match"] is True for item in comparison["pins"])
    assert comparison["returncode"] == 0
    assert comparison["timed_out"] is False
    assert comparison["timeout_seconds"] == 1800
    assert comparison["all_five_outputs_byte_identical"] is True
    assert comparison["stdout_only_output_path_differs"] is True
    assert comparison["stderr_bytes"] == len(EXPECTED_STDERR)
    assert comparison["stderr_text"].encode("utf-8") == EXPECTED_STDERR
    assert {item["name"] for item in comparison["files"]} == set(OUTPUT_NAMES)
    assert {path.name for path in (CORRECTION / "author-run-02").iterdir() if path.is_file()} == set(OUTPUT_NAMES)
    output_checks = []
    for record in comparison["files"]:
        new = CORRECTION / "author-run-02" / record["name"]
        old = AUTHOR / "run-01" / record["name"]
        assert new.stat().st_size == old.stat().st_size == record["bytes"]
        assert sha256(new) == sha256(old) == record["sha256"] == record["original_sha256"]
        assert new.read_bytes() == old.read_bytes()
        assert record["byte_identical"] is True
        output_checks.append({
            "name": record["name"],
            "bytes": record["bytes"],
            "sha256": record["sha256"],
            "byte_identical_to_original": True,
        })

    original_stdout = json.loads((AUTHOR / "logs/canonical-01/stdout.txt").read_text(encoding="utf-8"))
    new_without_path = {key: value for key, value in stdout.items() if key != "output_dir"}
    old_without_path = {key: value for key, value in original_stdout.items() if key != "output_dir"}
    assert new_without_path == old_without_path
    assert canonical_windows_path(original_stdout["output_dir"]) == canonical_windows_path(comparison["stdout_paths"]["old"])
    assert canonical_windows_path(stdout["output_dir"]) == canonical_windows_path(comparison["stdout_paths"]["new"])

    author_strict_total, author_strict_by_order = strict_count(AUTHOR / "run-01/pairs.jsonl", "author")
    independent_strict_total, independent_strict_by_order = strict_count(
        INDEPENDENT / "run-01/pairs.jsonl", "independent"
    )
    assert author_strict_total == independent_strict_total == 0
    assert author_strict_by_order == independent_strict_by_order == {n: 0 for n in range(2, 7)}
    p7 = json.loads((AUTHOR / "run-01/published-p7.json").read_text(encoding="utf-8"))
    p7_deltas = {
        "e": rational(p7["deltas"]["single_e_minus_base"]),
        "f": rational(p7["deltas"]["single_f_minus_base"]),
        "both": rational(p7["deltas"]["joint_minus_base"]),
    }
    assert p7_deltas == {"e": Fraction(-1, 14), "f": Fraction(-1, 14), "both": Fraction(1, 24)}

    report = {
        "schema_version": "kemeny-process-correction-independent-check-v1",
        "auditor": "/root/sol_symmetry_audit",
        "status": "pass",
        "inputs": {
            "freeze": {"path": str(freeze_path), "bytes": freeze_path.stat().st_size, "sha256": sha256(freeze_path)},
            "comparison": {"path": str(comparison_path), "bytes": comparison_path.stat().st_size, "sha256": sha256(comparison_path)},
            "wrapper": {
                "path": str(INDEPENDENT / "run_logged.py"),
                "bytes": (INDEPENDENT / "run_logged.py").stat().st_size,
                "sha256": sha256(INDEPENDENT / "run_logged.py"),
                "owner_from_preexecution_seal": independent_freeze["owner"],
            },
        },
        "checks": {
            "freeze_precedes_run": True,
            "all_42_pins_currently_match": True,
            "wrapper_was_independently_owned_and_preexecution_sealed": True,
            "wrapper_records_timeout_argv_cwd_utc_result_and_raw_streams": True,
            "child_argv_matches_freeze_after_windows_separator_normalization": True,
            "normalized_path_positions": normalized_positions,
            "returncode_zero": True,
            "not_timed_out": True,
            "elapsed_seconds": elapsed_seconds,
            "stdout_and_stderr_hashes_match": True,
            "five_deterministic_outputs_byte_identical_to_original": True,
            "outputs": output_checks,
        },
        "verdict": {
            "literal_wrapper_requirement": "satisfied_by_documented_corrective_rerun",
            "original_run": "retained_with_author-wrapper-ownership_deviation",
            "mathematical_result_changed": False,
            "stderr_interpretation": (
                "A single uv warning records that the inherited independent-project VIRTUAL_ENV was ignored "
                "because it did not match the inner author project. With --project fixed to the author project, "
                "this is environment-selection disclosure and not a mathematical failure."
            ),
            "path_interpretation": (
                "The freeze used Windows backslashes and the logged child argv used forward slashes at four "
                "absolute-path positions; ntpath normalization gives the same paths and every non-path token is exact."
            ),
        },
        "post_hoc_strict_singleton_corollary": {
            "status": "pass_as_secondary_derived_result",
            "definition": "delta_e<0 and delta_f<0 and delta_both>0",
            "strict_witness_count_through_order_6_author": author_strict_total,
            "strict_witness_count_through_order_6_independent": independent_strict_total,
            "strict_witness_counts_by_order": {str(n): author_strict_by_order[n] for n in range(2, 7)},
            "published_p7_deltas": {
                name: {"numerator": value.numerator, "denominator": value.denominator}
                for name, value in p7_deltas.items()
            },
            "minimum_order": 7,
            "logic": (
                "Every strict-singleton witness is also a weak-singleton witness. The complete unchanged ledger "
                "contains none at orders 2 through 5 and its unique weak witness at order 6 has delta_f=0, while "
                "the separately fixed published P7 control has both singleton deltas negative and its joint delta positive."
            ),
            "scope": (
                "Post hoc logical corollary of the frozen ledger and preselected P7 control; it was not the "
                "preregistered primary predicate and carries no novelty claim."
            ),
        },
        "limitations": [
            "The original author run remains a preserved process deviation; the corrective run repairs wrapper ownership prospectively and does not rewrite its chronology.",
            "The correction freeze records that output and log directories were absent before execution; this independent post-run review verifies chronology and resulting files but cannot retroactively observe directory absence.",
            "The wrapper evidence and recorded ownership establish the scoped process record; they cannot prove a universal negative about unrecorded filesystem access.",
        ],
    }
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8", newline="\n")
    print(json.dumps({"status": "pass", "output": str(OUTPUT), "sha256": sha256(OUTPUT)}, sort_keys=True))


if __name__ == "__main__":
    main()
