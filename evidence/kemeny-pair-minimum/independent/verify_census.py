from __future__ import annotations

import argparse
from collections import Counter
from dataclasses import dataclass
from fractions import Fraction
import hashlib
from itertools import combinations, permutations
import json
from math import comb, factorial
from pathlib import Path
import sys
from typing import Iterable, Sequence


EXPECTED_MANIFEST_SHA256 = (
    "e4a02bdeb62d8e6b0e68849b4aa3d65d9a37744578bebd48abe740fe94c52c7f"
)
EXPECTED_INPUTS = {
    2: {
        "path": "graph2c.g6",
        "bytes": 3,
        "sha256": "fae4bfc454bd04363dcd5222772f2973b1193e1ff6f676e822a427323a677ef9",
        "representatives": 1,
        "connected_labelled": 1,
    },
    3: {
        "path": "graph3c.g6",
        "bytes": 6,
        "sha256": "5966edf890849db6cb03626431916231a81a30c9db9a4781a4a8f2e5dc7e6129",
        "representatives": 2,
        "connected_labelled": 4,
    },
    4: {
        "path": "graph4c.g6",
        "bytes": 18,
        "sha256": "d7da485669f2dc74b81c02f18774a07430937684896833d59f138b10debb5005",
        "representatives": 6,
        "connected_labelled": 38,
    },
    5: {
        "path": "graph5c.g6",
        "bytes": 84,
        "sha256": "3c436a6a15f554e3eff3ce9178fddd3d75db6d365b3c6b102b64afe82145050b",
        "representatives": 21,
        "connected_labelled": 728,
    },
    6: {
        "path": "graph6c.g6",
        "bytes": 560,
        "sha256": "2dc8cbb1c05a12b5dcb28b6227cee86d585f203347f6aebb8fcbdb2b9bdf5fd7",
        "representatives": 112,
        "connected_labelled": 26704,
    },
}


class VerificationError(RuntimeError):
    pass


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def json_bytes(value: object, *, pretty: bool) -> bytes:
    if pretty:
        text = json.dumps(value, ensure_ascii=True, sort_keys=True, indent=2)
    else:
        text = json.dumps(
            value, ensure_ascii=True, sort_keys=True, separators=(",", ":")
        )
    return (text + "\n").encode("utf-8")


def write_json(path: Path, value: object) -> None:
    path.write_bytes(json_bytes(value, pretty=True))


def write_jsonl(path: Path, records: Iterable[object]) -> None:
    with path.open("wb") as stream:
        for record in records:
            stream.write(json_bytes(record, pretty=False))


def rational(value: Fraction) -> dict[str, int]:
    if value.denominator <= 0:
        raise VerificationError("Fraction denominator is not positive")
    return {"numerator": value.numerator, "denominator": value.denominator}


def sign_name(value: Fraction) -> str:
    if value < 0:
        return "negative"
    if value > 0:
        return "positive"
    return "zero"


def lex_edges(n: int) -> tuple[tuple[int, int], ...]:
    return tuple((u, v) for u in range(n) for v in range(u + 1, n))


def graph6_edges(n: int) -> tuple[tuple[int, int], ...]:
    return tuple((u, v) for v in range(1, n) for u in range(v))


def edge_index(n: int) -> dict[tuple[int, int], int]:
    return {edge: index for index, edge in enumerate(lex_edges(n))}


@dataclass(frozen=True)
class GraphState:
    n: int
    mask: int

    def __post_init__(self) -> None:
        if self.n < 0:
            raise VerificationError("negative graph order")
        edge_slots = comb(self.n, 2)
        if self.mask < 0 or self.mask >= (1 << edge_slots):
            raise VerificationError("graph mask outside the simple-graph range")

    def edges(self) -> tuple[tuple[int, int], ...]:
        return tuple(
            edge
            for index, edge in enumerate(lex_edges(self.n))
            if self.mask & (1 << index)
        )

    def missing_edges(self) -> tuple[tuple[int, int], ...]:
        return tuple(
            edge
            for index, edge in enumerate(lex_edges(self.n))
            if not self.mask & (1 << index)
        )

    def add_edge(self, edge: tuple[int, int]) -> GraphState:
        u, v = edge
        if not (0 <= u < v < self.n):
            raise VerificationError(f"invalid normalized edge: {edge}")
        bit = 1 << edge_index(self.n)[edge]
        if self.mask & bit:
            raise VerificationError(f"edge already present: {edge}")
        return GraphState(self.n, self.mask | bit)

    def add_two_edges(
        self, first: tuple[int, int], second: tuple[int, int]
    ) -> GraphState:
        if first == second:
            raise VerificationError("the two added edges must be distinct")
        return self.add_edge(first).add_edge(second)


