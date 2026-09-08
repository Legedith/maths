# MSC subject-index adapter contract v1

Purpose: make the full pinned MSC2020 subject classification and its recorded qualified cross-references usable for Atlas navigation. This extends vocabulary and bibliographic navigation, not the reviewed mathematical theorem graph. Source review is in progress and must pass before publication.

Frozen inputs, before importer implementation:

- Official CSV, SHA-256 f7c889354c202551fe01f89bad2ae95ccadec4c57ac1f6f9de38bbd658d3c78c, downloaded from https://msc2020.org/MSC_2020.csv. Decode the tab-separated bytes as ISO-8859-1, explicitly as a lossless interpretation. Preserve the original CSV bytes, both text and description fields, code and physical record line range.
- Suggested Turtle, SHA-256 ee4afa1f198ffd0f5ea807377e46420c5fd7537991928c67c759fa44640421e9, at TIBHannover/MSC2020_SKOS revision 33972ddb6a72c3660a6e499ee5f881b57fa92d41. Parse locally using RDFLib 7.1.4; do not follow owl:imports.
- Source attribution and retrieval records from the immutable msc-reuse-work source-manifest.json, SHA-256 90602331e367f13fb21b0bc1d535f45326b6adf67165a369a681b6738f468f70. Dataset copyright/attribution belongs to Mathematical Reviews/zbMATH and SKOS conversion contributors. Derived classification data remains CC-BY-NC-SA-4.0. Adapter source code is separately authored.

Output contract:

1. Emit exactly one subject record per official CSV code, in source order; the inspected snapshot has 6,603 codes including 63 top-level classes. Each record retains both official fields, source record/line locator, exact current SKOS URI, English RDF label(s), raw RDF broader-parent URIs, and source hash/revision identifiers. Differences in recorded labels remain differences, never silently corrected or declared erroneous.
2. For navigation, derive the parent from the documented code structure: XX-XX roots have no parent; XX-NN facet leaves and XXAxx letter groups have XX-XX as parent; XXANN leaves have XXAxx as parent. Every non-root parent must exist. Call this field navigation_parent_code and record its derivation separately from raw RDF parents. Flag every discrepancy; do not rewrite the eight observed extra-parent cases in the source record.
3. Emit every direct seeAlso, seeMainly and seeConditionally triple from a selected MSC subject, sorted by exact RDF terms. Each reference retains its exact predicate and endpoint URIs, target kind and relation-specific scopes. Preserve the dataset's lowercase seeForStatement IRI. Every conditional edge must match its explicit single-subject/predicate/object reification(s), preserving the scope lexical value, language/datatype and record URI. Any missing/malformed qualifier blocks conversion instead of degrading into an unqualified relation.
4. Resolve references to source-defined SKOS collections as collection targets with exact members and labels. A collection target is not a dangling subject or an inferred set of mathematical equivalences. Do not flatten collections into extra direct links. Unknown targets block conversion.
5. Preserve raw scope notes on subject records as RDF terms and references, with their source-defined fields where present. No term rewriting, HTML rendering, ontology inference, inferred equivalence, formal proof badge, generated mathematical prose, or open-problem status.
6. Emit attribution/limitations metadata and deterministic summary counts. JSON contains original strings escaped by the serializer; UI rendering must later treat strings as text. Files are deterministic UTF-8 with stable order, stable keys and no timestamps. Source metadata supplies the original retrieval timestamps separately.
7. CLI takes an explicit source-root and a new output directory. It verifies all declared source pins before writing. Existing output paths are rejected and unchanged; no hidden fetch or rerun. Source failures return nonzero and retain raw logs. Code/input freezes and an auditor-owned wrapper precede the canonical execution.

Validation contract:

An independent reviewer must compare every subject to the pinned CSV, every relation to parsed raw RDF, all conditional scopes and all collection members, hierarchy derivation and discrepancy flags, field-level attribution and status boundaries. Re-run the importer once into a fresh independent directory and compare every deterministic output byte-for-byte. Verify rejection of an existing output path without changing a sentinel. Review malformed-input handling through the strict pin and structural checks. Check code/description alignment and all four CoE integrity gates. No performance, discovery or universal-coverage claim is permitted by this contract.

This contract covers the data adapter only. A later product integration must validate its API/UI navigation and source/evidence display before being published. Root owns implementation in this staging directory and any serial shared-project integration. Reviewers own separate staging directories and cannot self-certify root's work.
