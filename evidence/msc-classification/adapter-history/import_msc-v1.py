"""Compile source-pinned classification navigation; never infer theorem edges."""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import re
from collections import Counter, defaultdict
from pathlib import Path

import rdflib
from rdflib import BNode, Graph, Literal, Namespace, URIRef
from rdflib.namespace import RDF, SKOS

CSV_HASH = "f7c889354c202551fe01f89bad2ae95ccadec4c57ac1f6f9de38bbd658d3c78c"
TTL_HASH = "ee4afa1f198ffd0f5ea807377e46420c5fd7537991928c67c759fa44640421e9"
MANIFEST_HASH = "90602331e367f13fb21b0bc1d535f45326b6adf67165a369a681b6738f468f70"
REVISION = "33972ddb6a72c3660a6e499ee5f881b57fa92d41"
PREFIX = "http://msc2020.org/resources/MSC/msc2020/"
VOCAB = Namespace(PREFIX + "mscvocab#")
PATTERN = re.compile(r"[0-9]{2}(?:-XX|-[0-9]{2}|[A-Z](?:xx|[0-9]{2}))\Z")


def require(condition: bool, message: str) -> None:
    if not condition:
        raise ValueError(message)


def pinned(path: Path, expected: str) -> bytes:
    data = path.read_bytes()
    require(hashlib.sha256(data).hexdigest() == expected, f"Source pin mismatch: {path.name}")
    return data


def term(value: URIRef | Literal | BNode) -> dict:
    if isinstance(value, URIRef):
        return {"kind": "uri", "value": str(value)}
    if isinstance(value, Literal):
        return {"kind": "literal", "value": str(value), "language": value.language,
                "datatype": str(value.datatype) if value.datatype else None}
    raise ValueError("Anonymous RDF node in selected subject data needs explicit preservation design")


def terms(values) -> list[dict]:
    return sorted((term(value) for value in values), key=lambda row: json.dumps(row, sort_keys=True))


def source_statements(graph: Graph, subject: URIRef) -> list[dict]:
    return [{"predicate_uri": str(predicate), "objects": terms(graph.objects(subject, predicate))}
            for predicate in sorted(set(graph.predicates(subject)), key=str)]


def parent(code: str) -> str | None:
    if code.endswith("-XX"):
        return None
    if code[2] == "-" or code.endswith("xx"):
        return code[:2] + "-XX"
    return code[:3] + "xx"


def classify(code: str) -> str:
    if code.endswith("-XX"):
        return "top_level"
    if code.endswith("xx"):
        return "letter_group"
    return "facet_leaf" if code[2] == "-" else "subject_leaf"


