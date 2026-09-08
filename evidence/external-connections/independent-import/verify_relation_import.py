"""Independent source-derived verifier for the frozen MathGloss relation import."""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any


HASHES = {
    "relations_csv": "54f58f2fe3303c7caf139132cd4301b44643c735334469ebcd7f995cc7884aec",
    "catalog_csv": "933a72820fe7ede53a803b750a480def205677e5722ae5f9589b0d1d9bf832b2",
    "probe_inputs": "0d651c128bc77695df9e3737956e0b8ce7dc16cd68b78e9554b12e8b7017284b",
    "probe_response": "b1c172ecdb9784ab3412431517740c1e7c9505d3f52d180a9f2870dad5878655",
    "probe_command_log": "5df43553b450c713a1866f4cbabce8fdc66471cfa2874f5feba76c3684a879d0",
    "semantics_response": "3db472c2cf98ff6f867f20d56a983a4703c317d6855a40ad2e0cdc096641bec1",
}
EXPECTED = {
    "total_rows": 9159,
    "included_rows": 5390,
    "excluded_rows": 3769,
    "endpoint_count": 3372,
    "property_count": 81,
}
FIELDS = [
    "source_id",
    "source_label",
    "property_id",
    "property_label",
    "target_id",
    "target_label",
]
LABEL_IDS = ["P460", "P518", "Q9085982"]


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def canon(value: Any) -> str:
    data = json.dumps(
        value, ensure_ascii=False, sort_keys=True, separators=(",", ":")
    ).encode("utf-8")
    return hashlib.sha256(data).hexdigest()


