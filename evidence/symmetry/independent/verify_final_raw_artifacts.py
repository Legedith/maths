"""Independent semantic verification of the promoted symmetry raw artifacts.

This verifier does not import the candidate symmetry module, the benchmark
runner, or the correctness runner.  It reconstructs the frozen graph sequence,
canonical forms, electrical equations, Markov hitting times, and spanning-tree
counts directly, then parses every retained raw record.
"""

from __future__ import annotations

import argparse
import hashlib
import itertools
import json
import math
import statistics
from collections import Counter
from fractions import Fraction
from pathlib import Path
from typing import Any, Iterable


PROJECT = Path("D:/CodexWorkspaces/mathematics-atlas/project")
AUDIT = Path("D:/CodexWorkspaces/mathematics-atlas/symmetry-audit-work")


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def json_hash(value: object) -> str:
    encoded = json.dumps(value, sort_keys=True, separators=(",", ":")).encode()
    return hashlib.sha256(encoded).hexdigest()


def load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def load_jsonl(path: Path) -> list[dict[str, Any]]:
    with path.open(encoding="utf-8") as stream:
        return [json.loads(line) for line in stream]


def connected(n: int, edges: tuple[tuple[int, int], ...]) -> bool:
    adjacency = [[] for _ in range(n)]
    for left, right in edges:
        adjacency[left].append(right)
        adjacency[right].append(left)
    seen = {0}
    pending = [0]
    while pending:
        vertex = pending.pop()
        for neighbor in adjacency[vertex]:
            if neighbor not in seen:
                seen.add(neighbor)
                pending.append(neighbor)
    return len(seen) == n


def connected_graphs(n: int) -> Iterable[tuple[tuple[int, int], ...]]:
    possible = tuple(itertools.combinations(range(n), 2))
    for mask in range(1 << len(possible)):
        edges = tuple(edge for bit, edge in enumerate(possible) if mask & (1 << bit))
        if connected(n, edges):
            yield edges


def six_vertex_families() -> dict[str, tuple[tuple[int, int], ...]]:
    return {
        "path-p6": tuple((vertex, vertex + 1) for vertex in range(5)),
        "cycle-c6": tuple((vertex, vertex + 1) for vertex in range(5)) + ((0, 5),),
        "star-k1-5": tuple((0, leaf) for leaf in range(1, 6)),
        "complete-k6": tuple(itertools.combinations(range(6), 2)),
        "two-triangles-one-bridge": (
            (0, 1), (0, 2), (1, 2), (2, 3), (3, 4), (3, 5), (4, 5),
        ),
    }


def normalized_edges(payload: dict[str, Any]) -> tuple[tuple[int, int], ...]:
    return tuple(sorted((min(u, v), max(u, v)) for u, v in payload["edges"]))


def mapped_edges(
    edges: tuple[tuple[int, int], ...], mapping: tuple[int, ...]
) -> tuple[tuple[int, int], ...]:
    return tuple(
        sorted((min(mapping[u], mapping[v]), max(mapping[u], mapping[v])) for u, v in edges)
    )


def edge_mask(n: int, edges: tuple[tuple[int, int], ...]) -> int:
    positions = {edge: bit for bit, edge in enumerate(itertools.combinations(range(n), 2))}
    return sum(1 << positions[edge] for edge in edges)


def minimizers(
    n: int,
    edges: tuple[tuple[int, int], ...],
    source: int,
    target: int,
) -> tuple[int, list[tuple[int, ...]]]:
    remaining = tuple(v for v in range(n) if v not in (source, target))
    best_mask: int | None = None
    best: list[tuple[int, ...]] = []
    for source_image, target_image in ((0, 1), (1, 0)):
        for rest_order in itertools.permutations(remaining):
            mapping = [-1] * n
            mapping[source] = source_image
            mapping[target] = target_image
            for image, vertex in enumerate(rest_order, start=2):
                mapping[vertex] = image
            frozen = tuple(mapping)
            mask = edge_mask(n, mapped_edges(edges, frozen))
            if best_mask is None or mask < best_mask:
                best_mask, best = mask, [frozen]
            elif mask == best_mask:
                best.append(frozen)
    assert best_mask is not None
    return best_mask, best