@dataclass(frozen=True)
class SourceGraph:
    n: int
    source_file: str
    source_line: int
    graph6: str
    state: GraphState


@dataclass(frozen=True)
class KemenyResult:
    value: Fraction
    coefficients_descending: tuple[Fraction, ...]
    q_constant: Fraction
    q_linear: Fraction
    degrees: tuple[int, ...]
    edge_count: int


def public_edge(edge: tuple[int, int]) -> list[int]:
    return [edge[0] + 1, edge[1] + 1]


def public_edges(edges: Iterable[tuple[int, int]]) -> list[list[int]]:
    return [public_edge(edge) for edge in sorted(edges)]


def graph_record(state: GraphState) -> dict[str, object]:
    return {"n": state.n, "edges": public_edges(state.edges())}


def state_id(state: GraphState) -> str:
    suffix = ",".join(f"{u + 1}-{v + 1}" for u, v in state.edges())
    return f"n={state.n};edges={suffix}"


def decode_graph6(line: bytes, expected_n: int) -> GraphState:
    if not line:
        raise VerificationError("empty graph6 record")
    if line.startswith(b">>graph6<<"):
        raise VerificationError("per-record graph6 header is not allowed in frozen files")
    if any(byte < 63 or byte > 126 for byte in line):
        raise VerificationError("graph6 record contains a byte outside 63..126")
    n = line[0] - 63
    if n > 62:
        raise VerificationError("extended graph6 order encoding is outside this contract")
    if n != expected_n:
        raise VerificationError(f"graph6 order {n} does not match expected {expected_n}")
    required_bits = comb(n, 2)
    required_payload = (required_bits + 5) // 6
    if len(line) != 1 + required_payload:
        raise VerificationError(
            f"graph6 record has {len(line) - 1} payload bytes; expected {required_payload}"
        )
    bits: list[int] = []
    for byte in line[1:]:
        value = byte - 63
        bits.extend((value >> shift) & 1 for shift in range(5, -1, -1))
    if any(bits[required_bits:]):
        raise VerificationError("nonzero graph6 padding bit")
    lookup = edge_index(n)
    mask = 0
    for bit, edge in zip(bits[:required_bits], graph6_edges(n), strict=True):
        if bit:
            mask |= 1 << lookup[edge]
    return GraphState(n, mask)


def adjacency_masks(state: GraphState) -> list[int]:
    adjacency = [0] * state.n
    for u, v in state.edges():
        adjacency[u] |= 1 << v
        adjacency[v] |= 1 << u
    return adjacency


def is_connected(state: GraphState) -> bool:
    if state.n == 0:
        return False
    adjacency = adjacency_masks(state)
    seen = 1
    frontier = 1
    while frontier:
        vertex_bit = frontier & -frontier
        frontier ^= vertex_bit
        vertex = vertex_bit.bit_length() - 1
        new_bits = adjacency[vertex] & ~seen
        seen |= new_bits
        frontier |= new_bits
    return seen == (1 << state.n) - 1


def degrees(state: GraphState) -> tuple[int, ...]:
    values = [0] * state.n
    for u, v in state.edges():
        values[u] += 1
        values[v] += 1
    return tuple(values)


def identity_matrix(n: int) -> list[list[Fraction]]:
    return [
        [Fraction(int(row == column)) for column in range(n)] for row in range(n)
    ]


def matrix_product(
    left: Sequence[Sequence[Fraction]], right: Sequence[Sequence[Fraction]]
) -> list[list[Fraction]]:
    n = len(left)
    if n == 0 or len(right) != n:
        raise VerificationError("matrix product requires equal nonzero square orders")
    output = [[Fraction(0) for _ in range(n)] for _ in range(n)]
    for row in range(n):
        for inner in range(n):
            coefficient = left[row][inner]
            if coefficient == 0:
                continue
            for column in range(n):
                other = right[inner][column]
                if other:
                    output[row][column] += coefficient * other
    return output


