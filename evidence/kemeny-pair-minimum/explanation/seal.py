from __future__ import annotations

import argparse
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path


ARTIFACT_PATHS = [
    ".python-version",
    "pyproject.toml",
    "uv.lock",
    "build_explanation.py",
    "run_logged.py",
    "seal.py",
    "witness-explanation.json",
    "logs/canonical-01/command.json",
    "logs/canonical-01/stdout.txt",
    "logs/canonical-01/stderr.txt",
]


def file_record(root: Path, relative_path: str) -> dict[str, object]:
    raw = (root / relative_path).read_bytes()
    return {
        "path": relative_path,
        "bytes": len(raw),
        "sha256": hashlib.sha256(raw).hexdigest(),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Seal the bounded witness explanation artifacts.")
    parser.add_argument("--root", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    args = parser.parse_args()
    root = args.root.resolve()
    output = args.output.resolve()
    if output.exists():
        raise FileExistsError(f"refusing to overwrite {output}")

    artifacts = [file_record(root, path) for path in ARTIFACT_PATHS]
    command_record = json.loads((root / "logs/canonical-01/command.json").read_bytes())
    explanation = json.loads((root / "witness-explanation.json").read_bytes())
    if command_record["return_code"] != 0:
        raise ValueError("canonical postprocessing command did not return zero")
    if explanation["status"] != "candidate_pending_final_audit":
        raise ValueError("unexpected explanation status")

    manifest = {
        "schema_version": "kemeny-witness-explanation-manifest-v1",
        "status": "sealed_explanation_pending_final_audit",
        "sealed_at_utc": datetime.now(timezone.utc).isoformat(),
        "scope": "postprocessing and explanation only; no graph evaluation",
        "artifacts": artifacts,
        "source_author_result_manifest_sha256": "78b4121cc83d7e06bed7470f70c1cbb365ba1d24543595f7620b9e15e0524a9d",
        "seal_reproduction_argv": [
            "uv",
            "run",
            "--project",
            ".",
            "--frozen",
            "python",
            "seal.py",
            "--root",
            ".",
            "--output",
            "result-manifest.json",
        ],
        "limitations": [
            "Author-produced explanation artifact; independent final audit remains pending.",
            "The source experiment and every author artifact remain outside this staging directory and were read only.",
        ],
    }
    output.write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
        newline="\n",
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
