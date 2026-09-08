"""Structural and hash validation for the independent symmetry audit package."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path


PROJECT = Path("D:/CodexWorkspaces/mathematics-atlas/project")
AUDIT = Path("D:/CodexWorkspaces/mathematics-atlas/symmetry-audit-work")
PREFIX = "evidence/symmetry/independent/"


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def resolve(path: str) -> Path:
    return AUDIT / path.removeprefix(PREFIX) if path.startswith(PREFIX) else PROJECT / path


def main() -> None:
    audit = json.loads((AUDIT / "final-audit.json").read_text(encoding="utf-8"))
    assert audit["candidate_sha256"] == digest(PROJECT / "src/atlas_engine/symmetry.py")
    assert [check["id"] for check in audit["checks"]] == [
        "reproduction",
        "specification_compliance",
        "source_verification",
        "implementation_alignment",
    ]
    assert all(check["status"] == "pass" for check in audit["checks"])
    evidence = [item for check in audit["checks"] for item in check["evidence"]]
    missing = [path for path in evidence if not resolve(path).is_file()]
    assert not missing, missing

    manifest = json.loads((AUDIT / "audited-project-files.json").read_text(encoding="utf-8"))
    mismatches = {
        path: {"expected": expected, "actual": digest(PROJECT / path)}
        for path, expected in manifest["files"].items()
        if digest(PROJECT / path) != expected
    }
    assert not mismatches, mismatches

    sources = json.loads((AUDIT / "primary-source-verification.json").read_text(encoding="utf-8"))
    for source in sources["sources"]:
        assert digest(AUDIT / source["pdf_path"]) == source["pdf_sha256"]
        if "extracted_text_path" in source:
            assert digest(AUDIT / source["extracted_text_path"]) == source["extracted_text_sha256"]

    result = {
        "status": "pass",
        "check_count": len(audit["checks"]),
        "evidence_reference_count": len(evidence),
        "unique_evidence_reference_count": len(set(evidence)),
        "audited_project_file_count": len(manifest["files"]),
        "primary_source_count": len(sources["sources"]),
        "candidate_sha256": audit["candidate_sha256"],
        "final_audit_sha256": digest(AUDIT / "final-audit.json"),
        "final_report_sha256": digest(AUDIT / "final-audit-report.md"),
    }
    (AUDIT / "final-audit-validation.json").write_text(
        json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    print(json.dumps(result, sort_keys=True))


if __name__ == "__main__":
    main()
