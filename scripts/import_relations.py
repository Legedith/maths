from __future__ import annotations

import argparse
import csv
import hashlib
import json
import re
import sys
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any, Iterable


SCHEMA_VERSION = "1.0"
MATHGLOSS_COMMIT = "b8f659605486f80f2816515f525af2c395c711fa"
MATHGLOSS_REPOSITORY = "https://github.com/MathGloss/MathGloss"
GRAPH_HEADER = (
    "source_id",
    "source_label",
    "property_id",
    "property_label",
    "target_id",
    "target_label",
)
CATALOG_HEADER = (
    "Wikidata ID",
    "Wikidata Label",
    "BCT Name",
    "BCT Link",
    "Chicago Name",
    "Chicago Link",
    "Clowder Name",
    "Clowder Link",
    "Context Name",
    "Context Link",
    "Mathlib Name",
    "Mathlib Link",
    "nLab Name",
    "nLab Link",
    "PlanetMath Name",
    "PlanetMath Link",
)
QID_RE = re.compile(r"Q[1-9][0-9]*\Z")
PROPERTY_RE = re.compile(r"P([1-9][0-9]*)\Z")
DISPLAY_LABEL_IDS = ("P460", "P518", "Q9085982")
EXPECTED_INVENTORY = {
    "total_rows": 9159,
    "included_rows": 5390,
    "excluded_rows": 3769,
    "endpoint_count": 3372,
    "property_count": 81,
}
PINNED_INPUTS = {
    "relations_csv": {
        "logical_path": "data/relations/graph_edges.csv",
        "bytes": 616177,
        "sha256": "54f58f2fe3303c7caf139132cd4301b44643c735334469ebcd7f995cc7884aec",
    },
    "catalog_csv": {
        "logical_path": "data/database.csv",
        "bytes": 674640,
        "sha256": "933a72820fe7ede53a803b750a480def205677e5722ae5f9589b0d1d9bf832b2",
    },
    "probe_inputs": {
        "logical_path": "relation-source-review-work/probe/frozen-inputs.json",
        "bytes": 3358,
        "sha256": "0d651c128bc77695df9e3737956e0b8ce7dc16cd68b78e9554b12e8b7017284b",
    },
    "probe_response": {
        "logical_path": "relation-source-review-work/probe/wikidata-response.json",
        "bytes": 15595,
        "sha256": "b1c172ecdb9784ab3412431517740c1e7c9505d3f52d180a9f2870dad5878655",
    },
    "probe_command_log": {
        "logical_path": "relation-source-review-work/probe/command-log.json",
        "bytes": 3820,
        "sha256": "5df43553b450c713a1866f4cbabce8fdc66471cfa2874f5feba76c3684a879d0",
    },
    "semantics_response": {
        "logical_path": "relation-source-review-work/semantics/wikidata-semantics-response.json",
        "bytes": 47391,
        "sha256": "3db472c2cf98ff6f867f20d56a983a4703c317d6855a40ad2e0cdc096641bec1",
    },
}


class RelationImportError(Exception):
    """A deterministic input, schema, or output precondition failure."""


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def verify_pinned_inputs(paths: dict[str, Path]) -> None:
    if set(paths) != set(PINNED_INPUTS):
        raise RelationImportError("internal input-role mismatch")
    for role, expected in PINNED_INPUTS.items():
        path = paths[role]
        if not path.is_file():
            raise RelationImportError(f"{role}: input file not found")
        size = path.stat().st_size
        if size != expected["bytes"]:
            raise RelationImportError(
                f"{role}: byte-size mismatch (expected {expected['bytes']}, got {size})"
            )
        actual_hash = sha256_file(path)
        if actual_hash != expected["sha256"]:
            raise RelationImportError(
                f"{role}: SHA256 mismatch (expected {expected['sha256']}, got {actual_hash})"
            )


def load_json_object(path: Path, role: str) -> dict[str, Any]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as error:
        raise RelationImportError(f"{role}: invalid UTF-8 JSON: {error}") from error
    if not isinstance(value, dict):
        raise RelationImportError(f"{role}: top-level JSON value must be an object")
    return value


