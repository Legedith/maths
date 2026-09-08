from __future__ import annotations

import argparse
import hashlib
import json
from collections import Counter
from datetime import datetime, timezone
from fractions import Fraction
from pathlib import Path
from typing import Any

EXPECTED_PLAINTEXT_SHA256 = "ddf50219b87547a9cae547d936a7afba76380f11c4cda7c5fbb473635a01d9ee"
EXPECTED_ALGORITHM_VERSION = "atlas-checks/1.0.2"


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def sha256_file(path: Path) -> str:
    return sha256_bytes(path.read_bytes())


def load_suite(cases_path: Path, oracle_path: Path) -> dict[str, Any]:
    cases_document = json.loads(cases_path.read_text(encoding="utf-8"))
    oracle_document = json.loads(oracle_path.read_text(encoding="utf-8"))
    oracle_by_id = {record["case_id"]: record["gold"] for record in oracle_document["records"]}
    case_ids = [record["case_id"] for record in cases_document["cases"]]
    if len(case_ids) != 80 or len(set(case_ids)) != 80 or set(case_ids) != set(oracle_by_id):
        raise RuntimeError("cases/oracle do not contain the same 80 unique IDs")
    return {
        "suite_id": cases_document["suite_id"],
        "cases": [{**record, "gold": oracle_by_id[record["case_id"]]} for record in cases_document["cases"]],
    }


def actual_error_tokens(actual: dict[str, Any]) -> set[str]:
    tokens: set[str] = set()
    for key in ("error_code", "error", "reason", "status"):
        value = actual.get(key)
        if isinstance(value, str):
            tokens.add(value)
    for error in actual.get("errors", []):
        if isinstance(error, dict):
            for key in ("code", "message"):
                value = error.get(key)
                if isinstance(value, str):
                    tokens.add(value)
    trace = actual.get("trace")
    if isinstance(trace, dict):
        tokens.update(actual_error_tokens(trace))
    return tokens


TYPE_ALIASES = {"vector": "rational_vector", "matrix": "rational_matrix"}
REASON_ALIASES = {
    "existing_edge_and_connected_required": {"terminal_nonedge", "disconnected_graph"},
    "zero_degree_vertex": {"isolated_vertex"},
    "period_requires_connected": {"disconnected_graph"},
    "interpretation_not_explicit": {
        "ambiguous_interpretation",
        "unsupported_interpretation",
        "provenance interpretation is ambiguous",
        "provenance interpretation is unsupported",
    },
}
ERROR_ALIASES = {
    "boolean_integer": {"invalid_n"},
    "floating_conductance": {"wrong_type"},
    "nonpositive_conductance": {"invalid_conductance"},
    "loop_edge": {"self_loop"},
    "duplicate_undirected_edge": {"duplicate_edge"},
    "edge_endpoint_out_of_range": {"invalid_vertex"},
    "terminal_out_of_range": {"invalid_terminal"},
    "terminals_not_distinct": {"invalid_terminal"},
    "unsupported_graph_property": {"unsupported_field"},
    "missing_required_field": {"missing_field"},
    "malformed_rational": {"invalid_rational"},
    "unknown_operator": {"unsupported_operator"},
    "ast_total_node_limit": {"ast_node_limit"},
}


def rational_semantic(value: Any) -> Any:
    if isinstance(value, str):
        try:
            return Fraction(value)
        except (ValueError, ZeroDivisionError):
            return value
    if isinstance(value, list):
        return [rational_semantic(item) for item in value]
    return value


def compare_value(label: str, expected: dict[str, Any], actual: dict[str, Any]) -> list[str]:
    failures: list[str] = []
    if "value" in expected:
        expected_type = TYPE_ALIASES.get(str(expected.get("type")), expected.get("type"))
        if actual.get("type") != expected_type:
            failures.append(f"{label}.type expected {expected.get('type')!r}, got {actual.get('type')!r}")
        expected_value = expected.get("value")
        actual_value = actual.get("value")
        if expected_type in {"rational", "rational_vector", "rational_matrix"}:
            equal = rational_semantic(actual_value) == rational_semantic(expected_value)
        else:
            equal = actual_value == expected_value
        if not equal:
            failures.append(f"{label}.value expected {expected.get('value')!r}, got {actual.get('value')!r}")
        return failures

    if "reason" in expected:
        expected_type = expected.get("type")
        if expected_type == "undefined" and actual.get("status") not in {
            "undefined",
            "abstain",
            "not_evaluated",
        }:
            failures.append(f"{label}.status expected undefined/abstain, got {actual.get('status')!r}")
        reason = str(expected["reason"])
        tokens = actual_error_tokens(actual)
        accepted = {reason, *REASON_ALIASES.get(reason, set())}
        if not any(
            accepted_reason == token or accepted_reason in token
            for accepted_reason in accepted
            for token in tokens
        ):
            failures.append(f"{label}.reason expected {reason!r}, observed tokens {sorted(tokens)!r}")
        return failures

    failures.append(f"{label}: evaluator does not understand expected descriptor {expected!r}")
    return failures


