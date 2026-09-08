from __future__ import annotations

import hashlib
import itertools
import json
import math
from collections import Counter, defaultdict
from datetime import datetime
from fractions import Fraction
from pathlib import Path


ROOT = Path("D:/CodexWorkspaces/mathematics-atlas")
AUTHOR = ROOT / "kemeny-author-work"
INDEPENDENT = ROOT / "kemeny-independent-work"
INPUTS = ROOT / "kemeny-input-work"
OUTPUT = ROOT / "kemeny-final-review-work/raw/audit-check.json"

EXPECTED = {
    2: ("graph2c.g6", 1, 1),
    3: ("graph3c.g6", 2, 4),
    4: ("graph4c.g6", 6, 38),
    5: ("graph5c.g6", 21, 728),
    6: ("graph6c.g6", 112, 26704),
}


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def check_file(path: Path, expected_bytes: int, expected_sha256: str) -> dict[str, object]:
    actual_bytes = path.stat().st_size
    actual_sha256 = sha256(path)
    assert actual_bytes == expected_bytes, (path, actual_bytes, expected_bytes)
    assert actual_sha256 == expected_sha256, (path, actual_sha256, expected_sha256)
    return {
        "path": str(path),
        "bytes": actual_bytes,
        "sha256": actual_sha256,
        "pass": True,
    }


def lex_edges(n: int) -> tuple[tuple[int, int], ...]:
    return tuple((u, v) for u in range(n) for v in range(u + 1, n))


def graph6_edges(n: int) -> tuple[tuple[int, int], ...]:
    return tuple((u, v) for v in range(1, n) for u in range(v))


def edges_from_mask(n: int, mask: int) -> tuple[tuple[int, int], ...]:
    return tuple(edge for i, edge in enumerate(lex_edges(n)) if mask & (1 << i))


def mask_from_edges(n: int, edges: tuple[tuple[int, int], ...]) -> int:
    lookup = {edge: i for i, edge in enumerate(lex_edges(n))}
    mask = 0
    for edge in edges:
        assert edge in lookup
        bit = 1 << lookup[edge]
        assert not mask & bit
        mask |= bit
    return mask


def decode_graph6(raw: bytes, expected_n: int) -> int:
    assert raw and not raw.startswith(b">>graph6<<")
    assert all(63 <= byte <= 126 for byte in raw)
    n = raw[0] - 63
    assert n == expected_n and n <= 62
    bit_count = math.comb(n, 2)
    assert len(raw) == 1 + (bit_count + 5) // 6
    bits: list[int] = []
    for byte in raw[1:]:
        value = byte - 63
        bits.extend((value >> shift) & 1 for shift in range(5, -1, -1))
    assert not any(bits[bit_count:])
    present = tuple(edge for bit, edge in zip(bits[:bit_count], graph6_edges(n), strict=True) if bit)
    return mask_from_edges(n, present)


def encode_graph6(n: int, mask: int) -> bytes:
    present = set(edges_from_mask(n, mask))
    bits = [int(edge in present) for edge in graph6_edges(n)]
    bits.extend([0] * ((-len(bits)) % 6))
    payload = []
    for start in range(0, len(bits), 6):
        value = 0
        for bit in bits[start : start + 6]:
            value = (value << 1) | bit
        payload.append(value + 63)
    return bytes([n + 63, *payload])


def connected(n: int, mask: int) -> bool:
    adjacency = [0] * n
    for u, v in edges_from_mask(n, mask):
        adjacency[u] |= 1 << v
        adjacency[v] |= 1 << u
    seen = 1
    frontier = 1
    while frontier:
        bit = frontier & -frontier
        frontier ^= bit
        vertex = bit.bit_length() - 1
        new = adjacency[vertex] & ~seen
        seen |= new
        frontier |= new
    return seen == (1 << n) - 1


def permute_mask(n: int, mask: int, permutation: tuple[int, ...]) -> int:
    transformed = tuple(tuple(sorted((permutation[u], permutation[v]))) for u, v in edges_from_mask(n, mask))
    return mask_from_edges(n, transformed)


