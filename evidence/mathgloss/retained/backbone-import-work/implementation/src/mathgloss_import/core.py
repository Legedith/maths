"""Exact, dependency-free import of the frozen MathGloss metadata CSV."""

from __future__ import annotations

import csv
import hashlib
import io
import json
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Iterable, Mapping
from urllib.parse import urlsplit


SCHEMA_VERSION = "mathgloss-metadata-seed-v1"
PINNED_COMMIT = "b8f659605486f80f2816515f525af2c395c711fa"
PINNED_REPOSITORY = "https://github.com/MathGloss/MathGloss"
PINNED_CSV_PATH = "data/database.csv"
PINNED_SOURCE_SHA256 = "933a72820fe7ede53a803b750a480def205677e5722ae5f9589b0d1d9bf832b2"
PINNED_SOURCE_BYTES = 674_640
PINNED_LICENSE_SHA256 = "5dc6b930900926814fc7bb9ff45dfcceae3aa33780eb010c83e6df58493594e7"
PINNED_SOURCE = Path(
    "D:/CodexWorkspaces/mathematics-atlas/backbone-reuse-work/raw/mathgloss/data/database.csv"
)
PINNED_LICENSE = Path(
    "D:/CodexWorkspaces/mathematics-atlas/backbone-reuse-work/raw/mathgloss/LICENSE"
)

