"""Copy the frozen worker candidate without certifying its mathematics."""
from __future__ import annotations
import hashlib
import json
import shutil
from datetime import datetime, timezone
from pathlib import Path

BASE = Path(__file__).resolve().parents[1]
STAGE = BASE / "assumption-work"
ROOT = BASE / "project"
EXPECTED_MANIFEST = "3f81fa516b2e9240abdc9141874b2108bc6b02af84de2f62b593a211ce58c8c5"


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


manifest_path = STAGE / "logs/code-freeze-manifest.json"
assert digest(manifest_path) == EXPECTED_MANIFEST
manifest = json.loads(manifest_path.read_text(encoding="utf-8-sig"))
for relative, expected in manifest["file_sha256"].items():
    assert digest(STAGE / relative) == expected.lower(), relative

mapping: dict[str, str] = {}
for relative in manifest["file_sha256"]:
    if relative.startswith("src/atlas_checks/"):
        mapping[relative] = relative
    elif relative.startswith("tests/"):
        mapping[relative] = relative.replace("tests/", "tests/assumption_checks/", 1)
mapping.update({
    "README-checks.md": "README-checks.md",
    "scripts/exhaustive_development.py": "scripts/check_assumption_development.py",
    "scripts/weighted-counterexample-input.json": "fixtures/assumption-checks/weighted-counterexample.json",
    "pyproject.toml": "evidence/assumption-checks/worker/package-source/pyproject.toml",
    "uv.lock": "evidence/assumption-checks/worker/package-source/uv.lock",
})
for path in sorted((STAGE / "logs").iterdir()):
    if path.is_file():
        relative = path.relative_to(STAGE).as_posix()
        mapping[relative] = "evidence/assumption-checks/worker/" + relative

records = []
for source_relative, target_relative in mapping.items():
    source, target = STAGE / source_relative, ROOT / target_relative
    target.parent.mkdir(parents=True, exist_ok=True)
    if target.exists() and digest(target) != digest(source):
        raise RuntimeError(f"Refusing to overwrite different existing file: {target_relative}")
    shutil.copyfile(source, target)
    assert digest(source) == digest(target)
    records.append({"source": source_relative, "target": target_relative, "sha256": digest(target)})

report = {
    "transferred_at": datetime.now(timezone.utc).isoformat(),
    "freeze_id": manifest["freeze_id"], "manifest_sha256": EXPECTED_MANIFEST,
    "scope": "Byte-preserving candidate integration only; independent evaluation is pending. Original package metadata is retained as evidence; the root package configuration is updated separately.",
    "count": len(records), "files": records,
}
target = ROOT / "evidence/assumption-checks/worker/integration-transfer.json"
target.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
print(json.dumps({"count": len(records), "runtime_files": sum(p.startswith("src/") for p in mapping), "scope": report["scope"]}, indent=2))
