"""Retain public prospective plans without opening sealed evaluator labels."""
from __future__ import annotations

import hashlib
import json
import shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PUBLIC_PLAN = ROOT.parent / "assumption-audit-work"
DEST = ROOT / "evidence" / "assumption-checks" / "prospective-audit"
NAMES = (
    "contract-audit.md",
    "evaluation-plan.md",
    "evaluator-schema-public.json",
    "sealed-suite-manifest.json",
    "source-locators.json",
)


def main() -> None:
    DEST.mkdir(parents=True, exist_ok=True)
    copied = []
    for name in NAMES:
        source = PUBLIC_PLAN / name
        target = DEST / name
        if target.exists() and target.read_bytes() != source.read_bytes():
            raise RuntimeError(f"Refusing to replace retained prospective plan: {name}")
        shutil.copyfile(source, target)
        copied.append({"path": target.relative_to(ROOT).as_posix(),
                       "sha256": hashlib.sha256(target.read_bytes()).hexdigest()})
    record = {"scope": "Public preimplementation audit plans only; sealed inputs, labels and secret seed were not read.",
              "source_directory": str(PUBLIC_PLAN), "files": copied}
    (DEST / "transfer-manifest.json").write_text(json.dumps(record, indent=2) + "\n", encoding="utf-8")

    path = ROOT / ".codex/evidence/runs/assumption-checks-v1/bundle.json"
    bundle = json.loads(path.read_text(encoding="utf-8"))
    entries = [
        ("A001", "spec", "docs/assumption-check-contract.md", "user-or-orchestrator"),
        ("A002", "spec", "docs/assumption-check-interface.md", "user-or-orchestrator"),
        ("A003", "spec", "docs/assumption-check-clarifications.md", "user-or-orchestrator"),
        ("A004", "spec", "docs/assumption-check-clarification-2.md", "user-or-orchestrator"),
        ("A005", "spec", "fixtures/retrieval-study-v1.json", "user-or-orchestrator"),
        ("A006", "source", "evidence/research-search/provider-source-notes.json", "root-source-reading"),
    ]
    public_kinds = ("report", "spec", "spec", "log", "source")
    for offset, (item, kind) in enumerate(zip(copied, public_kinds, strict=True), 7):
        entries.append((f"A{offset:03}", kind, item["path"], "independent-verifier-sol-atlas-audit"))
    bundle["artifacts"] = [
        {"id": ident, "kind": kind, "path": rel, "producer": producer,
         "sha256": hashlib.sha256((ROOT / rel).read_bytes()).hexdigest()}
        for ident, kind, rel, producer in entries
    ]
    bundle["limitations"] = [
        "Implementation and independent evaluation are in progress; no semantic gate is claimed passed.",
        "The blinded structured suite and both prospective retrieval reviews remain separate from development fixtures.",
    ]
    path.write_text(json.dumps(bundle, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(record, indent=2))


if __name__ == "__main__":
    main()