def read_catalog_qids(path: Path) -> set[str]:
    qids: set[str] = set()
    with path.open("r", encoding="utf-8", newline="") as stream:
        reader = csv.reader(stream, strict=True)
        try:
            header = next(reader)
        except StopIteration as error:
            raise RelationImportError("catalog_csv: missing header") from error
        if tuple(header) != CATALOG_HEADER:
            raise RelationImportError("catalog_csv: unexpected header")
        for record, row in enumerate(reader, start=1):
            if len(row) != len(CATALOG_HEADER):
                raise RelationImportError(
                    f"catalog_csv: record {record} has {len(row)} fields, expected {len(CATALOG_HEADER)}"
                )
            qid = row[0]
            if QID_RE.fullmatch(qid) is None:
                raise RelationImportError(f"catalog_csv: record {record} has invalid QID")
            if qid in qids:
                raise RelationImportError(f"catalog_csv: duplicate QID at record {record}: {qid}")
            qids.add(qid)
    return qids


def property_numeric_id(property_id: str) -> int:
    match = PROPERTY_RE.fullmatch(property_id)
    if match is None:
        raise RelationImportError(f"invalid Wikidata property ID: {property_id!r}")
    return int(match.group(1))


def read_relations(
    path: Path, catalog_qids: set[str]
) -> tuple[list[dict[str, Any]], list[dict[str, Any]], list[dict[str, Any]], dict[str, int]]:
    ledger_rows: list[dict[str, Any]] = []
    edges: list[dict[str, Any]] = []
    counts: Counter[str] = Counter()
    labels: defaultdict[str, set[str]] = defaultdict(set)
    endpoints: set[str] = set()

    with path.open("r", encoding="utf-8", newline="") as stream:
        reader = csv.reader(stream, strict=True)
        try:
            header = next(reader)
        except StopIteration as error:
            raise RelationImportError("relations_csv: missing header") from error
        if tuple(header) != GRAPH_HEADER:
            raise RelationImportError("relations_csv: unexpected header")

        previous_line_end = reader.line_num
        for record, row in enumerate(reader, start=1):
            line_start = previous_line_end + 1
            line_end = reader.line_num
            previous_line_end = line_end
            if len(row) != len(GRAPH_HEADER):
                raise RelationImportError(
                    f"relations_csv: record {record} has {len(row)} fields, expected {len(GRAPH_HEADER)}"
                )
            fields = dict(zip(GRAPH_HEADER, row, strict=True))
            missing_qids = [
                qid
                for qid in (fields["source_id"], fields["target_id"])
                if qid not in catalog_qids
            ]
            included = not missing_qids
            ledger_rows.append(
                {
                    "record": record,
                    "line_start": line_start,
                    "line_end": line_end,
                    "fields": fields,
                    "included": included,
                    "missing_qids": missing_qids,
                }
            )
            if not included:
                continue

            property_id = fields["property_id"]
            property_numeric_id(property_id)
            counts[property_id] += 1
            labels[property_id].add(fields["property_label"])
            endpoints.add(fields["source_id"])
            endpoints.add(fields["target_id"])
            edges.append(
                {
                    "id": f"mathgloss-row-{record}",
                    "source": {
                        "id": fields["source_id"],
                        "label": fields["source_label"],
                    },
                    "property": {
                        "id": property_id,
                        "label": fields["property_label"],
                    },
                    "target": {
                        "id": fields["target_id"],
                        "label": fields["target_label"],
                    },
                    "record": record,
                    "line_start": line_start,
                    "line_end": line_end,
                    "review_status": "unreviewed_external_assertion",
                    "legacy_statement_metadata": "not_retrieved",
                }
            )

    properties: list[dict[str, Any]] = []
    for property_id in sorted(counts, key=property_numeric_id):
        observed_labels = labels[property_id]
        if len(observed_labels) != 1:
            raise RelationImportError(
                f"relations_csv: property {property_id} has multiple labels: {sorted(observed_labels)!r}"
            )
        properties.append(
            {
                "id": property_id,
                "label": next(iter(observed_labels)),
                "count": counts[property_id],
            }
        )

    summary = {
        "total_rows": len(ledger_rows),
        "included_rows": len(edges),
        "excluded_rows": len(ledger_rows) - len(edges),
        "endpoint_count": len(endpoints),
        "property_count": len(properties),
    }
    for name, expected in EXPECTED_INVENTORY.items():
        actual = summary[name]
        if actual != expected:
            raise RelationImportError(
                f"inventory mismatch for {name}: expected {expected}, got {actual}"
            )
    return ledger_rows, edges, properties, summary


