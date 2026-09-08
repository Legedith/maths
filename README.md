# Mathematics Atlas

An expanding, source-backed map of mathematics and its connections to other fields. Start with a concept, follow an explained relation, inspect its assumptions, learn the prerequisites, and test a finite example.

The first region connects **graph Laplacians, electrical networks, random walks, spanning trees, spectral algorithms, image segmentation and chemical graph descriptors**. It contains 31 concepts, 40 directed relations, seven authoritative sources (four research papers and three first-party lecture notes), three learning journeys and five concrete contribution tasks. These are corpus counts, not measures of all mathematics. Economics, biology and most mathematical areas remain outside this first region.

## What works

- Search concepts and aliases; filter by field.
- Explore a concept's neighbors, relation directions, assumptions and source locators.
- Find a shortest navigation path between two concepts. Traversal may go against a relation's direction and is explicitly not a composed proof.
- Follow beginner journeys and find contribution tasks with acceptance criteria.
- Edit a graph with 2–6 vertices and compute exact resistance, directed hitting times, commute time and enumerated spanning-tree counts in your browser. Export the actual result.
- Search the live Loogle Mathlib index by declaration-name substring, with returned formal statement types and documentation links. External results remain separate from reviewed Atlas entries.
- Retrieve the corpus as JSON at `/api/atlas`. Five WebMCP tools expose the same curated search, navigation, path, experiment and external-library workflows to supporting agents.

## Run locally

Use Node 24 and [uv](https://docs.astral.sh/uv/). Python runs in the project `.venv`; the mathematical engine has no runtime dependencies.

```powershell
# Windows workspace used for this project; choose your own checkout elsewhere.
Set-Location D:\CodexWorkspaces\mathematics-atlas\project
$env:UV_CACHE_DIR = 'D:\CodexWorkspaces\mathematics-atlas\uv-cache'
$env:npm_config_cache = 'D:\CodexWorkspaces\mathematics-atlas\npm-cache'
npm ci
uv sync --frozen
npm run dev
```

Open the URL printed by the development server. To build the site, run `npm run build`.

## Reproduce the foundation

```powershell
uv run --frozen pytest
uv run --frozen python -m atlas_engine evaluate --output-dir evidence/baseline
uv run --frozen python scripts/validate_atlas.py
uv run --frozen python scripts/check_supplemental.py
uv run --frozen python scripts/check_normalization_case.py
node scripts/check-browser-engine.ts
node scripts/check-atlas.ts
node scripts/check-formal-search.ts
npx tsc --noEmit
npm run lint
```

The baseline evaluator checks one selected existing edge for every connected labelled simple graph on two through five vertices, plus a named six-vertex cycle: 772 records. The seven fixed positive examples also include a nonedge query; ten negative fixtures enforce the input boundary. Browser agreement compares every public output, not just the final resistance. Raw records and scope are under `evidence/` and `logs/`.

The engine separately solves the electrical equations, solves Markov first-step equations, and enumerates trees by subset connectivity. The first two share a generic rational equation solver; their agreement is not complete implementation independence. See [engine documentation](README-engine.md) and the [frozen contract](docs/engine-contract.md).

## Discovery and evidence

Known identities are useful rediscoveries, not new mathematics. A missing search result or graph edge never establishes that a problem is open. The project is investigating a provable optimization of its batch computation workload; its selection and evaluation requirements are frozen in [the symmetry contract](docs/symmetry-contract.md). Performance or novelty claims must wait for the retained canonical artifacts and a separate auditor.

The broader objective remains active: progressively map more mathematics and use its connections to support verified discoveries. This finite region does not fulfill that full coverage objective. Proof status, source support, finite computation and novelty are separate questions. No current entry claims Lean 4 verification.

See [contribution guidance](CONTRIBUTING.md), [data semantics](docs/data-model.md), and [coverage and next regions](docs/coverage.md). The evidence bundle in `.codex/evidence/runs/atlas-foundation/` is a provenance record; a pending gate is not a certification.

## Verification limits

Curated search uses explicit lexical substring scoring, with eight retrieval sanity cases. The separate external search reuses Loogle; neither is an evaluated novelty detector. See the [reuse decision](docs/reuse-decision.md) and [independently checked normalization case](docs/normalization-case.md). The exact lab is restricted to connected simple undirected unweighted graphs, even where a source entry discusses a weighted theorem. Source PDFs stay local under ignored `work/sources/`; only paraphrases, bibliographic metadata and limited evidence extracts belong in the repository. Untouched generated UI components are excluded from lint because the scaffold itself has existing lint violations; the full TypeScript project is checked. Browser checks cover focused WebMCP contracts, not general visual or responsive QA.
