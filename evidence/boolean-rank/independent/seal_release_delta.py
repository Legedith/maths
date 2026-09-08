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


def record(path: Path, *, relative: bool = True) -> dict[str, object]:
    return {
        "path": path.relative_to(ROOT).as_posix() if relative else str(path),
        "sha256": sha256(path),
        "bytes": path.stat().st_size,
    }


def write(path: Path, value: object) -> None:
    path.write_bytes(
        (json.dumps(value, ensure_ascii=True, sort_keys=True, indent=2) + "\n").encode(
            "utf-8"
        )
    )


def main() -> None:
    report = ROOT / "final-boolean-rank-integration-audit.json"
    original_manifest = ROOT / "publication-manifest.json"
    assembly = WORK / "release-assembly-01.json"
    bundle = PROJECT / ".codex" / "evidence" / "runs" / "boolean-rank-integration-v1" / "bundle.json"
    check = ROOT / "results" / "release-delta" / "check-attempt-03.json"
    frozen = ROOT / "release-delta-checker-freeze.json"
    expected = {
        report: "2787ef459e7266daaead4d9ab445b48597575cb986e31625638ab0be68cfc29a",
        original_manifest: "9a07b01eb998257fde7864349b32c53ad174915f3e9fa879d3ab00023e0bceed",
        assembly: "96c1f21edc7feb0ff82af90c70f462603c9c158bc4d96101608eccf1cc912991",
        bundle: "1a2f4d1b4e4c6c186e9d91e8605d6b4851accdf6d5ca5e28aaeee12c334b1f16",
        check: "e47b6b09f39ee79ae1ddda85c46a4d96ca6f24a99d2067d23892a06a7825bf89",
        frozen: "31ded9a5c1c011a08dda19126079346f119dfc67b38537684fbc22155488252b",
    }
    mismatches = {
        str(path): {"expected": digest, "actual": sha256(path)}
        for path, digest in expected.items()
        if sha256(path) != digest
    }
    if mismatches:
        raise SystemExit(json.dumps(mismatches, indent=2))
    check_value = json.loads(check.read_text(encoding="utf-8"))
    assert check_value["passed"] and len(check_value["checks"]) == 10
    assert all(item["passed"] for item in check_value["checks"])

    before_limitation = (
        "The independent product audit passed for the frozen implementation. The "
        "documentation, CI and evidence-assembly delta is pending its separate "
        "acknowledgment; publication remains withheld until then."
    )
    after_limitation = (
        "The independent product audit and its bounded documentation, CI and "
        "evidence-assembly delta passed. Actual CI, final production build and deployment "
        "are tracked separately during release."
    )
    acknowledgment = {
        "schema_version": "boolean-rank-release-delta-independent-acknowledgment-v1",
        "reviewed_at_utc": datetime.now(timezone.utc).isoformat(),
        "auditor": {
            "identity": "/root/sol_atlas_audit",
            "implementation_author": False,
            "prior_role": "earlier nonbinding integration-design author",
        },
        "status": "PASS_SCOPED",
        "base_product_audit": record(report, relative=False),
        "release_assembly": record(assembly, relative=False),
        "reviewed_bundle": record(bundle, relative=False),
        "delta_check": record(check),
        "checker_freeze": record(frozen),
        "reviewed_targets": [
            {
                "path": "docs/boolean-rank-bridge.md",
                "sha256": "5aa6c883f6aa6371702dc371df349d8a1d70edd9b604e77f0915a9f9bf80817a",
                "finding": "The pending-product-review sentence is replaced by a scoped-review link and explicitly says this is not a new primary-source proof.",
            },
            {
                "path": "docs/boolean-rank-verification.md",
                "sha256": "fb3d05c6f49d53e3677df786c9c0ee312d6609a8eb31c9c159e7b6f385fae7fb",
                "finding": "Counts, role disclosure, checked behavior, retained failures and all material limitations match the sealed audit.",
            },
            {
                "path": ".github/workflows/verify.yml",
                "sha256": "afbebe72181060269c6615d83e81b703a9aa395df31476f5f143ed4671b89cb0",
                "finding": "The existing uv/logged runner invokes the audited functional checker with a bounded timeout and uploads its raw/result folder using the pinned action.",
            },
            {
                "path": ".codex/evidence/runs/boolean-rank-integration-v1/bundle.json",
                "sha256": "1a2f4d1b4e4c6c186e9d91e8605d6b4851accdf6d5ca5e28aaeee12c334b1f16",
                "finding": "All 259 artifacts matched; all 144 selected independent records copied byte-identically; C001-C007 and the four sealed gate notes remain value-identical.",
            },
        ],
        "checks": [
            {
                "id": "documentation_alignment",
                "status": "PASS",
                "note": "The new verification note and sole frozen-file wording delta accurately state the independent audit and its limits.",
            },
            {
                "id": "ci_configuration_alignment",
                "status": "PASS",
                "note": "Static command/configuration review passed. This does not assert that hosted CI has run or succeeded.",
            },
            {
                "id": "evidence_assembly_alignment",
                "status": "PASS",
                "note": "All assembled artifact paths were unique and safe, all hashes matched, and the independent packet copy matched its manifest.",
            },
            {
                "id": "claim_and_gate_preservation",
                "status": "PASS",
                "note": "C001-C007 equal the reviewed draft values and the bundle carries the sealed four product-gate decisions without changing their notes.",
            },
        ],
        "permitted_post_review_mechanical_transform": {
            "authorized": True,
            "allowed_operations": [
                "Copy this acknowledgment and its publication manifest byte-for-byte into the independent evidence directory and append artifact records with their exact hashes.",
                "Append the already reviewed release-assembly-01.json and its retained command/stdout/stderr log artifacts with exact hashes.",
                "Add the acknowledgment artifact ID to each of the four existing product-check evidence arrays without changing check ID, status, auditor or note.",
                f"Replace only the first bundle limitation, from `{before_limitation}` to `{after_limitation}`.",
            ],
            "constraints": [
                "Do not change C001-C007, product code, corpus data, mathematical/source statements or the remaining limitations.",
                "Retain the original assembled bundle and raw assembly/check attempts in history.",
                "Run the existing deterministic bundle gate on the transformed bytes and retain its raw output.",
                "Actual hosted CI success, a final production build on the exact release tree and deployment remain separate release gates.",
            ],
        },
        "retained_checker_corrections": [
            {
                "attempt": "release-delta-01",
                "result": "9/10",
                "classification": "auditor matcher false failure",
                "reason": "The first checker expected a literal Markdown line break.",
            },
            {
                "attempt": "release-delta-02",
                "result": "9/10",
                "classification": "auditor matcher false failure",
                "reason": "The normalized matcher expected the word `not`, while the document uses the equivalent `neither ... treated` construction.",
            },
            {
                "attempt": "release-delta-03",
                "result": "10/10",
                "classification": "successful bounded check",
                "reason": "The final matcher checks both exact semantic clauses after whitespace normalization; all other assertions and inputs are unchanged.",
            },
        ],
        "limitations": [
            "No product/runtime, mathematical-source, browser, screenshot or visual-quality check was repeated for this additive delta.",
            "The workflow review verifies committed command structure only; it does not certify GitHub Actions execution.",
            "The acknowledged bundle is an intermediate pre-transform hash. Only the explicitly enumerated mechanical transformation is pre-authorized; any other content change requires review.",
            "Actual CI, final production build and deployment are not certified here.",
        ],
        "material_defects": [],
        "required_changes": [],
    }
    acknowledgment_path = ROOT / "release-delta-acknowledgment.json"
    write(acknowledgment_path, acknowledgment)

    paths = {
        acknowledgment_path,
        ROOT / "check_release_delta.py",
        ROOT / "freeze_release_delta.py",
        ROOT / "seal_release_delta.py",
        ROOT / "release-delta-checker-freeze.json",
        ROOT / "release-delta-checker-freeze-v1.json",
        ROOT / "release-delta-checker-freeze-v2.json",
    }
    paths.update(
        path
        for path in (ROOT / "history").glob("release-delta-checker-v*/*")
        if path.is_file()
    )
    paths.update(
        path for path in (ROOT / "logs" / "release-delta").glob("*") if path.is_file()
    )
    paths.update(
        path for path in (ROOT / "results" / "release-delta").glob("*") if path.is_file()
    )
    manifest = {
        "schema_version": "boolean-rank-release-delta-independent-publication-manifest-v1",
        "created_at_utc": datetime.now(timezone.utc).isoformat(),
        "auditor": "/root/sol_atlas_audit",
        "scope": "Compact additive documentation, CI-command and evidence-assembly acknowledgment packet, including both retained checker false failures.",
        "acknowledgment": record(acknowledgment_path),
        "records": [{**record(path), "copy": True} for path in sorted(paths)],
        "external_reviewed_inputs": [
            record(report, relative=False),
            record(original_manifest, relative=False),
            record(assembly, relative=False),
            record(bundle, relative=False),
        ],
        "manifest_self_excluded": True,
    }
    write(ROOT / "release-delta-publication-manifest.json", manifest)


if __name__ == "__main__":
    main()
