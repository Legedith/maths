"""Auditor-owned command wrapper: retain exact argv, bytes, hashes, and timing."""
from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys


def digest(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--attempt-id", required=True)
    parser.add_argument("--timeout-seconds", type=int, required=True)
    parser.add_argument("--working-directory", type=Path, required=True)
    parser.add_argument("--log-directory", type=Path, required=True)
    parser.add_argument("command", nargs=argparse.REMAINDER)
    args = parser.parse_args()
    command = args.command[1:] if args.command[:1] == ["--"] else args.command
    if not command:
        parser.error("command is required after --")

    args.log_directory.mkdir(parents=True, exist_ok=True)
    stdout_path = args.log_directory / f"{args.attempt_id}.stdout.bin"
    stderr_path = args.log_directory / f"{args.attempt_id}.stderr.bin"
    record_path = args.log_directory / f"{args.attempt_id}.json"
    for path in (stdout_path, stderr_path, record_path):
        if path.exists():
            raise FileExistsError(f"Refusing to overwrite audit log: {path}")

    started = dt.datetime.now(dt.timezone.utc)
    timed_out = False
    termination = None
    try:
        completed = subprocess.run(
            command,
            cwd=args.working_directory,
            env=os.environ.copy(),
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            timeout=args.timeout_seconds,
            check=False,
        )
        returncode = completed.returncode
        stdout = completed.stdout
        stderr = completed.stderr
    except subprocess.TimeoutExpired as exc:
        timed_out = True
        termination = "subprocess.run timeout; child killed by Python"
        returncode = 124
        stdout = exc.stdout or b""
        stderr = exc.stderr or b""
    ended = dt.datetime.now(dt.timezone.utc)

    stdout_path.write_bytes(stdout)
    stderr_path.write_bytes(stderr)
    record = {
        "schema_version": "independent-command-attempt-v1",
        "attempt_id": args.attempt_id,
        "argv": command,
        "working_directory": str(args.working_directory.resolve()),
        "started_at_utc": started.isoformat(),
        "ended_at_utc": ended.isoformat(),
        "elapsed_seconds": (ended - started).total_seconds(),
        "timeout_seconds": args.timeout_seconds,
        "timed_out": timed_out,
        "termination": termination,
        "returncode": returncode,
        "selected_environment": {
            "UV_CACHE_DIR": os.environ.get("UV_CACHE_DIR"),
            "UV_PROJECT_ENVIRONMENT": os.environ.get("UV_PROJECT_ENVIRONMENT"),
            "VIRTUAL_ENV": os.environ.get("VIRTUAL_ENV"),
            "PYTHONDONTWRITEBYTECODE": os.environ.get("PYTHONDONTWRITEBYTECODE"),
        },
        "stdout": {"path": stdout_path.name, "bytes": len(stdout), "sha256": digest(stdout)},
        "stderr": {"path": stderr_path.name, "bytes": len(stderr), "sha256": digest(stderr)},
    }
    record_path.write_text(json.dumps(record, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(json.dumps(record, sort_keys=True))
    return returncode


if __name__ == "__main__":
    sys.exit(main())