def laplacian(n: int, edges: tuple[tuple[int, int], ...]) -> list[list[int]]:
    result = [[0] * n for _ in range(n)]
    for left, right in edges:
        result[left][left] += 1
        result[right][right] += 1
        result[left][right] -= 1
        result[right][left] -= 1
    return result


def solve_fraction(matrix: list[list[Fraction]], rhs: list[Fraction]) -> list[Fraction]:
    n = len(rhs)
    work = [row[:] + [value] for row, value in zip(matrix, rhs, strict=True)]
    for column in range(n):
        pivot = next(row for row in range(column, n) if work[row][column])
        work[column], work[pivot] = work[pivot], work[column]
        scale = work[column][column]
        work[column] = [value / scale for value in work[column]]
        for row in range(n):
            if row == column:
                continue
            factor = work[row][column]
            if factor:
                work[row] = [
                    left - factor * right
                    for left, right in zip(work[row], work[column], strict=True)
                ]
    return [work[row][-1] for row in range(n)]


def hitting_time(
    n: int, edges: tuple[tuple[int, int], ...], source: int, target: int
) -> Fraction:
    adjacency = [[] for _ in range(n)]
    for left, right in edges:
        adjacency[left].append(right)
        adjacency[right].append(left)
    transient = [vertex for vertex in range(n) if vertex != target]
    position = {vertex: index for index, vertex in enumerate(transient)}
    matrix: list[list[Fraction]] = []
    rhs: list[Fraction] = []
    for vertex in transient:
        row = [Fraction(0) for _ in transient]
        row[position[vertex]] = 1
        degree = len(adjacency[vertex])
        for neighbor in adjacency[vertex]:
            if neighbor != target:
                row[position[neighbor]] -= Fraction(1, degree)
        matrix.append(row)
        rhs.append(Fraction(1))
    solution = solve_fraction(matrix, rhs)
    return solution[position[source]]


def bareiss_determinant(matrix: list[list[int]]) -> int:
    n = len(matrix)
    if n == 0:
        return 1
    work = [row[:] for row in matrix]
    sign, denominator = 1, 1
    for k in range(n - 1):
        if work[k][k] == 0:
            pivot = next((row for row in range(k + 1, n) if work[row][k]), None)
            if pivot is None:
                return 0
            work[k], work[pivot] = work[pivot], work[k]
            sign *= -1
        pivot_value = work[k][k]
        for i in range(k + 1, n):
            for j in range(k + 1, n):
                work[i][j] = (
                    work[i][j] * pivot_value - work[i][k] * work[k][j]
                ) // denominator
        denominator = pivot_value
        for i in range(k + 1, n):
            work[i][k] = 0
    return sign * work[-1][-1]


def tree_count(n: int, edges: tuple[tuple[int, int], ...]) -> int:
    lap = laplacian(n, edges)
    return bareiss_determinant([row[:-1] for row in lap[:-1]])


def contracted_tree_count(
    n: int, edges: tuple[tuple[int, int], ...], selected: tuple[int, int]
) -> int:
    left, right = selected
    representatives = [left if vertex == right else vertex for vertex in range(n)]
    surviving = sorted(set(representatives))
    relabel = {vertex: index for index, vertex in enumerate(surviving)}
    multiedges: list[tuple[int, int]] = []
    for u, v in edges:
        if (u, v) == selected:
            continue
        a, b = relabel[representatives[u]], relabel[representatives[v]]
        if a != b:
            multiedges.append((min(a, b), max(a, b)))
    return tree_count(n - 1, tuple(multiedges))


