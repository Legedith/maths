from __future__ import annotations

import argparse
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path


PACKAGE = Path(__file__).resolve().parent


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=PACKAGE / "publication-manifest.json")
    parser.add_argument(
        "--checker-result",
        type=Path,
        default=PACKAGE / "output" / "attempt-portable-check-01" / "certificate-check.json",
    )
    parser.add_argument(
        "--attempt-record",
        type=Path,
        default=PACKAGE / "logs" / "attempt-portable-check-01.json",
    )
    args = parser.parse_args()
    output = args.output.resolve()
    if output.exists():
        raise SystemExit(f"refusing to overwrite manifest: {output}")

    checker_result = json.loads(args.checker_result.read_text(encoding="utf-8"))
    attempt = json.loads(args.attempt_record.read_text(encoding="utf-8"))
    if attempt.get("returncode") != 0 or attempt.get("timed_out") is not False:
        raise SystemExit("canonical checker attempt did not exit cleanly")
    if checker_result.get("pass") is not True:
        raise SystemExit("author checker result did not report pass")

    excluded_parts = {".venv", "__pycache__"}
    files = []
    for path in sorted(PACKAGE.rglob("*"), key=lambda item: item.as_posix()):
        if not path.is_file() or path.resolve() == output:
            continue
        relative = path.relative_to(PACKAGE)
        if any(part in excluded_parts for part in relative.parts):
            continue
        files.append(
            {"path": relative.as_posix(), "bytes": path.stat().st_size, "sha256": sha256(path)}
        )

    record = {
        "schema_version": "kemeny-three-part-portable-publication-v1",
        "created_at_utc": datetime.now(timezone.utc).isoformat(),
        "status": "portable_author_checker_replay_complete_independent_proof_gate_pending",
        "selection_sha256": "c750ff018cc7e04db9d9b964486d71a0e5f9b5a42ea93e9de25b68c73632b996",
        "contract_sha256": "563d11151e21d31a21804e7871db6979996bc2cbe4dc0ed3673563975b1d2aba",
        "selected_source_identity": {
            "checker_sha256": "08aee29b87793cb288eaa7dfe54dd748b169972c32e46ed6e1b5bb2e1f3327f5",
            "certificate_sha256": "540ea590fb2e3d671e95102ab8ac5b80a22752f85354c7ded4aa84a4848fb8a9",
            "proposal_markdown_sha256": "53c78f650397b3a791dd6b2a715f2294c564bcb9440feabce7327ceb4dcfa3e4",
            "proposal_json_sha256": "6a821c189ce481d4138c4d7cda5a223332bf3317a0b91c0d84c63887d69c2c5d",
        },
        "canonical_attempt": {
            "record": args.attempt_record.relative_to(PACKAGE).as_posix(),
            "returncode": attempt["returncode"],
            "timed_out": attempt["timed_out"],
            "checker_result": args.checker_result.relative_to(PACKAGE).as_posix(),
            "author_checker_reported_pass": checker_result["pass"],
        },
        "claim_boundary": {
            "portable_replay": "complete",
            "independent_mathematical_validity": "pending",
            "publication_novelty": "unresolved",
            "broader_than_three_non_singleton_parts": "not_claimed",
        },
        "files": files,
        "file_count": len(files),
    }
    output.write_bytes(
        (json.dumps(record, ensure_ascii=True, sort_keys=True, indent=2) + "\n").encode("utf-8")
    )
    print(json.dumps({"output": str(output), "file_count": len(files)}, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
