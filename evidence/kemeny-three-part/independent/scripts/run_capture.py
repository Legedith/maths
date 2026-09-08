"""Run one command and retain an exact, byte-preserving attempt record."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
import platform
import subprocess
import sys
from datetime import datetime, timezone


def digest(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--workdir", required=True)
    parser.add_argument("--log-dir", required=True)
    parser.add_argument("--attempt", required=True)
    parser.add_argument("command", nargs=argparse.REMAINDER)
    args = parser.parse_args()

    command = args.command
    if command and command[0] == "--":
        command = command[1:]
    if not command:
        parser.error("a command is required after --")

    workdir = Path(args.workdir).resolve(strict=True)
    log_dir = Path(args.log_dir).resolve()
    log_dir.mkdir(parents=True, exist_ok=True)
    stdout_path = log_dir / f"{args.attempt}.stdout.bin"
    stderr_path = log_dir / f"{args.attempt}.stderr.bin"
    record_path = log_dir / f"{args.attempt}.json"

    started = datetime.now(timezone.utc)
    completed = subprocess.run(command, cwd=workdir, capture_output=True, check=False)
    ended = datetime.now(timezone.utc)

    stdout_path.write_bytes(completed.stdout)
    stderr_path.write_bytes(completed.stderr)
    record = {
        "schema_version": "independent-command-attempt-v1",
        "attempt": args.attempt,
        "command_argv": command,
        "command_display": subprocess.list2cmdline(command),
        "cwd": str(workdir),
        "started_at_utc": started.isoformat(),
        "ended_at_utc": ended.isoformat(),
        "returncode": completed.returncode,
        "stdout": {
            "path": stdout_path.name,
            "bytes": len(completed.stdout),
            "sha256": digest(completed.stdout),
        },
        "stderr": {
            "path": stderr_path.name,
            "bytes": len(completed.stderr),
            "sha256": digest(completed.stderr),
        },
        "runner_python": sys.version,
        "runner_executable": sys.executable,
        "platform": platform.platform(),
        "selected_environment": {
            key: os.environ.get(key)
            for key in ("UV_CACHE_DIR", "UV_PROJECT_ENVIRONMENT")
        },
    }
    record_path.write_text(json.dumps(record, indent=2) + "\n", encoding="utf-8")

    sys.stdout.buffer.write(completed.stdout)
    sys.stderr.buffer.write(completed.stderr)
    return completed.returncode


if __name__ == "__main__":
    raise SystemExit(main())
