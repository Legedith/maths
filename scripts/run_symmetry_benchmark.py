"""Frozen 21-round paired benchmark for exact terminal-symmetry reuse."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import platform
import statistics
import sys
import time
from pathlib import Path

from atlas_engine import SymmetryBatchAnalyzer, analyze_graph
from atlas_engine.evaluator import EXPECTED_CONNECTED_COUNTS, _connected_graphs


ROOT = Path(__file__).resolve().parents[1]
ROUND_COUNT = 21


def _arguments() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output-dir", type=Path, required=True)
    return parser.parse_args()


def _file_hash(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _relative(path: Path) -> str:
    return Path(os.path.relpath(path.resolve(), ROOT)).as_posix()


def _source_hashes() -> dict[str, str]:
    paths = [
        ROOT / "docs" / "symmetry-contract.md",
        ROOT / "src" / "atlas_engine" / "analysis.py",
        ROOT / "src" / "atlas_engine" / "linear.py",
        ROOT / "src" / "atlas_engine" / "markov.py",
        ROOT / "src" / "atlas_engine" / "resistance.py",
        ROOT / "src" / "atlas_engine" / "trees.py",
        ROOT / "src" / "atlas_engine" / "validation.py",
        ROOT / "src" / "atlas_engine" / "symmetry.py",
        Path(__file__).resolve(),
    ]
    return {_relative(path): _file_hash(path) for path in paths}


def _workload() -> tuple[list[dict[str, object]], dict[str, int]]:
    payloads: list[dict[str, object]] = []
    counts: dict[str, int] = {}
    for n in range(2, 6):
        count = 0
        for edges in _connected_graphs(n):
            source, target = edges[0]
            payloads.append(
                {
                    "n": n,
                    "edges": [list(edge) for edge in edges],
                    "source": source,
                    "target": target,
                }
            )
            count += 1
        counts[str(n)] = count
    return payloads, counts


def _result_hash(results: list[dict[str, object]]) -> str:
    encoded = json.dumps(results, sort_keys=True, separators=(",", ":")).encode()
    return hashlib.sha256(encoded).hexdigest()


def _direct_batch(payloads: list[dict[str, object]]) -> list[dict[str, object]]:
    return [analyze_graph(payload) for payload in payloads]


def _symmetry_batch(
    payloads: list[dict[str, object]],
) -> tuple[list[dict[str, object]], dict[str, int]]:
    analyzer = SymmetryBatchAnalyzer(capacity=len(payloads))
    results = [analyzer.analyze(payload) for payload in payloads]
    return results, analyzer.diagnostics()


def _timed_direct(
    payloads: list[dict[str, object]],
) -> tuple[list[dict[str, object]], int]:
    started = time.perf_counter_ns()
    results = _direct_batch(payloads)
    return results, time.perf_counter_ns() - started


def _timed_symmetry(
    payloads: list[dict[str, object]],
) -> tuple[list[dict[str, object]], dict[str, int], int]:
    started = time.perf_counter_ns()
    results, diagnostics = _symmetry_batch(payloads)
    return results, diagnostics, time.perf_counter_ns() - started


def main() -> int:
    args = _arguments()
    args.output_dir.mkdir(parents=True, exist_ok=True)
    rounds_path = args.output_dir / "rounds.jsonl"
    workload_path = args.output_dir / "workload.jsonl"
    summary_path = args.output_dir / "summary.json"
    payloads, counts_by_n = _workload()
    workload_count_ok = (
        counts_by_n == {str(n): count for n, count in EXPECTED_CONNECTED_COUNTS.items()}
        and len(payloads) == 771
    )
    with workload_path.open("w", encoding="utf-8", newline="\n") as workload_file:
        for index, payload in enumerate(payloads):
            workload_file.write(
                json.dumps(
                    {"id": f"workload-{index:04d}", "input": payload},
                    sort_keys=True,
                    separators=(",", ":"),
                )
                + "\n"
            )

    overall_started_wall = time.time()
    overall_started_perf = time.perf_counter()

    warm_direct = _direct_batch(payloads)
    warm_symmetry, warm_diagnostics = _symmetry_batch(payloads)
    warm_equal = warm_direct == warm_symmetry
    del warm_direct
    del warm_symmetry

    direct_times_ns: list[int] = []
    symmetry_times_ns: list[int] = []
    rounds: list[dict[str, object]] = []
    with rounds_path.open("w", encoding="utf-8", newline="\n") as rounds_file:
        for round_index in range(ROUND_COUNT):
            if round_index % 2 == 0:
                order = "direct-first"
                direct_results, direct_ns = _timed_direct(payloads)
                symmetry_results, diagnostics, symmetry_ns = _timed_symmetry(payloads)
            else:
                order = "symmetry-first"
                symmetry_results, diagnostics, symmetry_ns = _timed_symmetry(payloads)
                direct_results, direct_ns = _timed_direct(payloads)

            # Equality and hashing are intentionally outside both timed regions.
            equal = direct_results == symmetry_results
            direct_sha256 = _result_hash(direct_results)
            symmetry_sha256 = _result_hash(symmetry_results)
            diagnostics_consistent = (
                diagnostics["hits"] + diagnostics["misses"] == len(payloads)
                and diagnostics["core_calls"] == diagnostics["misses"]
                and diagnostics["size"] == diagnostics["misses"]
                and diagnostics["evictions"] == 0
            )
            record: dict[str, object] = {
                "round": round_index + 1,
                "order": order,
                "direct_nanoseconds": direct_ns,
                "direct_seconds": direct_ns / 1_000_000_000,
                "symmetry_nanoseconds": symmetry_ns,
                "symmetry_seconds": symmetry_ns / 1_000_000_000,
                "direct_call_count": len(payloads),
                "symmetry_diagnostics": diagnostics,
                "result_dictionaries_equal": equal,
                "direct_results_sha256": direct_sha256,
                "symmetry_results_sha256": symmetry_sha256,
                "diagnostics_consistent": diagnostics_consistent,
            }
            direct_times_ns.append(direct_ns)
            symmetry_times_ns.append(symmetry_ns)
            rounds.append(record)
            rounds_file.write(
                json.dumps(record, sort_keys=True, separators=(",", ":")) + "\n"
            )
            rounds_file.flush()
            print(json.dumps(record, sort_keys=True), flush=True)

    direct_median_ns = int(statistics.median(direct_times_ns))
    symmetry_median_ns = int(statistics.median(symmetry_times_ns))
    passed = (
        workload_count_ok
        and warm_equal
        and all(bool(record["result_dictionaries_equal"]) for record in rounds)
        and all(bool(record["diagnostics_consistent"]) for record in rounds)
    )
    overall_runtime = time.perf_counter() - overall_started_perf
    summary: dict[str, object] = {
        "schema_version": "1.0",
        "passed": passed,
        "workload": {
            "selection_policy": "lexicographically first existing edge per labelled connected graph",
            "counts_by_n": counts_by_n,
            "input_count": len(payloads),
            "generated_outside_timing": True,
            "workload_path": _relative(workload_path),
        },
        "warmup": {
            "separate_discarded_batches": True,
            "direct_batch_count": 1,
            "symmetry_batch_count": 1,
            "result_dictionaries_equal": warm_equal,
            "symmetry_diagnostics": warm_diagnostics,
        },
        "paired_round_count": ROUND_COUNT,
        "order": "alternating; odd rounds direct-first, even rounds symmetry-first",
        "timing_scope": {
            "direct": "all 771 unchanged analyze_graph calls and all public outputs/checks",
            "symmetry": "fresh analyzer construction, validation, canonicalization, cache misses/hits, unchanged core calls, output transport, and checks",
            "excluded": "workload generation, result dictionary equality, result hashing, and artifact writes",
        },
        "exact_result_dictionary_equality_outside_timers": True,
        "equal_round_count": sum(
            bool(record["result_dictionaries_equal"]) for record in rounds
        ),
        "direct_times_nanoseconds": direct_times_ns,
        "symmetry_times_nanoseconds": symmetry_times_ns,
        "direct_times_seconds": [value / 1_000_000_000 for value in direct_times_ns],
        "symmetry_times_seconds": [
            value / 1_000_000_000 for value in symmetry_times_ns
        ],
        "direct_median_nanoseconds": direct_median_ns,
        "symmetry_median_nanoseconds": symmetry_median_ns,
        "direct_median_seconds": direct_median_ns / 1_000_000_000,
        "symmetry_median_seconds": symmetry_median_ns / 1_000_000_000,
        "median_direct_over_symmetry_ratio": direct_median_ns / symmetry_median_ns,
        "median_time_saved_fraction": 1 - symmetry_median_ns / direct_median_ns,
        "direct_call_count_per_round": len(payloads),
        "direct_call_count_all_measured_rounds": len(payloads) * ROUND_COUNT,
        "symmetry_core_calls_per_round": [
            int(record["symmetry_diagnostics"]["core_calls"]) for record in rounds
        ],
        "symmetry_hits_per_round": [
            int(record["symmetry_diagnostics"]["hits"]) for record in rounds
        ],
        "symmetry_misses_per_round": [
            int(record["symmetry_diagnostics"]["misses"]) for record in rounds
        ],
        "symmetry_evictions_per_round": [
            int(record["symmetry_diagnostics"]["evictions"]) for record in rounds
        ],
        "symmetry_core_calls_all_measured_rounds": sum(
            int(record["symmetry_diagnostics"]["core_calls"]) for record in rounds
        ),
        "symmetry_hits_all_measured_rounds": sum(
            int(record["symmetry_diagnostics"]["hits"]) for record in rounds
        ),
        "symmetry_misses_all_measured_rounds": sum(
            int(record["symmetry_diagnostics"]["misses"]) for record in rounds
        ),
        "symmetry_evictions_all_measured_rounds": sum(
            int(record["symmetry_diagnostics"]["evictions"]) for record in rounds
        ),
        "rounds_path": _relative(rounds_path),
        "command": "uv run python scripts/run_symmetry_benchmark.py --output-dir logs/benchmark-attempt-XX",
        "argv": sys.argv,
        "working_directory": str(Path.cwd()),
        "python": sys.version,
        "implementation": platform.python_implementation(),
        "platform": platform.platform(),
        "processor": platform.processor(),
        "started_at_unix_seconds": overall_started_wall,
        "total_runtime_seconds": overall_runtime,
        "source_sha256": _source_hashes(),
        "caveat": "Wall-clock timings are machine- and load-dependent; the measured ratio applies only to this finite frozen workload on this recorded environment.",
    }
    summary_path.write_text(
        json.dumps(summary, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    print(json.dumps(summary, indent=2, sort_keys=True))
    return 0 if passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
