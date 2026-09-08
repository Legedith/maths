from __future__ import annotations

import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parent
PROJECT = Path("D:/CodexWorkspaces/mathematics-atlas/project")
IMPLEMENTATION_FREEZE = Path(
    "D:/CodexWorkspaces/mathematics-atlas/boolean-rank-integration-work/implementation-freeze-v2.json"
)
EXPECTED_FREEZE_SHA256 = "391aa34b932aa37c4ccb45e2b9ee589ba3eaec38540c15f9d43b9581c420f7f6"


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def record(path: Path) -> dict[str, object]:
    return {"path": str(path), "bytes": path.stat().st_size, "sha256": sha256(path)}


def main() -> int:
    if sha256(IMPLEMENTATION_FREEZE) != EXPECTED_FREEZE_SHA256:
        raise ValueError("implementation freeze hash mismatch")
    frozen = json.loads(IMPLEMENTATION_FREEZE.read_text(encoding="utf-8"))
    project_failures = []
    for row in frozen["files"]:
        path = PROJECT / row["path"]
        if (
            not path.is_file()
            or path.stat().st_size != row["bytes"]
            or sha256(path) != row["sha256"]
        ):
            project_failures.append(row["path"])
    if project_failures:
        raise ValueError(f"frozen project mismatch: {project_failures}")

    checker_names = [
        "environment.json",
        "freeze_checker.py",
        "independent_data_check.py",
        "independent_runtime_check.mjs",
        "pyproject.toml",
        "run_logged.py",
        "uv.lock",
    ]
    checker_records = [record(ROOT / name) for name in checker_names]
    inputs = [
        record(IMPLEMENTATION_FREEZE),
        record(PROJECT / "docs/boolean-rank-contract.md"),
        record(
            Path(
                "D:/CodexWorkspaces/mathematics-atlas/boolean-rank-clarification-work/corrected-records-v1.json"
            )
        ),
        record(
            Path(
                "D:/CodexWorkspaces/mathematics-atlas/boolean-rank-correction-review-work/correction-review.json"
            )
        ),
    ]
    manifest = {
        "schema_version": "boolean-rank-independent-checker-freeze-v5",
        "frozen_before_evaluation": True,
        "auditor": {
            "identity": "/root/sol_atlas_audit",
            "role": "independent product auditor and earlier integration-design author",
            "implementation_author": False,
        },
        "implementation": {
            "manifest": str(IMPLEMENTATION_FREEZE),
            "manifest_sha256": EXPECTED_FREEZE_SHA256,
            "verified_file_count": len(frozen["files"]),
            "all_hashes_match": True,
        },
        "supersedes": {
            "path": "checker-freeze-v4.json",
            "sha256": "8e5407ebb483011bb3fa08dae70794e1345ba6032c55cf7f0eb2ea83b0f56a80",
            "reason": "Classic JSX removed the jsx-runtime failure but importing the client tool module still hit Node-hook CommonJS named-export interop for react-dom. V5 binds useEffect and flushSync from the same installed packages through checker globals before transpilation; assertions and implementation inputs remain unchanged.",
            "retained_failed_runs": ["logs/runtime/attempt-independent-runtime-01.json", "logs/runtime/attempt-independent-runtime-02.json", "logs/runtime/attempt-independent-runtime-03.json"],
        },
        "prior_checker_correction": {
            "path": "checker-freeze-v1.json",
            "sha256": "fe29c855d651790b547de505d7c35a91a89ee26ed85be854b15f9a2b74b46ad9",
            "reason": "V2 normalized Markdown backticks and whitespace after the retained data-check false failure.",
            "retained_failed_run": "logs/data/attempt-independent-data-01.json",
        },
        "checker_files": checker_records,
        "inputs": inputs,
        "planned_commands": [
            "uv run --frozen python independent_data_check.py --project-root PROJECT --freeze-manifest FREEZE --admitted-records RECORDS --correction-review REVIEW --output-dir FRESH",
            "node independent_runtime_check.mjs --project-root PROJECT --output-dir FRESH --http-origin http://localhost:8598",
            "uv run --frozen python PROJECT/scripts/validate_atlas.py PROJECT/data/atlas.json --output FRESH",
            "node PROJECT/scripts/check-boolean-rank.mjs --output FRESH",
            "node PROJECT/scripts/check-atlas.ts --output FRESH",
            "uv run --frozen pytest -p no:cacheprovider PROJECT/tests/test_corpus_validation.py",
        ],
        "scope": "Frozen independent semantic/data/runtime/negative checks. The author scripts are also replayed, but do not replace the independent checkers. No browser DOM, screenshot, visual-quality, teaching-example, novelty or impact evaluation.",
    }
    (ROOT / "checker-freeze.json").write_text(
        json.dumps(manifest, ensure_ascii=True, sort_keys=True, indent=2) + "\n",
        encoding="utf-8",
    )
    print(json.dumps({"checker_files": len(checker_records), "input_files": len(inputs), "project_files": len(frozen["files"])}, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