def expected_sequence() -> list[tuple[str, str, dict[str, Any]]]:
    result: list[tuple[str, str, dict[str, Any]]] = []
    for n in range(2, 6):
        for graph_index, edges in enumerate(connected_graphs(n)):
            for source in range(n):
                for target in range(n):
                    if source == target:
                        continue
                    result.append(
                        (
                            f"labeled-n{n}-g{graph_index:04d}-s{source}-t{target}",
                            "exhaustive-ordered-terminal",
                            {
                                "n": n,
                                "edges": [list(edge) for edge in edges],
                                "source": source,
                                "target": target,
                            },
                        )
                    )
    for family, edges in six_vertex_families().items():
        for source in range(6):
            for target in range(6):
                if source != target:
                    result.append(
                        (
                            f"{family}-s{source}-t{target}",
                            "named-6-vertex-family",
                            {
                                "n": 6,
                                "edges": [list(edge) for edge in edges],
                                "source": source,
                                "target": target,
                            },
                        )
                    )
    return result


def assert_output_equations(
    output: dict[str, Any], payload: dict[str, Any], tree_cache: dict[Any, int]
) -> None:
    n = payload["n"]
    source, target = payload["source"], payload["target"]
    edges = normalized_edges(payload)
    expected_laplacian = laplacian(n, edges)
    assert output["n"] == n
    assert output["edges"] == [list(edge) for edge in edges]
    assert output["source"] == source and output["target"] == target
    assert output["laplacian"] == expected_laplacian

    potentials = [Fraction(value) for value in output["potentials"]]
    resistance = Fraction(output["resistance"])
    assert potentials[source] == resistance and potentials[target] == 0
    injection = [
        sum(Fraction(expected_laplacian[i][j]) * potentials[j] for j in range(n))
        for i in range(n)
    ]
    assert injection == [Fraction(1 if i == source else -1 if i == target else 0) for i in range(n)]

    forward = hitting_time(n, edges, source, target)
    backward = hitting_time(n, edges, target, source)
    commute = Fraction(output["commute"])
    assert Fraction(output["hit_forward"]) == forward
    assert Fraction(output["hit_backward"]) == backward
    assert commute == forward + backward == 2 * len(edges) * resistance

    graph_key = (n, edges)
    total = tree_cache.setdefault(graph_key, tree_count(n, edges))
    assert output["spanning_tree_count"] == total > 0
    selected = (min(source, target), max(source, target))
    if selected in edges:
        selected_key = (n, edges, selected)
        selected_count = tree_cache.setdefault(
            selected_key, contracted_tree_count(n, edges, selected)
        )
        assert output["tree_edge_count"] == selected_count
        assert Fraction(output["edge_probability"]) == Fraction(selected_count, total)
        expected_checks = {
            "laplacian_row_sums_zero": True,
            "commute_equals_2m_resistance": True,
            "spanning_tree_count_positive": True,
            "edge_probability_equals_resistance": True,
        }
    else:
        assert output["tree_edge_count"] is None and output["edge_probability"] is None
        expected_checks = {
            "laplacian_row_sums_zero": True,
            "commute_equals_2m_resistance": True,
            "spanning_tree_count_positive": True,
        }
    assert output["checks"] == expected_checks