def require_string(value: Any, context: str) -> str:
    if not isinstance(value, str) or not value:
        raise RelationImportError(f"{context}: expected nonempty string")
    return value


def extract_display_labels(semantics_response: dict[str, Any]) -> dict[str, str]:
    entities = semantics_response.get("entities")
    if not isinstance(entities, dict):
        raise RelationImportError("semantics_response: entities must be an object")
    result: dict[str, str] = {}
    for entity_id in DISPLAY_LABEL_IDS:
        entity = entities.get(entity_id)
        if not isinstance(entity, dict):
            result[entity_id] = entity_id
            continue
        labels = entity.get("labels")
        label = labels.get("en") if isinstance(labels, dict) else None
        value = label.get("value") if isinstance(label, dict) else None
        result[entity_id] = value if isinstance(value, str) and value else entity_id
    return result


def statement_matches(statement: Any, property_id: str, target_id: str) -> bool:
    if not isinstance(statement, dict):
        return False
    mainsnak = statement.get("mainsnak")
    if not isinstance(mainsnak, dict):
        return False
    if mainsnak.get("property") != property_id or mainsnak.get("snaktype") != "value":
        return False
    datavalue = mainsnak.get("datavalue")
    if not isinstance(datavalue, dict) or datavalue.get("type") != "wikibase-entityid":
        return False
    value = datavalue.get("value")
    return isinstance(value, dict) and value.get("id") == target_id