def random_walk_laplacian(state: GraphState) -> tuple[list[list[Fraction]], tuple[int, ...]]:
    degree = degrees(state)
    if any(value == 0 for value in degree):
        raise VerificationError("connected graph state unexpectedly has an isolate")
    matrix = identity_matrix(state.n)
    for u, v in state.edges():
        matrix[u][v] -= Fraction(1, degree[u])
        matrix[v][u] -= Fraction(1, degree[v])
    if any(sum(row, Fraction(0)) != 0 for row in matrix):
        raise VerificationError("I-P row-sum invariant failed")
    return matrix, degree


def characteristic_coefficients(
    matrix: Sequence[Sequence[Fraction]],
) -> tuple[Fraction, ...]:
    n = len(matrix)
    if n == 0 or any(len(row) != n for row in matrix):
        raise VerificationError("characteristic polynomial requires a square matrix")
    previous = identity_matrix(n)
    coefficients = [Fraction(1)]
    for k in range(1, n + 1):
        product = matrix_product(matrix, previous)
        coefficient = -sum(
            (product[index][index] for index in range(n)), Fraction(0)
        ) / k
        coefficients.append(coefficient)
        for index in range(n):
            product[index][index] += coefficient
        previous = product
    return tuple(coefficients)


def compute_kemeny(state: GraphState) -> KemenyResult:
    if state.n < 2 or not is_connected(state):
        raise VerificationError("Kemeny evaluator requires a connected graph of order >=2")
    matrix, degree = random_walk_laplacian(state)
    coefficients = characteristic_coefficients(matrix)
    if coefficients[-1] != 0:
        raise VerificationError("det(xI-(I-P)) has nonzero constant coefficient")
    q_constant = coefficients[-2]
    if q_constant == 0:
        raise VerificationError("zero eigenvalue is not simple: q(0)=0")
    q_linear = coefficients[-3]
    value = -q_linear / q_constant
    return KemenyResult(
        value=value,
        coefficients_descending=coefficients,
        q_constant=q_constant,
        q_linear=q_linear,
        degrees=degree,
        edge_count=len(state.edges()),
    )


def verify_input_manifest(input_dir: Path) -> list[dict[str, object]]:
    manifest_path = input_dir / "source-manifest.json"
    if sha256_file(manifest_path) != EXPECTED_MANIFEST_SHA256:
        raise VerificationError("source-manifest SHA-256 mismatch")
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    manifest_by_path = {record["path"]: record for record in manifest["files"]}
    if set(manifest_by_path) != {
        str(expected["path"]) for expected in EXPECTED_INPUTS.values()
    }:
        raise VerificationError("source-manifest file list mismatch")
    verified: list[dict[str, object]] = []
    for n, expected in EXPECTED_INPUTS.items():
        name = str(expected["path"])
        manifest_record = manifest_by_path[name]
        path = input_dir / name
        actual_bytes = path.stat().st_size
        actual_sha = sha256_file(path)
        if actual_bytes != expected["bytes"] or actual_sha != expected["sha256"]:
            raise VerificationError(f"frozen input mismatch: {name}")
        if (
            manifest_record["bytes"] != expected["bytes"]
            or manifest_record["sha256"] != expected["sha256"]
        ):
            raise VerificationError(f"manifest record mismatch: {name}")
        verified.append(
            {
                "n": n,
                "path": name,
                "bytes": actual_bytes,
                "sha256": actual_sha,
            }
        )
    return verified


def load_source_graphs(input_dir: Path) -> dict[int, list[SourceGraph]]:
    result: dict[int, list[SourceGraph]] = {}
    seen_records: set[bytes] = set()
    for n, expected in EXPECTED_INPUTS.items():
        name = str(expected["path"])
        raw_lines = (input_dir / name).read_bytes().splitlines()
        if len(raw_lines) != expected["representatives"]:
            raise VerificationError(f"source representative count mismatch for n={n}")
        records: list[SourceGraph] = []
        for line_number, raw_line in enumerate(raw_lines, start=1):
            if raw_line in seen_records:
                raise VerificationError(f"duplicate graph6 source record at {name}:{line_number}")
            seen_records.add(raw_line)
            state = decode_graph6(raw_line, n)
            if not is_connected(state):
                raise VerificationError(f"disconnected source graph at {name}:{line_number}")
            records.append(
                SourceGraph(
                    n=n,
                    source_file=name,
                    source_line=line_number,
                    graph6=raw_line.decode("ascii"),
                    state=state,
                )
            )
        result[n] = records
    return result


