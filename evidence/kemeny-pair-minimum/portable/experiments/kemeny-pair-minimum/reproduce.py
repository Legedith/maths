from __future__ import annotations

import argparse
import hashlib
import json
import os
import platform
import shutil
import signal
import subprocess
import sys
import time
import traceback
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


EXPECTED_PYTHON = (3, 12, 11)
EXPECTED_SOURCE_PINS_SHA256 = "a54738f15cdc11aa383a452e7a464be80aafe9eb3ad609e2313f65dfaa4b2b87"
TIMEOUT_SECONDS = 1800
BASELINE_FILES = {
    "author": [
        "summary.json",
        "graph-values.json",
        "pairs.jsonl",
        "witnesses.json",
        "published-p7.json",
    ],
    "independent": [
        "summary.json",
        "graph-values.json",
        "pairs.jsonl",
        "witnesses.json",
        "published-p7.json",
        "completeness.json",
    ],
}


class ReproductionError(RuntimeError):
    pass


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def file_record(path: Path, *, relative_to: Path | None = None) -> dict[str, Any]:
    raw = path.read_bytes()
    displayed = path.relative_to(relative_to).as_posix() if relative_to else path.as_posix()
    return {"path": displayed, "bytes": len(raw), "sha256": sha256_bytes(raw)}


def json_bytes(value: object, *, pretty: bool = True) -> bytes:
    options: dict[str, Any] = {"ensure_ascii": True, "sort_keys": True}
    if pretty:
        options["indent"] = 2
    else:
        options["separators"] = (",", ":")
    return (json.dumps(value, **options) + "\n").encode("utf-8")


def write_json(path: Path, value: object) -> None:
    path.write_bytes(json_bytes(value))


def verify_pinned_package(package_root: Path) -> dict[str, Any]:
    pins_path = package_root / "source-pins.json"
    raw = pins_path.read_bytes()
    actual_manifest_sha = sha256_bytes(raw)
    if actual_manifest_sha != EXPECTED_SOURCE_PINS_SHA256:
        raise ReproductionError(
            f"source-pins.json hash mismatch: {actual_manifest_sha}"
        )
    pins = json.loads(raw)
    verified: list[dict[str, Any]] = []
    for expected in pins["files"]:
        relative_path = Path(expected["path"])
        if relative_path.is_absolute() or ".." in relative_path.parts:
            raise ReproductionError(f"unsafe pinned path: {expected['path']}")
        path = package_root / relative_path
        if not path.is_file():
            raise ReproductionError(f"missing pinned file: {expected['path']}")
        actual = file_record(path, relative_to=package_root)
        if actual != {
            "path": expected["path"],
            "bytes": expected["bytes"],
            "sha256": expected["sha256"],
        }:
            raise ReproductionError(
                f"pinned file mismatch for {expected['path']}: {actual}"
            )
        verified.append({**actual, "role": expected["role"]})
    return {
        "source_pins_sha256": actual_manifest_sha,
        "verified_file_count": len(verified),
        "verified_files": verified,
        "upstream_seals": pins["upstream_seals"],
    }


def terminate_owned_process_tree(process: subprocess.Popen[bytes]) -> dict[str, Any]:
    result: dict[str, Any] = {"method": None, "errors": []}
    if process.poll() is not None:
        result["method"] = "already_exited"
        return result
    try:
        if os.name == "nt":
            completed = subprocess.run(
                ["taskkill", "/PID", str(process.pid), "/T", "/F"],
                capture_output=True,
                check=False,
                timeout=30,
            )
            result.update(
                {
                    "method": "taskkill_explicit_owned_pid_tree",
                    "taskkill_return_code": completed.returncode,
                    "taskkill_stdout_sha256": sha256_bytes(completed.stdout),
                    "taskkill_stderr_sha256": sha256_bytes(completed.stderr),
                }
            )
        else:
            os.killpg(os.getpgid(process.pid), signal.SIGKILL)
            result["method"] = "sigkill_owned_process_group"
    except Exception as error:  # pragma: no cover - only reached after a timeout
        result["errors"].append(f"{type(error).__name__}: {error}")
        try:
            process.kill()
            result["fallback"] = "direct_child_kill"
        except Exception as fallback_error:
            result["errors"].append(
                f"fallback {type(fallback_error).__name__}: {fallback_error}"
            )
    return result


