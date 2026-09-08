from __future__ import annotations

import csv
import hashlib
import json
import unittest
from collections import Counter
from pathlib import Path


STAGE = Path(__file__).resolve().parents[1]
WORKSPACE = STAGE.parent
OUTPUT = STAGE / "outputs"
GRAPH = WORKSPACE / "backbone-reuse-work/raw/mathgloss/data/relations/graph_edges.csv"
CATALOG = WORKSPACE / "project/data/mathgloss/source/database.csv"
PROBE_INPUTS = WORKSPACE / "relation-source-review-work/probe/frozen-inputs.json"
PROBE_RESPONSE = WORKSPACE / "relation-source-review-work/probe/wikidata-response.json"
PROBE_COMMAND = WORKSPACE / "relation-source-review-work/probe/command-log.json"
SEMANTICS = WORKSPACE / "relation-source-review-work/semantics/wikidata-semantics-response.json"
GRAPH_HEADER = (
    "source_id",
    "source_label",
    "property_id",
    "property_label",
    "target_id",
    "target_label",
)
EXPECTED_SUMMARY = {
    "total_rows": 9159,
    "included_rows": 5390,
    "excluded_rows": 3769,
    "endpoint_count": 3372,
    "property_count": 81,
}


def load(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def is_match(statement: dict, property_id: str, target_id: str) -> bool:
    mainsnak = statement.get("mainsnak", {})
    datavalue = mainsnak.get("datavalue", {})
    value = datavalue.get("value", {})
    return (
        mainsnak.get("property") == property_id
        and mainsnak.get("snaktype") == "value"
        and datavalue.get("type") == "wikibase-entityid"
        and value.get("id") == target_id
    )


class CanonicalOutputTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.index = load(OUTPUT / "relation-index.json")
        cls.ledger = load(OUTPUT / "relation-ledger.json")
        cls.summary = load(OUTPUT / "relation-summary.json")
        cls.probe_inputs = load(PROBE_INPUTS)
        cls.probe_response = load(PROBE_RESPONSE)
        cls.probe_command = load(PROBE_COMMAND)
        cls.semantics = load(SEMANTICS)
        with CATALOG.open("r", encoding="utf-8", newline="") as stream:
            reader = csv.reader(stream, strict=True)
            next(reader)
            cls.catalog_qids = {row[0] for row in reader}

    def test_three_files_are_utf8_lf_and_summary_hashes_match(self) -> None:
        for name in ("relation-index.json", "relation-ledger.json", "relation-summary.json"):
            raw = (OUTPUT / name).read_bytes()
            self.assertTrue(raw.endswith(b"\n"), name)
            self.assertNotIn(b"\r", raw, name)
            decoded = raw.decode("utf-8")
            self.assertNotIn("\ufffd", decoded, name)
        hashes = self.summary["output_file_hashes"]
        self.assertEqual(hashes["relation-index.json"], digest(OUTPUT / "relation-index.json"))
        self.assertEqual(hashes["relation-ledger.json"], digest(OUTPUT / "relation-ledger.json"))
        self.assertNotIn("timestamp", self.index)
        self.assertNotIn("timestamp", self.ledger)
        self.assertNotIn("timestamp", self.summary)

    def test_source_summary_and_properties_are_shared_exactly(self) -> None:
        self.assertEqual(self.index["source"], self.ledger["source"])
        self.assertEqual(self.index["source"], self.summary["source"])
        self.assertEqual(self.index["summary"], EXPECTED_SUMMARY)
        self.assertEqual(self.index["summary"], self.summary["summary"])
        self.assertEqual(self.index["properties"], self.summary["properties"])
        self.assertEqual(
            [int(item["id"][1:]) for item in self.index["properties"]],
            sorted(int(item["id"][1:]) for item in self.index["properties"]),
        )
        counts = Counter(edge["property"]["id"] for edge in self.index["edges"])
        self.assertEqual(
            self.index["properties"],
            [
                {
                    "id": property_id,
                    "label": next(
                        edge["property"]["label"]
                        for edge in self.index["edges"]
                        if edge["property"]["id"] == property_id
                    ),
                    "count": counts[property_id],
                }
                for property_id in sorted(counts, key=lambda item: int(item[1:]))
            ],
        )

    def test_every_csv_record_matches_ledger_and_included_edge(self) -> None:
        ledger_rows = self.ledger["rows"]
        edges = self.index["edges"]
        self.assertEqual(len(ledger_rows), 9159)
        self.assertEqual(len(edges), 5390)
        edge_index = 0
        with GRAPH.open("r", encoding="utf-8", newline="") as stream:
            reader = csv.reader(stream, strict=True)
            self.assertEqual(tuple(next(reader)), GRAPH_HEADER)
            previous_line_end = reader.line_num
            for record, row in enumerate(reader, start=1):
                line_start = previous_line_end + 1
                line_end = reader.line_num
                previous_line_end = line_end
                fields = dict(zip(GRAPH_HEADER, row, strict=True))
                missing_qids = [
                    qid
                    for qid in (fields["source_id"], fields["target_id"])
                    if qid not in self.catalog_qids
                ]
                expected_ledger = {
                    "record": record,
                    "line_start": line_start,
                    "line_end": line_end,
                    "fields": fields,
                    "included": not missing_qids,
                    "missing_qids": missing_qids,
                }
                self.assertEqual(ledger_rows[record - 1], expected_ledger)
                if missing_qids:
                    continue
                expected_edge = {
                    "id": f"mathgloss-row-{record}",
                    "source": {"id": fields["source_id"], "label": fields["source_label"]},
                    "property": {"id": fields["property_id"], "label": fields["property_label"]},
                    "target": {"id": fields["target_id"], "label": fields["target_label"]},
                    "record": record,
                    "line_start": line_start,
                    "line_end": line_end,
                    "review_status": "unreviewed_external_assertion",
                    "legacy_statement_metadata": "not_retrieved",
                }
                self.assertEqual(edges[edge_index], expected_edge)
                edge_index += 1
        self.assertEqual(edge_index, len(edges))

    def test_probe_observations_are_exact_raw_matches_with_presence_flags(self) -> None:
        request_event = next(
            event
            for event in self.probe_command["events"]
            if event.get("operation") == "one batched primary API request"
        )
        expected_labels = {
            entity_id: self.semantics["entities"][entity_id]["labels"]["en"]["value"]
            for entity_id in ("P460", "P518", "Q9085982")
        }
        expected_ids = {
            f"mathgloss-row-{selected['logical_data_record_1_based']}"
            for selected in self.probe_inputs["selected_rows"]
        }
        self.assertEqual(set(self.index["observations"]), expected_ids)
        for selected in self.probe_inputs["selected_rows"]:
            fields = selected["fields"]
            edge_id = f"mathgloss-row-{selected['logical_data_record_1_based']}"
            observation = self.index["observations"][edge_id]
            entity = self.probe_response["entities"][fields["source_id"]]
            matches = [
                statement
                for statement in entity["claims"][fields["property_id"]]
                if is_match(statement, fields["property_id"], fields["target_id"])
            ]
            self.assertEqual(observation["matching_statements"], matches)
            self.assertEqual(
                observation["field_presence"],
                [
                    {
                        "statement_id": "id" in statement,
                        "qualifiers": "qualifiers" in statement,
                        "references": "references" in statement,
                    }
                    for statement in matches
                ],
            )
            self.assertEqual(observation["requested_url"], request_event["requested_url"])
            self.assertEqual(observation["retrieved_at_utc"], request_event["ended_at_utc"])
            self.assertEqual(
                observation["source_entity"],
                {
                    "id": fields["source_id"],
                    "lastrevid": entity["lastrevid"],
                    "modified": entity["modified"],
                },
            )
            self.assertEqual(observation["display_labels"], expected_labels)

        p460 = self.index["observations"]["mathgloss-row-175"]
        statement = p460["matching_statements"][0]
        self.assertEqual(
            statement["qualifiers"]["P518"][0]["datavalue"]["value"]["id"],
            "Q9085982",
        )
        self.assertNotIn("references", statement)
        self.assertFalse(p460["field_presence"][0]["references"])


if __name__ == "__main__":
    unittest.main()
