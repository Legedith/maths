from __future__ import annotations

import hashlib
import json
from datetime import datetime
from pathlib import Path


ROOT = Path("D:/CodexWorkspaces/mathematics-atlas")
PORTABLE = ROOT / "kemeny-portable-work"
PACKAGE = PORTABLE / "experiments/kemeny-pair-minimum"
AUTHOR = ROOT / "kemeny-author-work"
INDEPENDENT = ROOT / "kemeny-independent-work"
INPUTS = ROOT / "kemeny-input-work"
SPEC = ROOT / "kemeny-spec-work"
OUTPUT = ROOT / "kemeny-final-review-work/raw/portable-adapter-check.json"

EXPECTED_MANIFEST_SHA256 = "d5bbdd58126de29f2db378c08a287ac4d28272569ee386aa2347fbc6f898f420"
EXPECTED_FREEZE_SHA256 = "8c490bc29364495c4eb3e154193824d8eb8cc8cd49828259745fee12a23adaea"
EXPECTED_RUN_SHA256 = "096c85f7dea51516b2038b8585b42d4bc266ca1bb398663fde5207cdab51b08d"
EXPECTED_PINS_SHA256 = "a54738f15cdc11aa383a452e7a464be80aafe9eb3ad609e2313f65dfaa4b2b87"
EXPECTED_WRAPPER_SHA256 = "b6f4c329387705b2adf67f7dd3f806bbcd0a5906d476f5214fe8278d5ea5bfa6"


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def instant(value: str) -> datetime:
    return datetime.fromisoformat(value.replace("Z", "+00:00"))


def current_publishable_files(root: Path) -> set[str]:
    result = set()
    for path in root.rglob("*"):
        if not path.is_file():
            continue
        relative = path.relative_to(root)
        if relative.as_posix() == "result-manifest.json":
            continue
        if ".venv" in relative.parts or "__pycache__" in relative.parts or path.suffix == ".pyc":
            continue
        result.add(relative.as_posix())
    return result


def expected_upstream(relative: str) -> Path:
    path = Path(relative)
    parts = path.parts
    if parts[0] == "author" and parts[1] in {".python-version", "pyproject.toml", "uv.lock", "census.py"}:
        return AUTHOR / Path(*parts[1:])
    if parts[0] == "independent" and parts[1] in {
        ".python-version",
        "pyproject.toml",
        "uv.lock",
        "verify_census.py",
        "run_logged.py",
    }:
        return INDEPENDENT / Path(*parts[1:])
    if parts[:1] == ("docs",) and parts[1] == "contract-v1.md":
        return SPEC / "contract-v1.md"
    if parts[:1] == ("data",):
        return INPUTS / Path(*parts[1:])
    if parts[:2] == ("baseline", "author"):
        return AUTHOR / "run-01" / Path(*parts[2:])
    if parts[:2] == ("baseline", "independent"):
        return INDEPENDENT / "run-01" / Path(*parts[2:])
    raise AssertionError(relative)