def run_child(
    *,
    implementation: str,
    package_root: Path,
    output_dir: Path,
    logs_dir: Path,
    uv_executable: str,
) -> dict[str, Any]:
    if output_dir.exists():
        raise ReproductionError(
            f"child output directory already exists before invocation: {output_dir}"
        )
    project_dir = package_root / implementation
    if implementation == "author":
        portable_command = [
            "uv",
            "run",
            "--project",
            "author",
            "--frozen",
            "python",
            "author/portable_entry.py",
            "--input-dir",
            "data",
            "--output-dir",
            output_dir.as_posix(),
            "--contract-path",
            "docs/contract-v1.md",
        ]
        census_command = [
            uv_executable,
            "run",
            "--project",
            str(project_dir),
            "--frozen",
            "python",
            str(package_root / "author/portable_entry.py"),
            "--input-dir",
            str(package_root / "data"),
            "--output-dir",
            str(output_dir),
            "--contract-path",
            str(package_root / "docs/contract-v1.md"),
        ]
    elif implementation == "independent":
        portable_command = [
            "uv",
            "run",
            "--project",
            "independent",
            "--frozen",
            "python",
            "independent/verify_census.py",
            "--input-dir",
            "data",
            "--output-dir",
            output_dir.as_posix(),
        ]
        census_command = [
            uv_executable,
            "run",
            "--project",
            str(project_dir),
            "--frozen",
            "python",
            str(package_root / "independent/verify_census.py"),
            "--input-dir",
            str(package_root / "data"),
            "--output-dir",
            str(output_dir),
        ]
    else:  # pragma: no cover - caller restricts this value
        raise ReproductionError(f"unknown implementation: {implementation}")

    attempt_id = f"portable-{implementation}"
    wrapper_command = [
        sys.executable,
        str(package_root / "independent/run_logged.py"),
        "--attempt-id",
        attempt_id,
        "--timeout-seconds",
        str(TIMEOUT_SECONDS),
        "--log-dir",
        str(logs_dir),
        "--",
        *census_command,
    ]

    child_environment = os.environ.copy()
    child_environment.pop("VIRTUAL_ENV", None)
    popen_options: dict[str, Any] = {
        "cwd": package_root,
        "env": child_environment,
        "stdout": subprocess.PIPE,
        "stderr": subprocess.PIPE,
    }
    if os.name == "nt":
        popen_options["creationflags"] = subprocess.CREATE_NEW_PROCESS_GROUP
    else:
        popen_options["start_new_session"] = True

    started_at = utc_now()
    started_monotonic = time.monotonic()
    process = subprocess.Popen(wrapper_command, **popen_options)
    outer_timed_out = False
    outer_cleanup: dict[str, Any] | None = None
    try:
        stdout, stderr = process.communicate(timeout=TIMEOUT_SECONDS + 60)
    except subprocess.TimeoutExpired:
        outer_timed_out = True
        outer_cleanup = terminate_owned_process_tree(process)
        stdout, stderr = process.communicate(timeout=30)
    ended_at = utc_now()
    duration_seconds = time.monotonic() - started_monotonic

    stdout_path = logs_dir / f"{implementation}.wrapper.stdout.bin"
    stderr_path = logs_dir / f"{implementation}.wrapper.stderr.bin"
    stdout_path.write_bytes(stdout)
    stderr_path.write_bytes(stderr)
    attempt_record_path = logs_dir / f"attempt-{attempt_id}.json"
    attempt_record = (
        json.loads(attempt_record_path.read_bytes())
        if attempt_record_path.is_file()
        else None
    )
    census_timed_out = bool(attempt_record and attempt_record["timed_out"])
    timed_out = outer_timed_out or census_timed_out
    target_return_code = (
        attempt_record["returncode"] if attempt_record is not None else None
    )
    effective_return_code = (
        124
        if timed_out
        else target_return_code
        if target_return_code is not None
        else process.returncode
    )
    record = {
        "implementation": implementation,
        "started_at_utc": started_at,
        "ended_at_utc": ended_at,
        "duration_seconds": duration_seconds,
        "timeout_seconds_for_census": TIMEOUT_SECONDS,
        "outer_wrapper_timeout_seconds": TIMEOUT_SECONDS + 60,
        "timed_out": timed_out,
        "return_code": effective_return_code,
        "cwd": package_root.as_posix(),
        "logging_wrapper": {
            "path": "independent/run_logged.py",
            "sha256": "b6f4c329387705b2adf67f7dd3f806bbcd0a5906d476f5214fe8278d5ea5bfa6",
            "lineage": "byte-identical independent auditor B wrapper",
        },
        "wrapper_argv": wrapper_command,
        "census_argv": census_command,
        "portable_argv_from_package_root": portable_command,
        "wrapper_return_code": process.returncode,
        "wrapper_stdout": file_record(stdout_path, relative_to=logs_dir.parent),
        "wrapper_stderr": file_record(stderr_path, relative_to=logs_dir.parent),
        "auditor_attempt_record": (
            file_record(attempt_record_path, relative_to=logs_dir.parent)
            if attempt_record_path.is_file()
            else None
        ),
        "auditor_attempt": attempt_record,
        "outer_cleanup": outer_cleanup,
    }
    write_json(logs_dir / f"{implementation}.command.json", record)
    return record


