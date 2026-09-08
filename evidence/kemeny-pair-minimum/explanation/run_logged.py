from __future__ import annotations

import argparse
import json
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def main() -> int:
    parser = argparse.ArgumentParser(description="Run one command and retain its exact process record.")
    parser.add_argument("--log-dir", required=True, type=Path)
    parser.add_argument("command", nargs=argparse.REMAINDER)
    args = parser.parse_args()
    command = args.command
    if command and command[0] == "--":
        command = command[1:]
    if not command:
        raise ValueError("missing command")

    log_dir = args.log_dir.resolve()
    if log_dir.exists():
        raise FileExistsError(f"refusing to overwrite {log_dir}")
    log_dir.mkdir(parents=True)
    cwd = Path.cwd().resolve()
    started = utc_now()
    completed = subprocess.run(command, cwd=cwd, capture_output=True, check=False)
    ended = utc_now()
    (log_dir / "stdout.txt").write_bytes(completed.stdout)
    (log_dir / "stderr.txt").write_bytes(completed.stderr)
    record = {
        "schema_version": "retained-command-v1",
        "started_at_utc": started,
        "ended_at_utc": ended,
        "cwd": cwd.as_posix(),
        "subject_argv": command,
        "uv_reproduction_argv": [
            "uv",
            "run",
            "--project",
            ".",
            "--frozen",
            "python",
            "run_logged.py",
            "--log-dir",
            "logs/canonical-01",
            "--",
            *command,
        ],
        "return_code": completed.returncode,
        "stdout_file": "stdout.txt",
        "stderr_file": "stderr.txt",
    }
    (log_dir / "command.json").write_text(
        json.dumps(record, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
        newline="\n",
    )
    sys.stdout.buffer.write(completed.stdout)
    sys.stderr.buffer.write(completed.stderr)
    return completed.returncode


if __name__ == "__main__":
    raise SystemExit(main())