def build_observations(
    probe_inputs: dict[str, Any],
    probe_response: dict[str, Any],
    probe_command_log: dict[str, Any],
    semantics_response: dict[str, Any],
    ledger_rows: list[dict[str, Any]],
) -> dict[str, Any]:
    selected_rows = probe_inputs.get("selected_rows")
    if not isinstance(selected_rows, list) or len(selected_rows) != 3:
        raise RelationImportError("probe_inputs: expected exactly three selected_rows")

    events = probe_command_log.get("events")
    if not isinstance(events, list):
        raise RelationImportError("probe_command_log: events must be an array")
    request_events = [
        event
        for event in events
        if isinstance(event, dict)
        and event.get("operation") == "one batched primary API request"
        and event.get("result", "success") == "success"
    ]
    if len(request_events) != 1:
        raise RelationImportError("probe_command_log: expected one successful request event")
    request_event = request_events[0]
    requested_url = require_string(request_event.get("requested_url"), "probe requested_url")
    retrieved_at_utc = require_string(request_event.get("ended_at_utc"), "probe ended_at_utc")
    frozen_request = probe_inputs.get("request")
    if not isinstance(frozen_request, dict) or frozen_request.get("url") != requested_url:
        raise RelationImportError("probe request URL disagrees with frozen inputs")

    entities = probe_response.get("entities")
    if not isinstance(entities, dict):
        raise RelationImportError("probe_response: entities must be an object")
    display_labels = extract_display_labels(semantics_response)
    ledger_by_record = {row["record"]: row for row in ledger_rows}
    observations: dict[str, Any] = {}

    for selected in selected_rows:
        if not isinstance(selected, dict):
            raise RelationImportError("probe_inputs: selected row must be an object")
        record = selected.get("logical_data_record_1_based")
        fields = selected.get("fields")
        if not isinstance(record, int) or isinstance(record, bool) or not isinstance(fields, dict):
            raise RelationImportError("probe_inputs: invalid selected row record or fields")
        ledger_row = ledger_by_record.get(record)
        if ledger_row is None or ledger_row["fields"] != fields:
            raise RelationImportError(f"probe_inputs: record {record} does not match relation CSV")
        if not ledger_row["included"]:
            raise RelationImportError(f"probe_inputs: record {record} is excluded by catalog join")
        expected_lines = [ledger_row["line_start"], ledger_row["line_end"]]
        frozen_lines = [
            selected.get("physical_line_start_1_based"),
            selected.get("physical_line_end_1_based"),
        ]
        if frozen_lines != expected_lines:
            raise RelationImportError(f"probe_inputs: record {record} physical locator mismatch")

        source_id = require_string(fields.get("source_id"), "probe source_id")
        property_id = require_string(fields.get("property_id"), "probe property_id")
        target_id = require_string(fields.get("target_id"), "probe target_id")
        if selected.get("property_id") != property_id:
            raise RelationImportError(f"probe_inputs: record {record} property mismatch")
        entity = entities.get(source_id)
        if not isinstance(entity, dict) or entity.get("missing") is not None:
            raise RelationImportError(f"probe_response: source entity absent: {source_id}")
        lastrevid = entity.get("lastrevid")
        modified = entity.get("modified")
        if not isinstance(lastrevid, int) or isinstance(lastrevid, bool):
            raise RelationImportError(f"probe_response: invalid lastrevid for {source_id}")
        modified = require_string(modified, f"probe_response modified for {source_id}")
        claims = entity.get("claims")
        property_statements = claims.get(property_id) if isinstance(claims, dict) else None
        if not isinstance(property_statements, list):
            raise RelationImportError(f"probe_response: no statement array for {source_id} {property_id}")
        matching_statements = [
            statement
            for statement in property_statements
            if statement_matches(statement, property_id, target_id)
        ]
        if len(matching_statements) != 1:
            raise RelationImportError(
                f"probe_response: expected one match for {source_id} {property_id} {target_id}, got {len(matching_statements)}"
            )
        field_presence = [
            {
                "statement_id": "id" in statement,
                "qualifiers": "qualifiers" in statement,
                "references": "references" in statement,
            }
            for statement in matching_statements
        ]
        edge_id = f"mathgloss-row-{record}"
        observations[edge_id] = {
            "requested_url": requested_url,
            "retrieved_at_utc": retrieved_at_utc,
            "raw_response_sha256": PINNED_INPUTS["probe_response"]["sha256"],
            "source_entity": {
                "id": source_id,
                "lastrevid": lastrevid,
                "modified": modified,
            },
            "triple": {
                "source_id": source_id,
                "property_id": property_id,
                "target_id": target_id,
            },
            "matching_statements": matching_statements,
            "field_presence": field_presence,
            "display_labels": display_labels,
        }
    return observations


def source_metadata() -> dict[str, Any]:
    return {
        "project": "MathGloss",
        "repository": MATHGLOSS_REPOSITORY,
        "commit": MATHGLOSS_COMMIT,
        "inputs": {
            role: {
                "path": details["logical_path"],
                "bytes": details["bytes"],
                "sha256": details["sha256"],
            }
            for role, details in PINNED_INPUTS.items()
        },
        "attribution": {
            "mathgloss": {
                "license": "MIT",
                "notice": "Copyright (c) GitHub, Inc.",
                "license_url": f"{MATHGLOSS_REPOSITORY}/blob/{MATHGLOSS_COMMIT}/LICENSE",
            },
            "wikidata_structured_data": {
                "license": "CC0 1.0",
                "license_url": "https://creativecommons.org/publicdomain/zero/1.0/",
                "source_url": "https://www.wikidata.org/",
            },
        },
    }


def deterministic_json_bytes(value: Any) -> bytes:
    text = json.dumps(
        value,
        ensure_ascii=False,
        allow_nan=False,
        sort_keys=True,
        separators=(",", ":"),
    )
    return (text + "\n").encode("utf-8")


def check_output_directory(output_dir: Path) -> None:
    if output_dir.exists():
        if not output_dir.is_dir():
            raise RelationImportError("output-dir exists and is not a directory")
        if any(output_dir.iterdir()):
            raise RelationImportError("output-dir exists and is nonempty")


