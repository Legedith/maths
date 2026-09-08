from __future__ import annotations

import csv
import hashlib
import io
import json
import tempfile
import unittest
from pathlib import Path

from mathgloss_import import (
    EXPECTED_HEADER,
    PINNED_LICENSE_SHA256,
    PINNED_SOURCE_BYTES,
    PINNED_SOURCE_SHA256,
    HeaderMismatchError,
    LicenseMismatchError,
    MalformedCSVError,
    MalformedUTF8Error,
    SourceHashMismatchError,
    import_csv_bytes,
    write_bundle,
)
from mathgloss_import.core import PINNED_LICENSE, PINNED_SOURCE


def csv_bytes(
    rows: list[list[str]],
    *,
    header: tuple[str, ...] | list[str] = EXPECTED_HEADER,
    line_ending: str = "\n",
) -> bytes:
    stream = io.StringIO(newline="")
    writer = csv.writer(stream, lineterminator=line_ending)
    writer.writerow(header)
    writer.writerows(rows)
    return stream.getvalue().encode("utf-8")


def valid_row(qid: str = "Q1", label: str = "label") -> list[str]:
    return [qid, label] + [""] * (len(EXPECTED_HEADER) - 2)


def fixture_import(data: bytes):
    return import_csv_bytes(
        data,
        expected_sha256=hashlib.sha256(data).hexdigest(),
        expected_size=len(data),
    )


class ValidationTests(unittest.TestCase):
    def test_hash_is_checked_before_decoding(self) -> None:
        with self.assertRaises(SourceHashMismatchError):
            import_csv_bytes(b"\xff", expected_sha256="0" * 64, expected_size=1)

    def test_size_is_checked_even_with_matching_hash(self) -> None:
        data = csv_bytes([valid_row()])
        with self.assertRaisesRegex(SourceHashMismatchError, "byte-size mismatch"):
            import_csv_bytes(
                data,
                expected_sha256=hashlib.sha256(data).hexdigest(),
                expected_size=len(data) + 1,
            )

    def test_malformed_utf8_is_explicit(self) -> None:
        data = b"\xff"
        with self.assertRaises(MalformedUTF8Error):
            fixture_import(data)

    def test_nul_is_explicitly_malformed(self) -> None:
        data = csv_bytes([valid_row(label="a\x00b")])
        with self.assertRaisesRegex(MalformedCSVError, "NUL"):
            fixture_import(data)

    def test_missing_extra_and_reordered_headers_fail_before_import(self) -> None:
        variants = [
            EXPECTED_HEADER[:-1],
            EXPECTED_HEADER + ("Unexpected",),
            (EXPECTED_HEADER[1], EXPECTED_HEADER[0], *EXPECTED_HEADER[2:]),
        ]
        for header in variants:
            with self.subTest(header=header):
                data = csv_bytes([], header=header)
                with self.assertRaises(HeaderMismatchError):
                    fixture_import(data)

    def test_empty_source_has_header_error(self) -> None:
        with self.assertRaises(HeaderMismatchError):
            fixture_import(b"")

    def test_malformed_quoted_csv_is_explicit(self) -> None:
        header = ",".join(EXPECTED_HEADER).encode("utf-8")
        data = header + b'\nQ1,"unterminated\n'
        with self.assertRaises(MalformedCSVError):
            fixture_import(data)