def mask_digest(n: int, values: set[int]) -> str:
    width = max(1, (math.comb(n, 2) + 3) // 4)
    payload = "".join(f"{value:0{width}x}\n" for value in sorted(values)).encode("ascii")
    return hashlib.sha256(payload).hexdigest()


def public_edges(edges: tuple[tuple[int, int], ...]) -> tuple[tuple[int, int], ...]:
    return tuple((u + 1, v + 1) for u, v in edges)


def private_edges(value: object) -> tuple[tuple[int, int], ...]:
    assert isinstance(value, list)
    result = tuple((int(edge[0]) - 1, int(edge[1]) - 1) for edge in value)
    assert result == tuple(sorted(result))
    assert all(0 <= u < v for u, v in result)
    return result


def rat(value: object) -> Fraction:
    assert isinstance(value, dict) and set(value) == {"denominator", "numerator"}
    numerator = value["numerator"]
    denominator = value["denominator"]
    assert isinstance(numerator, int) and isinstance(denominator, int)
    assert denominator > 0 and math.gcd(abs(numerator), denominator) == 1
    return Fraction(numerator, denominator)


def fraction_record(value: Fraction) -> dict[str, int]:
    return {"numerator": value.numerator, "denominator": value.denominator}


def sign(value: Fraction) -> str:
    return "positive" if value > 0 else "negative" if value < 0 else "zero"


def state_id(n: int, edges: tuple[tuple[int, int], ...]) -> str:
    return "n=" + str(n) + ";edges=" + ",".join(f"{u + 1}-{v + 1}" for u, v in edges)


def multiply(left: list[list[Fraction]], right: list[list[Fraction]]) -> list[list[Fraction]]:
    size = len(left)
    return [
        [sum((left[i][k] * right[k][j] for k in range(size)), Fraction(0)) for j in range(size)]
        for i in range(size)
    ]


def inverse(matrix: list[list[Fraction]]) -> list[list[Fraction]]:
    size = len(matrix)
    aug = [row[:] + [Fraction(int(i == j)) for j in range(size)] for i, row in enumerate(matrix)]
    for column in range(size):
        pivot = next((row for row in range(column, size) if aug[row][column]), None)
        assert pivot is not None
        aug[column], aug[pivot] = aug[pivot], aug[column]
        scale = aug[column][column]
        aug[column] = [entry / scale for entry in aug[column]]
        for row in range(size):
            if row == column:
                continue
            scale = aug[row][column]
            if scale:
                aug[row] = [a - scale * b for a, b in zip(aug[row], aug[column], strict=True)]
    result = [row[size:] for row in aug]
    identity = [[Fraction(int(i == j)) for j in range(size)] for i in range(size)]
    assert [row[:size] for row in aug] == identity
    assert multiply(matrix, result) == identity
    assert multiply(result, matrix) == identity
    return result


def kemeny_fundamental(n: int, edges: tuple[tuple[int, int], ...]) -> dict[str, object]:
    assert len(set(edges)) == len(edges)
    mask = mask_from_edges(n, tuple(sorted(edges)))
    assert connected(n, mask)
    degrees = [0] * n
    adjacency = [[0] * n for _ in range(n)]
    for u, v in edges:
        degrees[u] += 1
        degrees[v] += 1
        adjacency[u][v] = adjacency[v][u] = 1
    edge_count = len(edges)
    assert all(degrees) and sum(degrees) == 2 * edge_count
    transition = [[Fraction(adjacency[i][j], degrees[i]) for j in range(n)] for i in range(n)]
    assert all(sum(row, Fraction(0)) == 1 for row in transition)
    stationary = [Fraction(degree, 2 * edge_count) for degree in degrees]
    assert sum(stationary, Fraction(0)) == 1
    assert [
        sum((stationary[i] * transition[i][j] for i in range(n)), Fraction(0))
        for j in range(n)
    ] == stationary
    fundamental_input = [
        [Fraction(int(i == j)) - transition[i][j] + stationary[j] for j in range(n)]
        for i in range(n)
    ]
    fundamental = inverse(fundamental_input)
    value = sum((fundamental[i][i] for i in range(n)), Fraction(0)) - 1
    return {
        "n": n,
        "edges": [list(edge) for edge in public_edges(tuple(sorted(edges)))],
        "degrees": degrees,
        "stationary": [fraction_record(value) for value in stationary],
        "formula": "trace((I-P+1*pi^T)^-1)-1",
        "exact_inverse_verified_both_sides": True,
        "kemeny": fraction_record(value),
    }


def read_jsonl(path: Path) -> list[dict[str, object]]:
    records = []
    with path.open("r", encoding="utf-8", newline="") as handle:
        for line_number, line in enumerate(handle, start=1):
            assert line.endswith("\n")
            record = json.loads(line)
            assert isinstance(record, dict)
            records.append(record)
    return records


def instant(value: str) -> datetime:
    return datetime.fromisoformat(value.replace("Z", "+00:00"))


def normalize_pair(record: dict[str, object], flavor: str, source_lookup: dict[tuple[int, int], tuple[str, int]]) -> dict[str, object]:
    n = int(record["n"])
    source_line = int(record["source_line"])
    graph6 = str(record["source_graph6"] if flavor == "author" else record["graph6"])
    source_file = str(record["source_file"])
    expected_graph6, base_mask = source_lookup[(n, source_line)]
    assert source_file == EXPECTED[n][0] and graph6 == expected_graph6
    base_edges = private_edges(record["base_edges"])
    assert mask_from_edges(n, base_edges) == base_mask
    added = private_edges(record["added_edges"])
    assert len(added) == 2 and added[0] < added[1] and added[0] != added[1]
    assert all(edge not in base_edges for edge in added)
    e, f = added
    expected_states = {
        "base": base_edges,
        "e": tuple(sorted((*base_edges, e))),
        "f": tuple(sorted((*base_edges, f))),
        "both": tuple(sorted((*base_edges, e, f))),
    }
    if flavor == "author":
        state_names = {"base": "base", "e": "single_e", "f": "single_f", "both": "joint"}
        k_names = state_names
        delta_names = {"e": "single_e_minus_base", "f": "single_f_minus_base", "both": "joint_minus_base"}
        signs = record["signs"]
        flags = record["equality_flags"]
        flag_names = {"e": "single_e_equals_base", "f": "single_f_equals_base", "both": "joint_equals_base"}
    else:
        state_names = {"base": "G", "e": "G_plus_e", "f": "G_plus_f", "both": "G_plus_e_plus_f"}
        k_names = state_names
        delta_names = {"e": "e", "f": "f", "both": "both"}
        classification = record["classification"]
        signs = {name: classification[f"delta_{name}_sign"] for name in ("e", "f", "both")}
        flags = {name: classification[f"delta_{name}_equal"] for name in ("e", "f", "both")}
        flag_names = {"e": "e", "f": "f", "both": "both"}
    for canonical, actual in state_names.items():
        state = record["states"][actual]
        assert private_edges(state["edges"]) == expected_states[canonical]
        if flavor == "author":
            assert state["state_id"] == state_id(n, expected_states[canonical])
        else:
            assert state["n"] == n
    k = {name: rat(record["kemeny"][actual]) for name, actual in k_names.items()}
    deltas = {name: rat(record["deltas"][actual]) for name, actual in delta_names.items()}
    assert deltas == {"e": k["e"] - k["base"], "f": k["f"] - k["base"], "both": k["both"] - k["base"]}
    for name in ("e", "f", "both"):
        actual_sign = signs[delta_names[name]] if flavor == "author" else signs[name]
        actual_flag = flags[flag_names[name]]
        assert actual_sign == sign(deltas[name])
        assert actual_flag is (deltas[name] == 0)
    qualifies = deltas["e"] <= 0 and deltas["f"] <= 0 and deltas["both"] > 0
    if flavor == "author":
        assert record["qualifies"] is qualifies
    else:
        assert record["classification"]["qualifies"] is qualifies
    if flavor == "independent":
        classification = record["classification"]
        assert classification["singleton_e_nonincreasing"] is (deltas["e"] <= 0)
        assert classification["singleton_f_nonincreasing"] is (deltas["f"] <= 0)
        assert classification["joint_strict_increase"] is (deltas["both"] > 0)
    return {
        "key": (n, source_file, source_line, graph6, e, f),
        "states": expected_states,
        "k": k,
        "deltas": deltas,
        "qualifies": qualifies,
    }


def main() -> None:
    integrity: dict[str, object] = {}
    integrity["contract"] = check_file(
        ROOT / "kemeny-spec-work/contract-v1.md",
        10309,
        "1ff78636c4dcadc7d8f9d6a3a36c144e193e5f90cbb970ab846c877cdf0c6ac6",
    )

    author_manifest_path = AUTHOR / "result-manifest.json"
    integrity["author_manifest"] = check_file(
        author_manifest_path,
        5978,
        "78b4121cc83d7e06bed7470f70c1cbb365ba1d24543595f7620b9e15e0524a9d",
    )
    author_manifest = json.loads(author_manifest_path.read_text(encoding="utf-8"))
    integrity["author_artifacts"] = [
        check_file(AUTHOR / item["path"], item["bytes"], item["sha256"])
        for item in author_manifest["artifacts"]
    ]

    input_freeze_path = INDEPENDENT / "input-freeze-manifest.json"
    integrity["independent_input_freeze"] = check_file(
        input_freeze_path,
        7395,
        "e76e474f723cfdc6af6014cf35371601a2525a6ee78e148bb72ef99b9249019d",
    )
    input_freeze = json.loads(input_freeze_path.read_text(encoding="utf-8"))
    integrity["independent_frozen_inputs"] = [
        check_file(Path(item["path"]), item["bytes"], item["sha256"])
        for item in input_freeze["files"]
    ]

    output_seal_path = INDEPENDENT / "independent-output-seal.json"
    integrity["independent_output_seal"] = check_file(
        output_seal_path,
        2256,
        "7ccdcbbd54a21fec1bfdfc668c05c9cc06564a985e82e68e9c4958a110994b2d",
    )
    output_seal = json.loads(output_seal_path.read_text(encoding="utf-8"))
    assert output_seal["input_freeze_manifest_sha256"] == integrity["independent_input_freeze"]["sha256"]
    integrity["independent_outputs_and_logs"] = [
        check_file(INDEPENDENT / item["path"], item["bytes"], item["sha256"])
        for group in ("deterministic_outputs", "command_logs")
        for item in output_seal[group]
    ]

    comparison_seal_path = INDEPENDENT / "comparison-seal.json"
    integrity["independent_comparison_seal"] = check_file(
        comparison_seal_path,
        2642,
        "c7e0cd6892639dd5403c4275b3904afcf2536fedd32f059e4a7c77cc11829204",
    )
    comparison_seal = json.loads(comparison_seal_path.read_text(encoding="utf-8"))
    integrity["independent_comparison_artifacts"] = [
        check_file(INDEPENDENT / item["path"], item["bytes"], item["sha256"])
        for item in comparison_seal["files"]
    ]
    explanation_path = ROOT / "kemeny-explanation-work/witness-explanation.json"
    integrity["author_witness_explanation"] = check_file(
        explanation_path,
        7422,
        "944aedd72b479ea875fef53780da3d80d18007521eb8e774b5bfabef48baf396",
    )

    source_lookup: dict[tuple[int, int], tuple[str, int]] = {}
    source_rows: dict[int, list[tuple[str, int]]] = {}
    coverage_orders = []
    expected_pair_keys: list[tuple[object, ...]] = []
    for n, (filename, representative_count, labelled_count) in EXPECTED.items():
        raw_lines = (INPUTS / filename).read_bytes().splitlines()
        assert len(raw_lines) == representative_count and len(set(raw_lines)) == representative_count
        rows: list[tuple[str, int]] = []
        union: set[int] = set()
        orbit_details = []
        pair_count = 0
        zero_pair_rows = 0
        for line_number, raw in enumerate(raw_lines, start=1):
            mask = decode_graph6(raw, n)
            assert encode_graph6(n, mask) == raw
            assert connected(n, mask)
            graph6 = raw.decode("ascii")
            source_lookup[(n, line_number)] = (graph6, mask)
            rows.append((graph6, mask))
            orbit = {permute_mask(n, mask, permutation) for permutation in itertools.permutations(range(n))}
            assert not union.intersection(orbit)
            union.update(orbit)
            nonedges = tuple(edge for edge in lex_edges(n) if edge not in edges_from_mask(n, mask))
            pairs = tuple(itertools.combinations(nonedges, 2))
            if not pairs:
                zero_pair_rows += 1
            pair_count += len(pairs)
            expected_pair_keys.extend(
                (n, filename, line_number, graph6, e, f) for e, f in pairs
            )
            orbit_details.append(
                {
                    "source_line": line_number,
                    "graph6": graph6,
                    "orbit_size": len(orbit),
                    "orbit_sha256": mask_digest(n, orbit),
                    "nonedge_count": len(nonedges),
                    "pair_count": len(pairs),
                }
            )
        connected_set = {mask for mask in range(1 << math.comb(n, 2)) if connected(n, mask)}
        assert len(connected_set) == labelled_count
        assert union == connected_set
        digest = mask_digest(n, connected_set)
        source_rows[n] = rows
        coverage_orders.append(
            {
                "n": n,
                "representative_count": len(rows),
                "connected_labelled_count": len(connected_set),
                "orbit_union_count": len(union),
                "sets_equal": True,
                "orbits_pairwise_disjoint": True,
                "set_sha256": digest,
                "candidate_pair_count": pair_count,
                "zero_pair_source_row_count": zero_pair_rows,
                "representatives": orbit_details,
            }
        )

    independent_completeness = json.loads((INDEPENDENT / "run-01/completeness.json").read_text(encoding="utf-8"))
    assert independent_completeness["status"] == "complete_set_equality_verified"
    assert independent_completeness["pair_census_count_verified"] is True
    for actual, recorded in zip(coverage_orders, independent_completeness["orders"], strict=True):
        assert recorded["n"] == actual["n"]
        assert recorded["actual_representative_count"] == actual["representative_count"]
        assert recorded["actual_connected_labelled_count"] == actual["connected_labelled_count"]
        assert recorded["orbit_union_count"] == actual["orbit_union_count"]
        assert recorded["actual_sets_equal"] is True
        assert recorded["representative_orbits_pairwise_disjoint"] is True
        assert recorded["connected_labelled_set_sha256"] == actual["set_sha256"]
        assert recorded["representative_orbit_union_sha256"] == actual["set_sha256"]
        assert recorded["candidate_pair_count"] == actual["candidate_pair_count"]
        assert recorded["zero_pair_source_row_count"] == actual["zero_pair_source_row_count"]
        for observed_rep, expected_rep in zip(recorded["representatives"], actual["representatives"], strict=True):
            for field in ("source_line", "graph6", "orbit_size", "orbit_sha256", "nonedge_count", "pair_count"):
                assert observed_rep[field] == expected_rep[field]
            assert observed_rep["evaluated_pair_count"] == expected_rep["pair_count"]
            assert observed_rep["evaluated_pair_count_matches"] is True
    assert independent_completeness["totals"] == {
        "candidate_pair_count": len(expected_pair_keys),
        "connected_labelled_count": sum(item[2] for item in EXPECTED.values()),
        "representative_count": sum(item[1] for item in EXPECTED.values()),
    }

    expected_pair_key_digest = hashlib.sha256()
    for n, source_file, source_line, graph6, e, f in expected_pair_keys:
        key_record = {
            "n": n,
            "source_file": source_file,
            "source_line": source_line,
            "graph6": graph6,
            "e": [e[0] + 1, e[1] + 1],
            "f": [f[0] + 1, f[1] + 1],
        }
        expected_pair_key_digest.update(
            (json.dumps(key_record, ensure_ascii=True, sort_keys=True, separators=(",", ":")) + "\n").encode("utf-8")
        )

    author_values_doc = json.loads((AUTHOR / "run-01/graph-values.json").read_text(encoding="utf-8"))
    independent_values_doc = json.loads((INDEPENDENT / "run-01/graph-values.json").read_text(encoding="utf-8"))
    author_values: dict[str, Fraction] = {}
    independent_values: dict[str, Fraction] = {}
    for record in author_values_doc["values"]:
        n = record["n"]
        edges = private_edges(record["edges"])
        sid = state_id(n, edges)
        assert record["state_id"] == sid and sid not in author_values
        assert connected(n, mask_from_edges(n, edges))
        degree = [0] * n
        for u, v in edges:
            degree[u] += 1
            degree[v] += 1
        assert record["degrees"] == degree
        assert record["edge_count"] == len(edges)
        transition = [[rat(item) for item in row] for row in record["transition_matrix"]]
        assert all(sum(row, Fraction(0)) == 1 for row in transition)
        for row in range(n):
            for column in range(n):
                expected = Fraction(int(tuple(sorted((row, column))) in edges), degree[row]) if row != column else Fraction(0)
                assert transition[row][column] == expected
        assert record["ground_vertex"] == n
        assert record["grounded_laplacian_determinant"] > 0
        assert record["grounded_inverse_verified"] is True
        author_values[sid] = rat(record["kemeny"])
    for record in independent_values_doc["states"]:
        n = record["n"]
        edges = private_edges(record["edges"])
        sid = state_id(n, edges)
        assert record["state_id"] == sid and sid not in independent_values
        assert connected(n, mask_from_edges(n, edges))
        degree = [0] * n
        for u, v in edges:
            degree[u] += 1
            degree[v] += 1
        assert record["degrees"] == degree and record["edge_count"] == len(edges)
        method = record["method"]
        coefficients = [rat(value) for value in method["characteristic_coefficients_descending"]]
        assert len(coefficients) == n + 1 and coefficients[0] == 1 and coefficients[-1] == 0
        assert method["p_constant_zero"] is True
        assert coefficients[-2] != 0 and method["q_constant_nonzero"] is True
        assert rat(method["q_constant"]) == coefficients[-2]
        assert rat(method["q_linear"]) == coefficients[-3]
        k = rat(record["kemeny"])
        assert k == -coefficients[-3] / coefficients[-2]
        independent_values[sid] = k
    assert author_values_doc["state_count"] == len(author_values) == 1848
    assert independent_values_doc["state_count"] == len(independent_values) == 1848
    assert author_values.keys() == independent_values.keys()
    graph_value_mismatches = [sid for sid in author_values if author_values[sid] != independent_values[sid]]
    assert not graph_value_mismatches
    state_counts_by_order = Counter(int(sid.split(";", 1)[0].split("=", 1)[1]) for sid in author_values)
    assert set(state_counts_by_order) == {2, 3, 4, 5, 6, 7}
    assert state_counts_by_order[7] == 4
    periodic_state = "n=2;edges=1-2"
    assert author_values[periodic_state] == independent_values[periodic_state] == Fraction(1, 2)

    author_pairs_raw = read_jsonl(AUTHOR / "run-01/pairs.jsonl")
    independent_pairs_raw = read_jsonl(INDEPENDENT / "run-01/pairs.jsonl")
    assert len(author_pairs_raw) == len(independent_pairs_raw) == len(expected_pair_keys) == 2390
    author_pairs = [normalize_pair(record, "author", source_lookup) for record in author_pairs_raw]
    independent_pairs = [normalize_pair(record, "independent", source_lookup) for record in independent_pairs_raw]
    assert [record["key"] for record in author_pairs] == expected_pair_keys
    assert [record["key"] for record in independent_pairs] == expected_pair_keys
    assert [record["pair_index_global"] for record in author_pairs_raw] == list(range(1, 2391))
    per_graph_index: defaultdict[tuple[int, int], int] = defaultdict(int)
    for record in author_pairs_raw:
        key = (record["n"], record["source_line"])
        per_graph_index[key] += 1
        assert record["pair_index_in_graph"] == per_graph_index[key]
    semantic_pair_mismatches = []
    for index, (author, independent) in enumerate(zip(author_pairs, independent_pairs, strict=True), start=1):
        if author != independent:
            semantic_pair_mismatches.append(index)
        for name, edges in author["states"].items():
            sid = state_id(author["key"][0], edges)
            assert author["k"][name] == author_values[sid] == independent_values[sid]
    assert not semantic_pair_mismatches

    qualifying = [record for record in author_pairs if record["qualifies"]]
    assert len(qualifying) == 1
    order_counts = Counter(record["key"][0] for record in author_pairs)
    witness_counts = Counter(record["key"][0] for record in qualifying)
    equality_occurrences = {
        "e": sum(record["deltas"]["e"] == 0 for record in author_pairs),
        "f": sum(record["deltas"]["f"] == 0 for record in author_pairs),
        "both": sum(record["deltas"]["both"] == 0 for record in author_pairs),
        "pairs_with_any_singleton_equality": sum(
            record["deltas"]["e"] == 0 or record["deltas"]["f"] == 0 for record in author_pairs
        ),
    }
    minimum_order = min(record["key"][0] for record in qualifying)
    assert order_counts == Counter({4: 8, 5: 139, 6: 2243})
    assert witness_counts == Counter({6: 1}) and minimum_order == 6
    assert equality_occurrences == {"e": 2, "f": 5, "both": 0, "pairs_with_any_singleton_equality": 7}

    witness = qualifying[0]
    assert witness["key"] == (6, "graph6c.g6", 10, "E?zW", (0, 1), (2, 3))
    expected_candidate_k = {
        "base": Fraction(135, 28),
        "e": Fraction(77, 16),
        "f": Fraction(135, 28),
        "both": Fraction(1229, 252),
    }
    assert witness["k"] == expected_candidate_k
    assert witness["deltas"] == {"e": Fraction(-1, 112), "f": Fraction(0), "both": Fraction(1, 18)}

    author_witnesses = json.loads((AUTHOR / "run-01/witnesses.json").read_text(encoding="utf-8"))
    independent_witnesses = json.loads((INDEPENDENT / "run-01/witnesses.json").read_text(encoding="utf-8"))
    assert author_witnesses["witness_count"] == independent_witnesses["witness_count"] == 1
    assert normalize_pair(author_witnesses["witnesses"][0], "author", source_lookup) == witness
    assert normalize_pair(independent_witnesses["witnesses"][0], "independent", source_lookup) == witness

    author_p7 = json.loads((AUTHOR / "run-01/published-p7.json").read_text(encoding="utf-8"))
    independent_p7 = json.loads((INDEPENDENT / "run-01/published-p7.json").read_text(encoding="utf-8"))
    p7_base = tuple((i, i + 1) for i in range(6))
    p7_e, p7_f = (0, 2), (4, 6)
    assert private_edges(author_p7["base_edges"]) == p7_base
    assert private_edges(author_p7["added_edges"]) == (p7_e, p7_f)
    assert private_edges(independent_p7["fixed_labels"]["base_edges"]) == p7_base
    assert private_edges(independent_p7["fixed_labels"]["added_edges"]) == (p7_e, p7_f)
    independent_p7_pair = independent_p7["pair"]
    p7_expected_states = {
        "base": p7_base,
        "e": tuple(sorted((*p7_base, p7_e))),
        "f": tuple(sorted((*p7_base, p7_f))),
        "both": tuple(sorted((*p7_base, p7_e, p7_f))),
    }
    p7_expected_k = {
        "base": Fraction(73, 6),
        "e": Fraction(254, 21),
        "f": Fraction(254, 21),
        "both": Fraction(293, 24),
    }
    p7_expected_deltas = {
        "e": Fraction(-1, 14),
        "f": Fraction(-1, 14),
        "both": Fraction(1, 24),
    }
    author_p7_k = {
        "base": rat(author_p7["kemeny"]["base"]),
        "e": rat(author_p7["kemeny"]["single_e"]),
        "f": rat(author_p7["kemeny"]["single_f"]),
        "both": rat(author_p7["kemeny"]["joint"]),
    }
    independent_p7_k = {
        "base": rat(independent_p7_pair["kemeny"]["G"]),
        "e": rat(independent_p7_pair["kemeny"]["G_plus_e"]),
        "f": rat(independent_p7_pair["kemeny"]["G_plus_f"]),
        "both": rat(independent_p7_pair["kemeny"]["G_plus_e_plus_f"]),
    }
    author_p7_deltas = {
        "e": rat(author_p7["deltas"]["single_e_minus_base"]),
        "f": rat(author_p7["deltas"]["single_f_minus_base"]),
        "both": rat(author_p7["deltas"]["joint_minus_base"]),
    }
    independent_p7_deltas = {
        name: rat(independent_p7_pair["deltas"][name]) for name in ("e", "f", "both")
    }
    assert author_p7_k == independent_p7_k == p7_expected_k
    assert author_p7_deltas == independent_p7_deltas == p7_expected_deltas
    assert author_p7["qualifies"] is True
    assert independent_p7["source_inequalities_pass"] is True
    assert independent_p7_pair["classification"]["qualifies"] is True
    for canonical, author_name, independent_name in (
        ("base", "base", "G"),
        ("e", "single_e", "G_plus_e"),
        ("f", "single_f", "G_plus_f"),
        ("both", "joint", "G_plus_e_plus_f"),
    ):
        assert private_edges(author_p7["states"][author_name]["edges"]) == p7_expected_states[canonical]
        assert private_edges(independent_p7_pair["states"][independent_name]["edges"]) == p7_expected_states[canonical]
        sid = state_id(7, p7_expected_states[canonical])
        assert author_values[sid] == independent_values[sid] == p7_expected_k[canonical]

    required_state_ids = {
        state_id(n, edges_from_mask(n, mask))
        for (n, _source_line), (_graph6, mask) in source_lookup.items()
    }
    for pair in author_pairs:
        required_state_ids.update(state_id(pair["key"][0], edges) for edges in pair["states"].values())
    required_state_ids.update(state_id(7, edges) for edges in p7_expected_states.values())
    assert required_state_ids == set(author_values) == set(independent_values)

    candidate_direct = {
        name: kemeny_fundamental(6, edges) for name, edges in witness["states"].items()
    }
    p7_direct = {
        name: kemeny_fundamental(7, edges) for name, edges in p7_expected_states.items()
    }
    for name in ("base", "e", "f", "both"):
        assert rat(candidate_direct[name]["kemeny"]) == expected_candidate_k[name]
        assert rat(p7_direct[name]["kemeny"]) == p7_expected_k[name]
    periodic_direct = kemeny_fundamental(2, ((0, 1),))
    assert rat(periodic_direct["kemeny"]) == Fraction(1, 2)

    author_command = json.loads((AUTHOR / "logs/canonical-01/command.json").read_text(encoding="utf-8"))
    independent_command = json.loads((INDEPENDENT / "logs/attempt-run-01.json").read_text(encoding="utf-8"))
    assert author_command["return_code"] == 0 and author_command["timeout"] is False
    assert independent_command["returncode"] == 0 and independent_command["timed_out"] is False
    assert author_command["timeout_seconds"] == independent_command["timeout_seconds"] == 1800
    assert author_command["elapsed_milliseconds"] == 8295
    author_elapsed_ms = round((instant(author_command["ended_at_utc"]) - instant(author_command["started_at_utc"])).total_seconds() * 1000)
    independent_elapsed_ms = round((instant(independent_command["ended_at_utc"]) - instant(independent_command["started_at_utc"])).total_seconds() * 1000)
    assert author_elapsed_ms == author_command["elapsed_milliseconds"]
    assert 0 < author_elapsed_ms < 1_800_000 and 0 < independent_elapsed_ms < 1_800_000
    assert (AUTHOR / "logs/canonical-01/stderr.txt").stat().st_size == 0
    assert (INDEPENDENT / "logs/attempt-run-01.stderr.bin").stat().st_size == 0
    assert input_freeze["status"] == "frozen_before_any_study_graph_evaluation"
    assert all(value is False for value in input_freeze["blinding"].values())
    assert output_seal["status"] == "sealed_before_any_author_result_or_verdict_access"
    assert all(value is False for value in output_seal["blinding"].values())
    author_release = json.loads((INDEPENDENT / "author-manifest-verification.json").read_text(encoding="utf-8"))
    assert author_release["manifest_match"] is True and author_release["all_artifacts_match"] is True
    assert author_release["artifact_count"] == 31
    author_input_freeze = json.loads((AUTHOR / "input-freeze.json").read_text(encoding="utf-8"))
    assert instant(author_input_freeze["frozen_at_utc"]) < instant(author_command["started_at_utc"])
    assert instant(input_freeze["frozen_at_utc"]) < instant(independent_command["started_at_utc"])
    assert instant(independent_command["started_at_utc"]) < instant(independent_command["ended_at_utc"])
    assert instant(independent_command["ended_at_utc"]) < instant(output_seal["sealed_at_utc"])
    assert instant(output_seal["sealed_at_utc"]) < instant(author_release["verified_at_utc"])
    author_attempts = read_jsonl(AUTHOR / "logs/attempts.jsonl")
    independent_attempts = read_jsonl(INDEPENDENT / "logs/attempts.jsonl")
    comparison_attempts = read_jsonl(INDEPENDENT / "comparison-logs/attempts.jsonl")
    assert all(record["return_code"] == 0 and record["timeout"] is False for record in author_attempts)
    assert len(independent_attempts) == 1 and independent_attempts[0]["returncode"] == 0 and independent_attempts[0]["timed_out"] is False
    assert len(comparison_attempts) == 1 and comparison_attempts[0]["returncode"] == 0 and comparison_attempts[0]["timed_out"] is False

    author_summary = json.loads((AUTHOR / "run-01/summary.json").read_text(encoding="utf-8"))
    independent_summary = json.loads((INDEPENDENT / "run-01/summary.json").read_text(encoding="utf-8"))
    assert author_summary["candidate_minimum_order"] == 6
    assert author_summary["lower_order_witness_counts"] == {"2": 0, "3": 0, "4": 0, "5": 0}
    assert independent_summary["minimum_order_result"]["candidate_minimum_order"] == 6
    assert independent_summary["minimum_order_result"]["all_orders_2_through_6_completed"] is True
    assert independent_summary["totals"]["witness_count"] == 1
    assert independent_summary["totals"]["candidate_pair_count"] == 2390
    assert independent_summary["totals"]["graph_state_value_count_including_p7_states"] == 1848
    assert independent_summary["candidate_key_digest"]["sha256"] == expected_pair_key_digest.hexdigest()

    for actual, author_record in zip(coverage_orders, author_summary["input_completeness"], strict=True):
        assert author_record["n"] == actual["n"]
        assert author_record["representative_count"] == actual["representative_count"]
        assert author_record["orbit_union_count"] == actual["orbit_union_count"]
        assert author_record["connected_labelled_count"] == actual["connected_labelled_count"]
        assert author_record["orbit_union_sha256"] == actual["set_sha256"]
        assert author_record["connected_labelled_set_sha256"] == actual["set_sha256"]
        assert author_record["sets_equal"] is True
        assert author_record["orbits_pairwise_disjoint"] is True
        for observed_rep, expected_rep in zip(author_record["orbits"], actual["representatives"], strict=True):
            assert observed_rep["source_line"] == expected_rep["source_line"]
            assert observed_rep["graph6"] == expected_rep["graph6"]
            assert observed_rep["orbit_size"] == expected_rep["orbit_size"]

    author_per_graph = {(row["n"], row["source_line"]): row for row in author_summary["census"]["per_graph"]}
    assert len(author_per_graph) == 142
    for coverage in coverage_orders:
        n = coverage["n"]
        for expected_rep in coverage["representatives"]:
            row = author_per_graph[(n, expected_rep["source_line"])]
            assert row["source_file"] == EXPECTED[n][0]
            assert row["source_graph6"] == expected_rep["graph6"]
            assert row["nonedge_count"] == expected_rep["nonedge_count"]
            assert row["expected_pair_count"] == expected_rep["pair_count"]
            assert row["evaluated_pair_count"] == expected_rep["pair_count"]
            assert row["pair_count"] == expected_rep["pair_count"]

    author_order_summary = {row["n"]: row for row in author_summary["census"]["per_order"]}
    independent_order_summary = {row["n"]: row for row in independent_summary["orders"]}
    for n in range(2, 7):
        rows = [row for row in author_pairs if row["key"][0] == n]
        signs = Counter("|".join(sign(row["deltas"][name]) for name in ("e", "f", "both")) for row in rows)
        e_signs = Counter(sign(row["deltas"]["e"]) for row in rows)
        f_signs = Counter(sign(row["deltas"]["f"]) for row in rows)
        both_signs = Counter(sign(row["deltas"]["both"]) for row in rows)
        e_equal = sum(row["deltas"]["e"] == 0 for row in rows)
        f_equal = sum(row["deltas"]["f"] == 0 for row in rows)
        both_equal = sum(row["deltas"]["both"] == 0 for row in rows)
        any_single_equal = sum(row["deltas"]["e"] == 0 or row["deltas"]["f"] == 0 for row in rows)
        witnesses_n = sum(row["qualifies"] for row in rows)
        author_order = author_order_summary[n]
        independent_order = independent_order_summary[n]
        assert author_order["pair_count"] == independent_order["candidate_pair_count"] == len(rows)
        assert author_order["witness_count"] == independent_order["witness_count"] == witnesses_n
        assert author_order["single_equality_occurrences"] == independent_order["delta_e_equality_count"] == e_equal
        assert author_order["single_f_equality_occurrences"] == independent_order["delta_f_equality_count"] == f_equal
        assert author_order["joint_equality_occurrences"] == independent_order["delta_both_equality_count"] == both_equal
        assert author_order["pairs_with_any_single_equality"] == any_single_equal
        assert {key: value for key, value in author_order["sign_triples"].items() if value} == dict(signs)
        assert independent_order["sign_pattern_counts"] == dict(signs)
        assert independent_order["delta_e_sign_counts"] == dict(e_signs)
        assert independent_order["delta_f_sign_counts"] == dict(f_signs)
        assert independent_order["delta_both_sign_counts"] == dict(both_signs)
        assert author_order["zero_pair_graph_count"] == independent_order["zero_pair_source_row_count"] == coverage_orders[n - 2]["zero_pair_source_row_count"]

    comparison = json.loads((INDEPENDENT / "comparison-01/comparison.json").read_text(encoding="utf-8"))
    assert comparison["status"] == "pass_exact_cross_evaluator_agreement_pending_final_independent_review"
    assert comparison["result"] == {
        "all_checks_pass": True,
        "candidate_minimum_order": 6,
        "graph_state_count_including_p7": 1848,
        "pair_count": 2390,
        "qualifying_witness_count_through_order_6": 1,
    }
    assert all(check["status"] == "pass" for check in comparison["checks"])
    for field in (
        "aggregate_comparison",
        "completeness_comparison",
        "completeness_internal_checks",
        "graph_method_self_checks",
        "graph_state_comparison",
        "pair_comparison",
        "per_graph_comparison",
        "per_order_comparison",
        "published_p7_comparison",
        "witness_comparison",
    ):
        assert comparison[field]["pass"] is True
    assert comparison_seal["result"]["all_checks_pass"] is True
    assert comparison_seal["result"]["candidate_minimum_order"] == 6
    assert comparison_seal["result"]["pair_count"] == 2390

    explanation = json.loads(explanation_path.read_text(encoding="utf-8"))
    assert explanation["status"] == "candidate_pending_final_audit"
    assert explanation["candidate"]["identity"] == {
        "n": 6,
        "pair_index_global": 504,
        "source_file": "graph6c.g6",
        "source_graph6": "E?zW",
        "source_line": 10,
    }
    assert private_edges(explanation["candidate"]["base_graph"]["edges"]) == witness["states"]["base"]
    assert tuple(private_edges([explanation["candidate"]["added_edges"][name]])[0] for name in ("e", "f")) == (witness["key"][4], witness["key"][5])
    assert {
        "base": rat(explanation["candidate"]["exact_values"]["kemeny"]["base"]),
        "e": rat(explanation["candidate"]["exact_values"]["kemeny"]["single_e"]),
        "f": rat(explanation["candidate"]["exact_values"]["kemeny"]["single_f"]),
        "both": rat(explanation["candidate"]["exact_values"]["kemeny"]["joint"]),
    } == expected_candidate_k
    assert {
        "e": rat(explanation["candidate"]["exact_values"]["deltas"]["single_e_minus_base"]),
        "f": rat(explanation["candidate"]["exact_values"]["deltas"]["single_f_minus_base"]),
        "both": rat(explanation["candidate"]["exact_values"]["deltas"]["joint_minus_base"]),
    } == witness["deltas"]
    assert explanation["strictness_boundary"]["candidate_under_frozen_predicate"] is True
    assert explanation["strictness_boundary"]["candidate_under_alternative_predicate"] is False
    assert explanation["finite_census_minimum_logic"]["candidate_minimum_order"] == 6
    assert explanation["finite_census_minimum_logic"]["total_unordered_nonedge_pairs"] == 2390
    assert explanation["finite_census_minimum_logic"]["total_witnesses_through_order_6"] == 1
    assert any("novelty" in item.lower() and "unresolved" in item.lower() for item in explanation["limitations"])

    report = {
        "schema_version": "kemeny-final-raw-audit-check-v1",
        "auditor": "/root/sol_symmetry_audit",
        "scope": "Hash and semantic comparison of two sealed runs; independent labelled-coverage recomputation; exact small-case certificates only. The full Kemeny census was not rerun.",
        "status": "pass",
        "integrity": integrity,
        "coverage": {
            "status": "pass_independently_recomputed",
            "orders": coverage_orders,
            "totals": {
                "representatives": sum(item["representative_count"] for item in coverage_orders),
                "connected_labelled_graphs": sum(item["connected_labelled_count"] for item in coverage_orders),
                "candidate_pairs": len(expected_pair_keys),
                "zero_pair_source_rows": sum(item["zero_pair_source_row_count"] for item in coverage_orders),
            },
        },
        "sealed_output_comparison": {
            "status": "pass",
            "author_state_count": len(author_values),
            "independent_state_count": len(independent_values),
            "state_key_set_equal": True,
            "exact_kemeny_mismatches": len(graph_value_mismatches),
            "state_counts_by_order": {str(n): state_counts_by_order[n] for n in range(2, 8)},
            "state_tables_equal_exact_required_state_union": True,
            "author_pair_count": len(author_pairs),
            "independent_pair_count": len(independent_pairs),
            "expected_pair_count": len(expected_pair_keys),
            "pair_order_and_full_expected_key_sequence_equal": True,
            "expected_pair_key_sha256": expected_pair_key_digest.hexdigest(),
            "semantic_pair_mismatches": len(semantic_pair_mismatches),
            "all_recorded_deltas_signs_equalities_and_predicates_rederived": True,
            "all_author_and_independent_aggregate_summaries_rederived": True,
            "pair_counts_by_order": {str(n): order_counts[n] for n in range(2, 7)},
            "witness_counts_by_order": {str(n): witness_counts[n] for n in range(2, 7)},
            "equality_occurrences": equality_occurrences,
            "minimum_order": minimum_order,
        },
        "candidate_witness": {
            "status": "pass",
            "source_file": witness["key"][1],
            "source_line": witness["key"][2],
            "graph6": witness["key"][3],
            "base_edges": [list(edge) for edge in public_edges(witness["states"]["base"])],
            "added_edges": [list(edge) for edge in public_edges((witness["key"][4], witness["key"][5]))],
            "kemeny": {name: fraction_record(value) for name, value in expected_candidate_k.items()},
            "deltas": {name: fraction_record(value) for name, value in witness["deltas"].items()},
            "predicate": "delta_e<=0 and delta_f<=0 and delta_both>0",
            "singleton_equality_present": True,
            "third_exact_formula_records": candidate_direct,
        },
        "published_p7_control": {
            "status": "pass",
            "base_edges": [list(edge) for edge in public_edges(p7_base)],
            "added_edges": [list(edge) for edge in public_edges((p7_e, p7_f))],
            "kemeny": {name: fraction_record(value) for name, value in p7_expected_k.items()},
            "deltas": {name: fraction_record(value) for name, value in p7_expected_deltas.items()},
            "third_exact_formula_records": p7_direct,
        },
        "periodic_handling": {
            "status": "pass",
            "reason": "The connected periodic K2 state is retained and both sealed methods plus the third exact fundamental-matrix calculation return K=1/2; no aperiodicity assumption is imposed.",
            "record": periodic_direct,
        },
        "execution_and_independence": {
            "author": {
                "started_at_utc": author_command["started_at_utc"],
                "ended_at_utc": author_command["ended_at_utc"],
                "elapsed_milliseconds": author_command["elapsed_milliseconds"],
                "return_code": author_command["return_code"],
                "timeout": author_command["timeout"],
            },
            "independent": {
                "input_frozen_at_utc": input_freeze["frozen_at_utc"],
                "started_at_utc": independent_command["started_at_utc"],
                "ended_at_utc": independent_command["ended_at_utc"],
                "elapsed_milliseconds": independent_elapsed_ms,
                "output_sealed_at_utc": output_seal["sealed_at_utc"],
                "author_manifest_verified_at_utc": author_release["verified_at_utc"],
                "return_code": independent_command["returncode"],
                "timeout": independent_command["timed_out"],
                "recorded_blinding_declarations_pass": True,
            },
            "failed_canonical_attempts": 0,
            "limitation": "The hashes and timestamps establish freeze/run/release ordering and the records declare no author access before the independent seal; filesystem chronology alone cannot prove a negative access claim.",
        },
        "independent_cross_comparison": {
            "status": "pass",
            "comparison_sha256": integrity["independent_comparison_artifacts"][3]["sha256"],
            "comparison_seal_sha256": integrity["independent_comparison_seal"]["sha256"],
            "note": "The other independent review agrees with this audit on all 1848 states, 2390 pairs, 142 representative rows, completeness records, the P7 control, and the candidate minimum.",
        },
        "author_explanation_alignment": {
            "status": "pass",
            "sha256": integrity["author_witness_explanation"]["sha256"],
            "note": "The explanation preserves the exact graph, pair, rational values, equality boundary, finite-census evidence, and unresolved-novelty limitation. It remains explicitly marked pending final audit.",
        },
        "limitations": [
            "This verifies a finite exhaustive computation for the frozen connected simple undirected unweighted graph class through order 6; it is not a proof about unrestricted graph classes.",
            "The third exact evaluator was applied only to the selected order-6 witness, the published P7 control, and periodic K2; agreement over all 1848 states comes from the two sealed independent implementations.",
            "Novelty, openness, prevalence, empirical impact, and algorithmic novelty are unestablished and outside this check.",
        ],
    }
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8", newline="\n")
    print(json.dumps({"status": "pass", "output": str(OUTPUT), "sha256": sha256(OUTPUT)}, sort_keys=True))


if __name__ == "__main__":
    main()