EXPECTED_HEADER = (
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

SOURCE_PAIRS = tuple(
    (EXPECTED_HEADER[index][:-5], index, index + 1)
    for index in range(2, len(EXPECTED_HEADER), 2)
)
QID_PATTERN = re.compile(r"Q[1-9][0-9]*\Z")


class ImportFailure(Exception):
    """Base class for explicit import failures."""


class SourceHashMismatchError(ImportFailure):
    pass


class HeaderMismatchError(ImportFailure):
    pass


class MalformedUTF8Error(ImportFailure):
    pass


class MalformedCSVError(ImportFailure):
    pass


class LicenseMismatchError(ImportFailure):
    pass


@dataclass(frozen=True)
class ImportResult:
    candidate_index: Mapping[str, Any]
    ledger: tuple[Mapping[str, Any], ...]
    summary: Mapping[str, Any]


def _sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _source_metadata(source_sha256: str, source_bytes: int) -> dict[str, Any]:
    return {
        "project": "MathGloss",
        "repository": PINNED_REPOSITORY,
        "commit": PINNED_COMMIT,
        "csv_path": PINNED_CSV_PATH,
        "sha256": source_sha256,
        "bytes": source_bytes,
        "header": list(EXPECTED_HEADER),
    }


def _attribution(license_sha256: str = PINNED_LICENSE_SHA256) -> dict[str, Any]:
    return {
        "project": "MathGloss",
        "repository": PINNED_REPOSITORY,
        "commit": PINNED_COMMIT,
        "paper": {
            "title": "MathGloss: Building mathematical glossaries from text",
            "authors": ["Lucy Horowitz", "Valeria de Paiva"],
            "url": "https://arxiv.org/abs/2311.12649",
        },
        "repository_license_notice": {
            "bundle_file": "MATHGLOSS-LICENSE",
            "source_path": "LICENSE",
            "source_url": f"{PINNED_REPOSITORY}/blob/{PINNED_COMMIT}/LICENSE",
            "sha256": license_sha256,
            "scope_note": (
                "Notice retained verbatim; this importer makes no claim that it licenses "
                "content at outbound links."
            ),
        },
    }


def _record_key(number: int) -> str:
    return f"mathgloss:{PINNED_COMMIT}:{PINNED_CSV_PATH}:record:{number:08d}"


def _physical_span(start: int, end: int) -> dict[str, int]:
    return {"start": start, "end": end}


def _source_locator(number: int, start: int, end: int) -> dict[str, Any]:
    return {
        "project": "MathGloss",
        "repository": PINNED_REPOSITORY,
        "commit": PINNED_COMMIT,
        "csv_path": PINNED_CSV_PATH,
        "logical_data_record": number,
        "physical_lines": _physical_span(start, end),
    }


def _reason(code: str, detail: str) -> dict[str, str]:
    return {"code": code, "detail": detail}


def _is_blank(value: str) -> bool:
    return value.strip() == ""


def _validate_url(value: str) -> tuple[dict[str, str], ...]:
    reasons: list[dict[str, str]] = []
    if value != value.strip():
        reasons.append(_reason("url_surrounding_whitespace", "URL has leading or trailing whitespace"))
    if any(ord(char) < 0x20 or ord(char) == 0x7F for char in value):
        reasons.append(_reason("url_control_character", "URL contains an ASCII control character"))
    if "\\" in value:
        reasons.append(_reason("url_backslash", "URL contains a backslash"))
    try:
        parsed = urlsplit(value)
    except ValueError as exc:
        return tuple(reasons + [_reason("url_parse_error", str(exc))])

    if parsed.scheme.lower() not in {"http", "https"}:
        reasons.append(_reason("unsafe_url_scheme", "URL scheme must be http or https"))
    if not parsed.netloc or parsed.hostname is None:
        reasons.append(_reason("missing_url_hostname", "URL must be absolute and contain a hostname"))
    if parsed.username is not None or parsed.password is not None:
        reasons.append(_reason("url_credentials", "URL must not contain username or password information"))
    if parsed.hostname is not None and any(char.isspace() for char in parsed.hostname):
        reasons.append(_reason("hostname_whitespace", "URL hostname contains whitespace"))
    try:
        parsed.port
    except ValueError as exc:
        reasons.append(_reason("invalid_url_port", str(exc)))
    return tuple(reasons)


def _link_entry(
    source: str,
    name: str,
    url: str,
    *,
    parent_row_accepted: bool,
) -> dict[str, Any]:
    name_blank = _is_blank(name)
    url_blank = _is_blank(url)
    base: dict[str, Any] = {
        "source": source,
        "name_as_recorded": name,
        "url_as_recorded": url,
    }
    if name_blank and url_blank:
        return {**base, "disposition": "absent", "reasons": []}

    reasons: list[dict[str, str]] = []
    if name_blank:
        reasons.append(_reason("missing_link_name", "URL is present but source name is empty"))
    if url_blank:
        reasons.append(_reason("missing_link_url", "Source name is present but URL is empty"))
    if not url_blank:
        reasons.extend(_validate_url(url))
    if not parent_row_accepted:
        reasons.append(_reason("parent_row_rejected", "Link is not exported because its source row is rejected"))

    if reasons:
        return {**base, "disposition": "rejected", "reasons": reasons}
    return {**base, "disposition": "retained", "reasons": []}


def _parse_reader(text: str) -> csv.reader:
    return csv.reader(io.StringIO(text, newline=""), strict=True)


def import_csv_bytes(
    source_bytes: bytes,
    *,
    expected_sha256: str = PINNED_SOURCE_SHA256,
    expected_size: int | None = PINNED_SOURCE_BYTES,
) -> ImportResult:
    """Validate and import CSV bytes without fetching or interpreting linked pages."""

    actual_sha256 = _sha256(source_bytes)
    if actual_sha256 != expected_sha256:
        raise SourceHashMismatchError(
            f"source SHA-256 mismatch: expected {expected_sha256}, got {actual_sha256}"
        )
    if expected_size is not None and len(source_bytes) != expected_size:
        raise SourceHashMismatchError(
            f"source byte-size mismatch: expected {expected_size}, got {len(source_bytes)}"
        )
    try:
        text = source_bytes.decode("utf-8", errors="strict")
    except UnicodeDecodeError as exc:
        raise MalformedUTF8Error(
            f"source is not strict UTF-8 at byte range {exc.start}:{exc.end}"
        ) from exc
    if "\x00" in text:
        raise MalformedCSVError("source contains a NUL character")

    reader = _parse_reader(text)
    try:
        header = next(reader)
    except StopIteration as exc:
        raise HeaderMismatchError("source has no CSV header") from exc
    except csv.Error as exc:
        raise MalformedCSVError(f"malformed CSV in header near physical line {reader.line_num}: {exc}") from exc
    if tuple(header) != EXPECTED_HEADER:
        raise HeaderMismatchError(
            "header mismatch: expected "
            + json.dumps(EXPECTED_HEADER, ensure_ascii=False)
            + ", got "
            + json.dumps(header, ensure_ascii=False)
        )

    source_meta = _source_metadata(actual_sha256, len(source_bytes))
    candidates: list[dict[str, Any]] = []
    ledger: list[dict[str, Any]] = []
    qid_occurrences: dict[str, list[dict[str, Any]]] = {}
    previous_end_line = reader.line_num
    data_record_number = 0

    while True:
        start_line = previous_end_line + 1
        try:
            row = next(reader)
        except StopIteration:
            break
        except csv.Error as exc:
            raise MalformedCSVError(
                f"malformed CSV near physical line {reader.line_num}: {exc}"
            ) from exc
        end_line = reader.line_num
        previous_end_line = end_line
        data_record_number += 1
        key = _record_key(data_record_number)
        locator = _source_locator(data_record_number, start_line, end_line)
        row_reasons: list[dict[str, str]] = []

        if not row:
            row_reasons.append(_reason("blank_record", "CSV data record is blank"))
        if len(row) != len(EXPECTED_HEADER):
            row_reasons.append(
                _reason(
                    "record_width_mismatch",
                    f"expected {len(EXPECTED_HEADER)} fields, got {len(row)}",
                )
            )

        qid = row[0] if row else ""
        label = row[1] if len(row) > 1 else ""
        width_valid = len(row) == len(EXPECTED_HEADER)
        if width_valid:
            if qid == "":
                row_reasons.append(_reason("missing_qid", "Wikidata ID is empty"))
            elif QID_PATTERN.fullmatch(qid) is None:
                row_reasons.append(
                    _reason("invalid_qid", "Wikidata ID must match Q[1-9][0-9]* exactly")
                )
            if _is_blank(label):
                row_reasons.append(_reason("missing_label", "Wikidata Label is empty or whitespace"))

        row_accepted = not row_reasons
        link_entries: list[dict[str, Any]] = []
        if width_valid:
            for source, name_index, url_index in SOURCE_PAIRS:
                link_entries.append(
                    _link_entry(
                        source,
                        row[name_index],
                        row[url_index],
                        parent_row_accepted=row_accepted,
                    )
                )

        ledger_record: dict[str, Any] = {
            "record_key": key,
            "source_locator": locator,
            "field_count": len(row),
            "row_disposition": "accepted" if row_accepted else "rejected",
            "row_reasons": row_reasons,
            "qid_as_recorded": qid,
            "label_as_recorded": label,
            "links": link_entries,
            "link_interpretation": "complete" if width_valid else "not_interpreted_width_mismatch",
        }

        if width_valid and QID_PATTERN.fullmatch(qid) is not None:
            occurrence = {
                "record_key": key,
                "logical_data_record": data_record_number,
                "physical_lines": _physical_span(start_line, end_line),
                "row_disposition": ledger_record["row_disposition"],
            }
            qid_occurrences.setdefault(qid, []).append(occurrence)

        if row_accepted:
            retained_links = [
                {
                    "source": link["source"],
                    "name_as_recorded": link["name_as_recorded"],
                    "url": link["url_as_recorded"],
                }
                for link in link_entries
                if link["disposition"] == "retained"
            ]
            candidate = {
                "record_key": key,
                "identity_candidate": {
                    "id": f"wikidata:{qid}",
                    "qid": qid,
                    "uri": f"https://www.wikidata.org/entity/{qid}",
                    "status": "unreviewed",
                },
                "label_as_recorded": label,
                "links": retained_links,
                "mapping_status": "unreviewed",
                "asserted_by": "MathGloss",
                "source_locator": locator,
            }
            ledger_record["candidate_record_index"] = len(candidates)
            candidates.append(candidate)
        else:
            ledger_record["candidate_record_index"] = None
        ledger.append(ledger_record)

    link_entries_all = [link for record in ledger for link in record["links"]]
    duplicate_qids = [
        {"qid": qid, "occurrences": occurrences}
        for qid, occurrences in sorted(qid_occurrences.items())
        if len(occurrences) > 1
    ]
    counts = {
        "data_records_total": len(ledger),
        "ledger_records": len(ledger),
        "accepted_rows": sum(record["row_disposition"] == "accepted" for record in ledger),
        "rejected_rows": sum(record["row_disposition"] == "rejected" for record in ledger),
        "candidate_records": len(candidates),
        "record_width_mismatch_rows": sum(
            record["link_interpretation"] == "not_interpreted_width_mismatch" for record in ledger
        ),
        "interpreted_link_pair_slots": len(link_entries_all),
        "absent_link_pairs": sum(link["disposition"] == "absent" for link in link_entries_all),
        "nonempty_link_pairs": sum(link["disposition"] != "absent" for link in link_entries_all),
        "retained_link_pairs": sum(link["disposition"] == "retained" for link in link_entries_all),
        "rejected_link_pairs": sum(link["disposition"] == "rejected" for link in link_entries_all),
        "incomplete_link_pairs": sum(
            any(
                reason["code"] in {"missing_link_name", "missing_link_url"}
                for reason in link["reasons"]
            )
            for link in link_entries_all
        ),
        "unsafe_or_invalid_url_pairs": sum(
            any(
                reason["code"]
                in {
                    "url_surrounding_whitespace",
                    "url_control_character",
                    "url_backslash",
                    "url_parse_error",
                    "unsafe_url_scheme",
                    "missing_url_hostname",
                    "url_credentials",
                    "hostname_whitespace",
                    "invalid_url_port",
                }
                for reason in link["reasons"]
            )
            for link in link_entries_all
        ),
        "duplicate_qid_groups": len(duplicate_qids),
        "rows_in_duplicate_qid_groups": sum(
            len(group["occurrences"]) for group in duplicate_qids
        ),
    }
    accounting = {
        "rows_complete": counts["data_records_total"]
        == counts["accepted_rows"] + counts["rejected_rows"]
        == counts["ledger_records"],
        "interpreted_links_complete": counts["interpreted_link_pair_slots"]
        == counts["absent_link_pairs"]
        + counts["retained_link_pairs"]
        + counts["rejected_link_pairs"],
        "nonempty_links_complete": counts["nonempty_link_pairs"]
        == counts["retained_link_pairs"] + counts["rejected_link_pairs"],
    }
    summary = {
        "schema_version": SCHEMA_VERSION,
        "catalog_status": "unreviewed_external_link_catalogue",
        "source": source_meta,
        "counts": counts,
        "accounting": accounting,
        "duplicate_qids": duplicate_qids,
    }
    candidate_index = {
        "schema_version": SCHEMA_VERSION,
        "catalog_status": "unreviewed_external_link_catalogue",
        "source": source_meta,
        "attribution": _attribution(),
        "audit_counts": counts,
        "records": candidates,
    }
    return ImportResult(candidate_index, tuple(ledger), summary)


def _json_text(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + "\n"


def _jsonl_text(values: Iterable[Mapping[str, Any]]) -> str:
    return "".join(
        json.dumps(value, ensure_ascii=False, separators=(",", ":"), sort_keys=True) + "\n"
        for value in values
    )


def bundle_content(
    result: ImportResult,
    license_bytes: bytes,
    *,
    expected_license_sha256: str = PINNED_LICENSE_SHA256,
) -> dict[str, bytes | str]:
    actual_license_sha256 = _sha256(license_bytes)
    if actual_license_sha256 != expected_license_sha256:
        raise LicenseMismatchError(
            f"license SHA-256 mismatch: expected {expected_license_sha256}, "
            f"got {actual_license_sha256}"
        )
    candidate = dict(result.candidate_index)
    candidate["attribution"] = _attribution(actual_license_sha256)
    return {
        "MATHGLOSS-LICENSE": license_bytes,
        "candidate-index.json": _json_text(candidate),
        "import-ledger.jsonl": _jsonl_text(result.ledger),
        "summary.json": _json_text(result.summary),
    }


def write_bundle(
    result: ImportResult,
    output_dir: Path,
    license_bytes: bytes,
    *,
    expected_license_sha256: str = PINNED_LICENSE_SHA256,
) -> dict[str, str]:
    files = bundle_content(
        result,
        license_bytes,
        expected_license_sha256=expected_license_sha256,
    )
    output_dir = Path(output_dir)
    if output_dir.exists() and any(output_dir.iterdir()):
        raise OSError(f"output directory is not empty: {output_dir}")
    output_dir.mkdir(parents=True, exist_ok=True)
    hashes: dict[str, str] = {}
    for name in sorted(files):
        content = files[name]
        destination = output_dir / name
        if isinstance(content, bytes):
            destination.write_bytes(content)
            data = content
        else:
            # Write Unicode artifacts directly as strict UTF-8.  This avoids
            # console-codepage and PowerShell redirection transformations.
            destination.write_text(content, encoding="utf-8", errors="strict", newline="\n")
            data = destination.read_bytes()
        hashes[name] = _sha256(data)
    return hashes


def run_pinned_import(output_dir: Path) -> dict[str, str]:
    source_bytes = PINNED_SOURCE.read_bytes()
    license_bytes = PINNED_LICENSE.read_bytes()
    result = import_csv_bytes(source_bytes)
    return write_bundle(result, output_dir, license_bytes)
