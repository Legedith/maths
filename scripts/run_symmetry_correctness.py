"""Canonical exact comparison for the frozen terminal-symmetry contract."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import platform
import sys
import time
from fractions import Fraction
from itertools import combinations
from math import factorial
from pathlib import Path
from typing import Any

from atlas_engine import InputValidationError, SymmetryBatchAnalyzer, analyze_graph
from atlas_engine.evaluator import EXPECTED_CONNECTED_COUNTS, _connected_graphs
from atlas_engine.symmetry import _canonicalize_validated
from atlas_engine.validation import validate_payload


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_FIXTURES = ROOT / "fixtures" / "frozen.json"
EXPECTED_ORDERED_PAIRS = {2: 2, 3: 24, 4: 456, 5: 14_560}


def _arguments() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--fixtures", type=Path, default=DEFAULT_FIXTURES)
    return parser.parse_args()


def _json_hash(value: object) -> str:
    encoded = json.dumps(value, sort_keys=True, separators=(",", ":")).encode()
    return hashlib.sha256(encoded).hexdigest()


def _file_hash(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _relative(path: Path) -> str:
    return Path(os.path.relpath(path.resolve(), ROOT)).as_posix()


def _source_hashes(fixtures: Path) -> dict[str, str]:
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
        fixtures.resolve(),
    ]
    return {_relative(path): _file_hash(path) for path in paths}


def _canonical_description(payload: object) -> dict[str, object]:
    n, edges, source, target = validate_payload(payload)
    form = _canonicalize_validated(n, edges, source, target)
    return {
        "key": {"n": form.key[0], "edge_mask": form.key[1]},
        "caller_to_canonical": list(form.caller_to_canonical),
        "source_maps_to_zero": form.source_maps_to_zero,
        "tie_count": form.tie_count,
        "candidate_count": form.candidate_count,
    }


def _six_vertex_families() -> dict[str, list[list[int]]]:
    return {
        "path-p6": [[vertex, vertex + 1] for vertex in range(5)],
        "cycle-c6": [[vertex, vertex + 1] for vertex in range(5)] + [[0, 5]],
        "star-k1-5": [[0, leaf] for leaf in range(1, 6)],
        "complete-k6": [list(edge) for edge in combinations(range(6), 2)],
        "two-triangles-one-bridge": [
            [0, 1],
            [0, 2],
            [1, 2],
            [2, 3],
            [3, 4],
            [3, 5],
            [4, 5],
        ],
    }


def _compare(
    identifier: str,
    kind: str,
    payload: dict[str, object],
    analyzer: SymmetryBatchAnalyzer,
) -> tuple[dict[str, object], bool, dict[str, object] | None]:
    canonical = _canonical_description(payload)
    try:
        direct = analyze_graph(payload)
        optimized = analyzer.analyze(payload)
        equal = direct == optimized
        record: dict[str, object] = {
            "id": identifier,
            "kind": kind,
            "input": payload,
            "canonical": canonical,
            "direct_result": direct,
            "optimized_result": optimized,
            "direct_sha256": _json_hash(direct),
            "optimized_sha256": _json_hash(optimized),
            "equal": equal,
        }
        return record, equal, optimized
    except Exception as error:  # retained as a raw failed instance
        record = {
            "id": identifier,
            "kind": kind,
            "input": payload,
            "canonical": canonical,
            "equal": False,
            "error": f"{type(error).__name__}: {error}",
        }
        return record, False, None


def _reversal_relation(
    forward: dict[str, object], reverse: dict[str, object]
) -> bool:
    resistance = Fraction(str(forward["resistance"]))
    return (
        forward["laplacian"] == reverse["laplacian"]
        and forward["resistance"] == reverse["resistance"]
        and forward["commute"] == reverse["commute"]
        and forward["spanning_tree_count"] == reverse["spanning_tree_count"]
        and forward["tree_edge_count"] == reverse["tree_edge_count"]
        and forward["edge_probability"] == reverse["edge_probability"]
        and forward["hit_forward"] == reverse["hit_backward"]
        and forward["hit_backward"] == reverse["hit_forward"]
        and all(
            Fraction(str(left)) + Fraction(str(right)) == resistance
            for left, right in zip(
                forward["potentials"], reverse["potentials"], strict=True
            )
        )
    )


def _behavior_cases(fixtures: dict[str, Any]) -> list[dict[str, object]]:
    cases: list[dict[str, object]] = []

    mutation_payload = {
        "n": 4,
        "edges": [[0, 1], [1, 2], [2, 3], [0, 3]],
        "source": 0,
        "target": 2,
    }
    mutation_expected = analyze_graph(mutation_payload)
    mutation_analyzer = SymmetryBatchAnalyzer(capacity=4)
    exposed = mutation_analyzer.analyze(mutation_payload)
    exposed["edges"][0][0] = 99
    exposed["laplacian"][0][0] = 99
    exposed["potentials"][0] = "999"
    exposed["checks"]["laplacian_row_sums_zero"] = False
    mutation_passed = mutation_analyzer.analyze(mutation_payload) == mutation_expected
    cases.append(
        {
            "id": "returned-nested-mutation",
            "passed": mutation_passed,
            "diagnostics": mutation_analyzer.diagnostics(),
        }
    )

    ordered = {
        "n": 4,
        "edges": [[0, 1], [0, 3], [1, 2], [2, 3]],
        "source": 0,
        "target": 1,
    }
    scrambled = {
        "n": 4,
        "edges": [[3, 2], [2, 1], [3, 0], [1, 0]],
        "source": 0,
        "target": 1,
    }
    ordering_analyzer = SymmetryBatchAnalyzer()
    ordering_passed = (
        ordering_analyzer.analyze(scrambled) == analyze_graph(scrambled)
        and ordering_analyzer.analyze(ordered) == analyze_graph(ordered)
        and ordering_analyzer.diagnostics()["hits"] == 1
        and ordering_analyzer.diagnostics()["size"] == 1
    )
    cases.append(
        {
            "id": "edge-endpoint-and-input-order",
            "passed": ordering_passed,
            "diagnostics": ordering_analyzer.diagnostics(),
        }
    )

    first = {"n": 2, "edges": [[0, 1]], "source": 0, "target": 1}
    second = {"n": 3, "edges": [[0, 1], [1, 2]], "source": 0, "target": 1}
    third = {
        "n": 3,
        "edges": [[0, 1], [0, 2], [1, 2]],
        "source": 0,
        "target": 1,
    }
    lru = SymmetryBatchAnalyzer(capacity=2)
    for payload in (first, second, first, third, second):
        lru.analyze(payload)
    expected_lru = {
        "capacity": 2,
        "size": 2,
        "hits": 1,
        "misses": 4,
        "core_calls": 4,
        "evictions": 2,
    }
    cases.append(
        {
            "id": "bounded-lru-eviction",
            "passed": lru.diagnostics() == expected_lru,
            "diagnostics": lru.diagnostics(),
            "expected_diagnostics": expected_lru,
        }
    )
    lru.clear()
    expected_clear = {
        "capacity": 2,
        "size": 0,
        "hits": 0,
        "misses": 0,
        "core_calls": 0,
        "evictions": 0,
    }
    cases.append(
        {
            "id": "clear-resets-cache-and-diagnostics",
            "passed": lru.diagnostics() == expected_clear,
            "diagnostics": lru.diagnostics(),
            "expected_diagnostics": expected_clear,
        }
    )

    left = SymmetryBatchAnalyzer()
    right = SymmetryBatchAnalyzer()
    left.analyze(first)
    right_untouched = right.diagnostics()["core_calls"] == 0
    right.analyze(first)
    left.analyze(first)
    interleaved_passed = (
        right_untouched
        and left.diagnostics()["core_calls"] == 1
        and left.diagnostics()["hits"] == 1
        and right.diagnostics()["core_calls"] == 1
        and right.diagnostics()["hits"] == 0
    )
    cases.append(
        {
            "id": "interleaved-instance-isolation",
            "passed": interleaved_passed,
            "left_diagnostics": left.diagnostics(),
            "right_diagnostics": right.diagnostics(),
        }
    )

    complete4 = {
        "n": 4,
        "edges": [list(edge) for edge in combinations(range(4), 2)],
        "source": 0,
        "target": 1,
    }
    n, edges, source, target = validate_payload(complete4)
    tied = _canonicalize_validated(n, edges, source, target)
    tie_passed = (
        tied.candidate_count == 2 * factorial(n - 2)
        and tied.tie_count == tied.candidate_count
        and SymmetryBatchAnalyzer().analyze(complete4) == analyze_graph(complete4)
    )
    cases.append(
        {
            "id": "automorphism-tie",
            "passed": tie_passed,
            "tie_count": tied.tie_count,
            "candidate_count": tied.candidate_count,
        }
    )

    invalid_analyzer = SymmetryBatchAnalyzer()
    invalid_analyzer.analyze(first)
    before_invalid = invalid_analyzer.diagnostics()
    rejected = 0
    messages_equal = 0
    for fixture in fixtures["invalid"]:
        direct_message = None
        optimized_message = None
        try:
            analyze_graph(fixture["input"])
        except InputValidationError as error:
            direct_message = str(error)
        try:
            invalid_analyzer.analyze(fixture["input"])
        except InputValidationError as error:
            optimized_message = str(error)
            rejected += 1
        if direct_message is not None and direct_message == optimized_message:
            messages_equal += 1
    invalid_passed = (
        rejected == len(fixtures["invalid"])
        and messages_equal == len(fixtures["invalid"])
        and invalid_analyzer.diagnostics() == before_invalid
    )
    cases.append(
        {
            "id": "invalid-after-warm-key",
            "passed": invalid_passed,
            "rejected": rejected,
            "messages_equal": messages_equal,
            "diagnostics_before": before_invalid,
            "diagnostics_after": invalid_analyzer.diagnostics(),
        }
    )
    return cases


def main() -> int:
    args = _arguments()
    started_wall = time.time()
    started_perf = time.perf_counter()
    args.output_dir.mkdir(parents=True, exist_ok=True)
    records_path = args.output_dir / "ordered-pair-records.jsonl"
    fixtures_path = args.fixtures.resolve()
    fixtures = json.loads(fixtures_path.read_text(encoding="utf-8"))
    analyzer = SymmetryBatchAnalyzer(capacity=20_000)
    failures: list[dict[str, object]] = []
    graphs_by_n: dict[str, int] = {}
    pairs_by_n: dict[str, int] = {}
    existing_pairs_by_n: dict[str, int] = {}
    nonedge_pairs_by_n: dict[str, int] = {}
    reversal_pairs_by_n: dict[str, int] = {}
    canonical_classes_by_n: dict[str, int] = {}
    canonical_sets: dict[int, set[tuple[int, int]]] = {}
    record_count = 0

    with records_path.open("w", encoding="utf-8", newline="\n") as records:
        for n in range(2, 6):
            graph_count = 0
            pair_count = 0
            existing_pair_count = 0
            nonedge_pair_count = 0
            reversal_count = 0
            classes: set[tuple[int, int]] = set()
            for graph_index, edges in enumerate(_connected_graphs(n)):
                graph_count += 1
                edge_set = set(edges)
                graph_results: dict[tuple[int, int], dict[str, object]] = {}
                for source in range(n):
                    for target in range(n):
                        if source == target:
                            continue
                        payload: dict[str, object] = {
                            "n": n,
                            "edges": [list(edge) for edge in edges],
                            "source": source,
                            "target": target,
                        }
                        identifier = (
                            f"labeled-n{n}-g{graph_index:04d}-s{source}-t{target}"
                        )
                        record, equal, optimized = _compare(
                            identifier,
                            "exhaustive-ordered-terminal",
                            payload,
                            analyzer,
                        )
                        records.write(
                            json.dumps(record, sort_keys=True, separators=(",", ":"))
                            + "\n"
                        )
                        record_count += 1
                        pair_count += 1
                        canonical_key = record["canonical"]["key"]
                        classes.add(
                            (int(canonical_key["n"]), int(canonical_key["edge_mask"]))
                        )
                        if (min(source, target), max(source, target)) in edge_set:
                            existing_pair_count += 1
                        else:
                            nonedge_pair_count += 1
                        if not equal:
                            failures.append({"id": identifier, "kind": "field-mismatch"})
                        if optimized is not None:
                            graph_results[(source, target)] = optimized
                for source, target in combinations(range(n), 2):
                    reversal_count += 1
                    if not _reversal_relation(
                        graph_results[(source, target)],
                        graph_results[(target, source)],
                    ):
                        failures.append(
                            {
                                "id": f"labeled-n{n}-g{graph_index:04d}-u{source}-{target}",
                                "kind": "terminal-reversal-relation",
                            }
                        )
            graphs_by_n[str(n)] = graph_count
            pairs_by_n[str(n)] = pair_count
            existing_pairs_by_n[str(n)] = existing_pair_count
            nonedge_pairs_by_n[str(n)] = nonedge_pair_count
            reversal_pairs_by_n[str(n)] = reversal_count
            canonical_classes_by_n[str(n)] = len(classes)
            canonical_sets[n] = classes
            if graph_count != EXPECTED_CONNECTED_COUNTS[n]:
                failures.append(
                    {"kind": "graph-count", "n": n, "actual": graph_count}
                )
            if pair_count != EXPECTED_ORDERED_PAIRS[n]:
                failures.append(
                    {"kind": "ordered-pair-count", "n": n, "actual": pair_count}
                )

        family_classes: set[tuple[int, int]] = set()
        family_class_counts: dict[str, int] = {}
        family_pair_counts: dict[str, int] = {}
        family_nonedge_counts: dict[str, int] = {}
        family_reversal_counts: dict[str, int] = {}
        for family, edges in _six_vertex_families().items():
            family_keys: set[tuple[int, int]] = set()
            family_results: dict[tuple[int, int], dict[str, object]] = {}
            nonedges = 0
            edge_set = {tuple(edge) for edge in edges}
            for source in range(6):
                for target in range(6):
                    if source == target:
                        continue
                    payload = {
                        "n": 6,
                        "edges": edges,
                        "source": source,
                        "target": target,
                    }
                    identifier = f"{family}-s{source}-t{target}"
                    record, equal, optimized = _compare(
                        identifier, "named-6-vertex-family", payload, analyzer
                    )
                    records.write(
                        json.dumps(record, sort_keys=True, separators=(",", ":"))
                        + "\n"
                    )
                    record_count += 1
                    key = record["canonical"]["key"]
                    frozen_key = (int(key["n"]), int(key["edge_mask"]))
                    family_keys.add(frozen_key)
                    family_classes.add(frozen_key)
                    if (min(source, target), max(source, target)) not in edge_set:
                        nonedges += 1
                    if not equal:
                        failures.append({"id": identifier, "kind": "field-mismatch"})
                    if optimized is not None:
                        family_results[(source, target)] = optimized
            reversals = 0
            for source, target in combinations(range(6), 2):
                reversals += 1
                if not _reversal_relation(
                    family_results[(source, target)], family_results[(target, source)]
                ):
                    failures.append(
                        {
                            "id": f"{family}-u{source}-{target}",
                            "kind": "terminal-reversal-relation",
                        }
                    )
            family_class_counts[family] = len(family_keys)
            family_pair_counts[family] = len(family_results)
            family_nonedge_counts[family] = nonedges
            family_reversal_counts[family] = reversals

    fixture_records: list[dict[str, object]] = []
    fixture_analyzer = SymmetryBatchAnalyzer()
    valid_fixture_failures = 0
    for fixture in fixtures["valid"]:
        direct = analyze_graph(fixture["input"])
        optimized = fixture_analyzer.analyze(fixture["input"])
        expected_match = all(
            optimized[key] == expected
            for key, expected in fixture["expected"].items()
        )
        equal = direct == optimized
        fixture_records.append(
            {
                "id": fixture["id"],
                "kind": "frozen-valid",
                "input": fixture["input"],
                "direct_result": direct,
                "optimized_result": optimized,
                "equal": equal,
                "expected_fields_match": expected_match,
            }
        )
        if not equal or not expected_match:
            valid_fixture_failures += 1
            failures.append({"id": fixture["id"], "kind": "valid-fixture"})

    invalid_analyzer = SymmetryBatchAnalyzer()
    invalid_analyzer.analyze(fixtures["valid"][0]["input"])
    invalid_before = invalid_analyzer.diagnostics()
    invalid_fixture_failures = 0
    for fixture in fixtures["invalid"]:
        direct_error = None
        optimized_error = None
        try:
            analyze_graph(fixture["input"])
        except InputValidationError as error:
            direct_error = f"{type(error).__name__}: {error}"
        try:
            invalid_analyzer.analyze(fixture["input"])
        except InputValidationError as error:
            optimized_error = f"{type(error).__name__}: {error}"
        passed = (
            direct_error is not None
            and optimized_error == direct_error
            and invalid_analyzer.diagnostics() == invalid_before
        )
        fixture_records.append(
            {
                "id": fixture["id"],
                "kind": "frozen-invalid-after-warm",
                "input": fixture["input"],
                "direct_error": direct_error,
                "optimized_error": optimized_error,
                "cache_unchanged": invalid_analyzer.diagnostics() == invalid_before,
                "passed": passed,
            }
        )
        if not passed:
            invalid_fixture_failures += 1
            failures.append({"id": fixture["id"], "kind": "invalid-fixture"})
    fixture_records_path = args.output_dir / "fixture-records.json"
    fixture_records_path.write_text(
        json.dumps(fixture_records, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )

    behavior_cases = _behavior_cases(fixtures)
    behavior_path = args.output_dir / "behavior-cases.json"
    behavior_path.write_text(
        json.dumps(behavior_cases, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    for case in behavior_cases:
        if not case["passed"]:
            failures.append({"id": case["id"], "kind": "behavior-case"})

    ended_perf = time.perf_counter()
    summary: dict[str, object] = {
        "schema_version": "1.0",
        "passed": not failures,
        "exact_dictionary_comparison": True,
        "sampled": False,
        "canonical_edge_order": "lexicographic combinations(range(n), 2), low bit first",
        "canonical_relabellings_per_input": "2*(n-2)!",
        "exhaustive": {
            "graphs_by_n": graphs_by_n,
            "graph_count": sum(graphs_by_n.values()),
            "ordered_terminal_pairs_by_n": pairs_by_n,
            "ordered_terminal_pair_count": sum(pairs_by_n.values()),
            "existing_terminal_pairs_by_n": existing_pairs_by_n,
            "existing_terminal_pair_count": sum(existing_pairs_by_n.values()),
            "nonedge_terminal_pairs_by_n": nonedge_pairs_by_n,
            "nonedge_terminal_pair_count": sum(nonedge_pairs_by_n.values()),
            "terminal_reversal_pairs_by_n": reversal_pairs_by_n,
            "terminal_reversal_pair_count": sum(reversal_pairs_by_n.values()),
            "canonical_classes_by_n": canonical_classes_by_n,
            "canonical_class_count": sum(canonical_classes_by_n.values()),
        },
        "named_6_vertex_families": {
            "family_count": len(family_pair_counts),
            "ordered_terminal_pairs_by_family": family_pair_counts,
            "ordered_terminal_pair_count": sum(family_pair_counts.values()),
            "nonedge_terminal_pairs_by_family": family_nonedge_counts,
            "nonedge_terminal_pair_count": sum(family_nonedge_counts.values()),
            "terminal_reversal_pairs_by_family": family_reversal_counts,
            "terminal_reversal_pair_count": sum(family_reversal_counts.values()),
            "canonical_classes_by_family": family_class_counts,
            "canonical_class_count_across_families": len(family_classes),
        },
        "ordered_pair_record_count": record_count,
        "frozen_fixtures": {
            "valid_count": len(fixtures["valid"]),
            "invalid_count": len(fixtures["invalid"]),
            "valid_failure_count": valid_fixture_failures,
            "invalid_failure_count": invalid_fixture_failures,
        },
        "behavior_case_count": len(behavior_cases),
        "behavior_case_pass_count": sum(bool(case["passed"]) for case in behavior_cases),
        "cache_diagnostics": analyzer.diagnostics(),
        "failure_count": len(failures),
        "failures": failures,
        "records_path": _relative(records_path),
        "fixture_records_path": _relative(fixture_records_path),
        "behavior_cases_path": _relative(behavior_path),
        "command": "uv run python scripts/run_symmetry_correctness.py --output-dir logs/correctness-attempt-XX",
        "argv": sys.argv,
        "working_directory": str(Path.cwd()),
        "python": sys.version,
        "implementation": platform.python_implementation(),
        "platform": platform.platform(),
        "started_at_unix_seconds": started_wall,
        "runtime_seconds": ended_perf - started_perf,
        "source_sha256": _source_hashes(fixtures_path),
    }
    summary_path = args.output_dir / "summary.json"
    summary_path.write_text(
        json.dumps(summary, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    print(json.dumps(summary, indent=2, sort_keys=True))
    return 0 if summary["passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
