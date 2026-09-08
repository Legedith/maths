"""Independent exhaustive source-to-output checker for the frozen MSC adapter."""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import re
from collections import Counter, defaultdict
from pathlib import Path
import sys

import rdflib
from rdflib import BNode, Graph, Literal, Namespace, URIRef
from rdflib.namespace import RDF, SKOS

CSV_HASH = "f7c889354c202551fe01f89bad2ae95ccadec4c57ac1f6f9de38bbd658d3c78c"
TTL_HASH = "ee4afa1f198ffd0f5ea807377e46420c5fd7537991928c67c759fa44640421e9"
MANIFEST_HASH = "90602331e367f13fb21b0bc1d535f45326b6adf67165a369a681b6738f468f70"
IMPORTER_HASH = "ae950530f861a55ae894c27f02a759c68207eff18aba8a9dcfa5bf3b326fba12"
CONTRACT_HASH = "85108635a9b398db4d9c0fb3720aaccf3b69ef749666e8c83261659edf5404f6"
REVISION = "33972ddb6a72c3660a6e499ee5f881b57fa92d41"
PREFIX = "http://msc2020.org/resources/MSC/msc2020/"
VOCAB = Namespace(PREFIX + "mscvocab#")
CODE_PATTERN = re.compile(r"[0-9]{2}(?:-XX|-[0-9]{2}|[A-Z](?:xx|[0-9]{2}))\Z")


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def rdf_term(value: URIRef | Literal | BNode) -> dict:
    if isinstance(value, URIRef):
        return {"kind": "uri", "value": str(value)}
    if isinstance(value, Literal):
        return {
            "kind": "literal",
            "value": str(value),
            "language": value.language,
            "datatype": str(value.datatype) if value.datatype else None,
        }
    raise AssertionError(f"Unexpected anonymous RDF term: {value!r}")


def sorted_terms(values) -> list[dict]:
    return sorted((rdf_term(value) for value in values), key=lambda row: json.dumps(row, sort_keys=True))


def statements(graph: Graph, subject: URIRef) -> list[dict]:
    return [
        {"predicate_uri": str(predicate), "objects": sorted_terms(graph.objects(subject, predicate))}
        for predicate in sorted(set(graph.predicates(subject)), key=str)
    ]


def nav_parent(code: str) -> str | None:
    if code.endswith("-XX"):
        return None
    if code[2] == "-" or code.endswith("xx"):
        return code[:2] + "-XX"
    return code[:3] + "xx"


def kind(code: str) -> str:
    if code.endswith("-XX"):
        return "top_level"
    if code.endswith("xx"):
        return "letter_group"
    return "facet_leaf" if code[2] == "-" else "subject_leaf"