def compare_baseline(
    *, implementation: str, package_root: Path, output_dir: Path
) -> dict[str, Any]:
    expected_names = BASELINE_FILES[implementation]
    actual_names = sorted(
        path.relative_to(output_dir).as_posix()
        for path in output_dir.rglob("*")
        if path.is_file()
    )
    if actual_names != sorted(expected_names):
        raise ReproductionError(
            f"unexpected {implementation} output file set: {actual_names}"
        )
    comparisons: list[dict[str, Any]] = []
    for name in expected_names:
        baseline = package_root / "baseline" / implementation / name
        reproduced = output_dir / name
        baseline_raw = baseline.read_bytes()
        reproduced_raw = reproduced.read_bytes()
        item = {
            "path": name,
            "baseline_bytes": len(baseline_raw),
            "baseline_sha256": sha256_bytes(baseline_raw),
            "reproduced_bytes": len(reproduced_raw),
            "reproduced_sha256": sha256_bytes(reproduced_raw),
            "byte_identical": reproduced_raw == baseline_raw,
        }
        comparisons.append(item)
        if not item["byte_identical"]:
            raise ReproductionError(
                f"{implementation} output differs from baseline: {name}"
            )
    return {
        "implementation": implementation,
        "expected_file_count": len(expected_names),
        "actual_file_count": len(actual_names),
        "all_byte_identical": True,
        "files": comparisons,
    }


def runner_environment(uv_executable: str) -> dict[str, Any]:
    completed = subprocess.run(
        [uv_executable, "--version"], capture_output=True, check=False, timeout=30
    )
    if completed.returncode != 0:
        raise ReproductionError("uv --version failed")
    return {
        "python_version": platform.python_version(),
        "python_executable": sys.executable,
        "platform": platform.platform(),
        "os_name": os.name,
        "uv_executable": uv_executable,
        "uv_version_stdout": completed.stdout.decode("utf-8", errors="strict").strip(),
        "uv_version_stderr": completed.stderr.decode("utf-8", errors="strict").strip(),
        "uv_cache_dir": os.environ.get("UV_CACHE_DIR"),
        "author_project": "author/pyproject.toml",
        "independent_project": "independent/pyproject.toml",
    }


