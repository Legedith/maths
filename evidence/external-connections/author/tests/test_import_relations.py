from __future__ import annotations

import csv
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

import import_relations as importer


class RelationImporterTests(unittest.TestCase):
    def write_csv(self, path: Path, rows: list[list[str]]) -> None:
        with path.open("w", encoding="utf-8", newline="") as stream:
            writer = csv.writer(stream, lineterminator="\n")
            writer.writerows(rows)

    def test_multiline_locator_original_fields_and_strict_qid_join(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            catalog = root / "catalog.csv"
            relations = root / "relations.csv"
            catalog_rows = [list(importer.CATALOG_HEADER)]
            for qid, label in (("Q1", "Alpha"), ("Q2", "Beta")):
                catalog_rows.append([qid, label] + [""] * 14)
            self.write_csv(catalog, catalog_rows)
            self.write_csv(
                relations,
                [
                    list(importer.GRAPH_HEADER),
                    ["Q1", "alpha\nconcept", "P279", "subclass of", "Q2", "beta"],
                    ["Q2", "beta", "P31", "instance of", "Q3", "gamma"],
                ],
            )
            expected = {
                "total_rows": 2,
                "included_rows": 1,
                "excluded_rows": 1,
                "endpoint_count": 2,
                "property_count": 1,
            }
            with patch.dict(importer.EXPECTED_INVENTORY, expected, clear=True):
                qids = importer.read_catalog_qids(catalog)
                ledger, edges, properties, summary = importer.read_relations(relations, qids)

            self.assertEqual(summary, expected)
            self.assertEqual((ledger[0]["line_start"], ledger[0]["line_end"]), (2, 3))
            self.assertEqual((ledger[1]["line_start"], ledger[1]["line_end"]), (4, 4))
            self.assertEqual(ledger[0]["fields"]["source_label"], "alpha\nconcept")
            self.assertEqual(ledger[1]["missing_qids"], ["Q3"])
            self.assertEqual(edges[0]["source"]["label"], "alpha\nconcept")
            self.assertEqual(properties, [{"id": "P279", "label": "subclass of", "count": 1}])

    def test_observation_retains_raw_statement_and_presence_flags(self) -> None:
        fields = {
            "source_id": "Q1",
            "source_label": "source",
            "property_id": "P460",
            "property_label": "said to be the same as",
            "target_id": "Q2",
            "target_label": "target",
        }
        statement = {
            "mainsnak": {
                "snaktype": "value",
                "property": "P460",
                "datavalue": {
                    "value": {"entity-type": "item", "numeric-id": 2, "id": "Q2"},
                    "type": "wikibase-entityid",
                },
                "datatype": "wikibase-item",
            },
            "type": "statement",
            "qualifiers": {
                "P518": [
                    {
                        "snaktype": "value",
                        "property": "P518",
                        "datavalue": {
                            "value": {"entity-type": "item", "numeric-id": 3, "id": "Q3"},
                            "type": "wikibase-entityid",
                        },
                        "datatype": "wikibase-item",
                    }
                ]
            },
            "id": "Q1$statement",
            "rank": "normal",
        }
        probe_inputs = {
            "selected_rows": [
                {
                    "property_id": "P460",
                    "logical_data_record_1_based": 1,
                    "physical_line_start_1_based": 2,
                    "physical_line_end_1_based": 2,
                    "fields": fields,
                },
                {
                    "property_id": "P279",
                    "logical_data_record_1_based": 2,
                    "physical_line_start_1_based": 3,
                    "physical_line_end_1_based": 3,
                    "fields": {**fields, "property_id": "P279"},
                },
                {
                    "property_id": "P1889",
                    "logical_data_record_1_based": 3,
                    "physical_line_start_1_based": 4,
                    "physical_line_end_1_based": 4,
                    "fields": {**fields, "property_id": "P1889"},
                },
            ],
            "request": {"url": "https://example.invalid/frozen"},
        }
        ledger = [
            {
                "record": selected["logical_data_record_1_based"],
                "line_start": selected["physical_line_start_1_based"],
                "line_end": selected["physical_line_end_1_based"],
                "fields": selected["fields"],
                "included": True,
                "missing_qids": [],
            }
            for selected in probe_inputs["selected_rows"]
        ]
        entities = {}
        for selected in probe_inputs["selected_rows"]:
            prop = selected["property_id"]
            raw = statement if prop == "P460" else {
                **statement,
                "mainsnak": {**statement["mainsnak"], "property": prop},
                "id": f"Q1${prop}",
            }
            entities.setdefault(
                "Q1",
                {"lastrevid": 10, "modified": "2026-01-01T00:00:00Z", "claims": {}},
            )["claims"][prop] = [raw]
        command_log = {
            "events": [
                {
                    "operation": "one batched primary API request",
                    "result": "success",
                    "requested_url": "https://example.invalid/frozen",
                    "ended_at_utc": "2026-01-01T00:00:01Z",
                }
            ]
        }
        semantics = {
            "entities": {
                "P460": {"labels": {"en": {"value": "said to be the same as"}}},
                "P518": {"labels": {"en": {"value": "applies to part"}}},
                "Q9085982": {"labels": {"en": {"value": "type IIA string theory"}}},
            }
        }

        observations = importer.build_observations(
            probe_inputs, {"entities": entities}, command_log, semantics, ledger
        )
        observed = observations["mathgloss-row-1"]
        self.assertEqual(observed["matching_statements"], [statement])
        self.assertNotIn("references", observed["matching_statements"][0])
        self.assertEqual(
            observed["field_presence"],
            [{"statement_id": True, "qualifiers": True, "references": False}],
        )
        self.assertEqual(
            set(observed["display_labels"]), {"P460", "P518", "Q9085982"}
        )

    def test_existing_nonempty_output_directory_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            output = Path(temporary) / "out"
            output.mkdir()
            (output / "keep.txt").write_text("keep", encoding="utf-8")
            with self.assertRaisesRegex(importer.RelationImportError, "nonempty"):
                importer.check_output_directory(output)

    def test_deterministic_json_is_utf8_sorted_compact_and_lf_terminated(self) -> None:
        payload = importer.deterministic_json_bytes({"z": "\u0394", "a": 1})
        self.assertEqual(payload, '{"a":1,"z":"\u0394"}\n'.encode("utf-8"))


if __name__ == "__main__":
    unittest.main()
