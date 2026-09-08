"""Deterministic exhaustive evaluator for the frozen version-1 contract."""

from __future__ import annotations

import json
from itertools import combinations
from pathlib import Path
from typing import Iterator

from .analysis import analyze_graph
from .validation import InputValidationError


EXPECTED_CONNECTED_COUNTS = {2: 1, 3: 4, 4: 38, 5: 728}


def _connected(n: int, edges: list[tuple[int, int]]) -> bool:
    neighbors = [[] for _ in range(n)]
    for left, right in edges:
        neighbors[left].append(right)
        neighbors[right].append(left)
    seen = {0}
    pending = [0]
    while pending:
        vertex = pending.pop()
        for neighbor in neighbors[vertex]:
            if neighbor not in seen:
                seen.add(neighbor)
                pending.append(neighbor)
    return len(seen) == n


def _connected_graphs(n: int) -> Iterator[list[tuple[int, int]]]:
    possible = list(combinations(range(n), 2))
    for mask in range(1 << len(possible)):
        edges = [edge for index, edge in enumerate(possible) if mask & (1 << index)]
        if _connected(n, edges):
            yield edges


def _fixture_path() -> Path:
    candidates = [
        Path.cwd() / "fixtures" / "frozen.json",
        Path(__file__).resolve().parents[2] / "fixtures" / "frozen.json",
    ]
    for candidate in candidates:
        if candidate.is_file():
            return candidate
    raise FileNotFoundError("fixtures/frozen.json was not found")


def run_evaluation(output_dir: Path) -> dict[str, object]:
    output_dir.mkdir(parents=True, exist_ok=True)
    records_path = output_dir / "records.jsonl"
    summary_path = output_dir / "summary.json"
    failures: list[dict[str, object]] = []
    counts_by_n: dict[str, int] = {}
    record_count = 0

    with records_path.open("w", encoding="utf-8", newline="\n") as records:
        for n in range(2, 6):
            count = 0
            for graph_index, edges in enumerate(_connected_graphs(n)):
                source, target = edges[0]
                payload = {
                    "n": n,
                    "edges": [list(edge) for edge in edges],
                    "source": source,
                    "target": target,
                }
                try:
                    result = analyze_graph(payload)
                    record = {
                        "id": f"labeled-n{n}-{graph_index:04d}",
                        "kind": "exhaustive",
                        "input": payload,
                        "result": result,
                    }
                except Exception as error:  # retained in raw evaluator output
                    record = {
                        "id": f"labeled-n{n}-{graph_index:04d}",
                        "kind": "exhaustive",
                        "input": payload,
                        "error": f"{type(error).__name__}: {error}",
                    }
                    failures.append(record)
                records.write(json.dumps(record, sort_keys=True, separators=(",", ":")) + "\n")
                count += 1
                record_count += 1
            counts_by_n[str(n)] = count
            if count != EXPECTED_CONNECTED_COUNTS[n]:
                failures.append({"kind": "graph-count", "n": n, "actual": count})

        fixtures = json.loads(_fixture_path().read_text(encoding="utf-8"))
        for fixture in fixtures["valid"]:
            if fixture["input"]["n"] != 6:
                continue
            try:
                result = analyze_graph(fixture["input"])
                mismatches = {
                    key: {"expected": expected, "actual": result[key]}
                    for key, expected in fixture["expected"].items()
                    if result[key] != expected
                }
                record = {
                    "id": fixture["id"],
                    "kind": "named-6-vertex-fixture",
                    "input": fixture["input"],
                    "result": result,
                    "mismatches": mismatches,
                }
                if mismatches:
                    failures.append(record)
            except Exception as error:
                record = {
                    "id": fixture["id"],
                    "kind": "named-6-vertex-fixture",
                    "input": fixture["input"],
                    "error": f"{type(error).__name__}: {error}",
                }
                failures.append(record)
            records.write(json.dumps(record, sort_keys=True, separators=(",", ":")) + "\n")
            record_count += 1

    valid_fixture_failures = 0
    for fixture in fixtures["valid"]:
        result = analyze_graph(fixture["input"])
        if any(result[key] != expected for key, expected in fixture["expected"].items()):
            valid_fixture_failures += 1
    invalid_fixture_failures = 0
    for fixture in fixtures["invalid"]:
        try:
            analyze_graph(fixture["input"])
        except InputValidationError:
            pass
        else:
            invalid_fixture_failures += 1

    if valid_fixture_failures:
        failures.append({"kind": "valid-fixtures", "failures": valid_fixture_failures})
    if invalid_fixture_failures:
        failures.append({"kind": "invalid-fixtures", "accepted": invalid_fixture_failures})

    summary: dict[str, object] = {
        "schema_version": "1.0",
        "selection_policy": "lexicographically first existing edge per exhaustive graph",
        "exact_comparisons": True,
        "sampled": False,
        "counts_by_n": counts_by_n,
        "exhaustive_graph_count": sum(counts_by_n.values()),
        "named_6_vertex_fixture_count": sum(
            fixture["input"]["n"] == 6 for fixture in fixtures["valid"]
        ),
        "record_count": record_count,
        "edges_analyzed_per_graph": 1,
        "valid_fixture_count": len(fixtures["valid"]),
        "invalid_fixture_count": len(fixtures["invalid"]),
        "failure_count": len(failures),
        "failures": failures,
        "passed": not failures,
        "records_path": str(records_path.resolve()),
    }
    summary_path.write_text(json.dumps(summary, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return summary

