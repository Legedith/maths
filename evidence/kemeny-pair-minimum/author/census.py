from __future__ import annotations

import argparse
import hashlib
import itertools
import json
import math
import platform
import sys
import traceback
from collections import Counter
from pathlib import Path
from typing import Any, Iterable

import sympy as sp


SCHEMA_VERSION = "kemeny-jointly-braess-author-v1"
EXPECTED_PYTHON = (3, 12, 11)
EXPECTED_SYMPY = "1.14.0"
EXPECTED_SOURCE_MANIFEST_SHA256 = (
    "e4a02bdeb62d8e6b0e68849b4aa3d65d9a37744578bebd48abe740fe94c52c7f"
)
EXPECTED_CONTRACT_SHA256 = (
    "1ff78636c4dcadc7d8f9d6a3a36c144e193e5f90cbb970ab846c877cdf0c6ac6"
)
CONTRACT_PATH = Path(
    "D:/CodexWorkspaces/mathematics-atlas/kemeny-spec-work/contract-v1.md"
)
EXPECTED_INPUTS = {
    2: (
        "graph2c.g6",
        1,
        "fae4bfc454bd04363dcd5222772f2973b1193e1ff6f676e822a427323a677ef9",
        3,
        1,
    ),
    3: (
        "graph3c.g6",
        2,
        "5966edf890849db6cb03626431916231a81a30c9db9a4781a4a8f2e5dc7e6129",
        6,
        4,
    ),
    4: (
        "graph4c.g6",
        6,
        "d7da485669f2dc74b81c02f18774a07430937684896833d59f138b10debb5005",
        18,
        38,
    ),
    5: (
        "graph5c.g6",
        21,
        "3c436a6a15f554e3eff3ce9178fddd3d75db6d365b3c6b102b64afe82145050b",
        84,
        728,
    ),
    6: (
        "graph6c.g6",
        112,
        "2dc8cbb1c05a12b5dcb28b6227cee86d585f203347f6aebb8fcbdb2b9bdf5fd7",
        560,
        26704,
    ),
}


class CensusError(RuntimeError):
    pass


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def canonical_json_bytes(value: Any) -> bytes:
    return (
        json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
        + "\n"
    ).encode("utf-8")


def write_json(path: Path, value: Any) -> None:
    temporary = path.with_name(path.name + ".tmp")
    temporary.write_bytes(canonical_json_bytes(value))
    temporary.replace(path)


def write_jsonl(path: Path, records: Iterable[dict[str, Any]]) -> None:
    temporary = path.with_name(path.name + ".tmp")
    with temporary.open("wb") as stream:
        for record in records:
            stream.write(canonical_json_bytes(record))
    temporary.replace(path)


def rational_object(value: sp.Expr) -> dict[str, int]:
    exact = sp.cancel(value)
    if exact.is_Rational is not True:
        raise CensusError(f"Expected a rational value, got {exact!r}")
    numerator, denominator = exact.as_numer_denom()
    numerator_int = int(numerator)
    denominator_int = int(denominator)
    if denominator_int <= 0:
        raise CensusError("Rational denominator is not positive")
    if math.gcd(abs(numerator_int), denominator_int) != 1:
        raise CensusError("Rational output is not reduced")
    return {"numerator": numerator_int, "denominator": denominator_int}


def sign_name(value: sp.Expr) -> str:
    exact = sp.cancel(value)
    if exact == 0:
        return "zero"
    if exact.is_positive is True:
        return "positive"
    if exact.is_negative is True:
        return "negative"
    raise CensusError(f"Could not decide exact sign of {exact!r}")


def all_edges(n: int) -> tuple[tuple[int, int], ...]:
    return tuple((u, v) for u in range(n) for v in range(u + 1, n))


def edge_index(n: int) -> dict[tuple[int, int], int]:
    return {edge: index for index, edge in enumerate(all_edges(n))}


def edges_from_mask(n: int, mask: int) -> tuple[tuple[int, int], ...]:
    return tuple(
        edge for bit, edge in enumerate(all_edges(n)) if mask & (1 << bit)
    )


def public_edge(edge: tuple[int, int]) -> list[int]:
    return [edge[0] + 1, edge[1] + 1]


def public_edges(n: int, mask: int) -> list[list[int]]:
    return [public_edge(edge) for edge in edges_from_mask(n, mask)]


