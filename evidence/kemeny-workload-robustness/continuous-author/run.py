import hashlib
import json
import os
import subprocess
import sys
import time
from pathlib import Path

stage = Path(__file__).resolve().parent
argv = [sys.executable, str(stage / 'check.py')]
assert not (stage / 'run.json').exists()
started = time.perf_counter()
try:
    completed = subprocess.run(argv, cwd=stage, capture_output=True, timeout=60)
    rc, stdout, stderr = completed.returncode, completed.stdout, completed.stderr
except subprocess.TimeoutExpired as exc:
    rc, stdout, stderr = -1, exc.stdout or b'', exc.stderr or b''
(stage / 'stdout.bin').write_bytes(stdout)
(stage / 'stderr.bin').write_bytes(stderr)
record = {
    'argv': argv, 'cwd': str(stage), 'timeout_seconds': 60,
    'returncode': rc, 'elapsed_seconds': time.perf_counter() - started,
    'uv_cache_dir': os.environ.get('UV_CACHE_DIR'),
    'uv_project_environment': os.environ.get('UV_PROJECT_ENVIRONMENT'),
    'stdout_sha256': hashlib.sha256(stdout).hexdigest(),
    'stderr_sha256': hashlib.sha256(stderr).hexdigest(),
    'enclosing_execution': 'uv run --project D:/CodexWorkspaces/mathematics-atlas/project/experiments/kemeny-one-deletion-proof --frozen python D:/CodexWorkspaces/mathematics-atlas/kemeny-robustness-work/run.py',
}
(stage / 'run.json').write_text(json.dumps(record, indent=2) + '\n', encoding='utf-8')
print(json.dumps(record))
print(stdout.decode('utf-8', errors='strict'))
if stderr:
    print(stderr.decode('utf-8', errors='backslashreplace'), file=sys.stderr)
raise SystemExit(rc)
