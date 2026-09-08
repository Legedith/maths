# Mathematics Atlas

An expanding, source-backed map of mathematics and its connections to other fields. Start with a concept, follow an explained relation, inspect its assumptions, learn the prerequisites, and test a finite example.

The first region connects **graph Laplacians, electrical networks, random walks, spanning trees, spectral algorithms, image segmentation and chemical graph descriptors**, including Kemeny's constant and Braess sets. It contains 33 concepts, 44 directed relations, nine authoritative sources (six research papers and three first-party lecture notes), four learning journeys and six concrete contribution tasks. These are corpus counts, not measures of all mathematics. Economics, biology and most mathematical areas remain outside this first region.

A second region adds seven concepts connecting **Boolean relations, rectangle covers, fixed-side biclique covers and a precise nondeterministic communication model**. Eight added relations include explicit translations and representation boundaries; two new journeys guide the reader through them. The combined curated corpus has 40 concepts, 52 relations, 11 sources and six journeys. The [source-reviewed mathematics and integration status](docs/boolean-rank-bridge.md) distinguish known results from Atlas-local boundary conventions.

The broader **concept and resource library** reuses a pinned MathGloss export with 4,814 concept records and 7,217 resource links. Its source fidelity and navigation have [passed independent verification](docs/concept-library-verification.md); its proposed identities and resource mappings remain unreviewed. These records expand searchable vocabulary without being promoted to proved relationships in the curated map.

The **subject browser** at `/subjects` reuses the pinned MSC2020 classification: 6,603 subject records in 63 top-level areas, with 3,083 retained source cross-references. Browse the hierarchy, search recorded labels and descriptions, and inspect reference conditions and source differences. These are classification records, not a count of known theorems or proved connections. See [source scope and reproduction](docs/subject-browser.md).

## What works