class RowAndLocatorTests(unittest.TestCase):
    def test_quoted_commas_and_multiline_fields_keep_physical_spans(self) -> None:
        first = valid_row("Q11", "alpha,\nbeta")
        first[2] = "source, name"
        first[3] = "https://example.org/a,b"
        second = valid_row("Q12", "next")
        result = fixture_import(csv_bytes([first, second]))

        self.assertEqual(result.ledger[0]["source_locator"]["logical_data_record"], 1)
        self.assertEqual(
            result.ledger[0]["source_locator"]["physical_lines"], {"start": 2, "end": 3}
        )
        self.assertEqual(
            result.ledger[1]["source_locator"]["physical_lines"], {"start": 4, "end": 4}
        )
        self.assertEqual(result.candidate_index["records"][0]["label_as_recorded"], "alpha,\nbeta")
        self.assertEqual(
            result.candidate_index["records"][0]["links"][0]["name_as_recorded"],
            "source, name",
        )

    def test_record_locators_repeat_complete_pinned_provenance(self) -> None:
        result = fixture_import(csv_bytes([valid_row("Q17", "located")]))
        expected = {
            "project": "MathGloss",
            "repository": "https://github.com/MathGloss/MathGloss",
            "commit": "b8f659605486f80f2816515f525af2c395c711fa",
            "csv_path": "data/database.csv",
            "logical_data_record": 1,
            "physical_lines": {"start": 2, "end": 2},
        }
        self.assertEqual(result.ledger[0]["source_locator"], expected)
        self.assertEqual(result.candidate_index["records"][0]["source_locator"], expected)

    def test_crlf_multiline_locator(self) -> None:
        row = valid_row("Q9", "line one\r\nline two")
        result = fixture_import(csv_bytes([row], line_ending="\r\n"))
        self.assertEqual(
            result.ledger[0]["source_locator"]["physical_lines"], {"start": 2, "end": 3}
        )

    def test_blank_and_inconsistent_width_rows_are_retained_as_rejections(self) -> None:
        data = csv_bytes([valid_row("Q1"), [], ["Q2"], valid_row("Q3") + ["extra"]])
        result = fixture_import(data)
        self.assertEqual(result.summary["counts"]["data_records_total"], 4)
        self.assertEqual([row["row_disposition"] for row in result.ledger], [
            "accepted",
            "rejected",
            "rejected",
            "rejected",
        ])
        self.assertEqual(
            [reason["code"] for reason in result.ledger[1]["row_reasons"]],
            ["blank_record", "record_width_mismatch"],
        )
        self.assertEqual(
            result.ledger[2]["link_interpretation"], "not_interpreted_width_mismatch"
        )
        self.assertEqual(result.summary["counts"]["record_width_mismatch_rows"], 3)

    def test_invalid_qids_and_missing_labels_have_specific_reasons(self) -> None:
        rows = [
            valid_row("", "x"),
            valid_row("Q0", "x"),
            valid_row(" Q1", "x"),
            valid_row("Q2", "   "),
        ]
        result = fixture_import(csv_bytes(rows))
        codes = [[reason["code"] for reason in row["row_reasons"]] for row in result.ledger]
        self.assertEqual(codes, [["missing_qid"], ["invalid_qid"], ["invalid_qid"], ["missing_label"]])
        self.assertEqual(result.candidate_index["records"], [])

    def test_order_and_repeated_qids_are_preserved(self) -> None:
        rows = [valid_row("Q7", "first"), valid_row("Q2", "middle"), valid_row("Q7", "last")]
        result = fixture_import(csv_bytes(rows))
        records = result.candidate_index["records"]
        self.assertEqual([record["label_as_recorded"] for record in records], ["first", "middle", "last"])
        self.assertNotEqual(records[0]["record_key"], records[2]["record_key"])
        self.assertEqual(len(result.summary["duplicate_qids"]), 1)
        duplicate = result.summary["duplicate_qids"][0]
        self.assertEqual(duplicate["qid"], "Q7")
        self.assertEqual(
            [item["logical_data_record"] for item in duplicate["occurrences"]], [1, 3]
        )


