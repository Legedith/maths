"""Public structured transfer-check API."""

from __future__ import annotations

import hashlib
import json
from typing import Any

from .expressions import Evaluation, ExpressionEvaluator
from .quantities import QuantityStore
from .validation import InputValidationError, validate_payload


ALGORITHM_VERSION = "atlas-checks/1.0.0"


def _available_provenance(payload: object) -> dict[str, Any] | None:
    if not isinstance(payload, dict) or not isinstance(payload.get("provenance"), dict):
        return None
    fields = (
        "kind",
        "source_url",
        "source_locator",
        "annotation_id",
        "annotator",
        "interpretation",
    )
    return {
        field: value if isinstance(value, str) else None
        for field in fields
        if field in payload["provenance"]
        for value in [payload["provenance"].get(field)]
    }


def _not_evaluated(path: str, reason: str) -> dict[str, Any]:
    return {
        "status": "not_evaluated",
        "trace": {"path": path, "status": "not_evaluated", "reason": reason},
    }


def _base_output(check_id: Any, provenance: Any) -> dict[str, Any]:
    return {
        "algorithm_version": ALGORITHM_VERSION,
        "id": check_id,
        "verdict": None,
        "normalized_input": None,
        "normalized_input_sha256": None,
        "provenance": provenance,
        "evaluated_assumptions": [],
        "claim_evaluation": _not_evaluated("$.claim", "input has not been validated"),
        "quantities": {},
        "certificates": {},
        "errors": [],
    }


def invalid_input_result(payload: object, error: dict[str, str]) -> dict[str, Any]:
    check_id = payload.get("id") if isinstance(payload, dict) and isinstance(payload.get("id"), str) else None
    output = _base_output(check_id, _available_provenance(payload))
    output["verdict"] = "invalid_input"
    output["errors"] = [error]
    output["claim_evaluation"] = _not_evaluated("$.claim", "structural input validation failed")
    return output


def _evaluation_record(evaluation: Evaluation) -> dict[str, Any]:
    record: dict[str, Any] = {
        "status": "defined" if evaluation.defined else "abstain",
        "trace": evaluation.trace,
    }
    if evaluation.value is not None:
        record.update(evaluation.value.record())
    if evaluation.errors:
        record["errors"] = list(evaluation.errors)
    return record


def _boolean_evaluation(
    evaluation: Evaluation,
    path: str,
) -> tuple[str, dict[str, Any], list[dict[str, str]]]:
    record = _evaluation_record(evaluation)
    errors = list(evaluation.errors)
    if evaluation.value is None:
        return "abstain", record, errors
    if evaluation.value.type != "boolean":
        error = {
            "code": "nonboolean_result",
            "path": path,
            "message": "assumptions and the final claim must evaluate to a boolean",
        }
        record["status"] = "abstain"
        record.setdefault("errors", []).append(error)
        record["trace"] = {
            **record["trace"],
            "status": "abstain",
            "errors": [*record["trace"].get("errors", []), error],
        }
        errors.append(error)
        return "abstain", record, errors
    truth = bool(evaluation.value.data)
    record["status"] = "true" if truth else "false"
    return record["status"], record, errors


def check_transfer(payload: object) -> dict[str, Any]:
    """Validate and evaluate one frozen-interface structured transfer payload."""
    try:
        checked = validate_payload(payload)
    except InputValidationError as exc:
        return invalid_input_result(payload, exc.record())

    normalized = checked.normalized()
    normalized_json = json.dumps(normalized, sort_keys=True, separators=(",", ":"), ensure_ascii=False)
    output = _base_output(checked.id, checked.provenance.normalized())
    output["normalized_input"] = normalized
    output["normalized_input_sha256"] = hashlib.sha256(normalized_json.encode("utf-8")).hexdigest()

    if checked.provenance.interpretation != "explicit":
        reason = f"provenance interpretation is {checked.provenance.interpretation}"
        output["verdict"] = "abstain"
        output["evaluated_assumptions"] = [
            {
                "id": assumption.id,
                "expression": assumption.expression,
                **_not_evaluated(f"$.assumptions[{index}].expression", reason),
            }
            for index, assumption in enumerate(checked.assumptions)
        ]
        output["claim_evaluation"] = {
            "expression": checked.claim,
            **_not_evaluated("$.claim", reason),
        }
        output["certificates"] = {
            "gauge": {"status": "not_evaluated", "reason": reason},
            "period": {"status": "not_evaluated", "reason": reason},
        }
        output["errors"] = [
            {
                "code": "ambiguous_interpretation"
                if checked.provenance.interpretation == "ambiguous"
                else "unsupported_interpretation",
                "path": "$.provenance.interpretation",
                "message": reason,
            }
        ]
        return output

    quantities = QuantityStore(checked.graph)
    evaluator = ExpressionEvaluator(quantities)
    assumption_records: list[dict[str, Any]] = []
    assumption_statuses: list[str] = []
    errors: list[dict[str, str]] = []
    for index, assumption in enumerate(checked.assumptions):
        path = f"$.assumptions[{index}].expression"
        evaluated = evaluator.evaluate(assumption.expression, path)
        status, record, new_errors = _boolean_evaluation(evaluated, path)
        assumption_statuses.append(status)
        assumption_records.append(
            {"id": assumption.id, "expression": assumption.expression, **record}
        )
        errors.extend(new_errors)
    output["evaluated_assumptions"] = assumption_records

    if "false" in assumption_statuses:
        output["verdict"] = "not_applicable"
        output["claim_evaluation"] = {
            "expression": checked.claim,
            **_not_evaluated("$.claim", "at least one recorded theorem assumption is false"),
        }
    elif "abstain" in assumption_statuses:
        output["verdict"] = "abstain"
        output["claim_evaluation"] = {
            "expression": checked.claim,
            **_not_evaluated("$.claim", "at least one recorded theorem assumption is unevaluable"),
        }
    else:
        claim_evaluation = evaluator.evaluate(checked.claim, "$.claim")
        claim_status, claim_record, claim_errors = _boolean_evaluation(claim_evaluation, "$.claim")
        output["claim_evaluation"] = {"expression": checked.claim, **claim_record}
        errors.extend(claim_errors)
        if claim_status == "abstain":
            output["verdict"] = "abstain"
        elif claim_status == "false":
            output["verdict"] = "counterexample"
        else:
            output["verdict"] = "no_counterexample_in_instance"
            output["instance_scope_warning"] = (
                "The claim holds on this instance only; this is not a universal proof or novelty decision."
            )

    output["quantities"] = quantities.accessed_records()
    output["certificates"] = quantities.certificates()
    output["errors"] = errors
    return output
