from __future__ import annotations

import hashlib
import json
import math
from pathlib import Path


ROOT = Path(r"D:/CodexWorkspaces/mathematics-atlas")
SOURCE = ROOT / "backbone-import-work/outputs/full-run-final-01/candidate-index.json"
CONTRACT = ROOT / "project/docs/concept-library-contract.md"
OUT = ROOT / "library-audit-work/independent-cases.json"


def sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


source_raw = SOURCE.read_bytes()
catalog = json.loads(source_raw.decode("utf-8", errors="strict"))
records = catalog["records"]


def matches(record: dict[str, object], query: str, source: str | None) -> bool:
    links = record["links"]
    if source is not None and not any(link["source"] == source for link in links):
        return False
    needle = query.strip().casefold()
    if not needle:
        return True
    values = [
        record["identity_candidate"]["qid"],
        record["label_as_recorded"],
        *(link["name_as_recorded"] for link in links),
    ]
    return any(needle in value.casefold() for value in values)


case_inputs = [
    ("all-records", "", None),
    ("qid-exact", "Q1028209", None),
    ("unicode-en-dash-label", "Deutsch\u2013Jozsa algorithm", None),
    ("case-insensitive-label", "grover's algorithm", None),
    ("resource-name-not-label", "countable choice", None),
    ("multi-hit-label-fragment", "abelian group", None),
    ("filtered-chicago", "abelian group", "Chicago"),
    ("filtered-bct", "category theory", "BCT"),
    ("filtered-planetmath", "random variable", "PlanetMath"),
    ("filtered-mathlib-miss", "Fourier transform", "Mathlib"),
    ("search-miss", "compact Hausdorff", None),
    ("unicode-broad", "spectral sequence", "nLab"),
]
cases = []
for case_id, query, source in case_inputs:
    hits = [record for record in records if matches(record, query, source)]
    cases.append(
        {
            "id": case_id,
            "input": {"query": query, "source": source},
            "expected_count": len(hits),
            "expected_record_keys_in_frozen_source_order": [record["record_key"] for record in hits],
            "expected_qids_in_frozen_source_order": [record["identity_candidate"]["qid"] for record in hits],
            "expected_result_set_sha256": sha(
                ("\n".join(sorted(record["record_key"] for record in hits)) + "\n").encode("utf-8")
            ),
        }
    )

pagination_sweeps = []
for sweep_id, query, source, page_size in [
    ("all-catalog-pages", "", None, 37),
    ("all-nlab-pages", "", "nLab", 37),
    ("abelian-group-small-pages", "abelian group", None, 5),
]:
    hits = [record for record in records if matches(record, query, source)]
    pagination_sweeps.append(
        {
            "id": sweep_id,
            "input": {"query": query, "source": source, "page_size": page_size},
            "expected_total": len(hits),
            "expected_pages": math.ceil(len(hits) / page_size),
            "expected_unique_record_keys": len({record["record_key"] for record in hits}),
            "expected_result_set_sha256": sha(
                ("\n".join(sorted(record["record_key"] for record in hits)) + "\n").encode("utf-8")
            ),
            "checks": [
                "stable documented ordering across repeated calls",
                "concatenated pages have no duplicate or dropped record keys",
                "every page repeats the same total",
                "page after the last is empty and preserves the total",
            ],
        }
    )

sample_qids = [
    "Q1028209",
    "Q1028292",
    "Q1000116",
    "Q181296",
    "Q163310",
    "Q327069",
    "Q176623",
    "Q1006032",
    "Q17004665",
    "Q5506748",
]
record_by_qid = {record["identity_candidate"]["qid"]: record for record in records}
fidelity_samples = []
for qid in sample_qids:
    record = record_by_qid[qid]
    canonical = json.dumps(record, ensure_ascii=False, separators=(",", ":"), sort_keys=True).encode("utf-8")
    fidelity_samples.append(
        {
            "qid": qid,
            "record_key": record["record_key"],
            "logical_data_record": record["source_locator"]["logical_data_record"],
            "label_as_recorded": record["label_as_recorded"],
            "label_codepoints": [f"U+{ord(char):04X}" for char in record["label_as_recorded"]],
            "canonical_record_sha256": sha(canonical),
            "retained_link_count": len(record["links"]),
        }
    )