class LinkBoundaryTests(unittest.TestCase):
    def _one_link(self, name: str, url: str, *, qid: str = "Q1", label: str = "x"):
        row = valid_row(qid, label)
        row[2] = name
        row[3] = url
        return fixture_import(csv_bytes([row]))

    def test_absolute_http_and_https_links_are_retained_verbatim(self) -> None:
        for url in ["http://example.org/a", "https://例え.テスト/path?q=1#x"]:
            with self.subTest(url=url):
                result = self._one_link("source", url)
                link = result.ledger[0]["links"][0]
                self.assertEqual(link["disposition"], "retained")
                self.assertEqual(result.candidate_index["records"][0]["links"][0]["url"], url)

    def test_empty_pair_is_absent(self) -> None:
        result = fixture_import(csv_bytes([valid_row()]))
        self.assertEqual({link["disposition"] for link in result.ledger[0]["links"]}, {"absent"})
        self.assertEqual(result.summary["counts"]["absent_link_pairs"], 7)
        self.assertEqual(result.candidate_index["records"][0]["links"], [])

    def test_incomplete_pairs_are_rejected(self) -> None:
        cases = [
            ("name", "", "missing_link_url"),
            ("", "https://example.org", "missing_link_name"),
            ("   ", "https://example.org", "missing_link_name"),
        ]
        for name, url, reason in cases:
            with self.subTest(name=name, url=url):
                link = self._one_link(name, url).ledger[0]["links"][0]
                self.assertEqual(link["disposition"], "rejected")
                self.assertIn(reason, [item["code"] for item in link["reasons"]])

    def test_unsafe_or_invalid_urls_are_rejected(self) -> None:
        cases = [
            ("javascript:alert(1)", "unsafe_url_scheme"),
            ("//example.org/path", "unsafe_url_scheme"),
            ("https:///path", "missing_url_hostname"),
            ("https://user:pass@example.org/a", "url_credentials"),
            ("https://example.org\\evil", "url_backslash"),
            (" https://example.org", "url_surrounding_whitespace"),
            ("https://example.org:bad/a", "invalid_url_port"),
            ("https://exa mple.org", "hostname_whitespace"),
        ]
        for url, reason in cases:
            with self.subTest(url=url):
                result = self._one_link("name", url)
                link = result.ledger[0]["links"][0]
                self.assertEqual(link["disposition"], "rejected")
                self.assertIn(reason, [item["code"] for item in link["reasons"]])
                self.assertEqual(result.candidate_index["records"][0]["links"], [])

    def test_safe_link_on_rejected_parent_is_not_exported(self) -> None:
        result = self._one_link("name", "https://example.org", qid="Q0")
        link = result.ledger[0]["links"][0]
        self.assertEqual(link["disposition"], "rejected")
        self.assertIn("parent_row_rejected", [item["code"] for item in link["reasons"]])
        self.assertEqual(result.candidate_index["records"], [])

    def test_link_accounting_identity(self) -> None:
        row = valid_row()
        row[2:8] = [
            "kept",
            "https://example.org",
            "missing url",
            "",
            "bad",
            "file:///tmp/x",
        ]
        result = fixture_import(csv_bytes([row]))
        counts = result.summary["counts"]
        self.assertEqual(counts["nonempty_link_pairs"], 3)
        self.assertEqual(counts["retained_link_pairs"], 1)
        self.assertEqual(counts["rejected_link_pairs"], 2)
        self.assertTrue(result.summary["accounting"]["interpreted_links_complete"])
        self.assertTrue(result.summary["accounting"]["nonempty_links_complete"])