def main() -> None:
    manifest_path = PORTABLE / "result-manifest.json"
    freeze_path = PACKAGE / "preexecution-freeze.json"
    run_path = PORTABLE / "integration-run-01/run.json"
    pins_path = PACKAGE / "source-pins.json"
    assert sha256(manifest_path) == EXPECTED_MANIFEST_SHA256
    assert sha256(freeze_path) == EXPECTED_FREEZE_SHA256
    assert sha256(run_path) == EXPECTED_RUN_SHA256
    assert sha256(pins_path) == EXPECTED_PINS_SHA256

    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    freeze = json.loads(freeze_path.read_text(encoding="utf-8"))
    run = json.loads(run_path.read_text(encoding="utf-8"))
    pins = json.loads(pins_path.read_text(encoding="utf-8"))

    assert manifest["schema_version"] == "kemeny-portable-result-manifest-v1"
    assert manifest["status"] == "sealed_author_portable_evidence_pending_independent_adapter_audit"
    artifacts = manifest["artifacts_excluding_environments_and_this_manifest"]
    assert manifest["artifact_count"] == len(artifacts) == 84
    assert len({item["path"] for item in artifacts}) == len(artifacts)
    assert current_publishable_files(PORTABLE) == {item["path"] for item in artifacts}
    for item in artifacts:
        path = PORTABLE / item["path"]
        assert path.stat().st_size == item["bytes"], path
        assert sha256(path) == item["sha256"], path

    assert freeze["schema_version"] == "kemeny-portable-preexecution-freeze-v1"
    assert freeze["status"] == "frozen_before_portable_integration_census"
    assert freeze["source_pins_sha256"] == EXPECTED_PINS_SHA256
    assert freeze["file_count_excluding_this_manifest_and_environments"] == len(freeze["files"]) == 32
    assert len({item["path"] for item in freeze["files"]}) == 32
    for item in freeze["files"]:
        path = PACKAGE / item["path"]
        assert path.stat().st_size == item["bytes"]
        assert sha256(path) == item["sha256"]

    assert pins["schema_version"] == "kemeny-portable-source-pins-v1"
    assert pins["status"] == "copied_from_sealed_sources"
    assert len(pins["files"]) == 27
    assert len({item["path"] for item in pins["files"]}) == 27
    upstream_checks = []
    for item in pins["files"]:
        relative = item["path"]
        assert not Path(relative).is_absolute() and ".." not in Path(relative).parts
        packaged = PACKAGE / relative
        upstream = expected_upstream(relative)
        assert packaged.stat().st_size == upstream.stat().st_size == item["bytes"]
        assert sha256(packaged) == sha256(upstream) == item["sha256"]
        assert packaged.read_bytes() == upstream.read_bytes()
        upstream_checks.append({
            "path": relative,
            "role": item["role"],
            "bytes": item["bytes"],
            "sha256": item["sha256"],
            "byte_identical_to_sealed_upstream": True,
        })
    wrapper = PACKAGE / "independent/run_logged.py"
    assert sha256(wrapper) == EXPECTED_WRAPPER_SHA256

    adapter_path = PACKAGE / "author/portable_entry.py"
    adapter_text = adapter_path.read_text(encoding="utf-8")
    required_adapter_fragments = (
        'EXPECTED_CONTRACT_SHA256 = "1ff78636c4dcadc7d8f9d6a3a36c144e193e5f90cbb970ab846c877cdf0c6ac6"',
        'EXPECTED_CENSUS_SHA256 = "6560176884fc4ce67b8da38465867f0a89491f087794258c7bd627225b5d6341"',
        'if sha256_file(source_path) != EXPECTED_CENSUS_SHA256:',
        'if sha256_file(contract_path) != EXPECTED_CONTRACT_SHA256:',
        'module.CONTRACT_PATH = contract_path',
        'return module.run_census(args.input_dir.resolve(), args.output_dir.resolve())',
    )
    assert all(fragment in adapter_text for fragment in required_adapter_fragments)
    assert adapter_text.count("module.") == 2

    runner_path = PACKAGE / "reproduce.py"
    runner_text = runner_path.read_text(encoding="utf-8")
    required_runner_fragments = (
        'EXPECTED_PYTHON = (3, 12, 11)',
        f'EXPECTED_SOURCE_PINS_SHA256 = "{EXPECTED_PINS_SHA256}"',
        'TIMEOUT_SECONDS = 1800',
        'if output_root.exists():',
        '"status": "rejected_existing_output_directory"',
        'output_root.relative_to(package_root)',
        '"status": "rejected_output_inside_immutable_package"',
        'package_verification = verify_pinned_package(package_root)',
        'output_root.mkdir(parents=True, exist_ok=False)',
        'if output_dir.exists():',
        'child_environment.pop("VIRTUAL_ENV", None)',
        'str(package_root / "independent/run_logged.py")',
        'stdout_path.write_bytes(stdout)',
        'stderr_path.write_bytes(stderr)',
        'byte_identical": reproduced_raw == baseline_raw',
    )
    assert all(fragment in runner_text for fragment in required_runner_fragments)
    assert runner_text.index("if output_root.exists():") < runner_text.index("package_verification = verify_pinned_package(package_root)")
    assert runner_text.index("output_root.relative_to(package_root)") < runner_text.index("package_verification = verify_pinned_package(package_root)")
    assert runner_text.index("package_verification = verify_pinned_package(package_root)") < runner_text.index("output_root.mkdir(parents=True, exist_ok=False)")
    assert runner_text.index('child_environment.pop("VIRTUAL_ENV", None)') < runner_text.index("process = subprocess.Popen(wrapper_command")

    assert instant(freeze["frozen_at_utc"]) < instant(run["started_at_utc"])
    assert instant(run["started_at_utc"]) < instant(run["ended_at_utc"])
    assert instant(run["ended_at_utc"]) < instant(manifest["sealed_at_utc"])
    assert run["schema_version"] == "kemeny-portable-run-v1"
    assert run["status"] == "complete_all_deterministic_outputs_byte_identical"
    assert run["requested_implementation"] == "both"
    assert run["timeout_seconds_per_census"] == 1800
    assert run["deterministic_file_count"] == 11
    assert run["all_byte_identical"] is True
    assert run["package_verification"]["source_pins_sha256"] == EXPECTED_PINS_SHA256
    assert run["package_verification"]["verified_file_count"] == 27
    assert len(run["package_verification"]["verified_files"]) == 27
    assert run["environment"]["python_version"] == "3.12.11"
    assert run["environment"]["uv_version_stdout"] == "uv 0.8.19 (fc7c2f8b5 2025-09-19)"

    assert [child["implementation"] for child in run["children"]] == ["author", "independent"]
    for child in run["children"]:
        assert child["return_code"] == child["wrapper_return_code"] == child["auditor_attempt"]["returncode"] == 0
        assert child["timed_out"] is False and child["auditor_attempt"]["timed_out"] is False
        assert child["timeout_seconds_for_census"] == child["auditor_attempt"]["timeout_seconds"] == 1800
        assert child["outer_wrapper_timeout_seconds"] == 1860
        assert child["logging_wrapper"]["sha256"] == EXPECTED_WRAPPER_SHA256
        assert child["auditor_attempt"]["termination"] is None
        assert child["auditor_attempt"]["selected_environment"]["UV_PROJECT_ENVIRONMENT"] is None
        assert child["auditor_attempt"]["stderr"]["bytes"] == 0
        for stream_name in ("stdout", "stderr"):
            item = child["auditor_attempt"][stream_name]
            stream_path = PORTABLE / "integration-run-01/logs" / item["path"]
            assert stream_path.stat().st_size == item["bytes"]
            assert sha256(stream_path) == item["sha256"]
        assert instant(child["started_at_utc"]) <= instant(child["auditor_attempt"]["started_at_utc"])
        assert instant(child["auditor_attempt"]["ended_at_utc"]) <= instant(child["ended_at_utc"])
    comparisons = run["comparisons"]
    assert [item["implementation"] for item in comparisons] == ["author", "independent"]
    assert sum(item["actual_file_count"] for item in comparisons) == 11
    for comparison in comparisons:
        assert comparison["actual_file_count"] == comparison["expected_file_count"]
        assert comparison["all_byte_identical"] is True
        expected_names = set(
            ["summary.json", "graph-values.json", "pairs.jsonl", "witnesses.json", "published-p7.json"]
            + (["completeness.json"] if comparison["implementation"] == "independent" else [])
        )
        assert {item["path"] for item in comparison["files"]} == expected_names
        for item in comparison["files"]:
            assert item["byte_identical"] is True
            assert item["baseline_bytes"] == item["reproduced_bytes"]
            assert item["baseline_sha256"] == item["reproduced_sha256"]
            baseline = PACKAGE / "baseline" / comparison["implementation"] / item["path"]
            reproduced = PORTABLE / "integration-run-01" / comparison["implementation"] / item["path"]
            assert baseline.read_bytes() == reproduced.read_bytes()

    outer = manifest["integration_evaluation"]["outer_attempt"]
    assert outer["returncode"] == 0 and outer["timed_out"] is False and outer["timeout_seconds"] == 3700
    assert manifest["integration_evaluation"]["run_record"]["sha256"] == EXPECTED_RUN_SHA256
    assert manifest["integration_evaluation"]["all_byte_identical"] is True
    assert manifest["integration_evaluation"]["deterministic_file_count"] == 11

    rejection = manifest["existing_directory_rejection_probe"]
    assert rejection["outer_attempt"]["returncode"] == 2
    assert rejection["outer_attempt"]["timed_out"] is False
    assert rejection["status"]["status"] == "rejected_existing_output_directory"
    assert rejection["status"]["child_invocations"] == 0
    assert rejection["sentinel_unchanged"] is True
    sentinel = PORTABLE / "existing-output-probe/sentinel.txt"
    assert sentinel.read_bytes() == b"must remain unchanged"
    rejection_stderr = PORTABLE / "evidence/rejection/attempt-existing-dir-01.stderr.bin"
    assert json.loads(rejection_stderr.read_text(encoding="utf-8")) == rejection["status"]

    report = {
        "schema_version": "kemeny-portable-adapter-independent-check-v1",
        "auditor": "/root/sol_symmetry_audit",
        "status": "pass_with_platform_scope_limit",
        "inputs": {
            "result_manifest": {"path": str(manifest_path), "bytes": manifest_path.stat().st_size, "sha256": sha256(manifest_path)},
            "preexecution_freeze": {"path": str(freeze_path), "bytes": freeze_path.stat().st_size, "sha256": sha256(freeze_path)},
            "integration_run": {"path": str(run_path), "bytes": run_path.stat().st_size, "sha256": sha256(run_path)},
            "source_pins": {"path": str(pins_path), "bytes": pins_path.stat().st_size, "sha256": sha256(pins_path)},
        },
        "manifest_integrity": {
            "status": "pass",
            "artifact_count": len(artifacts),
            "all_current_non_environment_files_exactly_accounted_for": True,
            "all_recorded_bytes_and_sha256_match": True,
        },
        "source_alignment": {
            "status": "pass",
            "pin_count": len(upstream_checks),
            "all_pinned_package_files_byte_identical_to_sealed_upstream": True,
            "author_mathematical_source_unchanged": True,
            "independent_mathematical_source_unchanged": True,
            "contract_inputs_environments_baselines_and_wrapper_unchanged": True,
            "checks": upstream_checks,
        },
        "adapter_alignment": {
            "status": "pass",
            "author_adapter_sha256": sha256(adapter_path),
            "runner_sha256": sha256(runner_path),
            "author_adapter_effect": (
                "Hash-check the unchanged census and packaged contract, assign only the imported module's "
                "CONTRACT_PATH, then call the unchanged run_census with resolved explicit paths."
            ),
            "runner_effect": (
                "Verify 27 pinned package files, select pinned uv projects, remove inherited VIRTUAL_ENV, invoke "
                "both unchanged evaluators through the sealed independent wrapper, retain raw logs, and compare "
                "the exact expected output file sets byte-for-byte."
            ),
            "no_mathematical_predicate_or_evaluator_change": True,
        },
        "integration_reproduction": {
            "status": "pass_on_recorded_windows_environment",
            "python_version": run["environment"]["python_version"],
            "uv_version": run["environment"]["uv_version_stdout"],
            "children": [
                {
                    "implementation": child["implementation"],
                    "return_code": child["return_code"],
                    "timed_out": child["timed_out"],
                    "duration_seconds": child["duration_seconds"],
                }
                for child in run["children"]
            ],
            "deterministic_file_count": 11,
            "all_outputs_byte_identical": True,
        },
        "no_overwrite_boundary": {
            "status": "pass",
            "root_output_must_not_exist": True,
            "child_output_must_not_exist": True,
            "output_inside_package_rejected_by_resolved_path_check": True,
            "recorded_existing_directory_probe_returncode": 2,
            "recorded_existing_directory_probe_child_invocations": 0,
            "recorded_sentinel_unchanged": True,
        },
        "limitations": [
            "The retained integration replay was executed on Windows 10. Static review finds a POSIX process-group branch and no staging-specific path in the portable flow, but this audit does not claim an observed Ubuntu replay.",
            "The package reproduces two frozen finite computations; it is not a third mathematical implementation and adds no novelty or performance evidence.",
            "The source-pins manifest protects every mathematical input, environment lock, wrapper and baseline. The adapter and runner are instead pinned by the preexecution freeze and final result manifest, as expected for code that reads source-pins.json.",
        ],
    }
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8", newline="\n")
    print(json.dumps({"status": report["status"], "output": str(OUTPUT), "sha256": sha256(OUTPUT)}, sort_keys=True))


if __name__ == "__main__":
    main()
