from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
import signal
import subprocess
import sys
from datetime import datetime, timezone


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def canonical_json(value: object) -> bytes:
    return (
        json.dumps(value, ensure_ascii=True, sort_keys=True, separators=(",", ":"))
        + "\n"
    ).encode("utf-8")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--attempt-id", required=True)
    parser.add_argument("--timeout-seconds", type=int, required=True)
    parser.add_argument("--log-dir", type=Path, required=True)
    parser.add_argument("command", nargs=argparse.REMAINDER)
    args = parser.parse_args()
    if args.command and args.command[0] == "--":
        args.command = args.command[1:]
    if not args.command:
        parser.error("a child command is required after --")
    if args.timeout_seconds <= 0:
        parser.error("--timeout-seconds must be positive")
    return args


def terminate_process_tree(process: subprocess.Popen[bytes]) -> dict[str, object]:
    if os.name == "nt":
        result = subprocess.run(
            ["taskkill", "/PID", str(process.pid), "/T", "/F"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=False,
        )
        return {
            "method": "taskkill_tree_force",
            "returncode": result.returncode,
            "stdout": result.stdout.decode("utf-8", errors="replace"),
            "stderr": result.stderr.decode("utf-8", errors="replace"),
        }
    os.killpg(process.pid, signal.SIGKILL)
    return {"method": "kill_process_group_sigkill", "returncode": 0}


def main() -> int:
    args = parse_args()
    log_dir = args.log_dir.resolve()
    log_dir.mkdir(parents=True, exist_ok=True)
    record_path = log_dir / f"attempt-{args.attempt_id}.json"
    stdout_path = log_dir / f"attempt-{args.attempt_id}.stdout.bin"
    stderr_path = log_dir / f"attempt-{args.attempt_id}.stderr.bin"
    if record_path.exists() or stdout_path.exists() or stderr_path.exists():
        raise SystemExit(f"attempt id already exists: {args.attempt_id}")

    started = utc_now()
    popen_kwargs: dict[str, object] = {
        "cwd": str(Path.cwd().resolve()),
        "stdout": subprocess.PIPE,
        "stderr": subprocess.PIPE,
    }
    if os.name == "nt":
        popen_kwargs["creationflags"] = subprocess.CREATE_NEW_PROCESS_GROUP
    else:
        popen_kwargs["start_new_session"] = True

    process = subprocess.Popen(args.command, **popen_kwargs)
    timed_out = False
    termination: dict[str, object] | None = None
    try:
        stdout, stderr = process.communicate(timeout=args.timeout_seconds)
    except subprocess.TimeoutExpired:
        timed_out = True
        termination = terminate_process_tree(process)
        stdout, stderr = process.communicate()
    ended = utc_now()

    stdout_path.write_bytes(stdout)
    stderr_path.write_bytes(stderr)
    record: dict[str, object] = {
        "schema_version": "logged-command-attempt-v1",
        "attempt_id": args.attempt_id,
        "argv": args.command,
        "working_directory": str(Path.cwd().resolve()),
        "started_at_utc": started,
        "ended_at_utc": ended,
        "timeout_seconds": args.timeout_seconds,
        "timed_out": timed_out,
        "returncode": None if timed_out else process.returncode,
        "termination": termination,
        "stdout": {
            "path": stdout_path.name,
            "bytes": len(stdout),
            "sha256": sha256_bytes(stdout),
        },
        "stderr": {
            "path": stderr_path.name,
            "bytes": len(stderr),
            "sha256": sha256_bytes(stderr),
        },
        "selected_environment": {
            key: os.environ.get(key)
            for key in (
                "UV_CACHE_DIR",
                "UV_PROJECT_ENVIRONMENT",
                "PYTHONDONTWRITEBYTECODE",
            )
        },
    }
    record_bytes = json.dumps(
        record, ensure_ascii=True, sort_keys=True, indent=2
    ).encode("utf-8") + b"\n"
    record_path.write_bytes(record_bytes)
    with (log_dir / "attempts.jsonl").open("ab") as stream:
        stream.write(canonical_json(record))
    sys.stdout.buffer.write(canonical_json(record))
    return 124 if timed_out else int(process.returncode or 0)


if __name__ == "__main__":
    raise SystemExit(main())
