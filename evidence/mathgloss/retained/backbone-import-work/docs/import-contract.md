# MathGloss metadata seed import, version 1

Frozen by root before implementation, 2026-09-08. This is a separate next-step candidate; it does not change the active assumption-check evaluation or the reviewed atlas corpus.

## Source and objective

Reuse only the concept identifiers, recorded labels, source names and outbound links in MathGloss commit `b8f659605486f80f2816515f525af2c395c711fa`, path `data/database.csv`. Exact CSV SHA-256 is `933a72820fe7ede53a803b750a480def205677e5722ae5f9589b0d1d9bf832b2` (674640 bytes). The locally retained snapshot is `D:/CodexWorkspaces/mathematics-atlas/backbone-reuse-work/raw/mathgloss/`. Retain the repository's LICENSE notice and pinned attribution. Do not import definitions, relation files, inferred prerequisites, external page bodies or MaRDI data.

Produce a deterministic JSON candidate index and a complete import ledger from every CSV data record. This is an unreviewed external link catalogue, not a certification of concept identity or an expansion of the curated mathematical claims. Use uv, an isolated environment and no runtime dependencies.

## Representation

- Fail before import if the source SHA or expected pinned header schema differs. Treat malformed UTF-8/CSV or inconsistent record widths explicitly; do not silently reinterpret columns.
- Preserve source record order. Use a snapshot-and-record-index key, with separate `wikidata:Q...` identity candidate and full Wikidata URI. Never merge by label or silently overwrite repeated QIDs.
- Require QIDs matching `Q[1-9][0-9]*` and nonempty recorded labels. Retain rejected rows in the ledger with specific reasons. Empty links are absent, not relationships.
- Preserve each nonempty source name and original URL. Export clickable links only for absolute HTTP(S) URLs with a hostname and no username/password. Record rejected or incomplete link pairs in the ledger without losing their source location. Do not fetch linked URLs.
- Retain source project, repository, commit, CSV path, logical data-record number and physical line span. Physical locators must remain correct for quoted multiline fields; record number is not a substitute for line number.
- Mark every mapping `unreviewed` and `asserted_by: MathGloss`. No existence of a URL, shared QID or matching label proves equivalence, theorem support or beginner suitability.
- Keep method/confidence fields absent when absent from the canonical CSV. Do not reconstruct them from other files or assign fabricated scores.
- Duplicate QIDs are recorded as separate source rows and reported; consumers may group them for review but must not erase differing records.
- Outputs contain only this metadata/link schema, provenance, attribution and audit counts. No source prose is copied.

## Evaluation and handoff

The full-source run must account for every data record as accepted or rejected and every nonempty link pair as retained or rejected. Counts and duplicate reports must be derived from retained raw records. Two independent runs on the same source must produce identical output bytes, excluding separate run metadata such as time.

Development tests cover quoted commas and newlines, blank rows, invalid/missing QIDs/labels, duplicate QIDs, incomplete link pairs, credentials and unsafe schemes, extra/missing headers or fields, and source-hash mismatch. Retain all failed attempts and raw commands. The author cannot certify the final gate; a separate reviewer will inspect source fidelity, physical locators, counts, schema boundaries, license/attribution scope, and reproducibility before integration.

Worker owns only `backbone-import-work/` implementation/tests/outputs. Root retains ownership of this frozen contract and all project/Site/Git integration. The MathGloss snapshot and earlier source review remain read-only.