def reconstruct(source_root: Path) -> tuple[dict[str, dict], dict]:
    manifest_path = source_root / "source-manifest.json"
    csv_path = source_root / "raw" / "official.csv"
    ttl_path = source_root / "raw" / "suggestion4.ttl"
    assert sha(manifest_path) == MANIFEST_HASH
    assert sha(csv_path) == CSV_HASH
    assert sha(ttl_path) == TTL_HASH
    manifest = json.loads(manifest_path.read_bytes())
    assert manifest["failures"] == []
    assert manifest["repository_revision"] == REVISION
    by_name = {row["name"]: row for row in manifest["sources"]}
    assert by_name["official.csv"]["sha256"] == CSV_HASH
    assert by_name["official.csv"]["path"] == "raw/official.csv"
    assert by_name["suggestion4.ttl"]["sha256"] == TTL_HASH
    assert by_name["suggestion4.ttl"]["path"] == "raw/suggestion4.ttl"

    subjects = []
    with csv_path.open(encoding="iso-8859-1", newline="") as stream:
        reader = csv.DictReader(stream, delimiter="\t")
        assert reader.fieldnames == ["code", "text", "description"]
        previous_physical_line = reader.line_num
        for data_record, row in enumerate(reader, 1):
            assert set(row) == {"code", "text", "description"}
            assert all(isinstance(value, str) and value for value in row.values())
            assert CODE_PATTERN.fullmatch(row["code"])
            row_kind = kind(row["code"])
            subjects.append(
                {
                    "code": row["code"],
                    "label_as_recorded": row["text"],
                    "description_as_recorded": row["description"],
                    "kind": row_kind,
                    "navigation_parent_code": nav_parent(row["code"]),
                    "source_locator": {
                        "source_id": "msc2020-official-csv",
                        "data_record": data_record,
                        "physical_lines": {"start": previous_physical_line + 1, "end": reader.line_num},
                    },
                }
            )
            previous_physical_line = reader.line_num
    assert previous_physical_line == sum(1 for _ in csv_path.open(encoding="iso-8859-1", newline=""))
    codes = {row["code"] for row in subjects}
    assert len(subjects) == len(codes) == 6603
    assert all(row["navigation_parent_code"] is None or row["navigation_parent_code"] in codes for row in subjects)
    parents_used = {row["navigation_parent_code"] for row in subjects if row["navigation_parent_code"]}
    for row in subjects:
        row["hierarchy_level"] = 1 if row["kind"] == "top_level" else (3 if row["kind"] == "subject_leaf" else 2)
        row["is_leaf"] = row["code"] not in parents_used

    graph = Graph().parse(ttl_path, format="turtle")
    current = {URIRef(PREFIX + code) for code in codes}
    assert set(graph.subjects(RDF.type, SKOS.Concept)) == current
    note_sort_collisions = []
    for row in subjects:
        subject = URIRef(PREFIX + row["code"])
        row["uri"] = str(subject)
        row["classification_status"] = "upstream_subject_classification"
        row["rdf_source_id"] = "msc2020-skos-suggestion4"
        row["rdf_labels"] = sorted_terms(graph.objects(subject, SKOS.prefLabel))
        row["rdf_broader_uris"] = sorted(str(parent) for parent in graph.objects(subject, SKOS.broader))
        expected_parent = [] if row["navigation_parent_code"] is None else [PREFIX + row["navigation_parent_code"]]
        row["hierarchy_disagreement"] = row["rdf_broader_uris"] != expected_parent
        english = sorted(
            str(label)
            for label in graph.objects(subject, SKOS.prefLabel)
            if isinstance(label, Literal) and label.language == "en"
        )
        row["exact_label_difference"] = english != [row["label_as_recorded"]]
        raw_notes = list(graph.objects(subject, SKOS.scopeNote))
        grouped = Counter(str(note) for note in raw_notes)
        note_sort_collisions.extend((row["code"], lexical) for lexical, count in grouped.items() if count > 1)
        notes = []
        for note in sorted(raw_notes, key=str):
            item = {"term": rdf_term(note)}
            if isinstance(note, URIRef):
                item["source_statements"] = statements(graph, note)
            notes.append(item)
        row["rdf_scope_notes"] = notes
    assert note_sort_collisions == []

    scope_records = defaultdict(list)
    typed_statements = sorted(set(graph.subjects(RDF.type, VOCAB.seeForStatement)), key=str)
    for statement in typed_statements:
        endpoint_values = [list(graph.objects(statement, predicate)) for predicate in (RDF.subject, RDF.predicate, RDF.object)]
        assert all(len(values) == 1 for values in endpoint_values)
        source, predicate, target = (values[0] for values in endpoint_values)
        assert source in current
        assert predicate == VOCAB.seeConditionally
        qualifiers = sorted_terms(graph.objects(statement, VOCAB.scope))
        assert qualifiers and all(row["kind"] == "literal" and row["value"] for row in qualifiers)
        assert (source, predicate, target) in graph
        scope_records[(source, predicate, target)].append({"uri": str(statement), "scopes": qualifiers})

    selected_predicates = (VOCAB.seeAlso, VOCAB.seeMainly, VOCAB.seeConditionally)
    raw_reference_triples = sorted(
        ((source, predicate, target) for source in current for predicate in selected_predicates for target in graph.objects(source, predicate)),
        key=lambda triple: tuple(map(str, triple)),
    )
    relations = []
    collection_uris = set()
    for source, predicate, target in raw_reference_triples:
        if target in current:
            target_kind = "subject"
        elif (target, RDF.type, SKOS.Collection) in graph:
            target_kind = "collection"
            collection_uris.add(target)
        else:
            raise AssertionError(f"Unknown reference target: {target}")
        records = scope_records.get((source, predicate, target), [])
        if predicate == VOCAB.seeConditionally:
            assert records
        relations.append(
            {
                "from_uri": str(source),
                "predicate_uri": str(predicate),
                "to_uri": str(target),
                "target_kind": target_kind,
                "status": "upstream_classification_reference",
                "source_id": "msc2020-skos-suggestion4",
                "scope_records": records,
            }
        )
    collections = []
    for collection in sorted(collection_uris, key=str):
        members = list(graph.objects(collection, SKOS.member))
        assert all(member in current for member in members)
        collections.append(
            {
                "uri": str(collection),
                "kind": "classification_collection",
                "labels": sorted_terms(graph.objects(collection, SKOS.prefLabel)),
                "member_uris": sorted(map(str, members)),
                "source_id": "msc2020-skos-suggestion4",
            }
        )

    metadata = {
        "schema_version": "msc-subject-index-v1",
        "attribution": "MSC2020: Mathematical Reviews and zbMATH. SKOS conversion: Susanne Arndt, Patrick Ion, Mila Runnwerth, Moritz Schubotz and Olaf Teschke; TIBHannover/MSC2020_SKOS.",
        "data_license": "CC-BY-NC-SA-4.0",
        "data_license_url": "https://creativecommons.org/licenses/by-nc-sa/4.0/",
        "adaptations": "Converted to a navigation index; derived navigation parents from MSC code structure; retained source labels, descriptions, relation types, qualifiers, collection targets and recorded hierarchy disagreements.",
        "sources": [
            {
                "id": "msc2020-official-csv",
                "url": "https://msc2020.org/MSC_2020.csv",
                "sha256": CSV_HASH,
                "decoding": "ISO-8859-1 interpretation; raw source has no HTTP charset declaration",
            },
            {
                "id": "msc2020-skos-suggestion4",
                "repository": "https://github.com/TIBHannover/MSC2020_SKOS",
                "commit": REVISION,
                "path": "msc-2020-suggestion4.ttl",
                "sha256": TTL_HASH,
                "status": "upstream_suggested_serialization",
            },
        ],
        "source_manifest_sha256": MANIFEST_HASH,
        "navigation_parent_derivation": "Top-level XX-XX has no parent; XX-NN and XXAxx attach to XX-XX; XXANN attaches to XXAxx. This is separate from recorded RDF broader triples.",
        "limitations": [
            "Classification categories index subjects; they do not enumerate all known mathematics.",
            "Cross-references are upstream subject-navigation links, not proved equivalences or implications.",
            "No subject is labeled unsolved because the Atlas has no reviewed entry for it.",
            "Exact label differences and hierarchy disagreements remain visible source comparisons.",
            "The eight hierarchy disagreement flags are preserved; no RDF parent is silently removed.",
            "No automatic mapping from the curated Atlas or MathGloss to MSC codes is asserted.",
        ],
    }
    summary = {
        "schema_version": "msc-import-summary-v1",
        "subjects": len(subjects),
        "subject_kinds": dict(sorted(Counter(row["kind"] for row in subjects).items())),
        "hierarchy_levels": dict(sorted(Counter(row["hierarchy_level"] for row in subjects).items())),
        "references": len(relations),
        "references_by_predicate": dict(sorted(Counter(row["predicate_uri"] for row in relations).items())),
        "scope_records": sum(len(row["scope_records"]) for row in relations),
        "referenced_collections": len(collections),
        "hierarchy_disagreements": [row["code"] for row in subjects if row["hierarchy_disagreement"]],
        "exact_label_difference_count": sum(row["exact_label_difference"] for row in subjects),
        "rdf_scope_note_count": sum(len(row["rdf_scope_notes"]) for row in subjects),
    }
    expected_native = {
        "subjects.json": {"metadata": metadata, "subjects": subjects},
        "references.json": {"schema_version": "msc-references-v1", "relations": relations, "collections": collections},
        "summary.json": summary,
    }
    # Match the JSON data model: integer mapping keys become decimal strings.
    expected = json.loads(json.dumps(expected_native, ensure_ascii=False))
    scope_form_counts = Counter(
        (scope["language"], scope["datatype"])
        for records in scope_records.values()
        for record in records
        for scope in record["scopes"]
    )
    facts = {
        "csv_records": len(subjects),
        "csv_physical_lines": previous_physical_line,
        "hierarchy_levels": {str(key): value for key, value in summary["hierarchy_levels"].items()},
        "leaf_true": sum(row["is_leaf"] for row in subjects),
        "leaf_false": sum(not row["is_leaf"] for row in subjects),
        "hierarchy_disagreements": summary["hierarchy_disagreements"],
        "exact_label_difference_count": summary["exact_label_difference_count"],
        "rdf_labels": sum(len(row["rdf_labels"]) for row in subjects),
        "rdf_broader_terms": sum(len(row["rdf_broader_uris"]) for row in subjects),
        "rdf_scope_notes": summary["rdf_scope_note_count"],
        "reference_triples": len(raw_reference_triples),
        "reference_predicates": summary["references_by_predicate"],
        "typed_conditional_reifications": len(typed_statements),
        "scope_records": summary["scope_records"],
        "scope_terms": sum(len(record["scopes"]) for records in scope_records.values() for record in records),
        "scope_term_forms": {
            f"language={language!r};datatype={datatype!r}": count
            for (language, datatype), count in sorted(scope_form_counts.items(), key=lambda pair: str(pair[0]))
        },
        "referenced_collections": len(collections),
        "collection_members": sum(len(row["member_uris"]) for row in collections),
    }
    return expected, facts


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--source-root", type=Path, required=True)
    parser.add_argument("--candidate-dir", type=Path, required=True)
    parser.add_argument("--author-dir", type=Path, required=True)
    parser.add_argument("--project-data-dir", type=Path, required=True)
    parser.add_argument("--project-package-dir", type=Path, required=True)
    parser.add_argument("--output-json", type=Path, required=True)
    args = parser.parse_args()
    if args.output_json.exists():
        raise FileExistsError(args.output_json)

    checks = []
    def check(check_id: str, condition: bool, details) -> None:
        checks.append({"id": check_id, "pass": bool(condition), "details": details})

    check("rdflib-version", rdflib.__version__ == "7.1.4", rdflib.__version__)
    check("package-importer-pin", sha(args.project_package_dir / "import_msc.py") == IMPORTER_HASH, sha(args.project_package_dir / "import_msc.py"))
    check("package-contract-pin", sha(args.project_package_dir / "contract-v1.md") == CONTRACT_HASH, sha(args.project_package_dir / "contract-v1.md"))
    packaged_raw = sorted(path.relative_to(args.source_root).as_posix() for path in (args.source_root / "raw").iterdir() if path.is_file())
    check("portable-raw-file-set", packaged_raw == ["raw/official.csv", "raw/suggestion4.ttl"], packaged_raw)

    expected, facts = reconstruct(args.source_root)
    files = ["subjects.json", "references.json", "summary.json"]
    byte_records = []
    for name in files:
        candidate = args.candidate_dir / name
        author = args.author_dir / name
        project = args.project_data_dir / name
        expected_object = expected[name]
        candidate_object = json.loads(candidate.read_bytes())
        author_object = json.loads(author.read_bytes())
        project_object = json.loads(project.read_bytes())
        row_count = None
        if isinstance(candidate_object, dict):
            if isinstance(candidate_object.get("subjects"), list):
                row_count = len(candidate_object["subjects"])
            elif isinstance(candidate_object.get("relations"), list):
                row_count = len(candidate_object["relations"])
        check(f"source-object-{name}", candidate_object == expected_object, {"rows": row_count})
        check(f"author-object-{name}", author_object == expected_object, sha(author))
        check(f"project-object-{name}", project_object == expected_object, sha(project))
        hashes = {"candidate": sha(candidate), "author_run_03": sha(author), "project_data": sha(project)}
        check(f"byte-equality-{name}", len(set(hashes.values())) == 1, hashes)
        byte_records.append({"file": name, "bytes": candidate.stat().st_size, "sha256": hashes["candidate"], "all_three_equal": len(set(hashes.values())) == 1})

    expected_counts = {
        "csv_records": 6603,
        "hierarchy_levels": {"1": 63, "2": 1037, "3": 5503},
        "hierarchy_disagreements": ["32-00", "32-01", "32-02", "32-03", "32-04", "32-06", "32-08", "32-11"],
        "exact_label_difference_count": 120,
        "rdf_scope_notes": 2271,
        "reference_triples": 3083,
        "typed_conditional_reifications": 415,
        "scope_records": 415,
        "scope_terms": 415,
        "referenced_collections": 1,
        "collection_members": 62,
    }
    for key, value in expected_counts.items():
        check(f"count-{key}", facts[key] == value, facts[key])
    check("reference-predicate-counts", sorted(facts["reference_predicates"].values()) == [26, 415, 2642], facts["reference_predicates"])
    check("scope-term-forms", facts["scope_term_forms"] == {
        f"language={None!r};datatype={str(RDF.XMLLiteral)!r}": 414,
        f"language={'en'!r};datatype={None!r}": 1,
    }, facts["scope_term_forms"])
    check("hierarchy-level-vs-leaf-distinct", facts["leaf_true"] != 5503 and facts["hierarchy_levels"]["2"] == 1037, {"leaf_true": facts["leaf_true"], "leaf_false": facts["leaf_false"], "levels": facts["hierarchy_levels"]})

    result = {
        "schema_version": "msc-import-independent-check-v1",
        "auditor": "/root/sol_symmetry_audit",
        "all_pass": all(row["pass"] for row in checks),
        "checks": checks,
        "source_facts": facts,
        "byte_comparison": byte_records,
    }
    args.output_json.parent.mkdir(parents=True, exist_ok=True)
    args.output_json.write_text(json.dumps(result, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(json.dumps({"all_pass": result["all_pass"], "checks": len(checks), "facts": facts}, sort_keys=True, default=str))
    return 0 if result["all_pass"] else 1


if __name__ == "__main__":
    sys.exit(main())
