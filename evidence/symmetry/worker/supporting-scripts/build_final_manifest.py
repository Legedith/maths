"""Write deterministic hashes and structural checks for verifier handoff."""

from __future__ import annotations

import hashlib
import json
import os
import platform
import sys
from datetime import datetime, timezone
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PROJECT = ROOT.parent / "project"
OUTPUT = ROOT / "logs" / "final-manifest.json"


def _hash(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _relative(path: Path) -> str:
    return Path(os.path.relpath(path.resolve(), ROOT)).as_posix()


def _baseline_comparisons() -> list[dict[str, object]]:
    comparisons: list[dict[str, object]] = []
    source_root = PROJECT / "src" / "atlas_engine"
    staged_root = ROOT / "src" / "atlas_engine"
    for source in sorted(path for path in source_root.iterdir() if path.is_file()):
        staged = staged_root / source.name
        source_hash = _hash(source)
        staged_hash = _hash(staged)
        record: dict[str, object] = {
            "path": f"src/atlas_engine/{source.name}",
            "project_sha256": source_hash,
            "staged_sha256": staged_hash,
        }
        if source.name == "__init__.py":
            baseline_text = source.read_text(encoding="utf-8")
            expected_text = baseline_text.replace(
                "from .validation import InputValidationError\n",
                "from .symmetry import SymmetryBatchAnalyzer\n"
                "from .validation import InputValidationError\n",
            ).replace(
                '__all__ = ["InputValidationError", "analyze_graph"]',
                '__all__ = ["InputValidationError", "SymmetryBatchAnalyzer", "analyze_graph"]',
            )
            record["status"] = "allowed-export-change"
            record["only_expected_export_change"] = (
                staged.read_text(encoding="utf-8").rstrip("\n")
                == expected_text.rstrip("\n")
            )
        else:
            record["status"] = "byte-identical" if source_hash == staged_hash else "changed"
            record["byte_identical"] = source_hash == staged_hash
        comparisons.append(record)

    for name in ("pyproject.toml", "uv.lock"):
        source = PROJECT / name
        staged = ROOT / name
        comparisons.append(
            {
                "path": name,
                "project_sha256": _hash(source),
                "staged_sha256": _hash(staged),
                "status": "byte-identical" if _hash(source) == _hash(staged) else "changed",
                "byte_identical": _hash(source) == _hash(staged),
            }
        )
    return comparisons


def _controlled_files() -> list[Path]:
    explicit = [
        ROOT / "task-spec.md",
        ROOT / "pyproject.toml",
        ROOT / "uv.lock",
        ROOT / "README-symmetry.md",
    ]
    files = list(explicit)
    for directory in ("src", "tests", "scripts", "logs"):
        for path in (ROOT / directory).rglob("*"):
            if not path.is_file():
                continue
            if "__pycache__" in path.parts or path.suffix == ".pyc":
                continue
            if path == OUTPUT:
                continue
            files.append(path)
    return sorted(set(files), key=_relative)


def _line_count(path: Path) -> int:
    with path.open("r", encoding="utf-8") as handle:
        return sum(1 for _ in handle)


def main() -> int:
    baseline = _baseline_comparisons()
    correctness_summary_path = ROOT / "logs" / "correctness-attempt-01" / "summary.json"
    benchmark_summary_path = ROOT / "logs" / "benchmark-attempt-01" / "summary.json"
    correctness = json.loads(correctness_summary_path.read_text(encoding="utf-8"))
    benchmark = json.loads(benchmark_summary_path.read_text(encoding="utf-8"))
    structural_checks = {
        "correctness_summary_passed": correctness["passed"] is True,
        "correctness_ordered_pair_count": correctness["ordered_pair_record_count"],
        "correctness_jsonl_line_count": _line_count(
            ROOT / "logs" / "correctness-attempt-01" / "ordered-pair-records.jsonl"
        ),
        "benchmark_summary_passed": benchmark["passed"] is True,
        "benchmark_round_count": benchmark["paired_round_count"],
        "benchmark_rounds_jsonl_line_count": _line_count(
            ROOT / "logs" / "benchmark-attempt-01" / "rounds.jsonl"
        ),
        "benchmark_workload_count": benchmark["workload"]["input_count"],
        "benchmark_workload_jsonl_line_count": _line_count(
            ROOT / "logs" / "benchmark-attempt-01" / "workload.jsonl"
        ),
        "benchmark_equal_round_count": benchmark["equal_round_count"],
    }
    manifest = {
        "schema_version": "1.0",
        "created_at": datetime.now(timezone.utc).isoformat(),
        "purpose": "deterministic worker handoff; independent semantic audit remains required",
        "command": "uv run python scripts/build_final_manifest.py",
        "python": sys.version,
        "platform": platform.platform(),
        "baseline_comparisons": baseline,
        "baseline_requirement_satisfied": all(
            (
                record.get("byte_identical") is True
                if record["status"] != "allowed-export-change"
                else record.get("only_expected_export_change") is True
            )
            for record in baseline
        ),
        "structural_checks": structural_checks,
        "structural_checks_passed": (
            structural_checks["correctness_summary_passed"]
            and structural_checks["correctness_ordered_pair_count"] == 15_192
            and structural_checks["correctness_jsonl_line_count"] == 15_192
            and structural_checks["benchmark_summary_passed"]
            and structural_checks["benchmark_round_count"] == 21
            and structural_checks["benchmark_rounds_jsonl_line_count"] == 21
            and structural_checks["benchmark_workload_count"] == 771
            and structural_checks["benchmark_workload_jsonl_line_count"] == 771
            and structural_checks["benchmark_equal_round_count"] == 21
        ),
        "artifact_sha256": {
            _relative(path): _hash(path) for path in _controlled_files()
        },
        "exclusions": [
            ".venv runtime files",
            "generated __pycache__ and .pyc files",
            "this self-referential final-manifest.json",
        ],
    }
    OUTPUT.write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(manifest, indent=2, sort_keys=True))
    return 0 if manifest["baseline_requirement_satisfied"] and manifest["structural_checks_passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