def compare_case(case: dict[str, Any], run: dict[str, Any]) -> list[str]:
    gold = case["gold"]
    output = run.get("implementation_output")
    failures: list[str] = []
    if run.get("exception") is not None:
        return [f"implementation escaped with {run['exception']['class']}: {run['exception']['message']}"]
    if not isinstance(output, dict):
        return ["implementation output is not an object"]

    if output.get("algorithm_version") != EXPECTED_ALGORITHM_VERSION:
        failures.append(f"unexpected algorithm version {output.get('algorithm_version')!r}")

    if output.get("verdict") != gold["expected_verdict"]:
        failures.append(
            f"verdict expected {gold['expected_verdict']!r}, got {output.get('verdict')!r}"
        )

    expected_error = gold.get("expected_error_class")
    observed_codes = [
        item.get("code") for item in output.get("errors", []) if isinstance(item, dict)
    ]
    accepted_errors = {str(expected_error), *ERROR_ALIASES.get(str(expected_error), set())}
    if expected_error is not None and not accepted_errors.intersection(observed_codes):
        failures.append(
            f"error class expected {expected_error!r}, observed {observed_codes!r}"
        )
    if expected_error is None and output.get("verdict") == "invalid_input" and not observed_codes:
        failures.append("invalid_input output has no structured error code")

    expected_assumptions = gold.get("expected_assumptions", [])
    actual_assumptions = output.get("evaluated_assumptions", [])
    if expected_assumptions:
        actual_by_id = {
            item.get("id"): item for item in actual_assumptions if isinstance(item, dict)
        }
        for expected in expected_assumptions:
            actual = actual_by_id.get(expected.get("id"))
            if actual is None:
                failures.append(f"assumption {expected.get('id')!r} missing")
                continue
            descriptor = expected.get("value")
            if isinstance(descriptor, dict):
                failures.extend(compare_value(f"assumption.{expected.get('id')}", descriptor, actual))
            elif actual.get("value") != descriptor:
                failures.append(f"assumption {expected.get('id')!r} value mismatch")
    elif case["input"].get("assumptions") == [] and actual_assumptions != []:
        failures.append("expected no assumptions, but implementation returned assumption records")

    expected_claim = gold.get("expected_claim_value")
    claim_record = output.get("claim_evaluation", {})
    if output.get("verdict") == "not_applicable":
        if claim_record.get("status") != "not_evaluated":
            failures.append("claim should not be evaluated after a false assumption")
    elif output.get("verdict") == "abstain" and output.get("provenance", {}).get("interpretation") != "explicit":
        if claim_record.get("status") != "not_evaluated":
            failures.append("claim should not be evaluated after provenance abstention")
    elif isinstance(expected_claim, dict):
        failures.extend(compare_value("claim", expected_claim, claim_record))

    expected_quantities = gold.get("expected_referenced_values", {})
    actual_quantities = output.get("quantities", {})
    require_all_gold_quantities = output.get("verdict") not in {"not_applicable"} and not (
        output.get("verdict") == "abstain"
        and output.get("provenance", {}).get("interpretation") != "explicit"
    )
    missing_quantities = set(expected_quantities) - set(actual_quantities)
    extra_quantities = set(actual_quantities) - set(expected_quantities)
    # Unknown names are returned in the expression trace but are intentionally absent
    # from the cache of supported named quantities.
    if missing_quantities == {"future_unknown_quantity"}:
        if "unknown_quantity" in observed_codes:
            missing_quantities.clear()
        else:
            trace_tokens = actual_error_tokens(claim_record)
            if "unknown_quantity" in trace_tokens:
                missing_quantities.clear()
    if extra_quantities or (require_all_gold_quantities and missing_quantities):
        failures.append(
            f"referenced quantity keys expected {sorted(expected_quantities)!r}, "
            f"got {sorted(actual_quantities)!r}"
        )
    for name, expected in expected_quantities.items():
        actual = actual_quantities.get(name)
        if not isinstance(actual, dict):
            if name in missing_quantities and require_all_gold_quantities:
                failures.append(f"quantity {name!r} missing or nonobject")
            continue
        failures.extend(compare_value(f"quantity.{name}", expected, actual))

    expected_period = gold.get("expected_period_certificate")
    if isinstance(expected_period, dict):
        actual_period = output.get("certificates", {}).get("period", {})
        for key, expected in expected_period.items():
            if key == "kind" and expected == "bipartition":
                actual = actual_period.get("kind")
                equal = actual in {"bipartition", "bipartition_parity"}
            elif key == "sides":
                actual = [actual_period.get("left"), actual_period.get("right")]
                equal = actual == expected or actual[::-1] == expected
            elif key == "vertices":
                actual = actual_period.get("cycle")
                equal = actual == expected
            else:
                actual = actual_period.get(key)
                equal = actual == expected
            if not equal:
                failures.append(
                    f"period_certificate.{key} expected {expected!r}, got {actual!r}"
                )

    if output.get("verdict") == "no_counterexample_in_instance" and not output.get(
        "instance_scope_warning"
    ):
        failures.append("missing instance-scope warning")

    normalized = output.get("normalized_input")
    normalized_hash = output.get("normalized_input_sha256")
    if normalized is not None:
        encoded = json.dumps(
            normalized, sort_keys=True, separators=(",", ":"), ensure_ascii=True
        ).encode("utf-8")
        if sha256_bytes(encoded) != normalized_hash:
            failures.append("normalized_input_sha256 does not match normalized_input")

    return failures


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--cases", type=Path, required=True)
    parser.add_argument("--oracle", type=Path, required=True)
    parser.add_argument("--run-jsonl", type=Path, required=True)
    parser.add_argument("--detail-output", type=Path, required=True)
    parser.add_argument("--summary-output", type=Path, required=True)
    args = parser.parse_args()
    cases_path = args.cases.resolve()
    oracle_path = args.oracle.resolve()
    run_path = args.run_jsonl.resolve()
    detail_path = args.detail_output.resolve()
    summary_path = args.summary_output.resolve()
    if detail_path.exists() or summary_path.exists():
        raise RuntimeError("refusing to overwrite held-out comparison artifacts")
    suite = load_suite(cases_path, oracle_path)
    runs = [json.loads(line) for line in run_path.read_text(encoding="utf-8").splitlines()]
    run_by_id = {record["case_id"]: record for record in runs}
    if len(runs) != 80 or len(run_by_id) != 80:
        raise RuntimeError("delta-run artifact does not contain 80 unique cases")

    records: list[dict[str, Any]] = []
    for case in suite["cases"]:
        failures = compare_case(case, run_by_id[case["case_id"]])
        records.append(
            {
                "case_id": case["case_id"],
                "partition": case["partition"],
                "pair": case["pair"],
                "theme": case["theme"],
                "passed": not failures,
                "failures": failures,
                "gold": case["gold"],
                "observed_verdict": run_by_id[case["case_id"]]["implementation_output"].get("verdict")
                if run_by_id[case["case_id"]].get("implementation_output")
                else None,
            }
        )

    mismatch_records = [record for record in records if not record["passed"]]
    partition_counts: dict[str, dict[str, int]] = {}
    for partition in sorted({record["partition"] for record in records}):
        selected = [record for record in records if record["partition"] == partition]
        partition_counts[partition] = {
            "total": len(selected),
            "passed": sum(record["passed"] for record in selected),
            "failed": sum(not record["passed"] for record in selected),
        }
    expected_verdicts = Counter(case["gold"]["expected_verdict"] for case in suite["cases"])
    observed_verdicts = Counter(record["observed_verdict"] for record in records)
    compared_at = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
    detail = {
        "schema_version": "1.0",
        "auditor": "/root/sol_atlas_audit",
        "compared_at": compared_at,
        "suite_plaintext_sha256": EXPECTED_PLAINTEXT_SHA256,
        "cases_sha256": sha256_file(cases_path),
        "oracle_sha256": sha256_file(oracle_path),
        "first_run_jsonl_sha256": sha256_file(run_path),
        "case_count": len(records),
        "pass_count": len(records) - len(mismatch_records),
        "failure_count": len(mismatch_records),
        "partition_counts": partition_counts,
        "expected_verdict_histogram": dict(sorted(expected_verdicts.items())),
        "observed_verdict_histogram": dict(sorted(observed_verdicts.items())),
        "records": records,
    }
    detail_path.parent.mkdir(parents=True, exist_ok=True)
    detail_path.write_text(
        json.dumps(detail, indent=2, sort_keys=True, ensure_ascii=False) + "\n",
        encoding="utf-8",
        newline="\n",
    )
    public_summary = {
        key: value for key, value in detail.items() if key not in {"records", "expected_verdict_histogram"}
    }
    public_summary["mismatch_case_ids"] = [record["case_id"] for record in mismatch_records]
    public_summary["detail_path"] = str(detail_path)
    public_summary["detail_sha256"] = sha256_file(detail_path)
    summary_path.parent.mkdir(parents=True, exist_ok=True)
    summary_path.write_text(
        json.dumps(public_summary, indent=2, sort_keys=True, ensure_ascii=False) + "\n",
        encoding="utf-8",
        newline="\n",
    )
    print(json.dumps(public_summary, sort_keys=True))
    return 0 if not mismatch_records else 1


if __name__ == "__main__":
    raise SystemExit(main())