def verify_correctness(root: Path) -> dict[str, Any]:
    records_path = root / "ordered-pair-records.jsonl"
    fixtures_path = root / "fixture-records.json"
    behavior_path = root / "behavior-cases.json"
    summary_path = root / "summary.json"
    records = load_jsonl(records_path)
    expected = expected_sequence()
    assert len(records) == len(expected) == 15_192
    assert len({record["id"] for record in records}) == len(records)
    tree_cache: dict[Any, int] = {}
    classes_by_n: dict[int, set[tuple[int, int]]] = {n: set() for n in range(2, 6)}
    family_classes: dict[str, set[tuple[int, int]]] = {
        family: set() for family in six_vertex_families()
    }
    edge_pairs = Counter()
    nonedge_pairs = Counter()
    orientation_spanning_ties = 0
    tie_histogram = Counter()
    for record, (identifier, kind, payload) in zip(records, expected, strict=True):
        assert record["id"] == identifier and record["kind"] == kind
        assert record["input"] == payload
        assert record["equal"] is True
        assert record["direct_result"] == record["optimized_result"]
        assert record["direct_sha256"] == json_hash(record["direct_result"])
        assert record["optimized_sha256"] == json_hash(record["optimized_result"])
        assert_output_equations(record["direct_result"], payload, tree_cache)

        n, source, target = payload["n"], payload["source"], payload["target"]
        edges = normalized_edges(payload)
        mask, maps = minimizers(n, edges, source, target)
        chosen = min(maps)
        canonical = record["canonical"]
        assert canonical == {
            "key": {"n": n, "edge_mask": mask},
            "caller_to_canonical": list(chosen),
            "source_maps_to_zero": chosen[source] == 0,
            "tie_count": len(maps),
            "candidate_count": 2 * math.factorial(n - 2),
        }
        tie_histogram[len(maps)] += 1
        if {mapping[source] for mapping in maps} == {0, 1}:
            orientation_spanning_ties += 1
        key = (n, mask)
        if kind == "exhaustive-ordered-terminal":
            classes_by_n[n].add(key)
            selected = (min(source, target), max(source, target))
            (edge_pairs if selected in edges else nonedge_pairs)[n] += 1
        else:
            family = identifier.rsplit("-s", 1)[0]
            family_classes[family].add(key)

    fixtures = load_json(PROJECT / "fixtures" / "frozen.json")
    fixture_records = load_json(fixtures_path)
    assert len(fixture_records) == 17
    all_fixture_specs = [
        ("frozen-valid", fixture) for fixture in fixtures["valid"]
    ] + [
        ("frozen-invalid-after-warm", fixture) for fixture in fixtures["invalid"]
    ]
    for record, (expected_kind, fixture) in zip(
        fixture_records, all_fixture_specs, strict=True
    ):
        assert record["id"] == fixture["id"] and record["input"] == fixture["input"]
        assert record["kind"] == expected_kind
        if expected_kind == "frozen-valid":
            assert record["equal"] and record["expected_fields_match"]
            assert record["direct_result"] == record["optimized_result"]
            assert_output_equations(record["direct_result"], fixture["input"], tree_cache)
            for field, value in fixture["expected"].items():
                assert record["direct_result"][field] == value
        else:
            assert record["passed"]
            assert record["cache_unchanged"]
            assert record["direct_error"] == record["optimized_error"]

    behavior = load_json(behavior_path)
    assert [case["id"] for case in behavior] == [
        "returned-nested-mutation",
        "edge-endpoint-and-input-order",
        "bounded-lru-eviction",
        "clear-resets-cache-and-diagnostics",
        "interleaved-instance-isolation",
        "automorphism-tie",
        "invalid-after-warm-key",
    ]
    assert all(case["passed"] for case in behavior)
    assert behavior[2]["diagnostics"] == behavior[2]["expected_diagnostics"]
    assert behavior[3]["diagnostics"] == behavior[3]["expected_diagnostics"]
    assert behavior[5]["tie_count"] == behavior[5]["candidate_count"] == 4
    assert behavior[6]["diagnostics_before"] == behavior[6]["diagnostics_after"]
    assert behavior[6]["rejected"] == behavior[6]["messages_equal"] == 10

    summary = load_json(summary_path)
    assert summary["passed"] and summary["failure_count"] == 0
    assert summary["ordered_pair_record_count"] == len(records)
    assert summary["cache_diagnostics"] == {
        "capacity": 20_000,
        "size": 138,
        "hits": 15_054,
        "misses": 138,
        "core_calls": 138,
        "evictions": 0,
    }
    assert summary["exhaustive"]["canonical_classes_by_n"] == {
        str(n): len(classes_by_n[n]) for n in range(2, 6)
    }
    assert summary["exhaustive"]["canonical_class_count"] == 118
    assert summary["exhaustive"]["existing_terminal_pairs_by_n"] == {
        str(n): edge_pairs[n] for n in range(2, 6)
    }
    assert summary["exhaustive"]["nonedge_terminal_pairs_by_n"] == {
        str(n): nonedge_pairs[n] for n in range(2, 6)
    }
    assert summary["named_6_vertex_families"]["canonical_classes_by_family"] == {
        family: len(keys) for family, keys in family_classes.items()
    }

    for relative, claimed in summary["source_sha256"].items():
        assert sha256(PROJECT / relative) == claimed

    # Pair records are content-identical to the worker's independently retained run.
    worker = PROJECT / "evidence" / "symmetry" / "worker" / "logs" / "correctness-attempt-01"
    worker_comparison = {}
    for name in ("ordered-pair-records.jsonl", "fixture-records.json", "behavior-cases.json"):
        worker_comparison[name] = sha256(root / name) == sha256(worker / name)
        assert worker_comparison[name]

    return {
        "status": "pass",
        "record_count": len(records),
        "raw_full_dictionary_mismatch_count": 0,
        "independent_equation_oracle_mismatch_count": 0,
        "independent_canonicalization_mismatch_count": 0,
        "canonical_classes": sum(len(value) for value in classes_by_n.values())
        + len(set().union(*family_classes.values())),
        "cache_diagnostics": summary["cache_diagnostics"],
        "tree_oracle_cache_entry_count": len(tree_cache),
        "orientation_spanning_tie_instance_count": orientation_spanning_ties,
        "minimizer_count_histogram": dict(sorted(tie_histogram.items())),
        "fixture_count": len(fixture_records),
        "behavior_case_count": len(behavior),
        "worker_raw_content_identical": worker_comparison,
        "artifact_sha256": {
            name: sha256(root / name)
            for name in (
                "ordered-pair-records.jsonl",
                "fixture-records.json",
                "behavior-cases.json",
                "summary.json",
            )
        },
    }