def compile_index(source_root: Path) -> dict[str, dict]:
    require(rdflib.__version__ == "7.1.4", "Use the frozen RDFLib 7.1.4 environment")
    manifest_bytes = pinned(source_root / "source-manifest.json", MANIFEST_HASH)
    manifest = json.loads(manifest_bytes)
    require(not manifest["failures"], "Source retrieval has failures")
    require(manifest["repository_revision"] == REVISION, "Unexpected repository revision")
    for record in manifest["sources"]:
        source_path = (source_root / record["path"]).resolve()
        require(source_path.is_relative_to(source_root.resolve()), "Source path escapes source root")
        require(len(pinned(source_path, record["sha256"])) == record["bytes"], "Source size differs")
    pinned(source_root / "raw/official.csv", CSV_HASH)
    pinned(source_root / "raw/suggestion4.ttl", TTL_HASH)
    subjects = []
    with (source_root / "raw/official.csv").open(encoding="iso-8859-1", newline="") as stream:
        reader = csv.DictReader(stream, delimiter="\t")
        require(reader.fieldnames == ["code", "text", "description"], "Unexpected CSV header")
        previous_line = reader.line_num
        for number, row in enumerate(reader, 1):
            require(set(row) == {"code", "text", "description"}, "Unexpected CSV fields")
            require(all(isinstance(value, str) and value for value in row.values()), "Empty CSV field")
            require(PATTERN.fullmatch(row["code"]) is not None, "Invalid MSC code")
            subjects.append({"code": row["code"], "label_as_recorded": row["text"],
                             "description_as_recorded": row["description"],
                             "kind": classify(row["code"]),
                             "navigation_parent_code": parent(row["code"]),
                             "source_locator": {"source_id": "msc2020-official-csv",
                                                "data_record": number,
                                                "physical_lines": {"start": previous_line + 1,
                                                                   "end": reader.line_num}}})
            previous_line = reader.line_num
    codes = {row["code"] for row in subjects}
    require(len(codes) == len(subjects) == 6603, "Pinned CSV code count or uniqueness differs")
    require(all(row["navigation_parent_code"] in codes or row["navigation_parent_code"] is None
                for row in subjects), "Navigation parent missing")
    graph = Graph().parse(source_root / "raw/suggestion4.ttl", format="turtle")
    current = {URIRef(PREFIX + code) for code in codes}
    require(set(graph.subjects(RDF.type, SKOS.Concept)) == current, "CSV and RDF concept sets differ")

    for row in subjects:
        subject = URIRef(PREFIX + row["code"])
        row["uri"] = str(subject)
        row["classification_status"] = "upstream_subject_classification"
        row["rdf_source_id"] = "msc2020-skos-suggestion4"
        row["rdf_labels"] = terms(graph.objects(subject, SKOS.prefLabel))
        row["rdf_broader_uris"] = sorted(str(p) for p in graph.objects(subject, SKOS.broader))
        expected_parent = [] if row["navigation_parent_code"] is None else [PREFIX + row["navigation_parent_code"]]
        row["hierarchy_disagreement"] = row["rdf_broader_uris"] != expected_parent
        english_labels = sorted(str(label) for label in graph.objects(subject, SKOS.prefLabel)
                                if isinstance(label, Literal) and label.language == "en")
        row["exact_label_difference"] = english_labels != [row["label_as_recorded"]]
        notes = []
        for note in sorted(graph.objects(subject, SKOS.scopeNote), key=str):
            item = {"term": term(note)}
            if isinstance(note, URIRef):
                item["source_statements"] = source_statements(graph, note)
            notes.append(item)
        row["rdf_scope_notes"] = notes

    scopes = defaultdict(list)
    for statement in sorted(set(graph.subjects(RDF.type, VOCAB.seeForStatement)), key=str):
        endpoints = [list(graph.objects(statement, predicate))
                     for predicate in (RDF.subject, RDF.predicate, RDF.object)]
        require(all(len(values) == 1 for values in endpoints), "Malformed conditional endpoints")
        source, predicate, target = (values[0] for values in endpoints)
        require(source in current and predicate == VOCAB.seeConditionally, "Unexpected conditional triple")
        qualifiers = terms(graph.objects(statement, VOCAB.scope))
        require(bool(qualifiers), "Missing conditional scope")
        require(all(q["kind"] == "literal" and q["value"] for q in qualifiers), "Invalid scope term")
        require((source, predicate, target) in graph, "Reification lacks direct conditional triple")
        scopes[(source, predicate, target)].append({"uri": str(statement), "scopes": qualifiers})

    relations, collection_uris = [], set()
    predicates = (VOCAB.seeAlso, VOCAB.seeMainly, VOCAB.seeConditionally)
    triples = sorted(((s, p, o) for s in current for p in predicates for o in graph.objects(s, p)),
                     key=lambda triple: tuple(map(str, triple)))
    for source, predicate, target in triples:
        if target in current:
            target_kind = "subject"
        elif (target, RDF.type, SKOS.Collection) in graph:
            target_kind = "collection"
            collection_uris.add(target)
        else:
            raise ValueError(f"Unresolved classification-reference target: {target}")
        records = scopes.get((source, predicate, target), [])
        require(predicate != VOCAB.seeConditionally or bool(records), "Unqualified conditional edge")
        relations.append({"from_uri": str(source), "predicate_uri": str(predicate),
                          "to_uri": str(target), "target_kind": target_kind,
                          "status": "upstream_classification_reference",
                          "source_id": "msc2020-skos-suggestion4", "scope_records": records})
    collections = []
    for subject in sorted(collection_uris, key=str):
        members = list(graph.objects(subject, SKOS.member))
        require(all(member in current for member in members), "Non-subject collection member")
        collections.append({"uri": str(subject), "kind": "classification_collection",
                            "labels": terms(graph.objects(subject, SKOS.prefLabel)),
                            "member_uris": sorted(map(str, members)),
                            "source_id": "msc2020-skos-suggestion4"})

    metadata = {
        "schema_version": "msc-subject-index-v1",
        "attribution": "MSC2020: Mathematical Reviews and zbMATH. SKOS conversion: Susanne Arndt, Patrick Ion, Mila Runnwerth, Moritz Schubotz and Olaf Teschke; TIBHannover/MSC2020_SKOS.",
        "data_license": "CC-BY-NC-SA-4.0",
        "data_license_url": "https://creativecommons.org/licenses/by-nc-sa/4.0/",
        "adaptations": "Converted to a navigation index; derived navigation parents from MSC code structure; retained source labels, descriptions, relation types, qualifiers, collection targets and recorded hierarchy disagreements.",
        "sources": [
            {"id": "msc2020-official-csv", "url": "https://msc2020.org/MSC_2020.csv", "sha256": CSV_HASH,
             "decoding": "ISO-8859-1 interpretation; raw source has no HTTP charset declaration"},
            {"id": "msc2020-skos-suggestion4", "repository": "https://github.com/TIBHannover/MSC2020_SKOS",
             "commit": REVISION, "path": "msc-2020-suggestion4.ttl", "sha256": TTL_HASH,
             "status": "upstream_suggested_serialization"}],
        "source_manifest_sha256": MANIFEST_HASH,
        "navigation_parent_derivation": "Top-level XX-XX has no parent; XX-NN and XXAxx attach to XX-XX; XXANN attaches to XXAxx. This is separate from recorded RDF broader triples.",
        "limitations": ["Classification categories index subjects; they do not enumerate all known mathematics.",
                        "Cross-references are upstream subject-navigation links, not proved equivalences or implications.",
                        "No subject is labeled unsolved because the Atlas has no reviewed entry for it.",
                        "Exact label differences and hierarchy disagreements remain visible source comparisons.",
                        "The eight hierarchy disagreement flags are preserved; no RDF parent is silently removed.",
                        "No automatic mapping from the curated Atlas or MathGloss to MSC codes is asserted."]}
    summary = {"schema_version": "msc-import-summary-v1", "subjects": len(subjects),
               "subject_kinds": dict(sorted(Counter(row["kind"] for row in subjects).items())),
               "references": len(relations),
               "references_by_predicate": dict(sorted(Counter(row["predicate_uri"] for row in relations).items())),
               "scope_records": sum(len(row["scope_records"]) for row in relations),
               "referenced_collections": len(collections),
               "hierarchy_disagreements": [row["code"] for row in subjects if row["hierarchy_disagreement"]],
               "exact_label_difference_count": sum(row["exact_label_difference"] for row in subjects),
               "rdf_scope_note_count": sum(len(row["rdf_scope_notes"]) for row in subjects)}
    return {"subjects.json": {"metadata": metadata, "subjects": subjects},
            "references.json": {"schema_version": "msc-references-v1", "relations": relations,
                                "collections": collections}, "summary.json": summary}


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--source-root", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    args = parser.parse_args()
    require(not args.output_dir.exists(), "Output path exists; it will not be changed")
    outputs = compile_index(args.source_root.resolve())
    args.output_dir.mkdir(parents=True, exist_ok=False)
    for name, value in outputs.items():
        with (args.output_dir / name).open("x", encoding="utf-8", newline="\n") as stream:
            json.dump(value, stream, ensure_ascii=False, indent=2)
            stream.write("\n")
    print(json.dumps(outputs["summary.json"], sort_keys=True))


if __name__ == "__main__":
    main()