- Search concepts and aliases; filter by field.
- Explore a concept's neighbors, relation directions, assumptions and source locators.
- Find a shortest navigation path between two concepts. Traversal may go against a relation's direction and is explicitly not a composed proof.
- Follow beginner journeys and find contribution tasks with acceptance criteria.
- Edit a graph with 2–6 vertices and compute exact resistance, directed hitting times, commute time and enumerated spanning-tree counts in your browser. Export the actual result.
- Search the live Loogle Mathlib index by declaration-name substring, with returned formal statement types and documentation links. External results remain separate from reviewed Atlas entries.
- Describe a mathematical problem and search the existing TheoremSearch index. Inspect generated summaries separately from extracted statements and save a source packet for review.
- Browse `/library` by concept name or Wikidata QID, filter by resource, and follow each mapping to its original source record. See the [library's matching rules, import and limits](docs/concept-library.md).
- Browse `/subjects` and `/subjects/[code]` for the MSC2020 hierarchy, original descriptions and qualified cross-references. `/api/subjects` provides paginated lists or a single subject detail.
- Retrieve the corpus as JSON at `/api/atlas`. Six WebMCP tools expose the same curated search, navigation, path, experiment and external-library workflows to supporting agents.
- Use `search_learning_resources` on the library page to operate the same visible resource search and pagination through WebMCP.

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
node scripts/check-research-search.ts
node scripts/check-concept-library.ts
node scripts/check-subjects.ts
npx tsc --noEmit
npm run lint
```

The baseline evaluator checks one selected existing edge for every connected labelled simple graph on two through five vertices, plus a named six-vertex cycle: 772 records. The seven fixed positive examples also include a nonedge query; ten negative fixtures enforce the input boundary. Browser agreement compares every public output, not just the final resistance. Raw records and scope are under `evidence/` and `logs/`.

The engine separately solves the electrical equations, solves Markov first-step equations, and enumerates trees by subset connectivity. The first two share a generic rational equation solver; their agreement is not complete implementation independence. See [engine documentation](README-engine.md) and the [frozen contract](docs/engine-contract.md).

## Discovery and evidence

Known identities are useful rediscoveries, not new mathematics. A missing search result or graph edge never establishes that a problem is open. The terminal-symmetry cache now has an independently audited correctness argument and a bounded benchmark; see [its scope and reproduction commands](README-symmetry.md). Canonical graph caching has direct prior art, so this optimization is not claimed as a globally new algorithm.

The [Kemeny pair study](README-kemeny.md) determines a minimum of six vertices when individually neutral additions are allowed, and seven when both additions must individually decrease the constant. It retains two independent exact censuses, complete lower-order exclusion, a separately reviewed process correction, and a [portable uv reproduction package](experiments/kemeny-pair-minimum/README.md). The seven-vertex example and the evaluation formulas are prior work; publication-level novelty of the minimum results remains unresolved.

The [network-design research note](docs/kemeny-network-design.md) now gives two independently audited results: with at least three non-singleton parts of sizes at least three and at least one dominating vertex, any edge added inside a smallest non-singleton part strictly decreases the simple-random-walk Kemeny constant; a separate ranking theorem shows that this is an optimal single-edge location. A dependency-free exact polynomial certificate covers every number of parts. The [earlier three-part proof](README-kemeny-three-part.md) remains reproducible. Global novelty and practical impact remain unestablished.

The [single-failure research note](docs/kemeny-fault-tolerant-design.md) extends safety to every single original-edge deletion for three parts of sizes at least three and one hub. For a hub-link failure incident to a minimum part, restoring that link uniquely minimizes K among all one-edge insertions. A separate strict comparison eliminates an initially plausible alternate-upgrade rule. Complete integer certificates and independent audits support these scoped results; originality and real-world benefit remain unresolved.

When direct restoration is forbidden, the [complete alternative theorem](docs/kemeny-alternative-repair.md) identifies every optimal insertion: pairs between unaffected vertices of the damaged minimum part. There is one optimal orbit, with a unique edge only when that part has size three. These rules use each design's own stationary target weights; a fixed workload requires separate analysis.

For a fixed uniform start-and-destination workload, the [new decision rule](docs/kemeny-uniform-repair.md) selects a different repair: connect to the damaged vertex when all groups are equal; otherwise insert inside a largest group. Exact certificates prove the complete optimum set and that the best insertion beats doing nothing. A counterexample shows other legal links can worsen the same objective even while lowering electrical resistance.

The [weighted extension](docs/kemeny-weighted-repair.md) proves that these optimal locations remain unchanged for every common positive link strength, and gives the unique best strength when it can also be chosen. The proof links random walks, electrical resistance and established conductance optimization, while keeping the specific family result and its unresolved publication priority explicit.

The [workload and robustness extension](docs/kemeny-workload-robustness.md) gives the full repair rule when journeys increasingly involve the hub, for every common positive insertion strength. It also certifies a finite set of recommendations against any single old-link change up to 10%, and records exact counterexamples when several links change together. Portable exact checks and separate independent audits support these different scopes; publication priority and physical-network benefit remain unresolved.

The [action-choice study](docs/kemeny-workload-action-choice.md) includes doing nothing in the decision. Best unit repairs always improve the specified equal-part family, but an unequal12-vertex example has an exact workload interval where every unit addition is harmful. At a workload inside that interval, a weaker link helps; exact certificates identify the globally best edge set and strength. The result separates location, strength and the option to leave the network alone.

The [uncertain-workload study](docs/kemeny-unit-minimax.md) classifies every best deterministic unit repair across a traffic interval. A strict domination proof reduces the whole family to two repair types, selected by exact endpoint products. One example shows that choosing for the midpoint gives a worse worst-case relative regret; another refutes extending the unit-strength location rule to every strength. These are audited model results, with publication priority and practical impact still unresolved.

The broader objective remains active: progressively map more mathematics and use its connections to support verified discoveries. This finite region does not fulfill that full coverage objective. Proof status, source support, finite computation and novelty are separate questions. No current entry claims Lean 4 verification.

See [contribution guidance](CONTRIBUTING.md), [data semantics](docs/data-model.md), and [coverage and next regions](docs/coverage.md). The foundation evidence bundle certifies the published snapshot at commit `9e0adc5d7f7fb994d6e302086da47a13ac2a8561`; reproduce that historical gate from that revision. The structured-checker milestone has its own independently approved [evidence bundle](.codex/evidence/runs/assumption-checks-v1/bundle.json) and [passing gate](.codex/evidence/runs/assumption-checks-v1/gate-report-attempt-02.json). It passes 80 finite oracle cases, but the separate 24-result retrieval study added zero source-refutation detections. An earlier certificate does not certify later edits.

## Verification limits

Curated search uses explicit lexical substring scoring, with fifteen retrieval sanity cases. External searches reuse Loogle and TheoremSearch; none is an evaluated novelty detector. See the [reuse decision](docs/reuse-decision.md), [research-search boundary](docs/research-search.md) and [independently checked normalization case](docs/normalization-case.md). The exact browser lab is restricted to connected simple undirected unweighted graphs, even where a source entry discusses a weighted theorem. Source PDFs stay local under ignored `work/sources/`; only paraphrases, bibliographic metadata and limited evidence extracts belong in the repository. Untouched generated UI components are excluded from lint because the scaffold itself has existing lint violations. Historical evaluator source snapshots under `evidence/` are excluded from application lint and type checking; product source and the current portable checks remain checked. Browser checks cover focused WebMCP contracts, not general visual or responsive QA.
