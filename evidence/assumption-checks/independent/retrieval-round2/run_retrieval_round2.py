from __future__ import annotations

import argparse
import copy
import hashlib
import json
import sys
import traceback
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


EXPECTED_FREEZE_MANIFEST_SHA256 = "50fd6ed3f43f8bdd30e325b249e605cd2bbde33db2336cf0142eba9a1ec5505d"
EXPECTED_ALGORITHM_VERSION = "atlas-checks/1.0.2"


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> int:
    parser = argparse.ArgumentParser(description="Run the nine structured annotations derived from the fixed retrieval study.")
    parser.add_argument("--project-root", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--annotations", type=Path, default=Path(__file__).resolve().parent / "annotations.json")
    parser.add_argument(
        "--fixture-root",
        type=Path,
        default=Path(__file__).resolve().parent.parent,
        help="Root against which fixture_path values in annotations.json are resolved.",
    )
    args = parser.parse_args()
    project = args.project_root.resolve()
    output_dir = args.output_dir.resolve()
    annotations_path = args.annotations.resolve()
    fixture_root = args.fixture_root.resolve()
    output_dir.mkdir(parents=True, exist_ok=True)
    run_path = output_dir / "retrieval-round2-run.jsonl"
    summary_path = output_dir / "retrieval-round2-summary.json"
    console_path = output_dir / "retrieval-round2-console.txt"
    for path in (run_path, summary_path, console_path):
        if path.exists():
            raise RuntimeError(f"refusing to overwrite {path}")

    freeze_path = project / "evidence" / "assumption-checks" / "worker" / "root-patch-freeze-v1.0.2.json"
    if sha256(freeze_path) != EXPECTED_FREEZE_MANIFEST_SHA256:
        raise RuntimeError("1.0.2 freeze manifest hash mismatch")
    freeze = json.loads(freeze_path.read_text(encoding="utf-8"))
    frozen_file_checks = []
    for relative, expected in freeze["file_sha256"].items():
        actual = sha256(project / relative)
        frozen_file_checks.append({"path": relative, "expected": expected, "actual": actual, "matches": actual == expected})
    if len(frozen_file_checks) != 19 or not all(item["matches"] for item in frozen_file_checks):
        raise RuntimeError("frozen project file mismatch")

    annotations = json.loads(annotations_path.read_text(encoding="utf-8"))
    fixture_checks = []
    for record in annotations["records"]:
        path = fixture_root / record["fixture_path"]
        actual = sha256(path)
        fixture_checks.append({"case_id": record["case_id"], "path": str(path), "expected": record["fixture_sha256"], "actual": actual, "matches": actual == record["fixture_sha256"]})
    if len(fixture_checks) != 9 or not all(item["matches"] for item in fixture_checks):
        raise RuntimeError("retrieval fixture hash mismatch")

    sys.path.insert(0, str(project / "src"))
    from atlas_checks import ALGORITHM_VERSION, check_transfer  # noqa: PLC0415

    if ALGORITHM_VERSION != EXPECTED_ALGORITHM_VERSION:
        raise RuntimeError(f"unexpected algorithm version {ALGORITHM_VERSION!r}")
    started_at = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
    counts: Counter[str] = Counter()
    matches = 0
    exceptions = 0
    with run_path.open("x", encoding="utf-8", newline="\n") as stream:
        for sequence, (annotation, fixture_check) in enumerate(zip(annotations["records"], fixture_checks, strict=True), start=1):
            payload = json.loads(Path(fixture_check["path"]).read_text(encoding="utf-8"))
            result = None
            escaped = None
            try:
                result = check_transfer(copy.deepcopy(payload))
            except BaseException as exc:
                exceptions += 1
                escaped = {"class": type(exc).__name__, "message": str(exc), "traceback": traceback.format_exc()}
            actual = result.get("verdict") if isinstance(result, dict) else None
            expected = annotation["expected_verdict"]
            matched = escaped is None and actual == expected
            matches += int(matched)
            counts[str(actual)] += 1
            row: dict[str, Any] = {
                "sequence": sequence,
                "case_id": annotation["case_id"],
                "query_id": annotation["query_id"],
                "theorem_id": annotation["theorem_id"],
                "source_only_label": annotation["source_only_label"],
                "expected_verdict": expected,
                "observed_verdict": actual,
                "matches": matched,
                "escaped_exception": escaped,
                "implementation_output": result,
            }
            stream.write(json.dumps(row, sort_keys=True, separators=(",", ":"), ensure_ascii=True) + "\n")
            stream.flush()

    completed_at = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
    theorem_ids = {record["theorem_id"] for record in annotations["records"]}
    checks = {
        "all_19_frozen_files_match": len(frozen_file_checks) == 19 and all(item["matches"] for item in frozen_file_checks),
        "all_9_fixture_hashes_match": len(fixture_checks) == 9 and all(item["matches"] for item in fixture_checks),
        "nine_fixture_verdicts_match": matches == 9,
        "zero_escaped_exceptions": exceptions == 0,
        "seven_successes_and_two_abstentions": counts == Counter({"no_counterexample_in_instance": 7, "abstain": 2}),
        "zero_machine_counterexamples": counts.get("counterexample", 0) == 0,
        "eight_unique_syntax_mappable_theorem_ids": len(theorem_ids) == 8,
        "all_24_retrieval_rows_accounted_for": annotations["syntax_mappable_theorem_count"] + annotations["fully_ineligible_theorem_count"] == 24,
        "six_evaluable_plus_two_abstaining_theorem_ids": annotations["evaluable_theorem_count"] == 6 and annotations["syntax_mappable_but_abstaining_theorem_count"] == 2,
    }
    summary = {
        "schema_version": "1.0",
        "run_kind": "retrieval_round_two_structured_instance_checks",
        "auditor": "/root/sol_atlas_audit",
        "started_at": started_at,
        "completed_at": completed_at,
        "algorithm_version": ALGORITHM_VERSION,
        "freeze_manifest_sha256": sha256(freeze_path),
        "annotations_path": str(annotations_path),
        "annotations_sha256": sha256(annotations_path),
        "fixture_checks": fixture_checks,
        "fixture_count": len(fixture_checks),
        "unique_theorem_id_count": len(theorem_ids),
        "match_count": matches,
        "mismatch_count": len(fixture_checks) - matches,
        "escaped_exception_count": exceptions,
        "observed_verdict_histogram": dict(sorted(counts.items())),
        "incremental_source_refutation_detections": 0,
        "accounting": {
            "fixed_retrieval_rows": 24,
            "syntax_mappable_theorem_ids": 8,
            "evaluable_theorem_ids": 6,
            "syntax_mappable_but_abstaining_theorem_ids": 2,
            "fully_ineligible_theorem_ids": 16,
            "structured_fixture_count": 9,
        },
        "checks": checks,
        "all_checks_pass": all(checks.values()),
        "scope_limit": "These are exact structured instance checks. They do not revise source-only labels and do not measure natural-language accuracy, prevalence, retrieval timing, novelty, or practical impact. A no-counterexample result is not a theorem proof; an abstention is not a source judgment.",
        "run_jsonl": str(run_path),
        "run_jsonl_sha256": sha256(run_path),
    }
    summary_path.write_text(json.dumps(summary, indent=2, sort_keys=True, ensure_ascii=True) + "\n", encoding="utf-8", newline="\n")
    console_path.write_text(
        "\n".join([
            "Retrieval round-two structured instance checks",
            f"started_at={started_at}",
            f"completed_at={completed_at}",
            f"algorithm_version={ALGORITHM_VERSION}",
            f"fixtures={len(fixture_checks)}",
            f"matches={matches}",
            f"escaped_exceptions={exceptions}",
            f"observed_verdict_histogram={json.dumps(dict(sorted(counts.items())), sort_keys=True)}",
            f"run_jsonl_sha256={sha256(run_path)}",
            f"all_checks_pass={str(summary['all_checks_pass']).lower()}",
        ]) + "\n",
        encoding="utf-8",
        newline="\n",
    )
    print(json.dumps({
        "all_checks_pass": summary["all_checks_pass"],
        "match_count": matches,
        "verdicts": dict(sorted(counts.items())),
        "incremental_source_refutation_detections": 0,
        "run_jsonl_sha256": summary["run_jsonl_sha256"],
        "summary_sha256": sha256(summary_path),
    }, sort_keys=True))
    return 0 if summary["all_checks_pass"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
