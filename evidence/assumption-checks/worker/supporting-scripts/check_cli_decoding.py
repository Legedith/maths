"""Post-freeze CLI robustness probes; independent held-out cases are untouched."""
import json
import subprocess
import sys
from pathlib import Path

base = Path(__file__).resolve().parent
project = base.parent / "project"
cases = {
    "invalid-utf8": b"\xff",
    "parser-depth": ("[" * 2000 + "0" + "]" * 2000).encode("utf-8"),
    "parser-integer-limit": ("1" * 5000).encode("utf-8"),
}
records = []
for name, data in cases.items():
    source = base / f"{name}.json"
    source.write_bytes(data)
    command = [sys.executable, "-m", "atlas_checks", str(source)]
    run = subprocess.run(command, cwd=project, capture_output=True, text=True, encoding="utf-8", timeout=10)
    try:
        decoded = json.loads(run.stdout)
        structured_invalid = decoded.get("verdict") == "invalid_input"
    except (json.JSONDecodeError, AttributeError):
        structured_invalid = False
    records.append({"case": name, "command": command, "exit_code": run.returncode,
                    "stdout": run.stdout, "stderr": run.stderr, "structured_invalid": structured_invalid})
result = {"phase": "post-freeze root robustness probes, separate from blinded 80-case suite",
          "records": records, "all_structured_invalid": all(r["structured_invalid"] for r in records)}
target = project / "evidence/assumption-checks/worker/root-cli-decoding-attempt-01.json"
target.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
print(json.dumps({"cases": [{"case": r["case"], "exit_code": r["exit_code"], "structured_invalid": r["structured_invalid"]} for r in records]}, indent=2))