def load(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def property_key(property_id: str) -> tuple[int, str]:
    if len(property_id) > 1 and property_id[0] == "P" and property_id[1:].isdigit():
        return int(property_id[1:]), property_id
    raise ValueError(f"invalid property ID {property_id!r}")


def derive(args: argparse.Namespace):
    paths = {key: getattr(args, key) for key in HASHES}
    hash_checks = {}
    for key, path in paths.items():
        actual = sha(path)
        hash_checks[key] = {
            "path": str(path.resolve()),
            "bytes": path.stat().st_size,
            "sha256": actual,
            "pass": actual == HASHES[key],
        }
    if not all(check["pass"] for check in hash_checks.values()):
        raise ValueError("frozen source hash mismatch")

    with args.catalog_csv.open(encoding="utf-8-sig", newline="") as stream:
        catalog = list(csv.DictReader(stream))
    qid_list = [row["Wikidata ID"] for row in catalog if row["Wikidata ID"]]
    if len(qid_list) != len(set(qid_list)):
        raise ValueError("duplicate catalogue QID")
    qids = set(qid_list)

    rows = []
    edges = []
    property_counts: Counter[str] = Counter()
    property_labels: dict[str, set[str]] = defaultdict(set)
    endpoints: set[str] = set()
    with args.relations_csv.open(encoding="utf-8-sig", newline="") as stream:
        reader = csv.DictReader(stream)
        if reader.fieldnames != FIELDS:
            raise ValueError(f"unexpected relation header {reader.fieldnames!r}")
        previous_line = 1
        for record, original in enumerate(reader, 1):
            line_end = reader.line_num
            line_start = previous_line + 1
            previous_line = line_end
            fields = {key: original[key] for key in FIELDS}
            missing = []
            for qid in (fields["source_id"], fields["target_id"]):
                if (not qid or qid not in qids) and qid not in missing:
                    missing.append(qid)
            included = not missing
            rows.append(
                {
                    "record": record,
                    "line_start": line_start,
                    "line_end": line_end,
                    "fields": fields,
                    "included": included,
                    "missing_qids": missing,
                }
            )
            if included:
                edge = {
                    "id": f"mathgloss-row-{record}",
                    "source": {
                        "id": fields["source_id"],
                        "label": fields["source_label"],
                    },
                    "property": {
                        "id": fields["property_id"],
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
                edges.append(edge)
                property_counts[fields["property_id"]] += 1
                property_labels[fields["property_id"]].add(fields["property_label"])
                endpoints.update((fields["source_id"], fields["target_id"]))

    conflicts = {
        key: sorted(value) for key, value in property_labels.items() if len(value) != 1
    }
    if conflicts:
        raise ValueError(f"property label conflicts {conflicts!r}")
    properties = [
        {
            "id": property_id,
            "label": next(iter(property_labels[property_id])),
            "count": property_counts[property_id],
        }
        for property_id in sorted(property_counts, key=property_key)
    ]
    summary = {
        "total_rows": len(rows),
        "included_rows": len(edges),
        "excluded_rows": len(rows) - len(edges),
        "endpoint_count": len(endpoints),
        "property_count": len(properties),
    }
    if summary != EXPECTED:
        raise ValueError(f"inventory mismatch {summary!r}")

    probe_inputs = load(args.probe_inputs)
    probe_response = load(args.probe_response)
    command_log = load(args.probe_command_log)
    semantics = load(args.semantics_response)
    request_events = [
        event
        for event in command_log["events"]
        if event["operation"] == "one batched primary API request"
    ]
    if (
        len(request_events) != 1
        or request_events[0]["requested_url"] != probe_inputs["request"]["url"]
    ):
        raise ValueError("request provenance mismatch")
    display_labels = {
        entity_id: semantics["entities"][entity_id]["labels"]["en"]["value"]
        for entity_id in LABEL_IDS
    }
    edge_by_record = {edge["record"]: edge for edge in edges}
    observations = {}
    observation_summaries = []
    for selected in probe_inputs["selected_rows"]:
        record = selected["logical_data_record_1_based"]
        edge = edge_by_record.get(record)
        selected_tuple = (
            selected["fields"]["source_id"],
            selected["property_id"],
            selected["fields"]["target_id"],
        )
        if edge is None or (
            edge["source"]["id"], edge["property"]["id"], edge["target"]["id"]
        ) != selected_tuple:
            raise ValueError(f"probe/CSV mismatch record {record}")
        source_qid, property_id, target_qid = selected_tuple
        entity = probe_response["entities"][source_qid]
        matches = []
        for statement in entity.get("claims", {}).get(property_id, []):
            mainsnak = statement.get("mainsnak", {})
            value = mainsnak.get("datavalue", {}).get("value")
            if (
                mainsnak.get("property") == property_id
                and isinstance(value, dict)
                and value.get("id") == target_qid
            ):
                matches.append(statement)
        if len(matches) != 1:
            raise ValueError(
                f"raw match count {source_qid}/{property_id}/{target_qid}: {len(matches)}"
            )
        field_presence = [
            {
                "statement_id": "id" in statement,
                "qualifiers": "qualifiers" in statement,
                "references": "references" in statement,
            }
            for statement in matches
        ]
        observation = {
            "requested_url": probe_inputs["request"]["url"],
            "retrieved_at_utc": request_events[0]["ended_at_utc"],
            "raw_response_sha256": HASHES["probe_response"],
            "source_entity": {
                "id": source_qid,
                "lastrevid": entity["lastrevid"],
                "modified": entity["modified"],
            },
            "triple": {
                "source_id": source_qid,
                "property_id": property_id,
                "target_id": target_qid,
            },
            "matching_statements": matches,
            "field_presence": field_presence,
            "display_labels": display_labels,
        }
        observations[edge["id"]] = observation
        observation_summaries.append(
            {
                "edge_id": edge["id"],
                "source_qid": source_qid,
                "property_id": property_id,
                "target_qid": target_qid,
                "statement_id": matches[0].get("id"),
                "rank": matches[0].get("rank"),
                "field_presence": field_presence[0],
                "qualifier_ids": sorted(matches[0].get("qualifiers", {})),
                "raw_statement_sha256": canon(matches[0]),
            }
        )

    public_oracle = {
        "source_hash_checks": hash_checks,
        "catalog": {
            "logical_rows": len(catalog),
            "nonempty_unique_qids": len(qids),
        },
        "summary": summary,
        "properties": properties,
        "observation_summaries": observation_summaries,
        "digests": {
            "ledger_rows_canonical_sha256": canon(rows),
            "included_edges_canonical_sha256": canon(edges),
            "properties_canonical_sha256": canon(properties),
            "observations_canonical_sha256": canon(observations),
        },
        "retrieved_at_interpretation": (
            "response-completion ended_at_utc from the sole retained request event"
        ),
    }
    return public_oracle, rows, edges, properties, observations


def source_checks(source: Any) -> dict[str, bool]:
    text = json.dumps(source, ensure_ascii=False, sort_keys=True)
    return {
        "repository": "https://github.com/MathGloss/MathGloss" in text,
        "commit": "b8f659605486f80f2816515f525af2c395c711fa" in text,
        **{key: value in text for key, value in HASHES.items()},
        "MIT": "MIT" in text,
        "CC0": "CC0" in text,
    }


def compare(args, oracle, rows, edges, properties, observations):
    supplied = (args.index, args.ledger, args.summary)
    if not any(supplied):
        return None
    if not all(supplied):
        raise ValueError("supply all three generated outputs")
    index = load(args.index)
    ledger = load(args.ledger)
    summary_file = load(args.summary)
    actual_observations = index.get("observations")
    observation_checks = {}
    for edge_id, expected in observations.items():
        actual = (
            actual_observations.get(edge_id)
            if isinstance(actual_observations, dict)
            else None
        )
        observation_checks[edge_id] = {
            key: actual is not None and actual.get(key) == value
            for key, value in expected.items()
        }
    index_source = source_checks(index.get("source"))
    ledger_source = source_checks(ledger.get("source"))
    summary_source = source_checks(summary_file.get("source"))
    summary_text = json.dumps(summary_file, sort_keys=True)
    checks = {
        "index_schema": index.get("schema_version") == "1.0",
        "ledger_rows_exact": ledger.get("rows") == rows,
        "index_edges_exact": index.get("edges") == edges,
        "index_summary_exact": index.get("summary") == oracle["summary"],
        "summary_summary_exact": summary_file.get("summary") == oracle["summary"],
        "index_properties_exact": index.get("properties") == properties,
        "summary_properties_exact": summary_file.get("properties") == properties,
        "observation_keys_exact": isinstance(actual_observations, dict)
        and set(actual_observations) == set(observations),
        "observations_exact": all(
            all(check.values()) for check in observation_checks.values()
        ),
        "index_source": all(index_source.values()),
        "ledger_source": all(ledger_source.values()),
        "summary_source": all(summary_source.values()),
        "summary_has_index_hash": sha(args.index) in summary_text,
        "summary_has_ledger_hash": sha(args.ledger) in summary_text,
    }
    volatile = {
        "created_at",
        "created_at_utc",
        "generated_at",
        "generated_at_utc",
        "timestamp",
    }
    checks.update(
        {
            "index_no_volatile_timestamp": not volatile.intersection(index),
            "ledger_no_volatile_timestamp": not volatile.intersection(ledger),
            "summary_no_volatile_timestamp": not volatile.intersection(summary_file),
        }
    )
    return {
        "status": "pass" if all(checks.values()) else "fail",
        "checks": checks,
        "failed_checks": sorted(key for key, value in checks.items() if not value),
        "source_metadata_checks": {
            "index": index_source,
            "ledger": ledger_source,
            "summary": summary_source,
        },
        "observation_checks": observation_checks,
        "output_files": {
            "index": {
                "path": str(args.index.resolve()),
                "bytes": args.index.stat().st_size,
                "sha256": sha(args.index),
            },
            "ledger": {
                "path": str(args.ledger.resolve()),
                "bytes": args.ledger.stat().st_size,
                "sha256": sha(args.ledger),
            },
            "summary": {
                "path": str(args.summary.resolve()),
                "bytes": args.summary.stat().st_size,
                "sha256": sha(args.summary),
            },
        },
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    for name in HASHES:
        parser.add_argument(
            "--" + name.replace("_", "-"), dest=name, type=Path, required=True
        )
    parser.add_argument("--index", type=Path)
    parser.add_argument("--ledger", type=Path)
    parser.add_argument("--summary", type=Path)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    oracle, rows, edges, properties, observations = derive(args)
    comparison = compare(args, oracle, rows, edges, properties, observations)
    result = {
        "schema_version": "relation-import-independent-verification-v1",
        "mode": "import_comparison" if comparison else "source_oracle_only",
        "status": comparison["status"] if comparison else "oracle_ready",
        "oracle": oracle,
        "comparison": comparison,
        "scope": (
            "Arithmetic-free import fidelity only; no relation truth, equivalence, "
            "novelty, completeness, or impact claim."
        ),
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(
        json.dumps(result, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
        newline="\n",
    )
    print(
        json.dumps(
            {
                "status": result["status"],
                "summary": oracle["summary"],
                "digests": oracle["digests"],
                "statement_ids": [
                    row["statement_id"] for row in oracle["observation_summaries"]
                ],
                "failed_checks": comparison["failed_checks"] if comparison else [],
            },
            sort_keys=True,
        )
    )
    return 0 if comparison is None or comparison["status"] == "pass" else 1


if __name__ == "__main__":
    raise SystemExit(main())
