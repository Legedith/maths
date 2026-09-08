# Reuse existing concept relationships without erasing their meaning

Frozen engineering scope, 2026-09-08. Extend the existing Atlas with an external
relationship explorer over the already imported MathGloss concept catalogue.
This is navigation infrastructure, not a mathematical discovery experiment.
Reuse the existing library search and source mappings. Keep the curated graph
and its reviewed mathematical claims unchanged.

## Source and import

Pin MathGloss commit b8f659605486f80f2816515f525af2c395c711fa. Inputs:

- `data/relations/graph_edges.csv`, SHA256
  54f58f2fe3303c7caf139132cd4301b44643c735334469ebcd7f995cc7884aec;
- existing `data/mathgloss/source/database.csv`, SHA256
  933a72820fe7ede53a803b750a480def205677e5722ae5f9589b0d1d9bf832b2;
- the pinned MathGloss MIT license and source metadata;
- the retained three-row Wikidata probe and its independent review, as an
  explicitly separate dated observation for those three exact triples only.

Write a deterministic, standard-library Python importer run through uv. It must
preserve each original six-field CSV row, logical record and physical line
locator, direction, QIDs, property ID and labels. Join endpoints strictly by QID
to the catalogue. Produce a compact navigable JSON index, summary, and row ledger
that retains exclusions. The existing independent inventory expects 9,159 rows,
5,390 included triples, 3,769 excluded triples, 3,372 included endpoint QIDs and
81 property IDs; disagreements fail and remain recorded. Do not silently merge
labels, deduplicate different statements, infer equivalence, or invent edges.

Each included edge remains `unreviewed_external_assertion`. The legacy export
does not contain statement IDs, ranks, qualifiers, references or Wikidata query
revisions. Mark those fields `not_retrieved`; do not normalize that absence into
an assertion that there were no qualifiers or references.

For the three frozen probe triples, attach a separate observation with the
response hash, request time, entity revision, raw matching statement object,
and explicit field-presence flags. Do not replace the legacy row or generalize
this observation to other rows. Preserve missing raw JSON fields as missing;
a normalized display must distinguish missing fields from an empty container.
The P460 qualifier P518=Q9085982 must survive every layer to the visible detail.
The independent probe review corrects the author's claim that complete
qualifier/reference containers were returned. No new network fetch is needed
for this engineering import. Exclude the heuristic Mathlib inheritance export.

## User behavior

Add an external-connections route and an additive same-origin API. A person can
find an existing concept by its library label, alias or QID; select it; inspect
incoming and outgoing typed relations; filter by property and direction; follow
a neighbor; and open the concept's existing learning resources or original
Wikidata/MathGloss record. Keep the selected concept and filters in a shareable
URL. Show a useful initial result for a connected concept from computer science.

Use a readable directed neighborhood view and a complete paginated list. A
diagram may show a bounded subset only if its limit is explicit and the full
matching list remains accessible. Each edge displays its original direction and
property label/ID. Relations such as subclass, instance, difference, or 'said to
be the same as' remain distinct. Do not compose path proofs or merge identities.
Explain unknown conditions briefly beside the relation; put detailed provenance
in an expandable area. For the observed qualified relation, display the actual
qualifier and link its property/value. No page may imply that these imported
connections have been mathematically verified.

API input has strict QID/property/direction/page bounds, rejects duplicates and
unknown parameters with small non-echoing errors, and limits page size to 20.
Use deterministic ordering, accurate totals and no-store responses. Querying
the view contacts only this site's APIs; following external source links is an
explicit user action. Queries may appear in ordinary server access logs.

Expose one focused WebMCP tool for the same visible relation-selection workflow,
with typed bounded inputs and error behavior matching the UI. Preserve the
existing page's search behavior and registered tools.

## Verification and delivery

Use a compact CoE engineering bundle: this spec, pinned source records, importer
and application code, canonical import/check/build logs, typed claims and one
independent review. Root alone writes the shared Site checkout. A worker may
implement only the importer in separate assigned staging; independent agents
may check sources, arithmetic-free import fidelity, API and UI code.

Check every imported row against the pinned input; test that page traversal has
no losses or duplicates, direction/property filtering is correct, all three
observations retain exact raw statements and field-presence flags, and unknown
metadata stays unknown. Include the P460 qualifier regression and malformed API
inputs. Run the normal typecheck and production build once after implementation.
Do not run broad visual/browser QA without a user request. Follow Sites hosting
for the independently approved private update.

Success is a useful, reproducible way to navigate existing external assertions.
It is not a map of all mathematics, evidence of equivalence, a novelty detector,
or a measured improvement in researcher productivity.
