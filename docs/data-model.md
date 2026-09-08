# Data semantics, version 1.0

`data/atlas.json` is the canonical curated corpus. `/api/atlas` serves the same object. No external search or language-model call is hidden behind the current search box.

| Record | Required meaning |
|---|---|
| Node | Stable ID, concept/theorem/method/problem/example kind, domains, aliases, explanation, assumptions and evidence |
| Edge | Directed `from` and `to`, named relation, exact statement, assumptions, evidence status and source locators |
| Source | Primary bibliographic metadata, URL, source-level locator and scope note |
| Journey | Ordered existing concept IDs with an explicit learning prompt at each stop |
| Opportunity | A project contribution with difficulty, status and checkable acceptance criteria |

Nodes currently use `sourced`; edges use `established` for sourced definitions, known mathematical relations and documented modelling methods. These labels do not assert a formal proof or empirical efficacy. Future hypotheses use `proposed`; formal claims require a resolvable proof artifact and an independently checked proof environment. Applications inherit their modelling assumptions. Corpus gaps do not receive `unsolved` status merely because nothing is indexed.

Navigation uses an undirected view of these directed edges to help people explore in either direction. It preserves and displays each original relation. A sequence of mixed relations is not automatically a valid implication or equivalence. Graph coordinates are presentation metadata; distance is not a mathematical similarity score.

`scripts/validate_atlas.py` rejects duplicate IDs, dangling references, missing assumptions, missing evidence locators and unsupported status/kind values. It does not verify that the source entails the claim, that the URL remains available, or that a proof is correct. Those are separate independent audit responsibilities.

Search lowercases terms and normalizes punctuation to spaces, including hyphens in concept IDs. Each matching ID/title/alias term contributes four points; a term otherwise found in summary, explanation or domains contributes one. Results use AND matching, with ties retaining corpus order. This baseline favors transparency; no retrieval improvement is claimed.

Finite examples are a distinct `examples` collection with kind `example`, a frozen fixture ID, calculation artifact and related concepts. They are not source-backed general theorems. Their exact inputs and expected outputs live in `fixtures/frozen.json`.