report = {
    "schema_version": "concept-library-independent-cases-v1",
    "frozen_before_implementation_review": True,
    "oracle_policy": {
        "query_normalization": "strip then Unicode casefold",
        "lexical_match": "substring of recorded Wikidata QID, recorded label, or recorded resource name",
        "source_filter": "record has at least one retained link whose source exactly equals the selected source",
        "result_identity": "record_key",
        "comparison": "counts and sets are normative; frozen source order is retained for diagnosing the implementation's separately documented deterministic order",
        "url_fields_are_not_searchable": True,
    },
    "frozen_inputs": {
        "concept_library_contract_sha256": sha(CONTRACT.read_bytes()),
        "audited_candidate_index_sha256": sha(source_raw),
        "candidate_record_count": len(records),
        "catalog_status": catalog["catalog_status"],
        "source_commit": catalog["source"]["commit"],
    },
    "search_filter_cases": cases,
    "pagination_sweeps": pagination_sweeps,
    "fidelity_samples": fidelity_samples,
    "invalid_input_cases": [
        {"id": "page-zero", "abstract_input": {"page": "0"}, "expected": "bounded 4xx error; no search execution"},
        {"id": "page-negative", "abstract_input": {"page": "-1"}, "expected": "bounded 4xx error; no search execution"},
        {"id": "page-fraction", "abstract_input": {"page": "1.5"}, "expected": "bounded 4xx error; no search execution"},
        {"id": "page-nonnumeric", "abstract_input": {"page": "abc"}, "expected": "bounded 4xx error; no search execution"},
        {"id": "page-size-zero", "abstract_input": {"page_size": "0"}, "expected": "bounded 4xx error; no search execution"},
        {"id": "page-size-negative", "abstract_input": {"page_size": "-1"}, "expected": "bounded 4xx error; no search execution"},
        {"id": "page-size-fraction", "abstract_input": {"page_size": "2.5"}, "expected": "bounded 4xx error; no search execution"},
        {"id": "page-size-huge", "abstract_input": {"page_size": "100000"}, "expected": "bounded 4xx error or documented cap; response remains bounded"},
        {"id": "unknown-source", "abstract_input": {"source": "UnknownCorpus"}, "expected": "bounded 4xx error; source is not silently ignored"},
        {"id": "repeated-source", "abstract_input": {"source": ["nLab", "BCT"]}, "expected": "bounded 4xx error; ambiguous filter is not silently reinterpreted"},
        {"id": "oversized-query", "abstract_input": {"query_length": 4097}, "expected": "bounded 4xx error; response does not echo arbitrary input"},
    ],
    "api_and_privacy_checks": [
        "API is read-only and exposes no mutation method or server-side user state.",
        "A query performs no fetch to MathGloss or any outbound resource URL.",
        "Errors are bounded and do not expose filesystem paths, stacks, source bytes, or arbitrary parser messages.",
        "Responses document cache behavior appropriate for user-supplied search state.",
        "Returned records preserve unreviewed mapping and identity status plus source attribution and physical locator.",
    ],
    "ui_and_webmcp_checks": [
        "Ordinary form and WebMCP action update one shared visible query/source/page state.",
        "Tool output reports the same query, source, page, total and visible record keys as the rendered result state.",
        "A changed query or source resets page to one.",
        "Displayed links are the exact retained source links and pinned source-record link; no linked body is fetched or copied.",
        "Visible disclosure says mappings/resources are unreviewed and search misses do not establish novelty.",
    ],
    "limitations": [
        "These lexical cases test a frozen, source-derived policy; they do not assess semantic relevance or concept equivalence.",
        "Search misses and counts are properties of one pinned catalog snapshot, not claims about mathematics or the literature.",
        "No destination availability, safety, content, rights, learner level, or theorem support is inferred from a retained URL.",
    ],
}
OUT.write_text(json.dumps(report, ensure_ascii=True, indent=2, sort_keys=True) + "\n", encoding="utf-8", newline="\n")
print(json.dumps({"path": str(OUT), "bytes": len(OUT.read_bytes()), "sha256": sha(OUT.read_bytes()), "search_cases": len(cases), "pagination_sweeps": len(pagination_sweeps)}, sort_keys=True))
