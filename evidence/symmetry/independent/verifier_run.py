"""Run one verifier command without a shell and retain exact raw metadata."""

from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--name", required=True)
    parser.add_argument("--cwd", type=Path, required=True)
    parser.add_argument("argv", nargs=argparse.REMAINDER)
    args = parser.parse_args()
    argv = args.argv[1:] if args.argv[:1] == ["--"] else args.argv
    if not argv:
        parser.error("missing command after --")

    artifact_root = Path(__file__).resolve().parent
    log_path = artifact_root / f"{args.name}.console.log"
    metadata_path = artifact_root / f"{args.name}.command.json"
    environment = os.environ.copy()
    environment["UV_CACHE_DIR"] = "D:/CodexWorkspaces/mathematics-atlas/uv-cache"
    environment["PYTHONDONTWRITEBYTECODE"] = "1"

    started = datetime.now(timezone.utc)
    started_perf = time.perf_counter()
    completed = subprocess.run(
        argv,
        cwd=args.cwd,
        env=environment,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        encoding="utf-8",
        errors="replace",
        check=False,
    )
    elapsed = time.perf_counter() - started_perf
    ended = datetime.now(timezone.utc)
    log_path.write_text(completed.stdout, encoding="utf-8")
    metadata = {
        "argv": argv,
        "cwd": str(args.cwd.resolve()),
        "started_at": started.isoformat(),
        "ended_at": ended.isoformat(),
        "runtime_seconds": elapsed,
        "exit_code": completed.returncode,
        "environment_overrides": {
            "UV_CACHE_DIR": environment["UV_CACHE_DIR"],
            "PYTHONDONTWRITEBYTECODE": environment["PYTHONDONTWRITEBYTECODE"],
        },
        "console_log": str(log_path),
    }
    metadata_path.write_text(
        json.dumps(metadata, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    sys.stdout.write(completed.stdout)
    print(json.dumps(metadata, sort_keys=True))
    return completed.returncode


if __name__ == "__main__":
    raise SystemExit(main())