def final_status_bytes(status: dict[str, Any]) -> bytes:
    return json_bytes(status, pretty=False)


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Reproduce the two frozen exact Kemeny censuses and compare all outputs byte-for-byte."
    )
    parser.add_argument("--output-dir", required=True, type=Path)
    parser.add_argument(
        "--implementation",
        choices=("both", "author", "independent"),
        default="both",
        help="default: both",
    )
    args = parser.parse_args()

    package_root = Path(__file__).resolve().parent
    output_root = args.output_dir.resolve()
    if output_root.exists():
        status = {
            "schema_version": "kemeny-portable-run-status-v1",
            "status": "rejected_existing_output_directory",
            "output_dir": output_root.as_posix(),
            "child_invocations": 0,
        }
        sys.stderr.buffer.write(final_status_bytes(status))
        return 2
    try:
        output_root.relative_to(package_root)
    except ValueError:
        pass
    else:
        status = {
            "schema_version": "kemeny-portable-run-status-v1",
            "status": "rejected_output_inside_immutable_package",
            "output_dir": output_root.as_posix(),
            "child_invocations": 0,
        }
        sys.stderr.buffer.write(final_status_bytes(status))
        return 2

    if sys.version_info[:3] != EXPECTED_PYTHON:
        raise ReproductionError(
            f"runner Python {platform.python_version()} does not equal 3.12.11"
        )
    package_verification = verify_pinned_package(package_root)
    uv_executable = shutil.which("uv")
    if uv_executable is None:
        raise ReproductionError("uv executable not found on PATH")
    environment = runner_environment(uv_executable)

    output_root.mkdir(parents=True, exist_ok=False)
    logs_dir = output_root / "logs"
    logs_dir.mkdir()
    implementations = (
        ["author", "independent"]
        if args.implementation == "both"
        else [args.implementation]
    )
    record: dict[str, Any] = {
        "schema_version": "kemeny-portable-run-v1",
        "status": "running",
        "started_at_utc": utc_now(),
        "package_root": package_root.as_posix(),
        "output_root": output_root.as_posix(),
        "requested_implementation": args.implementation,
        "timeout_seconds_per_census": TIMEOUT_SECONDS,
        "runner_argv": [sys.executable, str(Path(__file__).resolve()), *sys.argv[1:]],
        "canonical_repository_root_argv": [
            "uv",
            "run",
            "--project",
            "experiments/kemeny-pair-minimum/independent",
            "--frozen",
            "python",
            "experiments/kemeny-pair-minimum/reproduce.py",
            "--output-dir",
            "work/kemeny-pair-run",
        ],
        "environment": environment,
        "package_verification": package_verification,
        "children": [],
        "comparisons": [],
    }
    write_json(output_root / "run.json", record)

    try:
        for implementation in implementations:
            child_output = output_root / implementation
            child = run_child(
                implementation=implementation,
                package_root=package_root,
                output_dir=child_output,
                logs_dir=logs_dir,
                uv_executable=uv_executable,
            )
            record["children"].append(child)
            write_json(output_root / "run.json", record)
            if child["timed_out"]:
                raise ReproductionError(
                    f"{implementation} census exceeded {TIMEOUT_SECONDS} seconds"
                )
            if child["return_code"] != 0:
                raise ReproductionError(
                    f"{implementation} census returned {child['return_code']}"
                )
            comparison = compare_baseline(
                implementation=implementation,
                package_root=package_root,
                output_dir=child_output,
            )
            record["comparisons"].append(comparison)
            write_json(output_root / "run.json", record)
        record["status"] = "complete_all_deterministic_outputs_byte_identical"
        record["ended_at_utc"] = utc_now()
        record["deterministic_file_count"] = sum(
            item["expected_file_count"] for item in record["comparisons"]
        )
        record["all_byte_identical"] = all(
            item["all_byte_identical"] for item in record["comparisons"]
        )
        record["limitations"] = [
            "This is a packaging reproduction of two frozen finite computations, not a new mathematical evaluation design.",
            "Byte identity establishes reproduction of the retained deterministic files; final evidence certification remains independent.",
            "The portable replay uses the byte-identical independent-auditor logging wrapper; it does not repair or restate the chronology of the original author run.",
            "No novelty claim is made.",
        ]
        write_json(output_root / "run.json", record)
        status = {
            "schema_version": "kemeny-portable-run-status-v1",
            "status": record["status"],
            "output_dir": output_root.as_posix(),
            "child_invocations": len(record["children"]),
            "deterministic_file_count": record["deterministic_file_count"],
            "all_byte_identical": record["all_byte_identical"],
            "run_record_sha256": sha256_file(output_root / "run.json"),
        }
        status_raw = final_status_bytes(status)
        (logs_dir / "runner.stdout.txt").write_bytes(status_raw)
        (logs_dir / "runner.stderr.txt").write_bytes(b"")
        sys.stdout.buffer.write(status_raw)
        return 0
    except Exception as error:
        record["status"] = "failed"
        record["ended_at_utc"] = utc_now()
        record["error"] = {
            "type": type(error).__name__,
            "message": str(error),
            "traceback": traceback.format_exc(),
        }
        write_json(output_root / "run.json", record)
        status = {
            "schema_version": "kemeny-portable-run-status-v1",
            "status": "failed",
            "output_dir": output_root.as_posix(),
            "child_invocations": len(record["children"]),
            "error_type": type(error).__name__,
            "message": str(error),
            "run_record_sha256": sha256_file(output_root / "run.json"),
        }
        status_raw = final_status_bytes(status)
        (logs_dir / "runner.stdout.txt").write_bytes(b"")
        (logs_dir / "runner.stderr.txt").write_bytes(status_raw)
        sys.stderr.buffer.write(status_raw)
        return 1


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as error:
        status = {
            "schema_version": "kemeny-portable-run-status-v1",
            "status": "failed_before_output_creation",
            "error_type": type(error).__name__,
            "message": str(error),
        }
        sys.stderr.buffer.write(final_status_bytes(status))
        raise SystemExit(1)
