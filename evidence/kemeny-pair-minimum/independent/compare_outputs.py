from __future__ import annotations

import argparse
import hashlib
import json
import math
from collections import Counter, defaultdict
from fractions import Fraction
from pathlib import Path
from typing import Any, Iterable


EXPECTED_AUTHOR_MANIFEST_SHA256 = (
    "78b4121cc83d7e06bed7470f70c1cbb365ba1d24543595f7620b9e15e0524a9d"
)
EXPECTED_INDEPENDENT_OUTPUT_SEAL_SHA256 = (
    "7ccdcbbd54a21fec1bfdfc668c05c9cc06564a985e82e68e9c4958a110994b2d"
)
EXPECTED_INDEPENDENT_INPUT_MANIFEST_SHA256 = (
    "e76e474f723cfdc6af6014cf35371601a2525a6ee78e148bb72ef99b9249019d"
)
EXPECTED_INDEPENDENT_INPUT_SEAL_SHA256 = (
    "d0ce60abc7d207bba46f86e4da7551d3c7b1b8f4d9f4eaf07bdeb68720932389"
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--author-dir", type=Path, required=True)
    parser.add_argument("--independent-dir", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    return parser.parse_args()


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def canonical_bytes(value: Any) -> bytes:
    return (
        json.dumps(value, ensure_ascii=True, sort_keys=True, separators=(",", ":"))
        + "\n"
    ).encode("ascii")


def canonical_sha256(value: Any) -> str:
    return hashlib.sha256(canonical_bytes(value)).hexdigest()


def load_json(path: Path) -> Any:
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def load_jsonl(path: Path) -> list[dict[str, Any]]:
    records: list[dict[str, Any]] = []
    with path.open("r", encoding="utf-8") as handle:
        for line_number, line in enumerate(handle, start=1):
            if not line.strip():
                raise ValueError(f"blank JSONL line at {path}:{line_number}")
            record = json.loads(line)
            if not isinstance(record, dict):
                raise TypeError(f"non-object JSONL record at {path}:{line_number}")
            records.append(record)
    return records


def normalized_path(path: Path) -> str:
    return path.as_posix()


def verify_records(root: Path, records: Iterable[dict[str, Any]]) -> dict[str, Any]:
    checks: list[dict[str, Any]] = []
    for record in records:
        path = root / record["path"]
        actual_bytes = path.stat().st_size
        actual_sha256 = sha256_file(path)
        checks.append(
            {
                "path": record["path"],
                "expected_bytes": record["bytes"],
                "actual_bytes": actual_bytes,
                "expected_sha256": record["sha256"],
                "actual_sha256": actual_sha256,
                "match": actual_bytes == record["bytes"]
                and actual_sha256 == record["sha256"],
            }
        )
    return {
        "record_count": len(checks),
        "all_match": all(record["match"] for record in checks),
        "records": checks,
    }


def verify_absolute_records(records: Iterable[dict[str, Any]]) -> dict[str, Any]:
    checks: list[dict[str, Any]] = []
    for record in records:
        path = Path(record["path"])
        actual_bytes = path.stat().st_size
        actual_sha256 = sha256_file(path)
        checks.append(
            {
                "role": record.get("role"),
                "path": normalized_path(path),
                "expected_bytes": record["bytes"],
                "actual_bytes": actual_bytes,
                "expected_sha256": record["sha256"],
                "actual_sha256": actual_sha256,
                "match": actual_bytes == record["bytes"]
                and actual_sha256 == record["sha256"],
            }
        )
    return {
        "record_count": len(checks),
        "all_match": all(record["match"] for record in checks),
        "records": checks,
    }


def rational(value: Any, location: str, issues: list[dict[str, Any]]) -> tuple[int, int]:
    valid_shape = isinstance(value, dict) and set(value) >= {"numerator", "denominator"}
    if not valid_shape:
        issues.append({"location": location, "issue": "invalid_rational_shape", "value": value})
        return (0, 1)
    numerator = value["numerator"]
    denominator = value["denominator"]
    if (
        isinstance(numerator, bool)
        or isinstance(denominator, bool)
        or not isinstance(numerator, int)
        or not isinstance(denominator, int)
    ):
        issues.append({"location": location, "issue": "non_integer_rational", "value": value})
        return (0, 1)
    if denominator <= 0:
        issues.append({"location": location, "issue": "nonpositive_denominator", "value": value})
    if math.gcd(numerator, denominator) != 1:
        issues.append({"location": location, "issue": "noncanonical_fraction", "value": value})
    return (numerator, denominator)


def fraction_value(value: tuple[int, int]) -> Fraction:
    return Fraction(value[0], value[1])


def fraction_json(value: tuple[int, int]) -> dict[str, int]:
    return {"numerator": value[0], "denominator": value[1]}


def sign_name(value: tuple[int, int]) -> str:
    numerator = value[0]
    if numerator < 0:
        return "negative"
    if numerator > 0:
        return "positive"
    return "zero"


def edges(value: Any, location: str, issues: list[dict[str, Any]]) -> tuple[tuple[int, int], ...]:
    result: list[tuple[int, int]] = []
    if not isinstance(value, list):
        issues.append({"location": location, "issue": "edges_not_list"})
        return tuple()
    for index, edge in enumerate(value):
        if (
            not isinstance(edge, list)
            or len(edge) != 2
            or isinstance(edge[0], bool)
            or isinstance(edge[1], bool)
            or not isinstance(edge[0], int)
            or not isinstance(edge[1], int)
        ):
            issues.append(
                {"location": f"{location}[{index}]", "issue": "invalid_edge", "value": edge}
            )
            continue
        u, v = sorted(edge)
        if u == v:
            issues.append({"location": f"{location}[{index}]", "issue": "loop_edge"})
        result.append((u, v))
    canonical = tuple(sorted(result))
    if len(set(canonical)) != len(canonical):
        issues.append({"location": location, "issue": "duplicate_edge"})
    if tuple(result) != canonical:
        issues.append({"location": location, "issue": "noncanonical_edge_order"})
    return canonical


def edges_json(value: tuple[tuple[int, int], ...]) -> list[list[int]]:
    return [[u, v] for u, v in value]


def state_id(n: int, state_edges: tuple[tuple[int, int], ...]) -> str:
    body = ",".join(f"{u}-{v}" for u, v in state_edges)
    return f"n={n};edges={body}"


def pair_key(
    n: int,
    source_file: str,
    source_line: int,
    graph6: str,
    added_edges: tuple[tuple[int, int], tuple[int, int]],
) -> str:
    e, f = added_edges
    return (
        f"n={n};source={source_file}:{source_line};graph6={graph6};"
        f"e={e[0]}-{e[1]};f={f[0]}-{f[1]}"
    )


def normalize_graph_records(
    records: list[dict[str, Any]], origin: str, issues: list[dict[str, Any]]
) -> tuple[dict[str, dict[str, Any]], dict[str, Any]]:
    result: dict[str, dict[str, Any]] = {}
    method_checks = {
        "origin": origin,
        "record_count": len(records),
        "all_author_grounded_inverse_verified": True,
        "all_independent_characteristic_invariants_verified": True,
        "all_independent_formula_values_verified": True,
    }
    for index, record in enumerate(records):
        location = f"{origin}.graph_values[{index}]"
        n = record["n"]
        state_edges = edges(record["edges"], f"{location}.edges", issues)
        identifier = state_id(n, state_edges)
        if record.get("state_id") != identifier:
            issues.append(
                {
                    "location": f"{location}.state_id",
                    "issue": "state_id_mismatch",
                    "expected": identifier,
                    "actual": record.get("state_id"),
                }
            )
        kemeny = rational(record["kemeny"], f"{location}.kemeny", issues)
        normalized = {
            "n": n,
            "edges": edges_json(state_edges),
            "edge_count": record["edge_count"],
            "degrees": record["degrees"],
            "kemeny": fraction_json(kemeny),
        }
        if record["edge_count"] != len(state_edges):
            issues.append({"location": location, "issue": "edge_count_mismatch"})
        computed_degrees = [0] * n
        for u, v in state_edges:
            computed_degrees[u - 1] += 1
            computed_degrees[v - 1] += 1
        if record["degrees"] != computed_degrees:
            issues.append(
                {
                    "location": f"{location}.degrees",
                    "issue": "degree_sequence_mismatch",
                    "expected": computed_degrees,
                    "actual": record["degrees"],
                }
            )
        if origin == "author":
            if record.get("grounded_inverse_verified") is not True:
                method_checks["all_author_grounded_inverse_verified"] = False
                issues.append({"location": location, "issue": "author_method_flag_false"})
        else:
            method = record.get("method", {})
            required = (
                method.get("matrix") == "I-D^-1 A"
                and method.get("formula") == "K=-q_linear/q_constant"
                and method.get("p_constant_zero") is True
                and method.get("q_constant_nonzero") is True
                and method.get("row_sums_zero") is True
            )
            if not required:
                method_checks["all_independent_characteristic_invariants_verified"] = False
                issues.append({"location": location, "issue": "independent_method_flag_false"})
            q_linear = rational(
                method.get("q_linear"), f"{location}.method.q_linear", issues
            )
            q_constant = rational(
                method.get("q_constant"), f"{location}.method.q_constant", issues
            )
            formula_value = -fraction_value(q_linear) / fraction_value(q_constant)
            if formula_value != fraction_value(kemeny):
                method_checks["all_independent_formula_values_verified"] = False
                issues.append(
                    {
                        "location": location,
                        "issue": "independent_stored_formula_value_mismatch",
                    }
                )
        if identifier in result:
            issues.append({"location": location, "issue": "duplicate_state_id", "key": identifier})
        result[identifier] = normalized
    method_checks["pass"] = all(
        value is True
        for key, value in method_checks.items()
        if key.startswith("all_")
    )
    return result, method_checks


def semantic_pair_core_author(
    record: dict[str, Any], location: str, issues: list[dict[str, Any]]
) -> dict[str, Any]:
    n = record["n"]
    base_edges = edges(record["base_edges"], f"{location}.base_edges", issues)
    added_raw = edges(record["added_edges"], f"{location}.added_edges", issues)
    if len(added_raw) != 2:
        issues.append({"location": location, "issue": "added_edge_pair_size_mismatch"})
        added_raw = (added_raw + ((0, 0), (0, 0)))[:2]
    raw_e = tuple(sorted(record["added_edges"][0]))
    raw_f = tuple(sorted(record["added_edges"][1]))
    added = tuple(sorted((raw_e, raw_f)))
    swap = raw_e != added[0]

    k_base = rational(record["kemeny"]["base"], f"{location}.kemeny.base", issues)
    k_raw_e = rational(
        record["kemeny"]["single_e"], f"{location}.kemeny.single_e", issues
    )
    k_raw_f = rational(
        record["kemeny"]["single_f"], f"{location}.kemeny.single_f", issues
    )
    k_joint = rational(record["kemeny"]["joint"], f"{location}.kemeny.joint", issues)
    d_raw_e = rational(
        record["deltas"]["single_e_minus_base"],
        f"{location}.deltas.single_e_minus_base",
        issues,
    )
    d_raw_f = rational(
        record["deltas"]["single_f_minus_base"],
        f"{location}.deltas.single_f_minus_base",
        issues,
    )
    d_joint = rational(
        record["deltas"]["joint_minus_base"],
        f"{location}.deltas.joint_minus_base",
        issues,
    )
    k_e, k_f = (k_raw_f, k_raw_e) if swap else (k_raw_e, k_raw_f)
    d_e, d_f = (d_raw_f, d_raw_e) if swap else (d_raw_e, d_raw_f)
    sign_raw_e = record["signs"]["single_e_minus_base"]
    sign_raw_f = record["signs"]["single_f_minus_base"]
    sign_e, sign_f = (sign_raw_f, sign_raw_e) if swap else (sign_raw_e, sign_raw_f)
    equal_raw_e = record["equality_flags"]["single_e_equals_base"]
    equal_raw_f = record["equality_flags"]["single_f_equals_base"]
    equal_e, equal_f = (equal_raw_f, equal_raw_e) if swap else (equal_raw_e, equal_raw_f)
    state_raw_e = record["states"]["single_e"]
    state_raw_f = record["states"]["single_f"]
    state_e, state_f = (state_raw_f, state_raw_e) if swap else (state_raw_e, state_raw_f)

    k_values = {"base": k_base, "e": k_e, "f": k_f, "joint": k_joint}
    delta_values = {"e": d_e, "f": d_f, "joint": d_joint}
    stored_signs = {
        "e": sign_e,
        "f": sign_f,
        "joint": record["signs"]["joint_minus_base"],
    }
    stored_equalities = {
        "e": equal_e,
        "f": equal_f,
        "joint": record["equality_flags"]["joint_equals_base"],
    }
    stored_qualifies = record["qualifies"]
    _validate_pair_arithmetic(
        k_values,
        delta_values,
        stored_signs,
        stored_equalities,
        stored_qualifies,
        None,
        location,
        issues,
    )

    role_states = {
        "base": record["states"]["base"],
        "e": state_e,
        "f": state_f,
        "joint": record["states"]["joint"],
    }
    normalized_states: dict[str, Any] = {}
    for role, state in role_states.items():
        role_edges = edges(state["edges"], f"{location}.states.{role}.edges", issues)
        identifier = state_id(n, role_edges)
        if state.get("state_id") != identifier:
            issues.append(
                {
                    "location": f"{location}.states.{role}.state_id",
                    "issue": "state_id_mismatch",
                    "expected": identifier,
                    "actual": state.get("state_id"),
                }
            )
        normalized_states[role] = {"n": n, "edges": edges_json(role_edges)}

    return {
        "n": n,
        "base_edges": edges_json(base_edges),
        "added_edges": edges_json(added),
        "kemeny": {key: fraction_json(value) for key, value in k_values.items()},
        "deltas": {key: fraction_json(value) for key, value in delta_values.items()},
        "signs": stored_signs,
        "equalities": stored_equalities,
        "classification": {
            "singleton_e_nonincreasing": sign_e in {"negative", "zero"},
            "singleton_f_nonincreasing": sign_f in {"negative", "zero"},
            "joint_strict_increase": stored_signs["joint"] == "positive",
            "qualifies": stored_qualifies,
        },
        "states": normalized_states,
    }


def semantic_pair_core_independent(
    record: dict[str, Any], location: str, issues: list[dict[str, Any]]
) -> dict[str, Any]:
    n = record["n"]
    base_edges = edges(record["base_edges"], f"{location}.base_edges", issues)
    added_raw = edges(record["added_edges"], f"{location}.added_edges", issues)
    if len(added_raw) != 2:
        issues.append({"location": location, "issue": "added_edge_pair_size_mismatch"})
        added_raw = (added_raw + ((0, 0), (0, 0)))[:2]
    raw_e = tuple(sorted(record["added_edges"][0]))
    raw_f = tuple(sorted(record["added_edges"][1]))
    added = tuple(sorted((raw_e, raw_f)))
    swap = raw_e != added[0]

    k_base = rational(record["kemeny"]["G"], f"{location}.kemeny.G", issues)
    k_raw_e = rational(
        record["kemeny"]["G_plus_e"], f"{location}.kemeny.G_plus_e", issues
    )
    k_raw_f = rational(
        record["kemeny"]["G_plus_f"], f"{location}.kemeny.G_plus_f", issues
    )
    k_joint = rational(
        record["kemeny"]["G_plus_e_plus_f"],
        f"{location}.kemeny.G_plus_e_plus_f",
        issues,
    )
    d_raw_e = rational(record["deltas"]["e"], f"{location}.deltas.e", issues)
    d_raw_f = rational(record["deltas"]["f"], f"{location}.deltas.f", issues)
    d_joint = rational(record["deltas"]["both"], f"{location}.deltas.both", issues)
    k_e, k_f = (k_raw_f, k_raw_e) if swap else (k_raw_e, k_raw_f)
    d_e, d_f = (d_raw_f, d_raw_e) if swap else (d_raw_e, d_raw_f)
    classification = record["classification"]
    sign_raw_e = classification["delta_e_sign"]
    sign_raw_f = classification["delta_f_sign"]
    sign_e, sign_f = (sign_raw_f, sign_raw_e) if swap else (sign_raw_e, sign_raw_f)
    equal_raw_e = classification["delta_e_equal"]
    equal_raw_f = classification["delta_f_equal"]
    equal_e, equal_f = (equal_raw_f, equal_raw_e) if swap else (equal_raw_e, equal_raw_f)
    nonincrease_raw_e = classification["singleton_e_nonincreasing"]
    nonincrease_raw_f = classification["singleton_f_nonincreasing"]
    nonincrease_e, nonincrease_f = (
        (nonincrease_raw_f, nonincrease_raw_e)
        if swap
        else (nonincrease_raw_e, nonincrease_raw_f)
    )
    state_raw_e = record["states"]["G_plus_e"]
    state_raw_f = record["states"]["G_plus_f"]
    state_e, state_f = (state_raw_f, state_raw_e) if swap else (state_raw_e, state_raw_f)

    k_values = {"base": k_base, "e": k_e, "f": k_f, "joint": k_joint}
    delta_values = {"e": d_e, "f": d_f, "joint": d_joint}
    stored_signs = {
        "e": sign_e,
        "f": sign_f,
        "joint": classification["delta_both_sign"],
    }
    stored_equalities = {
        "e": equal_e,
        "f": equal_f,
        "joint": classification["delta_both_equal"],
    }
    stored_classification = {
        "singleton_e_nonincreasing": nonincrease_e,
        "singleton_f_nonincreasing": nonincrease_f,
        "joint_strict_increase": classification["joint_strict_increase"],
        "qualifies": classification["qualifies"],
    }
    _validate_pair_arithmetic(
        k_values,
        delta_values,
        stored_signs,
        stored_equalities,
        classification["qualifies"],
        stored_classification,
        location,
        issues,
    )

    role_states = {
        "base": record["states"]["G"],
        "e": state_e,
        "f": state_f,
        "joint": record["states"]["G_plus_e_plus_f"],
    }
    normalized_states: dict[str, Any] = {}
    for role, state in role_states.items():
        role_edges = edges(state["edges"], f"{location}.states.{role}.edges", issues)
        if state.get("n") != n:
            issues.append({"location": f"{location}.states.{role}.n", "issue": "n_mismatch"})
        normalized_states[role] = {"n": n, "edges": edges_json(role_edges)}

    return {
        "n": n,
        "base_edges": edges_json(base_edges),
        "added_edges": edges_json(added),
        "kemeny": {key: fraction_json(value) for key, value in k_values.items()},
        "deltas": {key: fraction_json(value) for key, value in delta_values.items()},
        "signs": stored_signs,
        "equalities": stored_equalities,
        "classification": stored_classification,
        "states": normalized_states,
    }


def _validate_pair_arithmetic(
    k_values: dict[str, tuple[int, int]],
    delta_values: dict[str, tuple[int, int]],
    stored_signs: dict[str, str],
    stored_equalities: dict[str, bool],
    stored_qualifies: bool,
    stored_classification: dict[str, bool] | None,
    location: str,
    issues: list[dict[str, Any]],
) -> None:
    expected_deltas = {
        "e": fraction_value(k_values["e"]) - fraction_value(k_values["base"]),
        "f": fraction_value(k_values["f"]) - fraction_value(k_values["base"]),
        "joint": fraction_value(k_values["joint"]) - fraction_value(k_values["base"]),
    }
    for role, expected in expected_deltas.items():
        if expected != fraction_value(delta_values[role]):
            issues.append(
                {"location": location, "issue": "delta_arithmetic_mismatch", "role": role}
            )
        expected_sign = "negative" if expected < 0 else "positive" if expected > 0 else "zero"
        if stored_signs[role] != expected_sign:
            issues.append(
                {
                    "location": location,
                    "issue": "delta_sign_mismatch",
                    "role": role,
                    "expected": expected_sign,
                    "actual": stored_signs[role],
                }
            )
        if stored_equalities[role] != (expected == 0):
            issues.append(
                {"location": location, "issue": "equality_flag_mismatch", "role": role}
            )
    expected_classification = {
        "singleton_e_nonincreasing": expected_deltas["e"] <= 0,
        "singleton_f_nonincreasing": expected_deltas["f"] <= 0,
        "joint_strict_increase": expected_deltas["joint"] > 0,
    }
    expected_classification["qualifies"] = all(expected_classification.values())
    if stored_qualifies != expected_classification["qualifies"]:
        issues.append({"location": location, "issue": "qualifies_flag_mismatch"})
    if stored_classification is not None and stored_classification != expected_classification:
        issues.append(
            {
                "location": location,
                "issue": "stored_classification_mismatch",
                "expected": expected_classification,
                "actual": stored_classification,
            }
        )


def normalize_pair_records(
    records: list[dict[str, Any]],
    origin: str,
    issues: list[dict[str, Any]],
    *,
    check_sequence: bool = False,
) -> tuple[dict[str, dict[str, Any]], list[str]]:
    result: dict[str, dict[str, Any]] = {}
    line_keys: list[str] = []
    for index, record in enumerate(records):
        location = f"{origin}.pairs[{index + 1}]"
        core = (
            semantic_pair_core_author(record, location, issues)
            if origin == "author"
            else semantic_pair_core_independent(record, location, issues)
        )
        source_file = record["source_file"]
        source_line = record["source_line"]
        graph6 = record["source_graph6"] if origin == "author" else record["graph6"]
        added = tuple(tuple(edge) for edge in core["added_edges"])
        key = pair_key(core["n"], source_file, source_line, graph6, added)  # type: ignore[arg-type]
        normalized = {
            "source_file": source_file,
            "source_line": source_line,
            "graph6": graph6,
            **core,
        }
        if origin == "author" and check_sequence:
            if record.get("pair_index_global") != index + 1:
                issues.append(
                    {
                        "location": location,
                        "issue": "noncontiguous_author_global_index",
                        "expected": index + 1,
                        "actual": record.get("pair_index_global"),
                    }
                )
        elif origin == "independent":
            if record.get("record_id") != key:
                issues.append(
                    {
                        "location": f"{location}.record_id",
                        "issue": "record_id_mismatch",
                        "expected": key,
                        "actual": record.get("record_id"),
                    }
                )
        if key in result:
            issues.append({"location": location, "issue": "duplicate_pair_key", "key": key})
        result[key] = normalized
        line_keys.append(key)
    return result, line_keys


def compare_maps(
    author: dict[str, Any], independent: dict[str, Any], scope: str
) -> dict[str, Any]:
    author_keys = set(author)
    independent_keys = set(independent)
    shared = sorted(author_keys & independent_keys)
    mismatches = [
        {"key": key, "author": author[key], "independent": independent[key]}
        for key in shared
        if author[key] != independent[key]
    ]
    author_canonical = [{"key": key, "value": author[key]} for key in sorted(author)]
    independent_canonical = [
        {"key": key, "value": independent[key]} for key in sorted(independent)
    ]
    return {
        "scope": scope,
        "author_count": len(author),
        "independent_count": len(independent),
        "shared_count": len(shared),
        "missing_from_independent": sorted(author_keys - independent_keys),
        "extra_in_independent": sorted(independent_keys - author_keys),
        "value_mismatch_count": len(mismatches),
        "value_mismatches": mismatches,
        "author_normalized_sha256": canonical_sha256(author_canonical),
        "independent_normalized_sha256": canonical_sha256(independent_canonical),
        "pass": author_keys == independent_keys and not mismatches,
    }


def validate_pair_state_references(
    pairs: dict[str, dict[str, Any]],
    graph_values: dict[str, dict[str, Any]],
    origin: str,
    issues: list[dict[str, Any]],
) -> dict[str, Any]:
    reference_count = 0
    for key, pair in pairs.items():
        for role in ("base", "e", "f", "joint"):
            state = pair["states"][role]
            state_edges = tuple(tuple(edge) for edge in state["edges"])
            identifier = state_id(state["n"], state_edges)
            reference_count += 1
            if identifier not in graph_values:
                issues.append(
                    {
                        "location": f"{origin}.pair_state_reference",
                        "issue": "missing_graph_state",
                        "pair_key": key,
                        "role": role,
                        "state_id": identifier,
                    }
                )
                continue
            graph = graph_values[identifier]
            if graph["edges"] != state["edges"] or graph["n"] != state["n"]:
                issues.append(
                    {
                        "location": f"{origin}.pair_state_reference",
                        "issue": "graph_state_structure_mismatch",
                        "pair_key": key,
                        "role": role,
                    }
                )
            if graph["kemeny"] != pair["kemeny"][role]:
                issues.append(
                    {
                        "location": f"{origin}.pair_state_reference",
                        "issue": "graph_state_kemeny_mismatch",
                        "pair_key": key,
                        "role": role,
                    }
                )
    return {"origin": origin, "reference_count": reference_count}


def source_key(n: int, source_file: str, source_line: int, graph6: str) -> str:
    return f"n={n};source={source_file}:{source_line};graph6={graph6}"


def nonzero_counts(value: dict[str, int]) -> dict[str, int]:
    return {key: count for key, count in sorted(value.items()) if count != 0}


def aggregate_pair_records(records: dict[str, dict[str, Any]]) -> dict[str, dict[str, Any]]:
    grouped: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for record in records.values():
        key = source_key(
            record["n"], record["source_file"], record["source_line"], record["graph6"]
        )
        grouped[key].append(record)
    result: dict[str, dict[str, Any]] = {}
    for key, rows in grouped.items():
        sign_triples = Counter(
            f'{row["signs"]["e"]}|{row["signs"]["f"]}|{row["signs"]["joint"]}'
            for row in rows
        )
        result[key] = {
            "pair_count": len(rows),
            "witness_count": sum(row["classification"]["qualifies"] for row in rows),
            "single_equality_occurrences": sum(row["equalities"]["e"] for row in rows),
            "single_f_equality_occurrences": sum(row["equalities"]["f"] for row in rows),
            "joint_equality_occurrences": sum(row["equalities"]["joint"] for row in rows),
            "pairs_with_any_single_equality": sum(
                row["equalities"]["e"] or row["equalities"]["f"] for row in rows
            ),
            "pairs_with_both_single_equalities": sum(
                row["equalities"]["e"] and row["equalities"]["f"] for row in rows
            ),
            "sign_triples": nonzero_counts(dict(sign_triples)),
        }
    return result


def normalize_per_graph_author(summary: dict[str, Any]) -> dict[str, dict[str, Any]]:
    result: dict[str, dict[str, Any]] = {}
    for row in summary["census"]["per_graph"]:
        key = source_key(row["n"], row["source_file"], row["source_line"], row["source_graph6"])
        result[key] = {
            "n": row["n"],
            "source_file": row["source_file"],
            "source_line": row["source_line"],
            "graph6": row["source_graph6"],
            "base_edges": row["base_edges"],
            "nonedge_count": row["nonedge_count"],
            "expected_pair_count": row["expected_pair_count"],
            "evaluated_pair_count": row["evaluated_pair_count"],
            "pair_count": row["pair_count"],
            "zero_pair_row": row["pair_count"] == 0,
            "witness_count": row["witness_count"],
            "single_equality_occurrences": row["single_equality_occurrences"],
            "single_f_equality_occurrences": row["single_f_equality_occurrences"],
            "joint_equality_occurrences": row["joint_equality_occurrences"],
            "pairs_with_any_single_equality": row["pairs_with_any_single_equality"],
            "pairs_with_both_single_equalities": row["pairs_with_both_single_equalities"],
            "sign_triples": nonzero_counts(row["sign_triples"]),
        }
    return result


def normalize_per_graph_independent(
    completeness: dict[str, Any], pair_aggregates: dict[str, dict[str, Any]]
) -> dict[str, dict[str, Any]]:
    result: dict[str, dict[str, Any]] = {}
    empty = {
        "pair_count": 0,
        "witness_count": 0,
        "single_equality_occurrences": 0,
        "single_f_equality_occurrences": 0,
        "joint_equality_occurrences": 0,
        "pairs_with_any_single_equality": 0,
        "pairs_with_both_single_equalities": 0,
        "sign_triples": {},
    }
    for order in completeness["orders"]:
        for row in order["representatives"]:
            key = source_key(order["n"], row["source_file"], row["source_line"], row["graph6"])
            aggregate = pair_aggregates.get(key, empty)
            result[key] = {
                "n": order["n"],
                "source_file": row["source_file"],
                "source_line": row["source_line"],
                "graph6": row["graph6"],
                "base_edges": row["edges"],
                "nonedge_count": row["nonedge_count"],
                "expected_pair_count": row["expected_choose_nonedge_2"],
                "evaluated_pair_count": row["evaluated_pair_count"],
                "pair_count": row["pair_count"],
                "zero_pair_row": row["zero_pair_row"],
                **aggregate,
            }
    return result


def pair_stats_for_order(records: dict[str, dict[str, Any]], n: int) -> dict[str, Any]:
    rows = [row for row in records.values() if row["n"] == n]
    sign_triples = Counter(
        f'{row["signs"]["e"]}|{row["signs"]["f"]}|{row["signs"]["joint"]}'
        for row in rows
    )
    return {
        "pair_count": len(rows),
        "witness_count": sum(row["classification"]["qualifies"] for row in rows),
        "single_equality_occurrences": sum(row["equalities"]["e"] for row in rows),
        "single_f_equality_occurrences": sum(row["equalities"]["f"] for row in rows),
        "joint_equality_occurrences": sum(row["equalities"]["joint"] for row in rows),
        "pairs_with_any_single_equality": sum(
            row["equalities"]["e"] or row["equalities"]["f"] for row in rows
        ),
        "pairs_with_both_single_equalities": sum(
            row["equalities"]["e"] and row["equalities"]["f"] for row in rows
        ),
        "sign_triples": nonzero_counts(dict(sign_triples)),
    }


def normalize_per_order_author(summary: dict[str, Any]) -> dict[str, dict[str, Any]]:
    result: dict[str, dict[str, Any]] = {}
    for row in summary["census"]["per_order"]:
        result[str(row["n"])] = {
            "n": row["n"],
            "representative_count": row["representative_count"],
            "pair_count": row["pair_count"],
            "expected_pair_count": row["expected_pair_count"],
            "witness_count": row["witness_count"],
            "zero_pair_source_row_count": row["zero_pair_graph_count"],
            "single_equality_occurrences": row["single_equality_occurrences"],
            "single_f_equality_occurrences": row["single_f_equality_occurrences"],
            "joint_equality_occurrences": row["joint_equality_occurrences"],
            "pairs_with_any_single_equality": row["pairs_with_any_single_equality"],
            "pairs_with_both_single_equalities": row["pairs_with_both_single_equalities"],
            "sign_triples": nonzero_counts(row["sign_triples"]),
        }
    return result


def normalize_per_order_independent(summary: dict[str, Any]) -> dict[str, dict[str, Any]]:
    result: dict[str, dict[str, Any]] = {}
    for row in summary["orders"]:
        result[str(row["n"])] = {
            "n": row["n"],
            "representative_count": row["source_graph_count"],
            "pair_count": row["candidate_pair_count"],
            "expected_pair_count": row["candidate_pair_count"],
            "witness_count": row["witness_count"],
            "zero_pair_source_row_count": row["zero_pair_source_row_count"],
            "single_equality_occurrences": row["delta_e_equality_count"],
            "single_f_equality_occurrences": row["delta_f_equality_count"],
            "joint_equality_occurrences": row["delta_both_equality_count"],
            "pairs_with_any_single_equality": None,
            "pairs_with_both_single_equalities": None,
            "sign_triples": nonzero_counts(row["sign_pattern_counts"]),
        }
    return result


def normalize_completeness_author(summary: dict[str, Any]) -> dict[str, dict[str, Any]]:
    result: dict[str, dict[str, Any]] = {}
    for row in summary["input_completeness"]:
        result[str(row["n"])] = {
            "n": row["n"],
            "expected_connected_labelled_count": row["expected_connected_labelled_count"],
            "actual_connected_labelled_count": row["connected_labelled_count"],
            "expected_representative_count": row["expected_representative_count"],
            "actual_representative_count": row["representative_count"],
            "orbit_union_count": row["orbit_union_count"],
            "connected_labelled_set_sha256": row["connected_labelled_set_sha256"],
            "representative_orbit_union_sha256": row["orbit_union_sha256"],
            "representative_orbits_pairwise_disjoint": row["orbits_pairwise_disjoint"],
            "actual_sets_equal": row["sets_equal"],
            "permutation_count": row["permutation_count"],
            "orbits": sorted(
                [
                    {
                        "graph6": orbit["graph6"],
                        "source_line": orbit["source_line"],
                        "orbit_size": orbit["orbit_size"],
                    }
                    for orbit in row["orbits"]
                ],
                key=lambda value: value["source_line"],
            ),
        }
    return result


def normalize_completeness_independent(completeness: dict[str, Any]) -> dict[str, dict[str, Any]]:
    result: dict[str, dict[str, Any]] = {}
    for row in completeness["orders"]:
        result[str(row["n"])] = {
            "n": row["n"],
            "expected_connected_labelled_count": row["expected_connected_labelled_count"],
            "actual_connected_labelled_count": row["actual_connected_labelled_count"],
            "expected_representative_count": row["expected_representative_count"],
            "actual_representative_count": row["actual_representative_count"],
            "orbit_union_count": row["orbit_union_count"],
            "connected_labelled_set_sha256": row["connected_labelled_set_sha256"],
            "representative_orbit_union_sha256": row[
                "representative_orbit_union_sha256"
            ],
            "representative_orbits_pairwise_disjoint": row[
                "representative_orbits_pairwise_disjoint"
            ],
            "actual_sets_equal": row["actual_sets_equal"],
            "permutation_count": math.factorial(row["n"]),
            "orbits": sorted(
                [
                    {
                        "graph6": orbit["graph6"],
                        "source_line": orbit["source_line"],
                        "orbit_size": orbit["orbit_size"],
                    }
                    for orbit in row["representatives"]
                ],
                key=lambda value: value["source_line"],
            ),
        }
    return result


def shared_input_hashes(freeze: dict[str, Any], origin: str) -> dict[str, str]:
    records = freeze["frozen_files"] if origin == "author" else freeze["files"]
    wanted = {
        "contract-v1.md",
        "contract-freeze.json",
        "source-method-assessment.json",
        "source-manifest.json",
        "graph2c.g6",
        "graph3c.g6",
        "graph4c.g6",
        "graph5c.g6",
        "graph6c.g6",
    }
    result: dict[str, str] = {}
    for record in records:
        name = Path(record["path"]).name
        if name in wanted:
            result[name] = record["sha256"]
    return result


def main() -> int:
    args = parse_args()
    author_dir = args.author_dir.resolve()
    independent_dir = args.independent_dir.resolve()
    output_dir = args.output_dir.resolve()
    output_dir.mkdir(parents=True, exist_ok=False)

    issues: list[dict[str, Any]] = []

    author_manifest_path = author_dir / "result-manifest.json"
    author_manifest_sha256 = sha256_file(author_manifest_path)
    author_manifest = load_json(author_manifest_path)
    author_artifact_verification = verify_records(author_dir, author_manifest["artifacts"])

    independent_output_seal_path = independent_dir / "independent-output-seal.json"
    independent_output_seal_sha256 = sha256_file(independent_output_seal_path)
    independent_output_seal = load_json(independent_output_seal_path)
    independent_output_verification = verify_records(
        independent_dir,
        independent_output_seal["deterministic_outputs"]
        + independent_output_seal["command_logs"],
    )

    independent_input_manifest_path = independent_dir / "input-freeze-manifest.json"
    independent_input_manifest_sha256 = sha256_file(independent_input_manifest_path)
    independent_input_manifest = load_json(independent_input_manifest_path)
    independent_input_verification = verify_absolute_records(independent_input_manifest["files"])
    independent_input_seal_path = independent_dir / "input-freeze-seal.json"
    independent_input_seal_sha256 = sha256_file(independent_input_seal_path)

    author_run = author_dir / "run-01"
    independent_run = independent_dir / "run-01"
    author_summary = load_json(author_run / "summary.json")
    independent_summary = load_json(independent_run / "summary.json")
    author_graph_file = load_json(author_run / "graph-values.json")
    independent_graph_file = load_json(independent_run / "graph-values.json")
    author_pair_raw = load_jsonl(author_run / "pairs.jsonl")
    independent_pair_raw = load_jsonl(independent_run / "pairs.jsonl")
    author_witness_file = load_json(author_run / "witnesses.json")
    independent_witness_file = load_json(independent_run / "witnesses.json")
    author_p7_file = load_json(author_run / "published-p7.json")
    independent_p7_file = load_json(independent_run / "published-p7.json")
    independent_completeness_file = load_json(independent_run / "completeness.json")

    author_graphs, author_graph_method = normalize_graph_records(
        author_graph_file["values"], "author", issues
    )
    independent_graphs, independent_graph_method = normalize_graph_records(
        independent_graph_file["states"], "independent", issues
    )
    graph_comparison = compare_maps(
        author_graphs, independent_graphs, "every cached labelled graph state"
    )

    author_pairs, author_pair_order = normalize_pair_records(
        author_pair_raw, "author", issues, check_sequence=True
    )
    independent_pairs, independent_pair_order = normalize_pair_records(
        independent_pair_raw, "independent", issues, check_sequence=True
    )
    pair_comparison = compare_maps(
        author_pairs,
        independent_pairs,
        "every marked source graph and unordered distinct nonedge pair",
    )
    pair_comparison["line_order_match"] = author_pair_order == independent_pair_order
    pair_comparison["author_line_order_sha256"] = canonical_sha256(author_pair_order)
    pair_comparison["independent_line_order_sha256"] = canonical_sha256(
        independent_pair_order
    )
    pair_comparison["pass"] = pair_comparison["pass"] and pair_comparison[
        "line_order_match"
    ]

    author_pair_references = validate_pair_state_references(
        author_pairs, author_graphs, "author", issues
    )
    independent_pair_references = validate_pair_state_references(
        independent_pairs, independent_graphs, "independent", issues
    )

    author_aggregated_pairs = aggregate_pair_records(author_pairs)
    independent_aggregated_pairs = aggregate_pair_records(independent_pairs)
    author_per_graph = normalize_per_graph_author(author_summary)
    independent_per_graph = normalize_per_graph_independent(
        independent_completeness_file, independent_aggregated_pairs
    )
    per_graph_comparison = compare_maps(
        author_per_graph,
        independent_per_graph,
        "all 142 source representatives including zero-pair rows",
    )
    author_per_graph_vs_ledger = compare_maps(
        {
            key: {
                field: value[field]
                for field in (
                    "pair_count",
                    "witness_count",
                    "single_equality_occurrences",
                    "single_f_equality_occurrences",
                    "joint_equality_occurrences",
                    "pairs_with_any_single_equality",
                    "pairs_with_both_single_equalities",
                    "sign_triples",
                )
            }
            for key, value in author_per_graph.items()
            if value["pair_count"] > 0
        },
        author_aggregated_pairs,
        "author per-graph aggregates versus author pair ledger",
    )

    author_per_order = normalize_per_order_author(author_summary)
    independent_per_order = normalize_per_order_independent(independent_summary)
    for key, value in independent_per_order.items():
        stats = pair_stats_for_order(independent_pairs, value["n"])
        value["pairs_with_any_single_equality"] = stats[
            "pairs_with_any_single_equality"
        ]
        value["pairs_with_both_single_equalities"] = stats[
            "pairs_with_both_single_equalities"
        ]
    per_order_comparison = compare_maps(
        author_per_order, independent_per_order, "per-order pair census aggregates"
    )

    author_completeness = normalize_completeness_author(author_summary)
    independent_completeness = normalize_completeness_independent(
        independent_completeness_file
    )
    completeness_comparison = compare_maps(
        author_completeness,
        independent_completeness,
        "per-order labelled connected-set and representative-orbit coverage",
    )
    completeness_internal = {
        "all_author_set_hashes_equal": all(
            row["connected_labelled_set_sha256"]
            == row["representative_orbit_union_sha256"]
            for row in author_completeness.values()
        ),
        "all_independent_set_hashes_equal": all(
            row["connected_labelled_set_sha256"]
            == row["representative_orbit_union_sha256"]
            for row in independent_completeness.values()
        ),
        "all_author_sets_equal_flags_true": all(
            row["actual_sets_equal"]
            and row["representative_orbits_pairwise_disjoint"]
            for row in author_completeness.values()
        ),
        "all_independent_sets_equal_flags_true": all(
            row["actual_sets_equal"]
            and row["representative_orbits_pairwise_disjoint"]
            for row in independent_completeness.values()
        ),
        "independent_no_coverage_missing_or_extra": all(
            row["coverage_missing_count"] == 0 and row["coverage_extra_count"] == 0
            for row in independent_completeness_file["orders"]
        ),
    }
    completeness_internal["pass"] = all(completeness_internal.values())

    author_witnesses, _ = normalize_pair_records(
        author_witness_file["witnesses"], "author", issues
    )
    independent_witnesses, _ = normalize_pair_records(
        independent_witness_file["witnesses"], "independent", issues
    )
    witness_comparison = compare_maps(
        author_witnesses, independent_witnesses, "all qualifying witness records"
    )
    author_qualifying = {
        key: value for key, value in author_pairs.items() if value["classification"]["qualifies"]
    }
    independent_qualifying = {
        key: value
        for key, value in independent_pairs.items()
        if value["classification"]["qualifies"]
    }
    author_witness_vs_ledger = compare_maps(
        author_witnesses, author_qualifying, "author witness file versus pair ledger"
    )
    independent_witness_vs_ledger = compare_maps(
        independent_witnesses,
        independent_qualifying,
        "independent witness file versus pair ledger",
    )

    author_p7_core = semantic_pair_core_author(author_p7_file, "author.p7", issues)
    independent_p7_core = semantic_pair_core_independent(
        independent_p7_file["pair"], "independent.p7", issues
    )
    p7_math_match = author_p7_core == independent_p7_core
    p7_source = {
        "author_url": author_p7_file["source"]["url"],
        "independent_url": independent_p7_file["source"]["url"],
        "author_locator": author_p7_file["source"]["locator"],
        "independent_locator": independent_p7_file["source"]["locator"],
        "title_match": author_p7_file["source"]["title"]
        == independent_p7_file["source"]["title"],
        "same_arxiv_identifier": "2108.01061" in author_p7_file["source"]["url"]
        and "2108.01061" in independent_p7_file["source"]["url"],
        "same_locator_target": "Corollary 4.3" in author_p7_file["source"]["locator"]
        and "Corollary 4.3" in independent_p7_file["source"]["locator"],
    }
    p7_comparison = {
        "math_and_classification_match": p7_math_match,
        "author_normalized_sha256": canonical_sha256(author_p7_core),
        "independent_normalized_sha256": canonical_sha256(independent_p7_core),
        "source": p7_source,
        "pass": p7_math_match
        and all(
            p7_source[key]
            for key in ("title_match", "same_arxiv_identifier", "same_locator_target")
        ),
    }

    author_input_freeze = load_json(author_dir / "input-freeze.json")
    independent_input_freeze = independent_input_manifest
    author_shared_inputs = shared_input_hashes(author_input_freeze, "author")
    independent_shared_inputs = shared_input_hashes(independent_input_freeze, "independent")
    shared_input_comparison = compare_maps(
        author_shared_inputs,
        independent_shared_inputs,
        "shared frozen contract, source review, source manifest, and graph6 inputs",
    )

    author_aggregate = {
        "candidate_minimum_order": author_summary["candidate_minimum_order"],
        "witness_count_through_order_6": author_summary["census"][
            "witness_count_through_order_6"
        ],
        "pair_count": author_summary["census"]["pair_count"],
        "representative_count": author_summary["census"]["representative_count"],
        "graph_state_count_including_p7": author_summary["census"][
            "graph_state_count_including_p7_control"
        ],
        "connected_labelled_count": sum(
            row["connected_labelled_count"] for row in author_summary["input_completeness"]
        ),
        "lower_order_witness_counts": {
            str(n): next(row for row in author_summary["census"]["per_order"] if row["n"] == n)[
                "witness_count"
            ]
            for n in range(2, 6)
        },
    }
    independent_aggregate = {
        "candidate_minimum_order": independent_summary["minimum_order_result"][
            "candidate_minimum_order"
        ],
        "witness_count_through_order_6": independent_summary["totals"]["witness_count"],
        "pair_count": independent_summary["totals"]["candidate_pair_count"],
        "representative_count": independent_summary["totals"]["source_graph_count"],
        "graph_state_count_including_p7": independent_summary["totals"][
            "graph_state_value_count_including_p7_states"
        ],
        "connected_labelled_count": independent_completeness_file["totals"][
            "connected_labelled_count"
        ],
        "lower_order_witness_counts": {
            str(row["n"]): row["witness_count"]
            for row in independent_summary["orders"]
            if row["n"] < 6
        },
    }
    aggregate_comparison = compare_maps(
        {"aggregate": author_aggregate},
        {"aggregate": independent_aggregate},
        "headline counts and candidate minimum",
    )

    manifest_integrity_pass = (
        author_manifest_sha256 == EXPECTED_AUTHOR_MANIFEST_SHA256
        and author_artifact_verification["all_match"]
        and independent_output_seal_sha256 == EXPECTED_INDEPENDENT_OUTPUT_SEAL_SHA256
        and independent_output_verification["all_match"]
        and independent_input_manifest_sha256
        == EXPECTED_INDEPENDENT_INPUT_MANIFEST_SHA256
        and independent_input_seal_sha256 == EXPECTED_INDEPENDENT_INPUT_SEAL_SHA256
        and independent_input_verification["all_match"]
        and shared_input_comparison["pass"]
    )
    graph_pass = graph_comparison["pass"] and author_graph_method["pass"] and independent_graph_method["pass"]
    pair_pass = (
        pair_comparison["pass"]
        and per_graph_comparison["pass"]
        and author_per_graph_vs_ledger["pass"]
        and per_order_comparison["pass"]
        and witness_comparison["pass"]
        and author_witness_vs_ledger["pass"]
        and independent_witness_vs_ledger["pass"]
    )
    completeness_pass = completeness_comparison["pass"] and completeness_internal["pass"]
    headline_pass = aggregate_comparison["pass"] and p7_comparison["pass"]
    integrity_pass = len(issues) == 0
    all_pass = (
        manifest_integrity_pass
        and graph_pass
        and pair_pass
        and completeness_pass
        and headline_pass
        and integrity_pass
    )

    report = {
        "schema_version": "kemeny-independent-cross-evaluator-comparison-v1",
        "status": (
            "pass_exact_cross_evaluator_agreement_pending_final_independent_review"
            if all_pass
            else "fail_cross_evaluator_discrepancy"
        ),
        "auditor": "/root/sol_atlas_audit",
        "scope": (
            "Exact structural comparison of the already-sealed blind independent output "
            "against the explicitly authorized sealed author output."
        ),
        "blinding_chronology": {
            "independent_output_seal_created_before_author_access": True,
            "independent_output_seal_sha256": independent_output_seal_sha256,
            "author_result_manifest_opened_only_after_parent_authorization": True,
            "author_code_read": False,
        },
        "baseline_integrity": {
            "author_result_manifest": {
                "path": normalized_path(author_manifest_path),
                "expected_sha256": EXPECTED_AUTHOR_MANIFEST_SHA256,
                "actual_sha256": author_manifest_sha256,
                "match": author_manifest_sha256 == EXPECTED_AUTHOR_MANIFEST_SHA256,
            },
            "author_artifacts": author_artifact_verification,
            "independent_output_seal": {
                "path": normalized_path(independent_output_seal_path),
                "expected_sha256": EXPECTED_INDEPENDENT_OUTPUT_SEAL_SHA256,
                "actual_sha256": independent_output_seal_sha256,
                "match": independent_output_seal_sha256
                == EXPECTED_INDEPENDENT_OUTPUT_SEAL_SHA256,
            },
            "independent_sealed_outputs_and_logs": independent_output_verification,
            "independent_input_manifest": {
                "path": normalized_path(independent_input_manifest_path),
                "expected_sha256": EXPECTED_INDEPENDENT_INPUT_MANIFEST_SHA256,
                "actual_sha256": independent_input_manifest_sha256,
                "match": independent_input_manifest_sha256
                == EXPECTED_INDEPENDENT_INPUT_MANIFEST_SHA256,
            },
            "independent_input_seal": {
                "path": normalized_path(independent_input_seal_path),
                "expected_sha256": EXPECTED_INDEPENDENT_INPUT_SEAL_SHA256,
                "actual_sha256": independent_input_seal_sha256,
                "match": independent_input_seal_sha256
                == EXPECTED_INDEPENDENT_INPUT_SEAL_SHA256,
            },
            "independent_frozen_input_files": independent_input_verification,
            "shared_input_hash_comparison": shared_input_comparison,
            "pass": manifest_integrity_pass,
        },
        "graph_state_comparison": graph_comparison,
        "graph_method_self_checks": {
            "author": author_graph_method,
            "independent": independent_graph_method,
            "pair_state_references": {
                "author": author_pair_references,
                "independent": independent_pair_references,
            },
            "pass": graph_pass,
        },
        "pair_comparison": pair_comparison,
        "per_graph_comparison": per_graph_comparison,
        "author_per_graph_summary_vs_ledger": author_per_graph_vs_ledger,
        "per_order_comparison": per_order_comparison,
        "witness_comparison": witness_comparison,
        "author_witness_file_vs_ledger": author_witness_vs_ledger,
        "independent_witness_file_vs_ledger": independent_witness_vs_ledger,
        "completeness_comparison": completeness_comparison,
        "completeness_internal_checks": completeness_internal,
        "published_p7_comparison": p7_comparison,
        "aggregate_comparison": aggregate_comparison,
        "stored_output_integrity_issues": issues,
        "checks": [
            {
                "id": "baseline_integrity",
                "status": "pass" if manifest_integrity_pass else "fail",
                "note": "All authorized author-manifest and pre-author independent-seal bytes and hashes match.",
            },
            {
                "id": "exact_graph_state_values",
                "status": "pass" if graph_pass and integrity_pass else "fail",
                "note": "Every labelled graph-state structure and exact rational K value is compared across evaluators.",
            },
            {
                "id": "exact_pair_ledger",
                "status": "pass" if pair_pass and integrity_pass else "fail",
                "note": "Every pair, exact delta, sign, equality flag, classification, witness, and zero-pair source row is checked.",
            },
            {
                "id": "completeness_and_headlines",
                "status": "pass"
                if completeness_pass and headline_pass and integrity_pass
                else "fail",
                "note": "Connected-labelled/orbit set hashes, counts, P7 replay, aggregates, and the candidate minimum agree.",
            },
        ],
        "result": {
            "all_checks_pass": all_pass,
            "candidate_minimum_order": independent_aggregate["candidate_minimum_order"],
            "qualifying_witness_count_through_order_6": independent_aggregate[
                "witness_count_through_order_6"
            ],
            "pair_count": independent_aggregate["pair_count"],
            "graph_state_count_including_p7": independent_aggregate[
                "graph_state_count_including_p7"
            ],
        },
        "limitations": [
            "This is a cross-evaluator comparison, not the final semantic evidence gate; the designated final reviewer remains pending.",
            "The order-6 result is a candidate minimum within the frozen n=2..6 census and fixed P7 control.",
            "No publication-level novelty, performance, or broader graph-class claim is made.",
            "The author implementation source was not needed and was not read for this comparison.",
        ],
    }

    output_path = output_dir / "comparison.json"
    output_path.write_bytes(canonical_bytes(report))
    print(
        json.dumps(
            {
                "status": report["status"],
                "all_checks_pass": all_pass,
                "graph_states": len(independent_graphs),
                "pairs": len(independent_pairs),
                "witnesses": len(independent_witnesses),
                "issues": len(issues),
                "output": normalized_path(output_path),
                "output_sha256": sha256_file(output_path),
            },
            sort_keys=True,
            separators=(",", ":"),
        )
    )
    return 0 if all_pass else 1


if __name__ == "__main__":
    raise SystemExit(main())
