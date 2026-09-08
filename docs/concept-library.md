# Concept and resource library

The `/library` view exposes the independently checked MathGloss metadata import:
4,814 concept records and 7,217 links to seven resource collections. It retains
the source's recorded names, proposed Wikidata identities and exact source-row
locators. All proposed identities and mappings remain unreviewed here.

Search accepts recorded labels, resource names and Wikidata QIDs. It applies
Unicode NFKC normalization, lowercase conversion and punctuation separation,
then requires every query fragment to occur. An exact recorded label ranks
first, followed by a label prefix; ties preserve CSV order. Selecting a resource
restricts candidates to records with a link to that source, and restricts alias
matching to that source's recorded name. A matching record still displays its
other resources so the user can compare explanations. Pages contain at most 20
records, and the response retains the total count. No query is sent to an
external search service by this library.

The `search_learning_resources` WebMCP action uses the same search action and
visible state as the form. Research and formal search remain separate flows
with their previously recorded external-service behavior.

## Source and limits

The source is [MathGloss revision b8f6596](https://github.com/MathGloss/MathGloss/tree/b8f659605486f80f2816515f525af2c395c711fa),
`data/database.csv`, SHA-256
`933a72820fe7ede53a803b750a480def205677e5722ae5f9589b0d1d9bf832b2`.
The repository's exact license notice is retained at
`data/mathgloss/MATHGLOSS-LICENSE`. This metadata import does not copy or certify
the linked pages and does not establish their individual reuse terms.

The importer passed independent source, specification, reproduction and
implementation checks. The original sample's corrupted en dash is retained as
a failed attempt; the integrated full export preserves the exact source text.
The separate library integration review is pending. Neither source fidelity nor
successful lexical retrieval proves identity, mathematical equivalence, learner
level, practical impact or novelty. This expands coverage; it is not a complete
map of mathematics.

## Reproduce

```powershell
uv run --frozen python scripts/import_mathgloss.py --source-csv data/mathgloss/source/database.csv --source-license data/mathgloss/MATHGLOSS-LICENSE --output-dir work/mathgloss-reproduction
node scripts/check-concept-library.ts
```

The output directory must be new or empty. The adapter supplies explicit bytes
to the unchanged audited importer core; it does not use the historical
staging-path entry point. It requires all four output hashes to match the
independently audited export. Historical command failures and successful
reproductions remain in `evidence/mathgloss/` and `logs/`.
