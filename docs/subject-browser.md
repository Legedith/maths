# Browse the existing classification

The `/subjects` browser exposes the pinned MSC2020 subject classification. It starts at 63 top-level areas and reaches every one of the 6,603 imported records. A subject page shows its ancestors, children, original description, incoming and outgoing cross-references, and conditions attached to those references. Follow a reference as a navigation suggestion whose stated scope must still be read.

The official [MSC2020 CSV](https://msc2020.org/MSC_2020.csv) supplies display labels and descriptions. A [pinned suggested SKOS conversion](https://github.com/TIBHannover/MSC2020_SKOS/tree/33972ddb6a72c3660a6e499ee5f881b57fa92d41) supplies RDF labels, parents, notes and 3,083 selected cross-references. The conversion is not silently treated as the official version of record. All 415 conditional references retain their scope records. One reference targets a 62-member collection, which remains a collection instead of being expanded into invented direct subject references.

Both sources contain the same 6,603 codes. Their English labels differ exactly for 120 records; these differences have not been adjudicated as semantic errors. Eight RDF records have two parents where the classification-code structure gives one navigation parent. Both raw parents and the derived navigation parent remain inspectable. Hierarchy depth is separate from leaf status: the 503 hyphen-number classes are level-two records even though they have no children in this catalogue.

## Search and API

Search matches every query term against the recorded code, label or description after Unicode normalization, lowercasing and punctuation normalization. Results preserve official source order and use 24 records per page. It is lexical search, without an evaluated semantic-retrieval claim. A parent filter selects immediate children.

Examples:

```text
/subjects?q=complexity
/subjects/68Q25
/api/subjects?q=complexity
/api/subjects?parent=68-XX&page=2
/api/subjects?code=03B45
```

The API accepts one `code` for detail, or `q`, `parent` and `page` for a list. Unknown or repeated parameters, mixed detail/list requests, unknown codes and invalid page/query values return HTTP 400 with `Cache-Control: no-store`. Detail responses retain source locators and exact RDF identifiers; paginated lists contain subject summaries. Reading the hierarchy backwards does not reverse a source assertion.

## Reproduction and scope

Rebuild the three JSON outputs from retained source bytes with the [portable uv importer](../experiments/msc-index/README.md). The source manifest records pinned hashes. The importer requires only its packaged CSV, Turtle and manifest; full local research webpage snapshots are not redistributed. The [data notice](../data/msc/NOTICE.md) records attribution, modifications and CC-BY-NC-SA-4.0 data terms separately from application code.

Run `node scripts/check-subjects.ts` for complete catalogue traversal and input checks. With the development server running, add `--http-origin http://localhost:3000` to compare API responses and exercise subject routes. An optional `--output` path retains a machine-readable result and must not already exist. CI rebuilds the importer outputs and compares all three files byte-for-byte.

Source/importer and application verification have separate independent reviewers. Their final certificates must identify the exact published artifacts; the contract and author checks alone do not certify them. Tests cover source fidelity, navigation and HTTP behavior, with no general visual evaluation.

The classification, MathGloss library, curated Atlas concepts and external theorem results retain their separate meanings. This import does not establish prerequisites, equivalences, proofs, unresolved research problems, automatic cross-domain discovery or completeness of mathematical knowledge. It supplies existing subject navigation on which those more demanding capabilities can be built.
