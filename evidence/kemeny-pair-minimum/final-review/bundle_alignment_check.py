from __future__ import annotations

import hashlib
import json
from pathlib import Path


ROOT = Path("D:/CodexWorkspaces/mathematics-atlas")
PROJECT = ROOT / "project"
BUNDLE = PROJECT / ".codex/evidence/runs/kemeny-pair-minimum-v1/bundle.json"
REPORT = PROJECT / "README-kemeny.md"
OUTPUT = ROOT / "kemeny-final-review-work/raw/bundle-alignment-check.json"

EXPECTED_BUNDLE_SHA256 = "e503ebb7cd844c14ee85efe4267393c709fc8c4a8d4e189a23f0ce1aabe28a72"
EXPECTED_REPORT_SHA256 = "2761e3d592c5816511e2f1a90c1a2a7bc09224d71c52fa323bd49d26d71ed47f"
EXPECTED_CLAIMS = tuple(f"C{index:03d}" for index in range(1, 10))
EXPECTED_CHECKS = {
    "implementation_alignment",
    "reproduction",
    "source_verification",
    "specification_compliance",
}


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def json_pointer(value: object, pointer: str) -> object:
    assert pointer.startswith("/")
    current = value
    for raw_part in pointer[1:].split("/"):
        part = raw_part.replace("~1", "/").replace("~0", "~")
        if isinstance(current, list):
            current = current[int(part)]
        else:
            assert isinstance(current, dict)
            current = current[part]
    return current


def main() -> None:
    assert sha256(BUNDLE) == EXPECTED_BUNDLE_SHA256
    assert sha256(REPORT) == EXPECTED_REPORT_SHA256
    bundle = json.loads(BUNDLE.read_text(encoding="utf-8"))
    assert bundle["schema_version"] == "1.0"
    assert bundle["run_id"] == "kemeny-pair-minimum-v1"
    assert bundle["task_spec_artifact_id"] == "A001"

    artifacts = bundle["artifacts"]
    assert len(artifacts) == 284
    artifact_by_id = {item["id"]: item for item in artifacts}
    assert len(artifact_by_id) == len(artifacts)
    kind_counts: dict[str, int] = {}
    for artifact in artifacts:
        path = PROJECT / artifact["path"]
        assert path.is_file(), path
        assert sha256(path) == artifact["sha256"], path
        kind_counts[artifact["kind"]] = kind_counts.get(artifact["kind"], 0) + 1

    claims = bundle["claims"]
    assert tuple(item["id"] for item in claims) == EXPECTED_CLAIMS
    claim_by_id = {item["id"]: item for item in claims}
    assert len(claim_by_id) == len(claims)
    locator_count = 0
    dependency_count = 0
    for claim in claims:
        assert claim["status"] == "supported"
        assert claim["supports"]
        for support in claim["supports"]:
            if "claim_id" in support:
                assert support["claim_id"] in claim_by_id
                dependency_count += 1
                continue
            artifact = artifact_by_id[support["artifact_id"]]
            path = PROJECT / artifact["path"]
            locator = support.get("locator")
            if locator is None:
                continue
            locator_count += 1
            if locator.startswith("json:"):
                document = json.loads(path.read_text(encoding="utf-8"))
                actual = json_pointer(document, locator.removeprefix("json:"))
                if "expected" in support:
                    assert actual == support["expected"], (claim["id"], locator, actual, support["expected"])
            elif locator.startswith("contains:"):
                assert locator.removeprefix("contains:") in path.read_text(encoding="utf-8")
            else:
                raise AssertionError((claim["id"], locator))

    checks = bundle["checks"]
    assert {item["id"] for item in checks} == EXPECTED_CHECKS
    assert all(item["status"] == "pending" and item["auditor"] == "unassigned" for item in checks)
    assert bundle["evaluator_command"] == (
        "uv run --project experiments/kemeny-pair-minimum/independent --frozen python "
        "experiments/kemeny-pair-minimum/reproduce.py --output-dir work/kemeny-pair-run"
    )

    report_text = REPORT.read_text(encoding="utf-8")
    for statement in (
        "minimum order **6**",
        "135/28",
        "77/16",
        "1229/252",
        "2,390 marked pairs",
        "1,848 graph-state values",
        "the original author run used an author-owned logging wrapper",
        "post-hoc deduction from the unchanged outputs",
        "minimum is **7**",
        "Publication novelty is unresolved",
        "does not measure a real transport, communication, or biological network",
        "reproduces all 11 baseline files byte-for-byte",
    ):
        assert statement in report_text, statement

    result = {
        "schema_version": "kemeny-final-bundle-alignment-check-v1",
        "auditor": "/root/sol_symmetry_audit",
        "status": "pass_pending_semantic_attestation_in_final_audit",
        "inputs": {
            "bundle": {"path": str(BUNDLE), "bytes": BUNDLE.stat().st_size, "sha256": sha256(BUNDLE)},
            "user_report": {"path": str(REPORT), "bytes": REPORT.stat().st_size, "sha256": sha256(REPORT)},
        },
        "artifact_count": len(artifacts),
        "artifact_kind_counts": kind_counts,
        "all_artifact_hashes_match": True,
        "claim_count": len(claims),
        "claim_ids": list(EXPECTED_CLAIMS),
        "all_claim_support_references_resolve": True,
        "machine_checked_locator_count": locator_count,
        "claim_dependency_count": dependency_count,
        "all_machine_checkable_expected_values_match": True,
        "pending_check_ids": sorted(EXPECTED_CHECKS),
        "report_scope_anchors_present": True,
        "note": "Semantic approval and limitations are recorded separately in final-audit.json.",
    }
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8", newline="\n")
    print(json.dumps({"status": result["status"], "output": str(OUTPUT), "sha256": sha256(OUTPUT)}, sort_keys=True))


if __name__ == "__main__":
    main()
