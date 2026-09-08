from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import json
import os
import subprocess
import sys
import time
from pathlib import Path


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--record", type=Path, required=True)
    parser.add_argument("--stdout", type=Path, required=True)
    parser.add_argument("--stderr", type=Path, required=True)
    parser.add_argument("--timeout", type=float, default=300.0)
    parser.add_argument("command", nargs=argparse.REMAINDER)
    args = parser.parse_args()
    command = args.command[1:] if args.command[:1] == ["--"] else args.command
    if not command:
        parser.error("a command is required")

    for path in (args.record, args.stdout, args.stderr):
        path.parent.mkdir(parents=True, exist_ok=True)
    started = dt.datetime.now(dt.timezone.utc)
    before = time.perf_counter()
    timed_out = False
    try:
        result = subprocess.run(
            command,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            timeout=args.timeout,
            check=False,
            env=os.environ.copy(),
        )
        returncode = result.returncode
        stdout = result.stdout
        stderr = result.stderr
    except subprocess.TimeoutExpired as exc:
        timed_out = True
        returncode = None
        stdout = exc.stdout or b""
        stderr = exc.stderr or b""
    ended = dt.datetime.now(dt.timezone.utc)
    args.stdout.write_bytes(stdout)
    args.stderr.write_bytes(stderr)
    record = {
        "schema_version": "logged-command-v1",
        "started_at_utc": started.isoformat(),
        "ended_at_utc": ended.isoformat(),
        "elapsed_seconds": round(time.perf_counter() - before, 6),
        "cwd": str(Path.cwd()),
        "command": command,
        "timeout_seconds": args.timeout,
        "timed_out": timed_out,
        "returncode": returncode,
        "python": sys.version,
        "stdout": {
            "path": str(args.stdout.resolve()),
            "bytes": len(stdout),
            "sha256": digest(args.stdout),
        },
        "stderr": {
            "path": str(args.stderr.resolve()),
            "bytes": len(stderr),
            "sha256": digest(args.stderr),
        },
    }
    args.record.write_text(json.dumps(record, indent=2) + "\n", encoding="utf-8")
    raise SystemExit(124 if timed_out else returncode)


if __name__ == "__main__":
    main()
