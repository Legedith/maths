"""Independently verify the portable package's freeze, manifest, and bytes."""

from __future__ import annotations

import argparse
from datetime import datetime
import hashlib
import json
from pathlib import Path


EXPECTED = {
    "contract": "563d11151e21d31a21804e7871db6979996bc2cbe4dc0ed3673563975b1d2aba",
    "selection": "c750ff018cc7e04db9d9b964486d71a0e5f9b5a42ea93e9de25b68c73632b996",
    "proposal_md": "53c78f650397b3a791dd6b2a715f2294c564bcb9440feabce7327ceb4dcfa3e4",
    "proposal_json": "6a821c189ce481d4138c4d7cda5a223332bf3317a0b91c0d84c63887d69c2c5d",
    "certificate": "540ea590fb2e3d671e95102ab8ac5b80a22752f85354c7ded4aa84a4848fb8a9",
    "checker": "08aee29b87793cb288eaa7dfe54dd748b169972c32e46ed6e1b5bb2e1f3327f5",
}


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def require(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def verify_file_table(root: Path, table: list[dict], label: str) -> list[dict]:
    require(isinstance(table, list), f"{label} file table is not a list")
    seen: set[str] = set()
    verified = []
    for index, row in enumerate(table):
        require(isinstance(row, dict), f"{label} row {index} is malformed")
        relative = row.get("path")
        expected_hash = row.get("sha256")
        expected_bytes = row.get("bytes")
        require(isinstance(relative, str) and relative not in seen, f"{label} duplicate/bad path at {index}")
        seen.add(relative)
        target = (root / relative).resolve(strict=True)
        require(target.is_relative_to(root.resolve()), f"{label} path escapes package: {relative}")
        actual_hash = sha256(target)
        actual_bytes = target.stat().st_size
        require(actual_hash == expected_hash, f"{label} hash mismatch for {relative}")
        require(actual_bytes == expected_bytes, f"{label} byte-count mismatch for {relative}")
        verified.append({"path": relative, "sha256": actual_hash, "bytes": actual_bytes})
    return verified


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--portable", type=Path, required=True)
    parser.add_argument("--selected", type=Path, required=True)
    parser.add_argument("--selection", type=Path, required=True)
    parser.add_argument("--contract", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()

    portable = args.portable.resolve(strict=True)
    selected = args.selected.resolve(strict=True)
    package_freeze_path = portable / "package-freeze.json"
    publication_manifest_path = portable / "publication-manifest.json"
    package_freeze = json.loads(package_freeze_path.read_text(encoding="utf-8"))
    publication = json.loads(publication_manifest_path.read_text(encoding="utf-8"))

    require(package_freeze["schema_version"] == "kemeny-three-part-portable-freeze-v1", "wrong freeze schema")
    require(package_freeze["status"] == "frozen_before_first_portable_checker_run", "wrong freeze status")
    require(package_freeze["file_count"] == len(package_freeze["files"]) == 14, "freeze file count mismatch")
    freeze_verified = verify_file_table(portable, package_freeze["files"], "freeze")

    require(publication["schema_version"] == "kemeny-three-part-portable-publication-v1", "wrong publication schema")
    require(
        publication["status"] == "portable_author_checker_replay_complete_independent_proof_gate_pending",
        "unexpected publication status",
    )
    require(publication["file_count"] == len(publication["files"]), "publication file count mismatch")
    publication_verified = verify_file_table(portable, publication["files"], "publication")

    identity_pairs = (
        (portable / "coefficient-certificate.json", selected / "proof" / "coefficient-certificate.json", EXPECTED["certificate"]),
        (portable / "verify_coefficient_certificate.py", selected / "proof" / "verify_coefficient_certificate.py", EXPECTED["checker"]),
        (portable / "proposal.md", selected / "proposal.md", EXPECTED["proposal_md"]),
        (portable / "proposal.json", selected / "proposal.json", EXPECTED["proposal_json"]),
        (portable / "selection-v1.json", args.selection.resolve(strict=True), EXPECTED["selection"]),
        (portable / "contract-v1.md", args.contract.resolve(strict=True), EXPECTED["contract"]),
    )
    byte_identity = []
    for portable_file, frozen_file, expected_hash in identity_pairs:
        portable_hash = sha256(portable_file)
        frozen_hash = sha256(frozen_file)
        require(portable_hash == frozen_hash == expected_hash, f"byte identity failed for {portable_file.name}")
        require(portable_file.read_bytes() == frozen_file.read_bytes(), f"byte comparison failed for {portable_file.name}")
        byte_identity.append(
            {
                "portable": str(portable_file),
                "frozen_source": str(frozen_file),
                "sha256": expected_hash,
                "byte_identical": True,
            }
        )

    require(package_freeze["selected_certificate_sha256"] == EXPECTED["certificate"], "freeze certificate identity mismatch")
    require(package_freeze["selected_checker_sha256"] == EXPECTED["checker"], "freeze checker identity mismatch")
    require(package_freeze["selection_sha256"] == EXPECTED["selection"], "freeze selection identity mismatch")
    require(package_freeze["contract_sha256"] == EXPECTED["contract"], "freeze contract identity mismatch")
    require(package_freeze["independent_final_proof_gate"] == "pending", "freeze improperly self-certifies proof")

    canonical = publication["canonical_attempt"]
    require(canonical["returncode"] == 0 and canonical["timed_out"] is False, "packager canonical attempt failed")
    attempt_path = portable / canonical["record"]
    result_path = portable / canonical["checker_result"]
    attempt = json.loads(attempt_path.read_text(encoding="utf-8"))
    result = json.loads(result_path.read_text(encoding="utf-8"))
    require(attempt["returncode"] == 0 and attempt["timed_out"] is False, "attempt record is not successful")
    require(attempt["argv"][:2] == ["uv", "run"] and "--frozen" in attempt["argv"], "attempt was not a frozen uv run")
    require(result["pass"] is True and all(result["checks"].values()), "packager checker output is not a full pass")
    require(result["certificate"]["sha256"] == EXPECTED["certificate"], "packager result used wrong certificate")
    freeze_time = datetime.fromisoformat(package_freeze["created_at_utc"])
    run_time = datetime.fromisoformat(attempt["started_at_utc"])
    require(freeze_time < run_time, "package was not frozen before canonical run")

    report = {
        "schema_version": "independent-portable-alignment-v1",
        "status": "PASS",
        "portable": str(portable),
        "package_freeze": {
            "path": str(package_freeze_path),
            "sha256": sha256(package_freeze_path),
            "verified_files": len(freeze_verified),
            "frozen_before_canonical_run": True,
        },
        "publication_manifest": {
            "path": str(publication_manifest_path),
            "sha256": sha256(publication_manifest_path),
            "verified_files": len(publication_verified),
        },
        "selected_byte_identity": byte_identity,
        "packager_canonical_attempt": {
            "record": str(attempt_path),
            "returncode": attempt["returncode"],
            "timed_out": attempt["timed_out"],
            "all_checker_flags_true": all(result["checks"].values()),
        },
        "claim_boundary": publication["claim_boundary"],
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(report, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