class BundleAndPinnedSourceTests(unittest.TestCase):
    def test_bundle_is_byte_deterministic_and_retains_license(self) -> None:
        data = csv_bytes([valid_row("Q1", "one"), valid_row("Q1", "two")])
        result = fixture_import(data)
        license_bytes = b"test license notice\n"
        license_hash = hashlib.sha256(license_bytes).hexdigest()
        base = Path(__file__).resolve().parent
        with tempfile.TemporaryDirectory(dir=base) as temporary:
            first = Path(temporary) / "a"
            second = Path(temporary) / "b"
            hashes_a = write_bundle(
                result, first, license_bytes, expected_license_sha256=license_hash
            )
            hashes_b = write_bundle(
                result, second, license_bytes, expected_license_sha256=license_hash
            )
            self.assertEqual(hashes_a, hashes_b)
            for name in hashes_a:
                self.assertEqual((first / name).read_bytes(), (second / name).read_bytes())
            self.assertEqual((first / "MATHGLOSS-LICENSE").read_bytes(), license_bytes)
            candidate = json.loads((first / "candidate-index.json").read_text(encoding="utf-8"))
            serialized = json.dumps(candidate, sort_keys=True)
            self.assertNotIn('"confidence"', serialized)
            self.assertNotIn('"method"', serialized)
            self.assertEqual(
                candidate["attribution"]["repository_license_notice"]["sha256"],
                license_hash,
            )

    def test_unicode_is_written_directly_as_utf8_without_replacement(self) -> None:
        label = "Deutsch\u2013Jozsa \u03b1\u03bb\u03b3\u03cc\u03c1\u03b9\u03b8\u03bc\u03bf\u03c2"
        source_name = "\u03c3-map \u2013 source"
        row = valid_row("Q1028209", label)
        row[2] = source_name
        row[3] = "https://example.org/unicode"
        result = fixture_import(csv_bytes([row]))
        license_bytes = b"test license notice\n"
        license_hash = hashlib.sha256(license_bytes).hexdigest()
        base = Path(__file__).resolve().parent

        with tempfile.TemporaryDirectory(dir=base) as temporary:
            output = Path(temporary) / "unicode"
            write_bundle(
                result,
                output,
                license_bytes,
                expected_license_sha256=license_hash,
            )
            candidate_bytes = (output / "candidate-index.json").read_bytes()
            ledger_bytes = (output / "import-ledger.jsonl").read_bytes()
            for artifact_bytes in (candidate_bytes, ledger_bytes):
                artifact_text = artifact_bytes.decode("utf-8", errors="strict")
                self.assertIn(label, artifact_text)
                self.assertIn(source_name, artifact_text)
                self.assertNotIn("\ufffd", artifact_text)
                self.assertIn("\u2013".encode("utf-8"), artifact_bytes)
                self.assertIn("\u03b1".encode("utf-8"), artifact_bytes)

            candidate = json.loads(candidate_bytes)
            record = candidate["records"][0]
            self.assertEqual(record["label_as_recorded"], label)
            self.assertEqual(record["links"][0]["name_as_recorded"], source_name)

    def test_license_hash_mismatch_is_explicit(self) -> None:
        result = fixture_import(csv_bytes([valid_row()]))
        base = Path(__file__).resolve().parent
        with tempfile.TemporaryDirectory(dir=base) as temporary:
            with self.assertRaises(LicenseMismatchError):
                write_bundle(result, Path(temporary) / "out", b"wrong")

    def test_nonempty_output_directory_is_refused(self) -> None:
        result = fixture_import(csv_bytes([valid_row()]))
        license_bytes = b"license"
        license_hash = hashlib.sha256(license_bytes).hexdigest()
        base = Path(__file__).resolve().parent
        with tempfile.TemporaryDirectory(dir=base) as temporary:
            output = Path(temporary) / "out"
            output.mkdir()
            (output / "existing").write_text("keep", encoding="utf-8")
            with self.assertRaisesRegex(OSError, "not empty"):
                write_bundle(
                    result,
                    output,
                    license_bytes,
                    expected_license_sha256=license_hash,
                )
            self.assertEqual((output / "existing").read_text(encoding="utf-8"), "keep")

    def test_pinned_source_signature_schema_and_accounting(self) -> None:
        source = PINNED_SOURCE.read_bytes()
        self.assertEqual(len(source), PINNED_SOURCE_BYTES)
        self.assertEqual(hashlib.sha256(source).hexdigest(), PINNED_SOURCE_SHA256)
        result = import_csv_bytes(source)
        self.assertTrue(result.summary["accounting"]["rows_complete"])
        self.assertTrue(result.summary["accounting"]["interpreted_links_complete"])
        self.assertTrue(result.summary["accounting"]["nonempty_links_complete"])
        self.assertEqual(result.summary["counts"]["record_width_mismatch_rows"], 0)
        self.assertEqual(
            result.summary["counts"]["candidate_records"],
            result.summary["counts"]["accepted_rows"],
        )
        self.assertEqual(
            hashlib.sha256(PINNED_LICENSE.read_bytes()).hexdigest(), PINNED_LICENSE_SHA256
        )


if __name__ == "__main__":
    unittest.main()
