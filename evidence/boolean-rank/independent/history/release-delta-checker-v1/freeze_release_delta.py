from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path


ROOT = Path(__file__).resolve().parent
PROJECT = Path(r"D:\CodexWorkspaces\mathematics-atlas\project")
WORK = Path(r"D:\CodexWorkspaces\mathematics-atlas\boolean-rank-integration-work")


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def record(path: Path) -> dict[str, object]:
    return {"path": str(path), "sha256": sha256(path), "bytes": path.stat().st_size}


def main() -> None:
    named = {
        "release_assembly": WORK / "release-assembly-01.json",
        "assembled_bundle": PROJECT / ".codex" / "evidence" / "runs" / "boolean-rank-integration-v1" / "bundle.json",
        "original_bundle": PROJECT / "evidence" / "boolean-rank" / "author" / "history" / "release-docs" / "bundle-draft.json",
        "implementation_freeze": WORK / "implementation-freeze-v2.json",
        "independent_audit": ROOT / "final-boolean-rank-integration-audit.json",
        "independent_publication_manifest": ROOT / "publication-manifest.json",
    }
    inputs = [
        ROOT / "check_release_delta.py",
        ROOT / "run_logged.py",
        WORK / "release-assembly-01.json",
        WORK / "release-logs" / "boolean-review-assembly-01.json",
        WORK / "verification-note-draft.md",
        WORK / "implementation-freeze-v2.json",
        named["assembled_bundle"],
        named["original_bundle"],
        ROOT / "final-boolean-rank-integration-audit.json",
        ROOT / "publication-manifest.json",
        PROJECT / "evidence" / "boolean-rank" / "independent" / "final-boolean-rank-integration-audit.json",
        PROJECT / "evidence" / "boolean-rank" / "independent" / "publication-manifest.json",
        PROJECT / "docs" / "boolean-rank-bridge.md",
        PROJECT / "docs" / "boolean-rank-verification.md",
        PROJECT / ".github" / "workflows" / "verify.yml",
    ]
    output = {
        "schema_version": "boolean-rank-release-delta-checker-freeze-v1",
        "created_at_utc": datetime.now(timezone.utc).isoformat(),
        "auditor": "/root/sol_atlas_audit",
        "scope": "Frozen checker and inputs for the additive documentation, CI-command and evidence-assembly review.",
        "named_inputs": {name: str(path) for name, path in named.items()},
        "inputs": [record(path) for path in inputs],
    }
    path = ROOT / "release-delta-checker-freeze.json"
    path.write_bytes(
        (json.dumps(output, ensure_ascii=True, sort_keys=True, indent=2) + "\n").encode("utf-8")
    )


if __name__ == "__main__":
    main()