def state_id(n: int, mask: int) -> str:
    encoded_edges = ",".join(f"{u + 1}-{v + 1}" for u, v in edges_from_mask(n, mask))
    return f"n={n};edges={encoded_edges}"


def mask_from_edges(n: int, edges: Iterable[tuple[int, int]]) -> int:
    indices = edge_index(n)
    mask = 0
    for raw_u, raw_v in edges:
        if raw_u == raw_v:
            raise CensusError("Loop in a simple graph")
        u, v = sorted((raw_u, raw_v))
        if (u, v) not in indices:
            raise CensusError(f"Edge {(raw_u, raw_v)!r} outside graph order {n}")
        bit = 1 << indices[(u, v)]
        if mask & bit:
            raise CensusError(f"Duplicate edge {(u, v)!r}")
        mask |= bit
    return mask


def add_edge(n: int, mask: int, edge: tuple[int, int]) -> int:
    u, v = edge
    if not (0 <= u < v < n):
        raise CensusError(f"Invalid normalized edge {edge!r} for n={n}")
    bit = 1 << edge_index(n)[edge]
    if mask & bit:
        raise CensusError(f"Attempt to add existing edge {edge!r}")
    return mask | bit


def is_connected(n: int, mask: int) -> bool:
    if n == 0:
        return False
    adjacency = [[] for _ in range(n)]
    for u, v in edges_from_mask(n, mask):
        adjacency[u].append(v)
        adjacency[v].append(u)
    seen = {0}
    stack = [0]
    while stack:
        vertex = stack.pop()
        for neighbor in adjacency[vertex]:
            if neighbor not in seen:
                seen.add(neighbor)
                stack.append(neighbor)
    return len(seen) == n


def decode_graph6(record: str, expected_n: int) -> int:
    if not record or record != record.strip():
        raise CensusError("Empty graph6 record or surrounding whitespace")
    codes = [ord(character) for character in record]
    if any(code < 63 or code > 126 for code in codes):
        raise CensusError("graph6 contains a character outside ASCII 63..126")
    if codes[0] == 126:
        raise CensusError("Extended graph6 order encoding is outside the frozen domain")
    n = codes[0] - 63
    if n != expected_n:
        raise CensusError(f"graph6 order {n} does not match expected order {expected_n}")
    needed = n * (n - 1) // 2
    expected_payload_characters = (needed + 5) // 6
    if len(codes) != 1 + expected_payload_characters:
        raise CensusError(
            f"graph6 payload length {len(codes) - 1} does not match "
            f"expected {expected_payload_characters}"
        )
    bits: list[int] = []
    for code in codes[1:]:
        value = code - 63
        bits.extend((value >> shift) & 1 for shift in range(5, -1, -1))
    if any(bits[needed:]):
        raise CensusError("graph6 has nonzero padding bits")
    graph6_edges: list[tuple[int, int]] = []
    cursor = 0
    for v in range(1, n):
        for u in range(v):
            if bits[cursor]:
                graph6_edges.append((u, v))
            cursor += 1
    return mask_from_edges(n, graph6_edges)


def encode_graph6(n: int, mask: int) -> str:
    if not 0 <= n <= 62:
        raise CensusError("Only one-byte graph6 orders are supported")
    present = set(edges_from_mask(n, mask))
    bits: list[int] = []
    for v in range(1, n):
        for u in range(v):
            bits.append(1 if (u, v) in present else 0)
    while len(bits) % 6:
        bits.append(0)
    payload: list[str] = []
    for start in range(0, len(bits), 6):
        value = 0
        for bit in bits[start : start + 6]:
            value = (value << 1) | bit
        payload.append(chr(value + 63))
    return chr(n + 63) + "".join(payload)


def permute_mask(n: int, mask: int, permutation: tuple[int, ...]) -> int:
    transformed = []
    for u, v in edges_from_mask(n, mask):
        transformed.append(tuple(sorted((permutation[u], permutation[v]))))
    return mask_from_edges(n, transformed)


