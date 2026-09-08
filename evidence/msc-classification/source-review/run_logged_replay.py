"""Auditor-owned wrapper for one frozen MSC inspection replay."""

from __future__ import annotations

import hashlib
import json
import os
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path


SOURCE_ROOT = Path(r"D:/CodexWorkspaces/mathematics-atlas/msc-reuse-work")
AUDIT_ROOT = Path(r"D:/CodexWorkspaces/mathematics-atlas/msc-reuse-review-work")
RUN_ROOT = AUDIT_ROOT / "raw" / "replay-01"
OUTPUT = RUN_ROOT / "inspection.json"
STDOUT = RUN_ROOT / "stdout.bin"
STDERR = RUN_ROOT / "stderr.bin"
RECORD = RUN_ROOT / "run.json"
TIMEOUT_SECONDS = 180


def digest(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def main() -> int:
    if RUN_ROOT.exists():
        raise SystemExit(f"refusing to overwrite existing run directory: {RUN_ROOT}")
    RUN_ROOT.mkdir(parents=True)

    argv = [
        "uv",
        "run",
        "--frozen",
        "python",
        "inspect_sources.py",
        "--csv-encoding",
        "iso-8859-1",
        "--output",
        OUTPUT.as_posix(),
    ]
    env = os.environ.copy()
    env["UV_CACHE_DIR"] = "D:/CodexWorkspaces/mathematics-atlas/uv-cache"
    env.pop("VIRTUAL_ENV", None)
    env.pop("UV_PROJECT_ENVIRONMENT", None)

    uv_version = subprocess.run(
        ["uv", "--version"], capture_output=True, check=True, env=env
    ).stdout.decode("utf-8", errors="strict").strip()
    target_version = subprocess.run(
        [str(SOURCE_ROOT / ".venv" / "Scripts" / "python.exe"), "-c",
         "import json,platform,rdflib; print(json.dumps({'python':platform.python_version(),'rdflib':rdflib.__version__},sort_keys=True))"],
        capture_output=True,
        check=True,
        env=env,
    ).stdout.decode("utf-8", errors="strict").strip()

    started = datetime.now(timezone.utc).isoformat()
    timed_out = False
    termination = None
    try:
        completed = subprocess.run(
            argv,
            cwd=SOURCE_ROOT,
            env=env,
            capture_output=True,
            timeout=TIMEOUT_SECONDS,
            check=False,
        )
        returncode = completed.returncode
        stdout = completed.stdout
        stderr = completed.stderr
    except subprocess.TimeoutExpired as exc:
        timed_out = True
        termination = "subprocess.TimeoutExpired"
        returncode = None
        stdout = exc.stdout or b""
        stderr = exc.stderr or b""
    ended = datetime.now(timezone.utc).isoformat()

    STDOUT.write_bytes(stdout)
    STDERR.write_bytes(stderr)
    output_record = None
    if OUTPUT.exists():
        data = OUTPUT.read_bytes()
        output_record = {
            "path": OUTPUT.as_posix(),
            "bytes": len(data),
            "sha256": digest(data),
        }
    record = {
        "schema_version": "auditor-logged-command-v1",
        "attempt_id": "msc-independent-replay-01",
        "started_at_utc": started,
        "ended_at_utc": ended,
        "working_directory": SOURCE_ROOT.as_posix(),
        "argv": argv,
        "selected_environment": {
            "UV_CACHE_DIR": env["UV_CACHE_DIR"],
            "VIRTUAL_ENV": None,
            "UV_PROJECT_ENVIRONMENT": None,
        },
        "versions": {
            "uv": uv_version,
            "target_environment": json.loads(target_version),
        },
        "timeout_seconds": TIMEOUT_SECONDS,
        "timed_out": timed_out,
        "termination": termination,
        "returncode": returncode,
        "stdout": {"path": STDOUT.name, "bytes": len(stdout), "sha256": digest(stdout)},
        "stderr": {"path": STDERR.name, "bytes": len(stderr), "sha256": digest(stderr)},
        "output": output_record,
    }
    RECORD.write_text(json.dumps(record, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(record, indent=2))
    return 0 if returncode == 0 and not timed_out and output_record else 1


if __name__ == "__main__":
    sys.exit(main())
