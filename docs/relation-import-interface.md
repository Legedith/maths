# Relation import interface, frozen before implementation

Use the governing relation-explorer-contract.md (dc2f005e...). This interface
adds one explicit metadata input: the existing primary Wikidata semantics
response `relation-source-review-work/semantics/wikidata-semantics-response.json`,
SHA256 3db472c2cf98ff6f867f20d56a983a4703c317d6855a40ad2e0cdc096641bec1.
Use it only for English display labels of P460, P518 and Q9085982; retain IDs
when no label is available. Do not infer any additional mathematical relations.

Deliver a portable standard-library script `import_relations.py` in assigned
staging. Arguments: `--relations-csv`, `--catalog-csv`, `--probe-inputs`,
`--probe-response`, `--probe-command-log`, `--semantics-response`, `--output-dir`.
Pin all input hashes in code/manifest from the existing frozen artifacts and
fail on mismatch. Reject an existing nonempty output directory. Retain raw
canonical command, stdout/stderr and exit status in staging. No network calls.

Write three deterministic JSON files with UTF-8 and LF:

1. `relation-index.json`: object with `schema_version: "1.0"`, `source`
   (repository, commit, input hashes and MIT/CC0 attribution), `summary`
   (total_rows, included_rows, excluded_rows, endpoint_count, property_count),
   `properties` (array of `{id,label,count}` sorted by numeric property ID),
   `edges` (array in original CSV order), and `observations` (object keyed by
   edge ID, only the three exact probe matches).
2. `relation-ledger.json`: object with source metadata and `rows` in original
   CSV order. Each row has `record`, `line_start`, `line_end`, `fields` (the six
   original CSV fields without normalization), `included` and `missing_qids`.
3. `relation-summary.json`: same source/summary/properties metadata plus output
   file hashes for index and ledger. Do not add a volatile timestamp to any of
   these three deterministic outputs.

Each edge:

```json
{
  "id": "mathgloss-row-23",
  "source": {"id": "Q1000116", "label": "axiom of countable choice"},
  "property": {"id": "P279", "label": "subclass of"},
  "target": {"id": "Q179692", "label": "axiom of choice"},
  "record": 23,
  "line_start": 24,
  "line_end": 24,
  "review_status": "unreviewed_external_assertion",
  "legacy_statement_metadata": "not_retrieved"
}
```

Each observation preserves `requested_url`, `retrieved_at_utc`,
`raw_response_sha256`, source entity `lastrevid` and `modified`,
`matching_statements` (unmodified raw JSON statement objects), `field_presence`
(one `{statement_id,qualifiers,references}` record per match, with booleans), and
`display_labels` (only P460, P518, Q9085982 labels from the pinned semantics
response). Match on the mainsnak's property and item value exactly. Preserve
qualifiers/references in raw statement objects with their original structure,
including absence. Do not treat the normalized findings.json as raw input.

The application builds adjacency at module load; do not duplicate adjacency in
the JSON. Prefer compact serialization for the index and ledger. Assert the
known inventories as explicit checks in a retained canonical run report; those
checks are not an independent evidence gate. No self-certification. At most
one canonical author run after syntax checks; retain any failure before a fix.
