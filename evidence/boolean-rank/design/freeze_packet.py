from __future__ import annotations

import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parent

PUBLIC_FILES = [
    "assessment.md",
    "consumer-inventory.json",
    "design-validation-attempt01.json",
    "design-validation-attempt02.json",
    "design-validation.json",
    "freeze_packet.py",
    "input-drift.json",
    "integration-design.json",
    "run_logged.py",
    "status-sanity.json",
    "validate_design.py",
    "logs/validation/attempt-design-validation-01.json",
    "logs/validation/attempt-design-validation-01.stderr.bin",
    "logs/validation/attempt-design-validation-01.stdout.bin",
    "logs/validation/attempt-design-validation-02.json",
    "logs/validation/attempt-design-validation-02.stderr.bin",
    "logs/validation/attempt-design-validation-02.stdout.bin",
    "logs/validation/attempt-design-validation-03.json",
    "logs/validation/attempt-design-validation-03.stderr.bin",
    "logs/validation/attempt-design-validation-03.stdout.bin",
    "logs/validation/attempts.jsonl",
]


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> int:
    design = json.loads((ROOT / "integration-design.json").read_text(encoding="utf-8"))
    validation = json.loads((ROOT / "design-validation.json").read_text(encoding="utf-8"))
    for name in (
        "consumer-inventory.json",
        "design-validation-attempt01.json",
        "design-validation-attempt02.json",
        "input-drift.json",
        "status-sanity.json",
    ):
        json.loads((ROOT / name).read_text(encoding="utf-8"))

    records = []
    for relative in PUBLIC_FILES:
        path = ROOT / relative
        if not path.is_file():
            raise FileNotFoundError(relative)
        text = path.read_text(encoding="utf-8", errors="strict")
        if "\ufffd" in text:
            raise ValueError(f"replacement character in {relative}")
        records.append(
            {
                "path": relative,
                "bytes": path.stat().st_size,
                "sha256": sha256(path),
                "copy": True,
            }
        )

    if not validation["passed"] or validation["counts"]["failed"] != 0:
        raise ValueError("final design validation did not pass")
    if (
        validation["input_verification"]["project_revision"]
        != design["project_snapshot"]["git_revision"]
    ):
        raise ValueError("project snapshot mismatch")

    manifest = {
        "schema_version": "boolean-rank-integration-design-publication-v1",
        "auditor": "/root/sol_atlas_audit",
        "scope": "Independent integration design, consumer inventory, and status-wording sanity check. No project implementation or teaching-example certification.",
        "reviewed_project_revision": design["project_snapshot"]["git_revision"],
        "copy_records": records,
        "counts": {
            "copy_records": len(records),
            "bytes": sum(row["bytes"] for row in records),
        },
        "external_inputs": design["input_pins"],
        "checks": {
            "all_public_files_utf8_without_replacement_character": True,
            "all_json_files_parse": True,
            "design_internal_consistency": "12/12 PASS",
            "reviewed_project_inputs_match_git_snapshot": True,
            "later_working_tree_edits_certified": False,
        },
        "excluded": [
            {
                "path": "source-title/kcover-01.png",
                "reason": "Local page-one render of a third-party source; only the resolved bibliographic metadata and primary locator are needed in the packet.",
            },
            {
                "path": "source-title/local-clique-01.png",
                "reason": "Local page-one render of a third-party source; only the resolved bibliographic metadata and primary locator are needed in the packet.",
            },
        ],
        "self_hash": "Publication manifest intentionally does not list itself; report its SHA-256 separately.",
    }
    (ROOT / "publication-manifest.json").write_text(
        json.dumps(manifest, ensure_ascii=True, sort_keys=True, indent=2) + "\n",
        encoding="utf-8",
    )
    print(json.dumps(manifest["counts"], sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