def permute_mask(state: GraphState, permutation: tuple[int, ...]) -> int:
    lookup = edge_index(state.n)
    mask = 0
    for u, v in state.edges():
        image = tuple(sorted((permutation[u], permutation[v])))
        mask |= 1 << lookup[image]
    return mask


def mask_set_digest(values: set[int], edge_slots: int) -> str:
    width = max(1, (edge_slots + 3) // 4)
    digest = hashlib.sha256()
    for value in sorted(values):
        digest.update(f"{value:0{width}x}\n".encode("ascii"))
    return digest.hexdigest()


def representative_key(record: SourceGraph) -> tuple[int, str, int, str]:
    return (record.n, record.source_file, record.source_line, record.graph6)


def establish_completeness(
    source_graphs: dict[int, list[SourceGraph]],
) -> tuple[dict[str, object], dict[tuple[int, str, int, str], int]]:
    per_order: list[dict[str, object]] = []
    expected_pair_counts: dict[tuple[int, str, int, str], int] = {}
    for n in range(2, 7):
        records = source_graphs[n]
        edge_slots = comb(n, 2)
        connected_labelled = {
            mask
            for mask in range(1 << edge_slots)
            if is_connected(GraphState(n, mask))
        }
        expected_labelled = int(EXPECTED_INPUTS[n]["connected_labelled"])
        if len(connected_labelled) != expected_labelled:
            raise VerificationError(f"connected labelled count mismatch for n={n}")

        union: set[int] = set()
        representative_rows: list[dict[str, object]] = []
        for record in records:
            orbit = {
                permute_mask(record.state, permutation)
                for permutation in permutations(range(n))
            }
            overlap = union.intersection(orbit)
            if overlap:
                raise VerificationError(
                    f"representative permutation orbits overlap for n={n}"
                )
            union.update(orbit)
            nonedge_count = len(record.state.missing_edges())
            actual_pair_count = len(
                list(combinations(record.state.missing_edges(), 2))
            )
            expected_pair_count = comb(nonedge_count, 2)
            if actual_pair_count != expected_pair_count:
                raise VerificationError("per-representative pair-count identity failed")
            expected_pair_counts[representative_key(record)] = expected_pair_count
            representative_rows.append(
                {
                    "source_file": record.source_file,
                    "source_line": record.source_line,
                    "graph6": record.graph6,
                    "edges": public_edges(record.state.edges()),
                    "orbit_size": len(orbit),
                    "permutation_count": factorial(n),
                    "automorphism_multiplicity": factorial(n) // len(orbit),
                    "orbit_sha256": mask_set_digest(orbit, edge_slots),
                    "nonedge_count": nonedge_count,
                    "pair_count": actual_pair_count,
                    "expected_choose_nonedge_2": expected_pair_count,
                    "zero_pair_row": actual_pair_count == 0,
                }
            )
        missing = connected_labelled - union
        extra = union - connected_labelled
        if missing or extra or union != connected_labelled:
            raise VerificationError(f"labelled orbit coverage failed for n={n}")
        union_hash = mask_set_digest(union, edge_slots)
        connected_hash = mask_set_digest(connected_labelled, edge_slots)
        if union_hash != connected_hash:
            raise VerificationError(f"equal labelled sets hashed differently for n={n}")
        per_order.append(
            {
                "n": n,
                "source_file": EXPECTED_INPUTS[n]["path"],
                "expected_representative_count": EXPECTED_INPUTS[n][
                    "representatives"
                ],
                "actual_representative_count": len(records),
                "all_source_graphs_connected": True,
                "source_records_unique": True,
                "representative_orbits_pairwise_disjoint": True,
                "all_labelled_simple_graph_count": 1 << edge_slots,
                "expected_connected_labelled_count": expected_labelled,
                "actual_connected_labelled_count": len(connected_labelled),
                "orbit_union_count": len(union),
                "coverage_missing_count": len(missing),
                "coverage_extra_count": len(extra),
                "actual_sets_equal": True,
                "mask_hash_encoding": "lowercase zero-padded hexadecimal masks in lexicographic edge-bit order, numerically sorted, one per ASCII line with terminal newline",
                "connected_labelled_set_sha256": connected_hash,
                "representative_orbit_union_sha256": union_hash,
                "candidate_pair_count": sum(
                    row["pair_count"] for row in representative_rows
                ),
                "zero_pair_source_row_count": sum(
                    bool(row["zero_pair_row"]) for row in representative_rows
                ),
                "representatives": representative_rows,
            }
        )
    return (
        {
            "schema_version": "kemeny-independent-completeness-v1",
            "status": "complete_set_equality_verified",
            "decoder": {
                "format": "graph6 for n<=62",
                "payload_bit_order": "(0,1),(0,2),(1,2),(0,3),(1,3),(2,3),...",
                "internal_mask_edge_order": "lexicographic (u,v), 0<=u<v<n",
            },
            "orders": per_order,
            "totals": {
                "representative_count": sum(len(rows) for rows in source_graphs.values()),
                "connected_labelled_count": sum(
                    int(EXPECTED_INPUTS[n]["connected_labelled"])
                    for n in range(2, 7)
                ),
                "candidate_pair_count": sum(expected_pair_counts.values()),
            },
        },
        expected_pair_counts,
    )


def pair_classification(
    delta_e: Fraction, delta_f: Fraction, delta_both: Fraction
) -> dict[str, object]:
    singleton_e_nonincreasing = delta_e <= 0
    singleton_f_nonincreasing = delta_f <= 0
    joint_strict_increase = delta_both > 0
    return {
        "delta_e_sign": sign_name(delta_e),
        "delta_f_sign": sign_name(delta_f),
        "delta_both_sign": sign_name(delta_both),
        "delta_e_equal": delta_e == 0,
        "delta_f_equal": delta_f == 0,
        "delta_both_equal": delta_both == 0,
        "singleton_e_nonincreasing": singleton_e_nonincreasing,
        "singleton_f_nonincreasing": singleton_f_nonincreasing,
        "joint_strict_increase": joint_strict_increase,
        "qualifies": (
            singleton_e_nonincreasing
            and singleton_f_nonincreasing
            and joint_strict_increase
        ),
    }


def evaluate_pair(
    *,
    record: SourceGraph,
    edge_e: tuple[int, int],
    edge_f: tuple[int, int],
    get_kemeny,
) -> dict[str, object]:
    base = record.state
    plus_e = base.add_edge(edge_e)
    plus_f = base.add_edge(edge_f)
    plus_both = base.add_two_edges(edge_e, edge_f)
    k_base = get_kemeny(base).value
    k_e = get_kemeny(plus_e).value
    k_f = get_kemeny(plus_f).value
    k_both = get_kemeny(plus_both).value
    delta_e = k_e - k_base
    delta_f = k_f - k_base
    delta_both = k_both - k_base
    classification = pair_classification(delta_e, delta_f, delta_both)
    return {
        "record_id": (
            f"n={record.n};source={record.source_file}:{record.source_line};"
            f"graph6={record.graph6};e={edge_e[0] + 1}-{edge_e[1] + 1};"
            f"f={edge_f[0] + 1}-{edge_f[1] + 1}"
        ),
        "n": record.n,
        "source_file": record.source_file,
        "source_line": record.source_line,
        "graph6": record.graph6,
        "base_edges": public_edges(base.edges()),
        "added_edges": [public_edge(edge_e), public_edge(edge_f)],
        "states": {
            "G": graph_record(base),
            "G_plus_e": graph_record(plus_e),
            "G_plus_f": graph_record(plus_f),
            "G_plus_e_plus_f": graph_record(plus_both),
        },
        "kemeny": {
            "G": rational(k_base),
            "G_plus_e": rational(k_e),
            "G_plus_f": rational(k_f),
            "G_plus_e_plus_f": rational(k_both),
        },
        "deltas": {
            "e": rational(delta_e),
            "f": rational(delta_f),
            "both": rational(delta_both),
        },
        "classification": classification,
    }


def evaluate_published_p7(get_kemeny) -> dict[str, object]:
    base_mask = 0
    lookup = edge_index(7)
    path_edges = tuple((vertex, vertex + 1) for vertex in range(6))
    for edge in path_edges:
        base_mask |= 1 << lookup[edge]
    base = GraphState(7, base_mask)
    edge_e = (0, 2)
    edge_f = (4, 6)
    synthetic_source = SourceGraph(
        n=7,
        source_file="published-P7-fixed-control",
        source_line=1,
        graph6="not-applicable-explicit-edge-list",
        state=base,
    )
    pair = evaluate_pair(
        record=synthetic_source,
        edge_e=edge_e,
        edge_f=edge_f,
        get_kemeny=get_kemeny,
    )
    return {
        "schema_version": "kemeny-published-p7-independent-v1",
        "source": {
            "title": "A 1-Separation Formula for the Graph Kemeny Constant and Braess Edges",
            "url": "https://arxiv.org/html/2108.01061v1",
            "locator": "paragraph immediately after Corollary 4.3",
            "known_not_novel": True,
        },
        "fixed_labels": {
            "vertices": list(range(1, 8)),
            "base_edges": public_edges(path_edges),
            "added_edges": [public_edge(edge_e), public_edge(edge_f)],
        },
        "pair": pair,
        "source_inequalities_pass": bool(pair["classification"]["qualifies"]),
        "status": (
            "pass_published_upper_bound_replayed"
            if pair["classification"]["qualifies"]
            else "invalid_source_control_failed"
        ),
    }


def graph_value_table(
    cache: dict[GraphState, KemenyResult],
) -> dict[str, object]:
    rows: list[dict[str, object]] = []
    for state in sorted(cache, key=lambda item: (item.n, item.edges())):
        result = cache[state]
        rows.append(
            {
                "state_id": state_id(state),
                "n": state.n,
                "edges": public_edges(state.edges()),
                "edge_count": result.edge_count,
                "degrees": list(result.degrees),
                "kemeny": rational(result.value),
                "method": {
                    "matrix": "I-D^-1 A",
                    "characteristic_coefficients_descending": [
                        rational(value)
                        for value in result.coefficients_descending
                    ],
                    "p_constant_zero": result.coefficients_descending[-1] == 0,
                    "q_constant": rational(result.q_constant),
                    "q_constant_nonzero": result.q_constant != 0,
                    "q_linear": rational(result.q_linear),
                    "formula": "K=-q_linear/q_constant",
                    "row_sums_zero": True,
                },
            }
        )
    return {
        "schema_version": "kemeny-independent-graph-values-v1",
        "arithmetic": "python_stdlib_fractions.Fraction_only",
        "cache_key": "graph order plus full labelled lexicographic edge mask",
        "state_count": len(rows),
        "states": rows,
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input-dir", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    input_dir = args.input_dir.resolve()
    output_dir = args.output_dir.resolve()
    if output_dir.exists():
        raise VerificationError(f"output directory already exists: {output_dir}")
    output_dir.mkdir(parents=True, exist_ok=False)

    verified_inputs = verify_input_manifest(input_dir)
    cache: dict[GraphState, KemenyResult] = {}

    def get_kemeny(state: GraphState) -> KemenyResult:
        if state not in cache:
            cache[state] = compute_kemeny(state)
        return cache[state]

    p7 = evaluate_published_p7(get_kemeny)
    write_json(output_dir / "published-p7.json", p7)
    if not p7["source_inequalities_pass"]:
        invalid_summary = {
            "schema_version": "kemeny-independent-summary-v1",
            "status": "invalid_published_p7_control_failed",
            "census_started": False,
            "published_p7_path": "published-p7.json",
        }
        write_json(output_dir / "summary.json", invalid_summary)
        print(json.dumps(invalid_summary, sort_keys=True), flush=True)
        return 2

    source_graphs = load_source_graphs(input_dir)
    completeness, expected_pair_counts = establish_completeness(source_graphs)

    pair_records: list[dict[str, object]] = []
    witnesses: list[dict[str, object]] = []
    evaluated_counts: Counter[tuple[int, str, int, str]] = Counter()
    per_order_counters: dict[int, dict[str, object]] = {}
    zero_pair_graphs: list[dict[str, object]] = []
    pair_key_digest = hashlib.sha256()

    for n in range(2, 7):
        per_order_counters[n] = {
            "n": n,
            "source_graph_count": len(source_graphs[n]),
            "candidate_pair_count": 0,
            "witness_count": 0,
            "delta_e_sign_counts": Counter(),
            "delta_f_sign_counts": Counter(),
            "delta_both_sign_counts": Counter(),
            "sign_pattern_counts": Counter(),
            "delta_e_equality_count": 0,
            "delta_f_equality_count": 0,
            "delta_both_equality_count": 0,
            "zero_pair_source_row_count": 0,
        }
        for record in source_graphs[n]:
            # Retain every representative's base value, including source rows with
            # fewer than two nonedges and therefore no marked-pair ledger row.
            get_kemeny(record.state)
            missing = record.state.missing_edges()
            pairs = tuple(combinations(missing, 2))
            key = representative_key(record)
            if len(pairs) != expected_pair_counts[key]:
                raise VerificationError("pair enumeration disagrees with completeness record")
            if not pairs:
                per_order_counters[n]["zero_pair_source_row_count"] += 1
                zero_pair_graphs.append(
                    {
                        "n": n,
                        "source_file": record.source_file,
                        "source_line": record.source_line,
                        "graph6": record.graph6,
                        "edges": public_edges(record.state.edges()),
                        "nonedge_count": len(missing),
                        "pair_count": 0,
                    }
                )
            for edge_e, edge_f in pairs:
                if not edge_e < edge_f:
                    raise VerificationError("added edge pair is not lexicographically sorted")
                pair = evaluate_pair(
                    record=record,
                    edge_e=edge_e,
                    edge_f=edge_f,
                    get_kemeny=get_kemeny,
                )
                pair_records.append(pair)
                evaluated_counts[key] += 1
                counters = per_order_counters[n]
                counters["candidate_pair_count"] += 1
                classification = pair["classification"]
                e_sign = classification["delta_e_sign"]
                f_sign = classification["delta_f_sign"]
                both_sign = classification["delta_both_sign"]
                counters["delta_e_sign_counts"][e_sign] += 1
                counters["delta_f_sign_counts"][f_sign] += 1
                counters["delta_both_sign_counts"][both_sign] += 1
                counters["sign_pattern_counts"][
                    f"{e_sign}|{f_sign}|{both_sign}"
                ] += 1
                counters["delta_e_equality_count"] += int(
                    classification["delta_e_equal"]
                )
                counters["delta_f_equality_count"] += int(
                    classification["delta_f_equal"]
                )
                counters["delta_both_equality_count"] += int(
                    classification["delta_both_equal"]
                )
                if classification["qualifies"]:
                    counters["witness_count"] += 1
                    witnesses.append(pair)
                pair_key = {
                    "n": n,
                    "source_file": record.source_file,
                    "source_line": record.source_line,
                    "graph6": record.graph6,
                    "e": public_edge(edge_e),
                    "f": public_edge(edge_f),
                }
                pair_key_digest.update(json_bytes(pair_key, pretty=False))

    for key, expected_count in expected_pair_counts.items():
        if evaluated_counts[key] != expected_count:
            raise VerificationError(f"evaluated pair-count mismatch for {key}")
    expected_total_pairs = int(completeness["totals"]["candidate_pair_count"])
    if len(pair_records) != expected_total_pairs:
        raise VerificationError("total pair-count mismatch")

    for order in completeness["orders"]:
        n = order["n"]
        for row in order["representatives"]:
            key = (n, row["source_file"], row["source_line"], row["graph6"])
            row["evaluated_pair_count"] = evaluated_counts[key]
            row["evaluated_pair_count_matches"] = (
                evaluated_counts[key] == row["pair_count"]
            )
    completeness["pair_census_count_verified"] = True
    write_json(output_dir / "completeness.json", completeness)

    write_jsonl(output_dir / "pairs.jsonl", pair_records)
    witness_document = {
        "schema_version": "kemeny-independent-witnesses-v1",
        "scope": "connected simple undirected unweighted representatives, all unordered distinct nonedge pairs, n=2..6",
        "witness_count": len(witnesses),
        "witnesses": witnesses,
    }
    write_json(output_dir / "witnesses.json", witness_document)
    values_document = graph_value_table(cache)
    write_json(output_dir / "graph-values.json", values_document)

    order_summaries: list[dict[str, object]] = []
    for n in range(2, 7):
        counters = per_order_counters[n]
        order_summaries.append(
            {
                "n": n,
                "source_graph_count": counters["source_graph_count"],
                "candidate_pair_count": counters["candidate_pair_count"],
                "witness_count": counters["witness_count"],
                "delta_e_sign_counts": dict(counters["delta_e_sign_counts"]),
                "delta_f_sign_counts": dict(counters["delta_f_sign_counts"]),
                "delta_both_sign_counts": dict(counters["delta_both_sign_counts"]),
                "sign_pattern_counts": dict(counters["sign_pattern_counts"]),
                "delta_e_equality_count": counters["delta_e_equality_count"],
                "delta_f_equality_count": counters["delta_f_equality_count"],
                "delta_both_equality_count": counters[
                    "delta_both_equality_count"
                ],
                "zero_pair_source_row_count": counters[
                    "zero_pair_source_row_count"
                ],
                "complete": True,
            }
        )
    witness_orders = sorted({record["n"] for record in witnesses})
    minimum_order = witness_orders[0] if witness_orders else 7
    minimum_basis = (
        "smallest complete census order containing an exact witness"
        if witness_orders
        else "no witness in complete n=2..6 census plus passing fixed published P7 witness"
    )

    pre_summary_paths = [
        "published-p7.json",
        "completeness.json",
        "pairs.jsonl",
        "witnesses.json",
        "graph-values.json",
    ]
    summary = {
        "schema_version": "kemeny-independent-summary-v1",
        "status": "complete_independent_evaluator_result_not_final_gate",
        "definition": {
            "transition_matrix": "P=D^-1 A",
            "kemeny": "sum of reciprocals of nonzero eigenvalues of I-P",
            "qualifying_predicate": "delta_e<=0 and delta_f<=0 and delta_both>0",
            "equality_handling": "singleton equality is non-Braess and retained separately",
        },
        "method": {
            "arithmetic": "python_stdlib_fractions.Fraction_only",
            "formula": "Faddeev-LeVerrier characteristic polynomial of I-P; K=-q_linear/q_constant after one exact factor x",
            "cache_key": "full labelled graph state: n plus lexicographic edge mask",
            "early_stop": False,
        },
        "inputs": {
            "source_manifest_sha256": EXPECTED_MANIFEST_SHA256,
            "verified_files": verified_inputs,
        },
        "published_p7": {
            "status": p7["status"],
            "source_inequalities_pass": p7["source_inequalities_pass"],
            "path": "published-p7.json",
        },
        "orders": order_summaries,
        "totals": {
            "source_graph_count": sum(len(rows) for rows in source_graphs.values()),
            "candidate_pair_count": len(pair_records),
            "witness_count": len(witnesses),
            "graph_state_value_count_including_p7_states": values_document[
                "state_count"
            ],
            "zero_pair_source_row_count": len(zero_pair_graphs),
        },
        "zero_pair_source_rows": zero_pair_graphs,
        "candidate_key_digest": {
            "encoding": "canonical compact sorted-key ASCII JSON object per pair with terminal newline, in required census order",
            "sha256": pair_key_digest.hexdigest(),
        },
        "minimum_order_result": {
            "candidate_minimum_order": minimum_order,
            "basis": minimum_basis,
            "all_orders_2_through_6_completed": True,
            "orders_0_and_1_out_of_scope_and_have_fewer_than_two_nonedges": True,
            "final_semantic_gate_pending": True,
            "global_novelty_not_certified": True,
        },
        "deterministic_pre_summary_output_hashes": {
            name: sha256_file(output_dir / name) for name in pre_summary_paths
        },
    }
    write_json(output_dir / "summary.json", summary)
    print(
        json.dumps(
            {
                "status": summary["status"],
                "candidate_pair_count": len(pair_records),
                "witness_count": len(witnesses),
                "candidate_minimum_order": minimum_order,
                "output_dir": str(output_dir),
                "summary_sha256": sha256_file(output_dir / "summary.json"),
            },
            ensure_ascii=True,
            sort_keys=True,
        ),
        flush=True,
    )
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except VerificationError as error:
        print(f"VERIFICATION_ERROR: {error}", file=sys.stderr, flush=True)
        raise SystemExit(2)
