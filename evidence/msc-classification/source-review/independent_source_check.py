"""Independent structural checks over the frozen MSC source snapshots."""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import re
from collections import Counter, defaultdict
from pathlib import Path

from rdflib import Graph, Literal, Namespace, URIRef
from rdflib.namespace import OWL, RDF, SKOS


SOURCE = Path(r"D:/CodexWorkspaces/mathematics-atlas/msc-reuse-work")
PREFIX = "http://msc2020.org/resources/MSC/msc2020/"
DATA_VOCAB = Namespace(PREFIX + "mscvocab#")
FILE_VOCAB_PREFIX = "https://msc2020.org/resources/MSC/2020/MSC2020/mscvocab#"
CODE = re.compile(r"(?:\d{2}-XX|\d{2}-\d{2}|\d{2}[A-Z]xx|\d{2}[A-Z]\d{2})\Z")


def sha_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def canonical_sha(value: object) -> str:
    return sha_bytes(json.dumps(value, ensure_ascii=False, sort_keys=True,
                                separators=(",", ":")).encode("utf-8"))


def values(graph: Graph, subject: URIRef, predicate: URIRef) -> list[str]:
    return sorted(str(value) for value in graph.objects(subject, predicate))


def code_level(code: str) -> str:
    if re.fullmatch(r"\d{2}-XX", code):
        return "top"
    if re.fullmatch(r"\d{2}[A-Z]xx", code):
        return "letter_group"
    if re.fullmatch(r"\d{2}-\d{2}", code):
        return "hyphen_leaf"
    if re.fullmatch(r"\d{2}[A-Z]\d{2}", code):
        return "letter_leaf"
    return "invalid"


def expected_parent(code: str) -> list[str]:
    level = code_level(code)
    if level == "top":
        return []
    if level in {"letter_group", "hyphen_leaf"}:
        return [PREFIX + code[:2] + "-XX"]
    if level == "letter_leaf":
        return [PREFIX + code[:3] + "xx"]
    raise ValueError(code)


def locate(lines: list[str], needle: str) -> int:
    matches = [i + 1 for i, line in enumerate(lines) if needle in line]
    if len(matches) != 1:
        raise AssertionError((needle, matches))
    return matches[0]