def verify_benchmark(root: Path) -> dict[str, Any]:
    workload_path = root / "workload.jsonl"
    rounds_path = root / "rounds.jsonl"
    summary_path = root / "summary.json"
    workload = load_jsonl(workload_path)
    expected_payloads: list[dict[str, Any]] = []
    expected_counts = {}
    for n in range(2, 6):
        graphs = list(connected_graphs(n))
        expected_counts[str(n)] = len(graphs)
        for edges in graphs:
            source, target = edges[0]
            expected_payloads.append(
                {"n": n, "edges": [list(edge) for edge in edges], "source": source, "target": target}
            )
    assert len(workload) == len(expected_payloads) == 771
    for index, (record, payload) in enumerate(zip(workload, expected_payloads, strict=True)):
        assert record == {"id": f"workload-{index:04d}", "input": payload}

    keys = {
        (payload["n"], minimizers(
            payload["n"], normalized_edges(payload), payload["source"], payload["target"]
        )[0])
        for payload in expected_payloads
    }
    assert len(keys) == 69

    rounds = load_jsonl(rounds_path)
    assert len(rounds) == 21
    expected_result_hash = "98d8462e4fe3475af8f65ede32b2ad4130d06d1939058d63011f3e99a21f202b"
    for index, record in enumerate(rounds, start=1):
        assert record["round"] == index
        assert record["order"] == ("direct-first" if index % 2 else "symmetry-first")
        assert record["direct_call_count"] == 771
        assert record["result_dictionaries_equal"] and record["diagnostics_consistent"]
        assert record["direct_results_sha256"] == expected_result_hash
        assert record["symmetry_results_sha256"] == expected_result_hash
        assert record["direct_nanoseconds"] > 0 and record["symmetry_nanoseconds"] > 0
        assert record["direct_seconds"] == record["direct_nanoseconds"] / 1_000_000_000
        assert record["symmetry_seconds"] == record["symmetry_nanoseconds"] / 1_000_000_000
        assert record["symmetry_diagnostics"] == {
            "capacity": 771,
            "size": 69,
            "hits": 702,
            "misses": 69,
            "core_calls": 69,
            "evictions": 0,
        }

    summary = load_json(summary_path)
    direct = [record["direct_nanoseconds"] for record in rounds]
    symmetry = [record["symmetry_nanoseconds"] for record in rounds]
    direct_median, symmetry_median = int(statistics.median(direct)), int(statistics.median(symmetry))
    assert summary["passed"] and summary["paired_round_count"] == 21
    assert summary["equal_round_count"] == 21
    assert summary["workload"]["counts_by_n"] == expected_counts
    assert summary["workload"]["input_count"] == 771
    assert summary["direct_times_nanoseconds"] == direct
    assert summary["symmetry_times_nanoseconds"] == symmetry
    assert summary["direct_median_nanoseconds"] == direct_median
    assert summary["symmetry_median_nanoseconds"] == symmetry_median
    assert summary["median_direct_over_symmetry_ratio"] == direct_median / symmetry_median
    assert summary["median_time_saved_fraction"] == 1 - symmetry_median / direct_median
    assert summary["direct_call_count_all_measured_rounds"] == 771 * 21
    assert summary["symmetry_core_calls_all_measured_rounds"] == 69 * 21
    assert summary["symmetry_hits_all_measured_rounds"] == 702 * 21
    assert summary["symmetry_misses_all_measured_rounds"] == 69 * 21
    assert summary["symmetry_evictions_all_measured_rounds"] == 0
    assert summary["warmup"]["result_dictionaries_equal"]
    assert summary["warmup"]["symmetry_diagnostics"] == rounds[0]["symmetry_diagnostics"]
    for relative, claimed in summary["source_sha256"].items():
        assert sha256(PROJECT / relative) == claimed

    worker_workload = (
        PROJECT / "evidence" / "symmetry" / "worker" / "logs"
        / "benchmark-attempt-01" / "workload.jsonl"
    )
    assert sha256(workload_path) == sha256(worker_workload)
    return {
        "status": "pass",
        "workload_count": len(workload),
        "independent_workload_sequence_mismatch_count": 0,
        "independent_canonical_class_count": len(keys),
        "equal_round_count": len(rounds),
        "direct_median_nanoseconds": direct_median,
        "symmetry_median_nanoseconds": symmetry_median,
        "median_direct_over_symmetry_ratio": direct_median / symmetry_median,
        "median_time_saved_fraction": 1 - symmetry_median / direct_median,
        "worker_workload_content_identical": True,
        "artifact_sha256": {
            name: sha256(root / name)
            for name in ("workload.jsonl", "rounds.jsonl", "summary.json")
        },
    }


