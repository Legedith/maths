# External concept connections

`/connections` turns the existing MathGloss relation export into a directed
neighborhood that you can browse. Search for a library concept, select it, filter
the relation type or direction, follow a neighbor, and open the concept's linked
learning resources. The URL preserves the selected concept and filters.

The pinned export has 9,159 rows. Strict QID joins to the existing 4,814-record
catalogue retain 5,390 rows connecting 3,372 QIDs through 81 property IDs. The
remaining 3,769 rows stay in the import ledger with their missing endpoints.
These are counts of imported records, not measures of mathematical coverage or
truth. The separate curated graph is unchanged.

Every connection retains its original source, property and target, labels, CSV
record and line locator. “Subclass of”, “instance of”, “different from”, and
“said to be the same as” are distinct relations. The explorer neither merges
their nodes nor composes them into proofs. The diagram draws at most six
incoming and six outgoing edges from the current result page; the complete list
has 20 rows per page in source order.

## Conditions and provenance

MathGloss's six-column export omits Wikidata statement IDs, ranks, qualifiers,
references and query revisions. Those fields remain `not_retrieved`. This does
not mean that the original statements had no conditions or references.

A separately dated Wikidata response is attached to three preselected rows.
For those rows the import preserves the exact raw statement objects, entity
revisions, field-presence flags, request time and response hash. Missing fields
stay absent. In particular, the NS5-brane → M5-brane P460 assertion retains
P518 = Q9085982, displayed as “applies to part: type IIA string theory”. This is
Wikidata's assertion, not a physics equivalence proved by the Atlas.

The [independent probe review](../evidence/external-connections/sources/relation-probe-review.json)
corrects the earlier normalized findings' wording: empty arrays in that summary
were not literally returned on every raw statement. The explorer uses the raw
response and distinguishes absent fields from supplied empty containers.
Property meanings and labels come from the retained primary
[Wikidata source notes](../evidence/external-connections/sources/semantics/source-notes.json).

## Reproduce the import

Use uv and a new output directory:

```powershell
uv run --frozen python scripts/import_relations.py --relations-csv data/mathgloss/relations/source/graph_edges.csv --catalog-csv data/mathgloss/source/database.csv --probe-inputs evidence/external-connections/sources/probe/frozen-inputs.json --probe-response evidence/external-connections/sources/probe/wikidata-response.json --probe-command-log evidence/external-connections/sources/probe/command-log.json --semantics-response evidence/external-connections/sources/semantics/wikidata-semantics-response.json --output-dir work/relation-reproduction
node scripts/check-external-relations.ts --reproduced-dir work/relation-reproduction
```

The importer verifies the pinned input hashes and writes deterministic index,
ledger and summary files without network access. MathGloss is reused under its
MIT license, retained at `data/mathgloss/MATHGLOSS-LICENSE`; the originating
Wikidata structured data is CC0. Linked resources retain their own licenses.

## API and agent workflow

`GET /api/external-relations?qid=Q8366&property=All&direction=both&page=1`
returns the selected concept, a relation page, totals, available property types
and any separately retained observations for those rows. Directions are `both`,
`incoming` and `outgoing`. Unknown or repeated parameters and invalid values
receive a small non-echoing error. Responses use `Cache-Control: no-store`.

The page's `explore_external_connections` WebMCP tool uses the same selection
callback as the interface. It changes the visible neighborhood and URL.
Concept search reuses the existing same-origin library API. Searches and
selections do not query external services, but can appear in normal site access
logs. Opening a source link is an explicit external request.

The new feature has its own
[evidence bundle](../.codex/evidence/runs/external-connections-v1/bundle.json).
The previous library certificate refers to the earlier published snapshot at
commit `6693dac91804dd9da76e300652b63d2db46284ed`. This update adds a homepage
navigation link; its earlier bytes are retained for the new review. No prior
certificate is silently expanded to cover the new feature.

The view supports investigation of existing assertions. It does not identify
open problems, certify equivalence, detect novelty, or establish a measured
benefit to researchers.