def write_outputs(
    output_dir: Path,
    ledger_rows: list[dict[str, Any]],
    edges: list[dict[str, Any]],
    properties: list[dict[str, Any]],
    summary: dict[str, int],
    observations: dict[str, Any],
) -> dict[str, dict[str, Any]]:
    source = source_metadata()
    index = {
        "schema_version": SCHEMA_VERSION,
        "source": source,
        "summary": summary,
        "properties": properties,
        "edges": edges,
        "observations": observations,
    }
    ledger = {
        "schema_version": SCHEMA_VERSION,
        "source": source,
        "rows": ledger_rows,
    }
    index_bytes = deterministic_json_bytes(index)
    ledger_bytes = deterministic_json_bytes(ledger)
    output_file_hashes = {
        "relation-index.json": sha256_bytes(index_bytes),
        "relation-ledger.json": sha256_bytes(ledger_bytes),
    }
    relation_summary = {
        "schema_version": SCHEMA_VERSION,
        "source": source,
        "summary": summary,
        "properties": properties,
        "output_file_hashes": output_file_hashes,
    }
    summary_bytes = deterministic_json_bytes(relation_summary)

    output_dir.mkdir(parents=True, exist_ok=True)
    payloads = {
        "relation-index.json": index_bytes,
        "relation-ledger.json": ledger_bytes,
        "relation-summary.json": summary_bytes,
    }
    for name, payload in payloads.items():
        (output_dir / name).write_bytes(payload)
    return {
        name: {"bytes": len(payload), "sha256": sha256_bytes(payload)}
        for name, payload in payloads.items()
    }


def run_import(args: argparse.Namespace) -> dict[str, Any]:
    input_paths = {
        "relations_csv": Path(args.relations_csv),
        "catalog_csv": Path(args.catalog_csv),
        "probe_inputs": Path(args.probe_inputs),
        "probe_response": Path(args.probe_response),
        "probe_command_log": Path(args.probe_command_log),
        "semantics_response": Path(args.semantics_response),
    }
    output_dir = Path(args.output_dir)
    verify_pinned_inputs(input_paths)
    check_output_directory(output_dir)

    catalog_qids = read_catalog_qids(input_paths["catalog_csv"])
    ledger_rows, edges, properties, summary = read_relations(
        input_paths["relations_csv"], catalog_qids
    )
    observations = build_observations(
        load_json_object(input_paths["probe_inputs"], "probe_inputs"),
        load_json_object(input_paths["probe_response"], "probe_response"),
        load_json_object(input_paths["probe_command_log"], "probe_command_log"),
        load_json_object(input_paths["semantics_response"], "semantics_response"),
        ledger_rows,
    )
    if len(observations) != 3:
        raise RelationImportError(
            f"observation count mismatch: expected 3, got {len(observations)}"
        )
    output_files = write_outputs(
        output_dir, ledger_rows, edges, properties, summary, observations
    )
    return {
        "status": "success",
        "inventory_checks": {
            name: {
                "expected": expected,
                "actual": summary[name],
                "passed": summary[name] == expected,
            }
            for name, expected in EXPECTED_INVENTORY.items()
        },
        "observation_check": {
            "expected": 3,
            "actual": len(observations),
            "passed": len(observations) == 3,
        },
        "output_files": output_files,
    }


def parse_args(argv: Iterable[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Import the pinned MathGloss relation CSV into deterministic JSON."
    )
    parser.add_argument("--relations-csv", required=True)
    parser.add_argument("--catalog-csv", required=True)
    parser.add_argument("--probe-inputs", required=True)
    parser.add_argument("--probe-response", required=True)
    parser.add_argument("--probe-command-log", required=True)
    parser.add_argument("--semantics-response", required=True)
    parser.add_argument("--output-dir", required=True)
    return parser.parse_args(argv)


def main(argv: Iterable[str] | None = None) -> int:
    args = parse_args(argv)
    try:
        report = run_import(args)
    except RelationImportError as error:
        print(f"error: {error}", file=sys.stderr)
        return 2
    print(json.dumps(report, ensure_ascii=False, sort_keys=True, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