def verify_wrapper_metadata(name: str) -> dict[str, Any]:
    metadata_path = AUDIT / f"{name}.command.json"
    console_path = AUDIT / f"{name}.console.log"
    metadata = load_json(metadata_path)
    assert metadata["exit_code"] == 0
    assert Path(metadata["cwd"]).resolve() == PROJECT.resolve()
    assert Path(metadata["console_log"]).resolve() == console_path.resolve()
    assert metadata["environment_overrides"] == {
        "PYTHONDONTWRITEBYTECODE": "1",
        "UV_CACHE_DIR": "D:/CodexWorkspaces/mathematics-atlas/uv-cache",
    }
    return {
        "command": metadata["argv"],
        "exit_code": metadata["exit_code"],
        "runtime_seconds": metadata["runtime_seconds"],
        "metadata_sha256": sha256(metadata_path),
        "console_sha256": sha256(console_path),
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--correctness",
        type=Path,
        default=AUDIT / "verifier-correctness-attempt-02",
    )
    parser.add_argument(
        "--benchmark",
        type=Path,
        default=AUDIT / "verifier-benchmark-attempt-01",
    )
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    result: dict[str, Any] = {
        "schema_version": "1.0",
        "auditor": "/root/sol_symmetry_audit (independent verifier; no candidate authorship)",
        "scope": "frozen project-specific unordered-terminal cache and finite benchmark",
        "correctness": verify_correctness(args.correctness),
        "benchmark": verify_benchmark(args.benchmark),
        "wrapper_metadata": {
            "pytest": verify_wrapper_metadata("verifier-pytest-attempt-03"),
            "correctness": verify_wrapper_metadata("verifier-correctness-attempt-02"),
            "benchmark": verify_wrapper_metadata("verifier-benchmark-attempt-01"),
        },
        "candidate_sha256": sha256(PROJECT / "src" / "atlas_engine" / "symmetry.py"),
        "status": "pass",
        "limitations": [
            "The exhaustive component is bounded to all labelled connected simple graphs on 2 through 5 vertices.",
            "The 6-vertex component covers five named families, not all 6-vertex graphs.",
            "The benchmark conclusion applies only to the frozen 771-input workload and recorded environment.",
            "Passing finite enumeration does not prove unrestricted correctness or global novelty.",
        ],
    }
    args.output.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(result, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