def locate_exact(lines: list[str], text: str) -> int:
    matches = [i + 1 for i, line in enumerate(lines) if line == text]
    if len(matches) != 1:
        raise AssertionError((text, matches))
    return matches[0]


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    if args.output.exists():
        parser.error("output exists")

    manifest_bytes = (SOURCE / "source-manifest.json").read_bytes()
    manifest = json.loads(manifest_bytes)
    source_integrity = []
    for item in manifest["sources"]:
        path = SOURCE / item["path"]
        raw = path.read_bytes()
        source_integrity.append({
            "path": item["path"],
            "bytes_match": len(raw) == item["bytes"],
            "sha256_match": sha_bytes(raw) == item["sha256"],
        })

    csv_raw = (SOURCE / "raw/official.csv").read_bytes()
    utf8_failure = None
    try:
        csv_raw.decode("utf-8-sig", errors="strict")
    except UnicodeDecodeError as error:
        utf8_failure = {
            "start": error.start,
            "end": error.end,
            "reason": error.reason,
            "byte_hex": csv_raw[error.start:error.end].hex(),
        }
    latin_text = csv_raw.decode("iso-8859-1", errors="strict")
    non_ascii = Counter(byte for byte in csv_raw if byte >= 128)
    csv_rows = list(csv.DictReader(latin_text.splitlines(), delimiter="\t"))
    csv_by_code: dict[str, list[dict[str, str | int]]] = defaultdict(list)
    for record_index, row in enumerate(csv_rows, 2):
        csv_by_code[row["code"]].append({"record_index": record_index, **row})
    csv_codes = set(csv_by_code)
    levels = Counter(code_level(code) for code in csv_codes)

    graph = Graph().parse(SOURCE / "raw/suggestion4.ttl", format="turtle")
    vocab_graph = Graph().parse(SOURCE / "raw/vocabulary.ttl", format="turtle")
    concepts = set(graph.subjects(RDF.type, SKOS.Concept))
    current = {
        subject for subject in concepts
        if str(subject).startswith(PREFIX) and CODE.fullmatch(str(subject)[len(PREFIX):])
    }
    by_code = {str(subject)[len(PREFIX):]: subject for subject in current}

    label_rows = []
    for code in sorted(csv_codes & set(by_code)):
        source_row = csv_by_code[code][0]
        labels = sorted(
            str(value) for value in graph.objects(by_code[code], SKOS.prefLabel)
            if isinstance(value, Literal) and value.language == "en"
        )
        if labels != [source_row["text"]]:
            label_rows.append({
                "code": code,
                "csv_record_index": source_row["record_index"],
                "rdf_uri": str(by_code[code]),
                "csv_text": source_row["text"],
                "rdf_english_preferred_labels": labels,
                "exact_label_match": False,
            })

    hierarchy_rows = []
    all_hierarchy = []
    for code, subject in sorted(by_code.items()):
        parents = sorted(str(value) for value in graph.objects(subject, SKOS.broader))
        all_hierarchy.append({"code": code, "parents": parents})
        expected = expected_parent(code)
        if parents != expected:
            hierarchy_rows.append({
                "code": code,
                "recorded_parents": parents,
                "notation_derived_parents": expected,
            })

    predicates = [DATA_VOCAB.seeAlso, DATA_VOCAB.seeMainly,
                  DATA_VOCAB.seeConditionally]
    direct = sorted(
        (str(subject), str(predicate), str(obj))
        for subject in current for predicate in predicates
        for obj in graph.objects(subject, predicate)
    )
    direct_conditionals = {
        (subject, obj) for subject, predicate, obj in direct
        if predicate == str(DATA_VOCAB.seeConditionally)
    }
    reification_subjects = sorted(
        set(graph.subjects(RDF.type, DATA_VOCAB.seeForStatement)), key=str
    )
    linkage_ledger = []
    linkage_errors = []
    for node in reification_subjects:
        subjects = list(graph.objects(node, RDF.subject))
        predicates_found = list(graph.objects(node, RDF.predicate))
        objects = list(graph.objects(node, RDF.object))
        scopes = list(graph.objects(node, DATA_VOCAB.scope))
        incoming = list(graph.subjects(DATA_VOCAB.seeFor, node))
        row = {
            "reification_uri": str(node),
            "subjects": sorted(str(value) for value in subjects),
            "predicates": sorted(str(value) for value in predicates_found),
            "objects": sorted(str(value) for value in objects),
            "scopes": sorted({
                "lexical": str(value),
                "datatype": str(value.datatype) if isinstance(value, Literal) and value.datatype else None,
                "language": value.language if isinstance(value, Literal) else None,
            }.items() for value in scopes),
            "incoming_see_for_subjects": sorted(str(value) for value in incoming),
        }
        # Convert the sortable item-pair lists back to dictionaries for readable JSON.
        row["scopes"] = [dict(value) for value in row["scopes"]]
        linkage_ledger.append(row)
        good = (
            len(subjects) == len(predicates_found) == len(objects) == len(scopes) == len(incoming) == 1
            and predicates_found[0] == DATA_VOCAB.seeConditionally
            and incoming[0] == subjects[0]
            and subjects[0] in current
            and objects[0] in current
            and (str(subjects[0]), str(objects[0])) in direct_conditionals
            and bool(str(scopes[0]))
        )
        if not good:
            linkage_errors.append(str(node))
    reified_pairs = [
        (row["subjects"][0], row["objects"][0]) for row in linkage_ledger
        if len(row["subjects"]) == len(row["objects"]) == 1
    ]
    scope_types = Counter(
        (scope["datatype"], scope["language"])
        for row in linkage_ledger for scope in row["scopes"]
    )

    collection = URIRef(PREFIX + "GeneralReferenceWorksCollection")
    collection_members = sorted(str(value) for value in graph.objects(collection, SKOS.member))
    collection_record = {
        "uri": str(collection),
        "types": sorted(str(value) for value in graph.objects(collection, RDF.type)),
        "labels": sorted((str(value), value.language) for value in graph.objects(collection, SKOS.prefLabel)),
        "notations": sorted(str(value) for value in graph.objects(collection, SKOS.notation)),
        "member_count": len(collection_members),
        "all_members_are_current_concepts": all(URIRef(value) in current for value in collection_members),
        "incoming_selected_references": [row for row in direct if row[2] == str(collection)],
    }
    nonconcept_targets = sorted({
        obj for _, _, obj in direct if URIRef(obj) not in current
    })

    used_data_vocab = sorted({
        str(predicate) for _, predicate, _ in graph
        if str(predicate).startswith(str(DATA_VOCAB))
    })
    vocabulary_subjects = {str(subject) for subject in vocab_graph.subjects()}
    data_class = URIRef(str(DATA_VOCAB.seeForStatement))
    file_class = URIRef(FILE_VOCAB_PREFIX + "SeeForStatement")
    equivalence_predicates = {OWL.sameAs, OWL.equivalentClass, OWL.equivalentProperty}
    explicit_bridges = sorted(
        (str(s), str(p), str(o)) for s, p, o in set(graph) | set(vocab_graph)
        if p in equivalence_predicates and {s, o} == {data_class, file_class}
    )

    ttl_lines = (SOURCE / "raw/suggestion4.ttl").read_text(encoding="utf-8").splitlines()
    csv_lines = latin_text.splitlines()
    hierarchy_locators = []
    for row in hierarchy_rows:
        code = row["code"]
        header = locate(ttl_lines, "###  " + PREFIX + code)
        # Parents recur globally, so scan only this subject block.
        stop = next((i for i in range(header, len(ttl_lines)) if not ttl_lines[i].strip()), len(ttl_lines))
        block = ttl_lines[header - 1:stop]
        parent_lines = [
            header + i for i, line in enumerate(block)
            if any(parent in line for parent in row["recorded_parents"])
        ]
        hierarchy_locators.append({"code": code, "header_line": header,
                                   "parent_lines": parent_lines})

    label_probe_codes = ["00A79", "01A07", "01A29"]
    label_probes = []
    by_difference = {row["code"]: row for row in label_rows}
    for code in label_probe_codes:
        item = dict(by_difference[code])
        item["csv_physical_line"] = int(item["csv_record_index"])
        item["rdf_header_line"] = locate(ttl_lines, "###  " + PREFIX + code)
        label_probes.append(item)

    home_lines = (SOURCE / "raw/official-home.html").read_text(encoding="utf-8").splitlines()
    readme_lines = (SOURCE / "raw/upstream-readme.md").read_text(encoding="utf-8").splitlines()
    license_lines = (SOURCE / "raw/upstream-license.md").read_text(encoding="utf-8").splitlines()
    vocab_lines = (SOURCE / "raw/vocabulary.ttl").read_text(encoding="utf-8").splitlines()
    source_terms = {
        "official_home": {
            "csv_link_line": locate(home_lines, 'href="/MSC_2020.csv"'),
            "maintainers_line": locate(home_lines, "collaborate on maintaining"),
            "published_license_line": locate(home_lines, "jointly published"),
            "historical_count_line": locate(home_lines, "The new MSC contains"),
            "license_href_present": any("creativecommons.org/licenses/by-nc-sa/4.0" in line for line in home_lines),
            "historical_prose_counts": {"top": 63, "three_digit": 529, "five_digit": 6022},
        },
        "suggestion_repository": {
            "suggestion_wording_line": locate(readme_lines, "suggest a SKOS serialisation"),
            "license_title_line": locate_exact(license_lines, "Attribution-NonCommercial-ShareAlike 4.0 International"),
            "attribution_condition_line": locate(license_lines, "a. Attribution."),
            "sharealike_condition_line": locate(license_lines, "b. ShareAlike."),
        },
        "vocabulary": {
            "namespace_line": locate(vocab_lines, "@prefix : <" + FILE_VOCAB_PREFIX + ">"),
            "class_line": locate(vocab_lines, FILE_VOCAB_PREFIX + "SeeForStatement"),
        },
    }

    author = json.loads((SOURCE / "inspection-03.json").read_text(encoding="utf-8"))
    author_simplified_reifications = [
        {
            "uri": row["reification_uri"],
            "subjects": row["subjects"],
            "predicates": row["predicates"],
            "objects": row["objects"],
            "scopes": sorted(scope["lexical"] for scope in row["scopes"]),
        }
        for row in linkage_ledger
    ]
    comparisons = {
        "csv_summary_matches": author["csv"] == {
            "format": "tab-delimited despite .csv filename",
            "decoding": "iso-8859-1",
            "decoding_status": "explicit interpretation; source bytes retained; no charset declared by HTTP",
            "row_count": len(csv_rows),
            "unique_code_count": len(csv_codes),
            "duplicate_codes": sorted(code for code, group in csv_by_code.items() if len(group) != 1),
            "invalid_codes": sorted(code for code in csv_codes if code_level(code) == "invalid"),
            "top_level_count": levels["top"],
            "letter_group_count": levels["letter_group"],
            "hyphen_leaf_count": levels["hyphen_leaf"],
            "letter_leaf_count": levels["letter_leaf"],
        },
        "code_sets_match_author": author["code_comparison"] == {
            "csv_only": sorted(csv_codes - set(by_code)),
            "rdf_only": sorted(set(by_code) - csv_codes),
            "shared_count": len(csv_codes & set(by_code)),
        },
        "label_difference_rows_match_author": label_rows == author["labels"]["differences"],
        "hierarchy_disagreements_match_author": hierarchy_rows == author["hierarchy"]["notation_disagreements"],
        "all_hierarchy_rows_match_author": all_hierarchy == author["hierarchy"]["records"],
        "direct_references_match_author": [list(row) for row in direct] == author["cross_references"]["direct_triples"],
        "reifications_match_author": author_simplified_reifications == author["cross_references"]["reified_conditionals"],
    }

    checks = {
        "all_source_hashes_match": all(row["bytes_match"] and row["sha256_match"] for row in source_integrity),
        "utf8_strict_decode_failed": utf8_failure is not None,
        "latin1_round_trip_exact": latin_text.encode("iso-8859-1") == csv_raw,
        "no_replacement_character": "\ufffd" not in latin_text,
        "encoding_non_ascii_counts_match_correction": dict(sorted(non_ascii.items())) == {201: 6, 224: 12, 225: 2, 228: 22, 232: 16, 233: 36, 243: 2, 246: 44, 252: 14, 253: 2},
        "csv_header_exact": list(csv_rows[0]) == ["code", "text", "description"],
        "csv_codes_unique_and_valid": len(csv_rows) == len(csv_codes) and levels["invalid"] == 0,
        "code_sets_equal": csv_codes == set(by_code),
        "label_count_accounting": len(label_rows) == 120 and len(csv_codes) - len(label_rows) == 6483,
        "hierarchy_issue_set_exact": [row["code"] for row in hierarchy_rows] == ["32-00", "32-01", "32-02", "32-03", "32-04", "32-06", "32-08", "32-11"],
        "no_dangling_hierarchy_parent": all(URIRef(parent) in current for row in all_hierarchy for parent in row["parents"]),
        "conditional_linkage_count": len(direct_conditionals) == len(reification_subjects) == len(linkage_ledger) == 415,
        "conditional_linkages_complete": not linkage_errors,
        "conditional_linkages_bijective": len(set(reified_pairs)) == 415 and set(reified_pairs) == direct_conditionals,
        "reification_headers_count": sum(line.startswith("###  " + PREFIX + "seeForStatement-") for line in ttl_lines) == 415,
        "selected_reference_counts": Counter(predicate for _, predicate, _ in direct) == Counter({str(DATA_VOCAB.seeAlso): 2642, str(DATA_VOCAB.seeConditionally): 415, str(DATA_VOCAB.seeMainly): 26}),
        "only_nonconcept_target_is_collection": nonconcept_targets == [str(collection)],
        "collection_resolves_as_collection": str(SKOS.Collection) in collection_record["types"] and collection_record["member_count"] == 62 and collection_record["all_members_are_current_concepts"],
        "data_vocab_predicates_absent_from_separate_vocab": all(value not in vocabulary_subjects for value in used_data_vocab),
        "vocabulary_iri_and_case_mismatch_present": len(reification_subjects) == 415 and len(set(graph.subjects(RDF.type, URIRef(str(DATA_VOCAB) + "SeeForStatement")))) == 0 and str(file_class) in vocabulary_subjects,
        "no_explicit_class_bridge": not explicit_bridges,
        "author_comparisons_all_match": all(comparisons.values()),
        "source_term_locators_present": all([
            source_terms["official_home"]["license_href_present"],
            source_terms["official_home"]["csv_link_line"] > 0,
            source_terms["suggestion_repository"]["suggestion_wording_line"] > 0,
            source_terms["suggestion_repository"]["attribution_condition_line"] > 0,
        ]),
    }

    special_scope_rows = [
        row for row in linkage_ledger
        if any(scope["datatype"] is None or scope["language"] for scope in row["scopes"])
    ]
    result = {
        "schema_version": "msc-independent-source-check-v1",
        "source_manifest_sha256": sha_bytes(manifest_bytes),
        "source_integrity": source_integrity,
        "encoding": {
            "utf8_failure": utf8_failure,
            "iso_8859_1_round_trip": checks["latin1_round_trip_exact"],
            "replacement_character_count": latin_text.count("\ufffd"),
            "non_ascii_byte_counts": {str(key): value for key, value in sorted(non_ascii.items())},
        },
        "codes": {
            "csv_rows": len(csv_rows),
            "csv_unique": len(csv_codes),
            "rdf_current": len(by_code),
            "level_counts": dict(sorted(levels.items())),
            "csv_minus_rdf": sorted(csv_codes - set(by_code)),
            "rdf_minus_csv": sorted(set(by_code) - csv_codes),
        },
        "labels": {
            "exact_match_count": len(csv_codes) - len(label_rows),
            "difference_count": len(label_rows),
            "difference_ledger_sha256": canonical_sha(label_rows),
            "probes": label_probes,
            "interpretation": "Exact inequality is a byte-level/string observation. The probes include surface rewording, a moved usage qualification, and a potentially scope-changing omission; no blanket error label is assigned to all 120 rows.",
        },
        "hierarchy": {
            "record_count": len(all_hierarchy),
            "disagreement_count": len(hierarchy_rows),
            "disagreements": hierarchy_rows,
            "source_locators": hierarchy_locators,
            "interpretation": "All eight are actual dual-parent RDF records. The notation rule supplies a comparison expectation only; neither parent is silently deleted or declared erroneous.",
        },
        "cross_references": {
            "selected_count": len(direct),
            "counts_by_predicate": dict(sorted(Counter(predicate for _, predicate, _ in direct).items())),
            "conditional_count": len(direct_conditionals),
            "reification_count": len(linkage_ledger),
            "linkage_ledger_sha256": canonical_sha(linkage_ledger),
            "linkage_errors": linkage_errors,
            "scope_term_forms": [
                {"datatype": key[0], "language": key[1], "count": count}
                for key, count in sorted(scope_types.items(), key=lambda pair: str(pair[0]))
            ],
            "special_scope_records": special_scope_rows,
            "nonconcept_targets": nonconcept_targets,
            "collection_target": collection_record,
            "interpretation": "Outside the selected code-concept set does not mean unresolved. The sole such target is a defined SKOS collection and must retain target_kind=collection rather than being expanded into inferred code-to-code edges.",
        },
        "vocabulary_mismatch": {
            "dataset_namespace": str(DATA_VOCAB),
            "separate_vocabulary_namespace": FILE_VOCAB_PREFIX,
            "dataset_reification_class": str(data_class),
            "separate_vocabulary_class": str(file_class),
            "used_dataset_predicates": used_data_vocab,
            "used_dataset_predicates_absent_as_separate_vocabulary_subjects": sorted(value for value in used_data_vocab if value not in vocabulary_subjects),
            "explicit_equivalence_bridges": explicit_bridges,
            "interpretation": "The pinned files use distinct case-sensitive IRIs with no checked explicit bridge. Preserve the observed source IRIs and do not merge them by spelling similarity.",
        },
        "source_and_terms": source_terms,
        "comparison_to_inspection_03": comparisons,
        "checks": checks,
        "all_pass": all(checks.values()),
        "limitations": [
            "This verifies the declared structural fields and full selected relation ledgers, not every RDF triple or the mathematical correctness of classifications.",
            "No label mismatch is called an error without semantic adjudication.",
            "No importer, product behavior, performance, completeness, impact, or novelty claim is tested here.",
        ],
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({
        "output": str(args.output),
        "all_pass": result["all_pass"],
        "checks": len(checks),
        "codes": len(csv_codes),
        "label_differences": len(label_rows),
        "hierarchy_disagreements": len(hierarchy_rows),
        "conditional_linkages": len(linkage_ledger),
    }, sort_keys=True))


if __name__ == "__main__":
    main()