def mask_set_digest(n: int, masks: Iterable[int]) -> str:
    width = max(1, (len(all_edges(n)) + 3) // 4)
    payload = "".join(f"{mask:0{width}x}\n" for mask in sorted(masks)).encode(
        "ascii"
    )
    return sha256_bytes(payload)


def read_and_verify_inputs(input_dir: Path) -> dict[int, list[dict[str, Any]]]:
    manifest_path = input_dir / "source-manifest.json"
    if sha256_file(manifest_path) != EXPECTED_SOURCE_MANIFEST_SHA256:
        raise CensusError("Source manifest hash mismatch")
    if sha256_file(CONTRACT_PATH) != EXPECTED_CONTRACT_SHA256:
        raise CensusError("Frozen contract hash mismatch")
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    manifest_entries = {entry["path"]: entry for entry in manifest.get("files", [])}
    if set(manifest_entries) != {
        details[0] for details in EXPECTED_INPUTS.values()
    }:
        raise CensusError("Source manifest file membership mismatch")

    records_by_order: dict[int, list[dict[str, Any]]] = {}
    for n, (filename, advertised_count, expected_hash, expected_bytes, _) in sorted(
        EXPECTED_INPUTS.items()
    ):
        path = input_dir / filename
        raw = path.read_bytes()
        actual_hash = sha256_bytes(raw)
        if actual_hash != expected_hash or len(raw) != expected_bytes:
            raise CensusError(f"Frozen input mismatch for {filename}")
        manifest_entry = manifest_entries[filename]
        if (
            manifest_entry.get("sha256") != expected_hash
            or manifest_entry.get("bytes") != expected_bytes
        ):
            raise CensusError(f"Manifest metadata mismatch for {filename}")
        try:
            text = raw.decode("ascii")
        except UnicodeDecodeError as error:
            raise CensusError(f"Non-ASCII graph6 input {filename}") from error
        lines = text.splitlines()
        if len(lines) != advertised_count:
            raise CensusError(
                f"{filename} has {len(lines)} records, expected {advertised_count}"
            )
        if len(set(lines)) != len(lines):
            raise CensusError(f"Duplicate graph6 source record in {filename}")
        parsed: list[dict[str, Any]] = []
        labelled_masks: set[int] = set()
        for source_line, graph6 in enumerate(lines, start=1):
            mask = decode_graph6(graph6, n)
            if mask in labelled_masks:
                raise CensusError(f"Duplicate labelled graph in {filename}")
            labelled_masks.add(mask)
            if not is_connected(n, mask):
                raise CensusError(f"Disconnected source graph {filename}:{source_line}")
            if encode_graph6(n, mask) != graph6:
                raise CensusError(f"graph6 round-trip mismatch at {filename}:{source_line}")
            parsed.append(
                {
                    "n": n,
                    "source_file": filename,
                    "source_line": source_line,
                    "graph6": graph6,
                    "mask": mask,
                }
            )
        records_by_order[n] = parsed
    return records_by_order


def establish_labelled_completeness(
    records_by_order: dict[int, list[dict[str, Any]]]
) -> list[dict[str, Any]]:
    results: list[dict[str, Any]] = []
    for n, records in sorted(records_by_order.items()):
        permutations = tuple(itertools.permutations(range(n)))
        orbit_union: set[int] = set()
        orbit_records: list[dict[str, Any]] = []
        for record in records:
            orbit = {
                permute_mask(n, record["mask"], permutation)
                for permutation in permutations
            }
            overlap = orbit_union.intersection(orbit)
            if overlap:
                raise CensusError(
                    f"Representative orbits overlap at n={n}, line={record['source_line']}"
                )
            orbit_union.update(orbit)
            orbit_records.append(
                {
                    "source_line": record["source_line"],
                    "graph6": record["graph6"],
                    "orbit_size": len(orbit),
                }
            )

        labelled_connected = {
            mask
            for mask in range(1 << len(all_edges(n)))
            if is_connected(n, mask)
        }
        expected_labelled = EXPECTED_INPUTS[n][4]
        if len(labelled_connected) != expected_labelled:
            raise CensusError(
                f"Derived connected labelled count {len(labelled_connected)} for n={n}, "
                f"expected {expected_labelled}"
            )
        if orbit_union != labelled_connected:
            missing = labelled_connected.difference(orbit_union)
            extra = orbit_union.difference(labelled_connected)
            raise CensusError(
                f"Labelled coverage mismatch for n={n}: missing={len(missing)}, "
                f"extra={len(extra)}"
            )
        orbit_digest = mask_set_digest(n, orbit_union)
        labelled_digest = mask_set_digest(n, labelled_connected)
        if orbit_digest != labelled_digest:
            raise CensusError(f"Set digest mismatch despite equality for n={n}")
        results.append(
            {
                "n": n,
                "representative_count": len(records),
                "expected_representative_count": EXPECTED_INPUTS[n][1],
                "permutation_count": len(permutations),
                "orbit_union_count": len(orbit_union),
                "connected_labelled_count": len(labelled_connected),
                "expected_connected_labelled_count": expected_labelled,
                "orbit_union_sha256": orbit_digest,
                "connected_labelled_set_sha256": labelled_digest,
                "sets_equal": True,
                "orbits_pairwise_disjoint": True,
                "orbits": orbit_records,
            }
        )
    return results


class StateEvaluator:
    def __init__(self) -> None:
        self._cache: dict[tuple[int, int], tuple[sp.Rational, dict[str, Any]]] = {}
        self.cache_hits = 0
        self.cache_misses = 0

    def evaluate(self, n: int, mask: int) -> tuple[sp.Rational, dict[str, Any]]:
        key = (n, mask)
        cached = self._cache.get(key)
        if cached is not None:
            self.cache_hits += 1
            return cached
        self.cache_misses += 1
        result = self._compute(n, mask)
        self._cache[key] = result
        return result

    def _compute(self, n: int, mask: int) -> tuple[sp.Rational, dict[str, Any]]:
        if n < 2 or not is_connected(n, mask):
            raise CensusError("Kemeny evaluation requires a connected graph of order >=2")
        adjacency_data = [[sp.Integer(0) for _ in range(n)] for _ in range(n)]
        for u, v in edges_from_mask(n, mask):
            adjacency_data[u][v] = sp.Integer(1)
            adjacency_data[v][u] = sp.Integer(1)
        adjacency = sp.Matrix(adjacency_data)
        degrees = [sp.Integer(sum(adjacency_data[row])) for row in range(n)]
        if any(degree <= 0 for degree in degrees):
            raise CensusError("Connected graph unexpectedly has an isolated vertex")
        edge_count = len(edges_from_mask(n, mask))
        if sum(degrees) != 2 * edge_count:
            raise CensusError("Degree sum does not equal twice the edge count")

        transition = sp.Matrix(
            n,
            n,
            lambda row, column: sp.Rational(
                adjacency_data[row][column], degrees[row]
            ),
        )
        if any(sum(transition[row, column] for column in range(n)) != 1 for row in range(n)):
            raise CensusError("Recomputed transition matrix is not row stochastic")

        laplacian = sp.diag(*degrees) - adjacency
        ground = n - 1
        grounded = laplacian[:ground, :ground]
        determinant = sp.expand(grounded.det())
        if determinant == 0:
            raise CensusError("Grounded Laplacian minor is singular")
        if determinant.is_Integer is not True or determinant <= 0:
            raise CensusError("Grounded Laplacian determinant is not a positive integer")
        inverse = grounded.inv()
        if grounded * inverse != sp.eye(n - 1):
            raise CensusError("Grounded Laplacian inverse failed exact identity check")

        weighted_resistance_sum = sp.Integer(0)
        for i in range(n):
            for j in range(n):
                if i == j:
                    resistance = sp.Integer(0)
                elif i == ground:
                    resistance = inverse[j, j]
                elif j == ground:
                    resistance = inverse[i, i]
                else:
                    resistance = inverse[i, i] + inverse[j, j] - 2 * inverse[i, j]
                resistance = sp.cancel(resistance)
                if resistance.is_Rational is not True or resistance < 0:
                    raise CensusError("Invalid exact effective resistance")
                weighted_resistance_sum += degrees[i] * degrees[j] * resistance
        kemeny = sp.cancel(weighted_resistance_sum / sp.Integer(4 * edge_count))
        if kemeny.is_Rational is not True:
            raise CensusError("Kemeny result is not exact rational")

        record = {
            "n": n,
            "state_id": state_id(n, mask),
            "edges": public_edges(n, mask),
            "edge_count": edge_count,
            "degrees": [int(degree) for degree in degrees],
            "transition_matrix": [
                [rational_object(transition[row, column]) for column in range(n)]
                for row in range(n)
            ],
            "ground_vertex": n,
            "grounded_laplacian_determinant": int(determinant),
            "grounded_inverse_verified": True,
            "kemeny": rational_object(kemeny),
        }
        return sp.Rational(kemeny), record

    def sorted_records(self) -> list[dict[str, Any]]:
        return [
            self._cache[key][1]
            for key in sorted(
                self._cache,
                key=lambda item: (item[0], edges_from_mask(item[0], item[1])),
            )
        ]

    @property
    def state_count(self) -> int:
        return len(self._cache)


def evaluate_pair(
    evaluator: StateEvaluator,
    n: int,
    base_mask: int,
    edge_e: tuple[int, int],
    edge_f: tuple[int, int],
) -> dict[str, Any]:
    if edge_e >= edge_f:
        raise CensusError("Added edge pair is not in strict lexicographic order")
    single_e_mask = add_edge(n, base_mask, edge_e)
    single_f_mask = add_edge(n, base_mask, edge_f)
    joint_mask = add_edge(n, single_e_mask, edge_f)
    base_value, _ = evaluator.evaluate(n, base_mask)
    single_e_value, _ = evaluator.evaluate(n, single_e_mask)
    single_f_value, _ = evaluator.evaluate(n, single_f_mask)
    joint_value, _ = evaluator.evaluate(n, joint_mask)
    delta_e = sp.cancel(single_e_value - base_value)
    delta_f = sp.cancel(single_f_value - base_value)
    delta_joint = sp.cancel(joint_value - base_value)
    qualifies = bool(delta_e <= 0 and delta_f <= 0 and delta_joint > 0)
    return {
        "added_edges": [public_edge(edge_e), public_edge(edge_f)],
        "states": {
            "base": {"state_id": state_id(n, base_mask), "edges": public_edges(n, base_mask)},
            "single_e": {
                "state_id": state_id(n, single_e_mask),
                "edges": public_edges(n, single_e_mask),
            },
            "single_f": {
                "state_id": state_id(n, single_f_mask),
                "edges": public_edges(n, single_f_mask),
            },
            "joint": {"state_id": state_id(n, joint_mask), "edges": public_edges(n, joint_mask)},
        },
        "kemeny": {
            "base": rational_object(base_value),
            "single_e": rational_object(single_e_value),
            "single_f": rational_object(single_f_value),
            "joint": rational_object(joint_value),
        },
        "deltas": {
            "single_e_minus_base": rational_object(delta_e),
            "single_f_minus_base": rational_object(delta_f),
            "joint_minus_base": rational_object(delta_joint),
        },
        "signs": {
            "single_e_minus_base": sign_name(delta_e),
            "single_f_minus_base": sign_name(delta_f),
            "joint_minus_base": sign_name(delta_joint),
        },
        "equality_flags": {
            "single_e_equals_base": bool(delta_e == 0),
            "single_f_equals_base": bool(delta_f == 0),
            "joint_equals_base": bool(delta_joint == 0),
        },
        "qualifies": qualifies,
    }


def published_p7_record(evaluator: StateEvaluator) -> dict[str, Any]:
    n = 7
    base_edges = tuple((vertex, vertex + 1) for vertex in range(6))
    base_mask = mask_from_edges(n, base_edges)
    edge_e = (0, 2)
    edge_f = (4, 6)
    evaluation = evaluate_pair(evaluator, n, base_mask, edge_e, edge_f)
    return {
        "schema_version": SCHEMA_VERSION,
        "record_type": "published_p7_control",
        "source": {
            "title": "A 1-Separation Formula for the Graph Kemeny Constant and Braess Edges",
            "authors": ["Nolan Faught", "Mark Kempton", "Adam Knudson"],
            "locator": "arXiv:2108.01061v1, immediately after Corollary 4.3",
            "url": "https://arxiv.org/abs/2108.01061",
            "novelty_status": "published_example_not_new_here",
        },
        "definition": {
            "braess": "strict K increase",
            "qualifying_inequalities": [
                "K(G+e) <= K(G)",
                "K(G+f) <= K(G)",
                "K(G+e+f) > K(G)",
            ],
        },
        "n": n,
        "base_graph6": encode_graph6(n, base_mask),
        "base_edges": public_edges(n, base_mask),
        **evaluation,
    }


def empty_sign_counts() -> dict[str, int]:
    return {
        "negative|negative|negative": 0,
        "negative|negative|zero": 0,
        "negative|negative|positive": 0,
        "negative|zero|negative": 0,
        "negative|zero|zero": 0,
        "negative|zero|positive": 0,
        "negative|positive|negative": 0,
        "negative|positive|zero": 0,
        "negative|positive|positive": 0,
        "zero|negative|negative": 0,
        "zero|negative|zero": 0,
        "zero|negative|positive": 0,
        "zero|zero|negative": 0,
        "zero|zero|zero": 0,
        "zero|zero|positive": 0,
        "zero|positive|negative": 0,
        "zero|positive|zero": 0,
        "zero|positive|positive": 0,
        "positive|negative|negative": 0,
        "positive|negative|zero": 0,
        "positive|negative|positive": 0,
        "positive|zero|negative": 0,
        "positive|zero|zero": 0,
        "positive|zero|positive": 0,
        "positive|positive|negative": 0,
        "positive|positive|zero": 0,
        "positive|positive|positive": 0,
    }


def summarize_records(records: list[dict[str, Any]]) -> dict[str, Any]:
    sign_counts = Counter(
        "|".join(
            [
                record["signs"]["single_e_minus_base"],
                record["signs"]["single_f_minus_base"],
                record["signs"]["joint_minus_base"],
            ]
        )
        for record in records
    )
    expanded_sign_counts = empty_sign_counts()
    expanded_sign_counts.update(sign_counts)
    return {
        "pair_count": len(records),
        "witness_count": sum(1 for record in records if record["qualifies"]),
        "single_equality_occurrences": sum(
            1 for record in records if record["equality_flags"]["single_e_equals_base"]
        ),
        "single_f_equality_occurrences": sum(
            1 for record in records if record["equality_flags"]["single_f_equals_base"]
        ),
        "pairs_with_any_single_equality": sum(
            1
            for record in records
            if record["equality_flags"]["single_e_equals_base"]
            or record["equality_flags"]["single_f_equals_base"]
        ),
        "pairs_with_both_single_equalities": sum(
            1
            for record in records
            if record["equality_flags"]["single_e_equals_base"]
            and record["equality_flags"]["single_f_equals_base"]
        ),
        "joint_equality_occurrences": sum(
            1 for record in records if record["equality_flags"]["joint_equals_base"]
        ),
        "sign_triples": expanded_sign_counts,
    }


def run_census(input_dir: Path, output_dir: Path) -> int:
    if sys.version_info[:3] != EXPECTED_PYTHON:
        raise CensusError(
            f"Python version {platform.python_version()} does not equal 3.12.11"
        )
    if sp.__version__ != EXPECTED_SYMPY:
        raise CensusError(
            f"SymPy version {sp.__version__} does not equal {EXPECTED_SYMPY}"
        )
    output_dir.mkdir(parents=True, exist_ok=False)
    evaluator = StateEvaluator()

    # The published control is intentionally evaluated before any study graph is decoded.
    if sha256_file(input_dir / "source-manifest.json") != EXPECTED_SOURCE_MANIFEST_SHA256:
        raise CensusError("Source manifest hash mismatch before P7 control")
    if sha256_file(CONTRACT_PATH) != EXPECTED_CONTRACT_SHA256:
        raise CensusError("Contract hash mismatch before P7 control")
    p7 = published_p7_record(evaluator)
    write_json(output_dir / "published-p7.json", p7)
    if not p7["qualifies"]:
        write_json(
            output_dir / "graph-values.json",
            {
                "schema_version": SCHEMA_VERSION,
                "status": "invalid_published_p7_control",
                "values": evaluator.sorted_records(),
            },
        )
        write_jsonl(output_dir / "pairs.jsonl", [])
        write_json(
            output_dir / "witnesses.json",
            {
                "schema_version": SCHEMA_VERSION,
                "status": "invalid_published_p7_control",
                "witness_count": 0,
                "witnesses": [],
            },
        )
        write_json(
            output_dir / "summary.json",
            {
                "schema_version": SCHEMA_VERSION,
                "status": "invalid_published_p7_control",
                "p7_qualifies": False,
                "census_interpreted": False,
            },
        )
        print(
            json.dumps(
                {"status": "invalid_published_p7_control", "output_dir": str(output_dir)},
                sort_keys=True,
            )
        )
        return 2

    records_by_order = read_and_verify_inputs(input_dir)
    completeness = establish_labelled_completeness(records_by_order)
    all_pair_records: list[dict[str, Any]] = []
    witnesses: list[dict[str, Any]] = []
    graph_summaries: list[dict[str, Any]] = []
    pair_index_global = 0

    for n, records in sorted(records_by_order.items()):
        possible_edges = all_edges(n)
        for source_record in records:
            base_mask = source_record["mask"]
            evaluator.evaluate(n, base_mask)
            nonedges = tuple(
                edge
                for bit, edge in enumerate(possible_edges)
                if not base_mask & (1 << bit)
            )
            expected_pairs = math.comb(len(nonedges), 2)
            graph_pair_records: list[dict[str, Any]] = []
            for pair_index_in_graph, (edge_e, edge_f) in enumerate(
                itertools.combinations(nonedges, 2), start=1
            ):
                pair_index_global += 1
                evaluation = evaluate_pair(
                    evaluator, n, base_mask, edge_e, edge_f
                )
                pair_record = {
                    "schema_version": SCHEMA_VERSION,
                    "record_type": "marked_nonedge_pair",
                    "pair_index_global": pair_index_global,
                    "pair_index_in_graph": pair_index_in_graph,
                    "n": n,
                    "source_file": source_record["source_file"],
                    "source_line": source_record["source_line"],
                    "source_graph6": source_record["graph6"],
                    "base_edges": public_edges(n, base_mask),
                    "nonedge_count": len(nonedges),
                    **evaluation,
                }
                graph_pair_records.append(pair_record)
                all_pair_records.append(pair_record)
                if evaluation["qualifies"]:
                    witnesses.append(
                        {
                            "schema_version": SCHEMA_VERSION,
                            "record_type": "qualifying_witness",
                            "n": n,
                            "source_file": source_record["source_file"],
                            "source_line": source_record["source_line"],
                            "source_graph6": source_record["graph6"],
                            "base_edges": public_edges(n, base_mask),
                            "pair_index_global": pair_index_global,
                            **evaluation,
                        }
                    )
            if len(graph_pair_records) != expected_pairs:
                raise CensusError(
                    f"Pair count mismatch at n={n}, line={source_record['source_line']}"
                )
            graph_summary = {
                "n": n,
                "source_file": source_record["source_file"],
                "source_line": source_record["source_line"],
                "source_graph6": source_record["graph6"],
                "base_edges": public_edges(n, base_mask),
                "nonedge_count": len(nonedges),
                "expected_pair_count": expected_pairs,
                "evaluated_pair_count": len(graph_pair_records),
                **summarize_records(graph_pair_records),
            }
            graph_summaries.append(graph_summary)

    if pair_index_global != len(all_pair_records):
        raise CensusError("Global pair index is inconsistent")
    expected_from_graphs = sum(
        graph["expected_pair_count"] for graph in graph_summaries
    )
    if expected_from_graphs != len(all_pair_records):
        raise CensusError("Full pair ledger count differs from per-graph expected sum")

    per_order: list[dict[str, Any]] = []
    for n in sorted(records_by_order):
        order_records = [record for record in all_pair_records if record["n"] == n]
        order_graphs = [graph for graph in graph_summaries if graph["n"] == n]
        per_order.append(
            {
                "n": n,
                "representative_count": len(records_by_order[n]),
                "zero_pair_graph_count": sum(
                    1 for graph in order_graphs if graph["evaluated_pair_count"] == 0
                ),
                "expected_pair_count": sum(
                    graph["expected_pair_count"] for graph in order_graphs
                ),
                **summarize_records(order_records),
            }
        )

    graph_values_path = output_dir / "graph-values.json"
    pairs_path = output_dir / "pairs.jsonl"
    witnesses_path = output_dir / "witnesses.json"
    p7_path = output_dir / "published-p7.json"
    write_json(
        graph_values_path,
        {
            "schema_version": SCHEMA_VERSION,
            "status": "complete_author_evaluation",
            "method": "exact grounded Laplacian inverse and d^T R d/(4m)",
            "cache_key": "(n, full labelled graph edge bitmask)",
            "state_count": evaluator.state_count,
            "values": evaluator.sorted_records(),
        },
    )
    write_jsonl(pairs_path, all_pair_records)
    write_json(
        witnesses_path,
        {
            "schema_version": SCHEMA_VERSION,
            "status": "author_only_pending_independent_evaluation",
            "definition": {
                "single_edges": "delta <= 0",
                "joint_addition": "delta > 0",
            },
            "witness_count": len(witnesses),
            "witnesses": witnesses,
        },
    )

    if witnesses:
        candidate_minimum = min(witness["n"] for witness in witnesses)
        minimum_basis = "author witness plus complete author exclusion of lower orders"
    else:
        candidate_minimum = 7
        minimum_basis = "published P7 control plus complete author exclusion through order 6"
    lower_order_witness_counts = {
        str(entry["n"]): entry["witness_count"]
        for entry in per_order
        if entry["n"] < candidate_minimum
    }
    if any(lower_order_witness_counts.values()):
        raise CensusError("Candidate minimum has a witness on a lower order")

    output_hashes = {
        path.name: {"sha256": sha256_file(path), "bytes": path.stat().st_size}
        for path in [graph_values_path, pairs_path, witnesses_path, p7_path]
    }
    summary = {
        "schema_version": SCHEMA_VERSION,
        "status": "complete_author_evaluation_pending_independent_verification",
        "claim_status": "candidate_exact_finite_computation_not_novelty_certified",
        "definition": {
            "graph_class": "finite connected simple undirected unweighted graphs",
            "transition_matrix": "P=D^-1 A with row orientation",
            "kemeny": "sum of reciprocals of nonzero eigenvalues of I-P; no additive return-time constant",
            "qualifying_inequalities": [
                "K(G+e) <= K(G)",
                "K(G+f) <= K(G)",
                "K(G+e+f) > K(G)",
            ],
        },
        "environment": {
            "python": platform.python_version(),
            "sympy": sp.__version__,
        },
        "frozen_inputs": {
            "contract_sha256": EXPECTED_CONTRACT_SHA256,
            "source_manifest_sha256": EXPECTED_SOURCE_MANIFEST_SHA256,
        },
        "published_p7": {
            "qualifies": p7["qualifies"],
            "base_graph6": p7["base_graph6"],
            "added_edges": p7["added_edges"],
            "kemeny": p7["kemeny"],
            "deltas": p7["deltas"],
            "signs": p7["signs"],
            "novelty_status": "published_example_not_new_here",
        },
        "input_completeness": completeness,
        "census": {
            "orders": sorted(records_by_order),
            "representative_count": sum(len(records) for records in records_by_order.values()),
            "expected_representative_count": 142,
            "pair_count": len(all_pair_records),
            "pair_count_from_per_graph_choose_nonedges_2": expected_from_graphs,
            "witness_count_through_order_6": len(witnesses),
            "graph_state_count_including_p7_control": evaluator.state_count,
            "cache": {
                "key": "(n, full labelled graph edge bitmask)",
                "hits": evaluator.cache_hits,
                "misses": evaluator.cache_misses,
                "semantic_note": "cache only; no speedup or algorithm novelty claim",
            },
            "per_order": per_order,
            "per_graph": graph_summaries,
            "pair_ledger_sha256": output_hashes["pairs.jsonl"]["sha256"],
        },
        "candidate_minimum_order": candidate_minimum,
        "candidate_minimum_basis": minimum_basis,
        "lower_order_witness_counts": lower_order_witness_counts,
        "limitations": [
            "Author result has not yet been independently reproduced or compared.",
            "Publication-level novelty is unresolved; search absence is not evidence of novelty.",
            "The computation makes no algorithmic novelty, prevalence, real-network, runtime, impact, or human-time claim.",
        ],
        "deterministic_output_files": output_hashes,
    }
    write_json(output_dir / "summary.json", summary)
    print(
        json.dumps(
            {
                "status": summary["status"],
                "candidate_minimum_order": candidate_minimum,
                "pair_count": len(all_pair_records),
                "witness_count_through_order_6": len(witnesses),
                "output_dir": str(output_dir),
            },
            sort_keys=True,
        )
    )
    return 0


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Exact author census for a jointly Braess pair"
    )
    parser.add_argument("--input-dir", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    try:
        return run_census(args.input_dir.resolve(), args.output_dir.resolve())
    except Exception as error:
        output_dir = args.output_dir.resolve()
        if output_dir.exists() and output_dir.is_dir():
            failure = {
                "schema_version": SCHEMA_VERSION,
                "status": "failed",
                "exception_type": type(error).__name__,
                "message": str(error),
            }
            write_json(output_dir / "failure.json", failure)
        traceback.print_exc(file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
