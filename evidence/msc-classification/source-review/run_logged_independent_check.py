"""Log one independent MSC source-check execution without overwriting evidence."""

from __future__ import annotations

import hashlib
import json
import os
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path


SOURCE = Path(r"D:/CodexWorkspaces/mathematics-atlas/msc-reuse-work")
AUDIT = Path(r"D:/CodexWorkspaces/mathematics-atlas/msc-reuse-review-work")
RUN = AUDIT / "raw" / "independent-check-01"
OUTPUT = RUN / "result.json"
TIMEOUT = 180


def sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def main() -> int:
    if RUN.exists():
        raise SystemExit(f"refusing to overwrite {RUN}")
    RUN.mkdir(parents=True)
    argv = [
        "uv", "run", "--project", SOURCE.as_posix(), "--frozen", "python",
        (AUDIT / "independent_source_check.py").as_posix(),
        "--output", OUTPUT.as_posix(),
    ]
    env = os.environ.copy()
    env["UV_CACHE_DIR"] = "D:/CodexWorkspaces/mathematics-atlas/uv-cache"
    env.pop("VIRTUAL_ENV", None)
    env.pop("UV_PROJECT_ENVIRONMENT", None)
    started = datetime.now(timezone.utc).isoformat()
    timed_out = False
    try:
        child = subprocess.run(argv, cwd=AUDIT, env=env, capture_output=True,
                               timeout=TIMEOUT, check=False)
        returncode = child.returncode
        stdout, stderr = child.stdout, child.stderr
        termination = None
    except subprocess.TimeoutExpired as error:
        timed_out = True
        returncode = None
        stdout, stderr = error.stdout or b"", error.stderr or b""
        termination = "subprocess.TimeoutExpired"
    ended = datetime.now(timezone.utc).isoformat()
    stdout_path, stderr_path = RUN / "stdout.bin", RUN / "stderr.bin"
    stdout_path.write_bytes(stdout)
    stderr_path.write_bytes(stderr)
    output_record = None
    if OUTPUT.exists():
        data = OUTPUT.read_bytes()
        output_record = {"path": OUTPUT.as_posix(), "bytes": len(data), "sha256": sha(data)}
    record = {
        "schema_version": "auditor-logged-command-v1",
        "attempt_id": "msc-independent-source-check-01",
        "started_at_utc": started,
        "ended_at_utc": ended,
        "working_directory": AUDIT.as_posix(),
        "argv": argv,
        "selected_environment": {"UV_CACHE_DIR": env["UV_CACHE_DIR"],
                                 "VIRTUAL_ENV": None, "UV_PROJECT_ENVIRONMENT": None},
        "timeout_seconds": TIMEOUT,
        "timed_out": timed_out,
        "termination": termination,
        "returncode": returncode,
        "stdout": {"path": stdout_path.name, "bytes": len(stdout), "sha256": sha(stdout)},
        "stderr": {"path": stderr_path.name, "bytes": len(stderr), "sha256": sha(stderr)},
        "output": output_record,
    }
    (RUN / "run.json").write_text(json.dumps(record, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(record, indent=2))
    return 0 if returncode == 0 and not timed_out and output_record else 1


if __name__ == "__main__":
    sys.exit(main())
