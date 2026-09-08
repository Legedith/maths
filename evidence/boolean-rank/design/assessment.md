# Boolean-rank bridge integration assessment

## Recommendation

Integrate the independently admitted R1-R4 records as a second curated region, after adding typed edge fields for source scope, two-way witness translation, Atlas-local boundary cases, notation boundaries and retained review provenance. Use Atlas schema `1.1` because dropping those new fields would change the meaning of the relations.

The exact proposed records and file actions are in `integration-design.json`. This is design work only; no project file was changed.

The reviewed project baseline is Git revision `08434cb8f3a0923a7b781503cec64a86878cf171`. Root-authored implementation edits appeared in the working tree after the baseline was pinned. `input-drift.json` retains that boundary; this packet does not certify those later bytes.

`consumer-inventory.json` enumerates every active atlas consumer, the sole runtime equality check for schema `1.0`, unrelated `1.0` schemas that must remain unchanged, and the SVG's fixed geometry.

## Why the current schema is insufficient

The current `AtlasEdge` model in `lib/atlas.ts` stores a statement, assumptions and source locators. `Connection` in `components/atlas-map.tsx` renders only those fields. That cannot represent the most important boundary in the reviewed records: the papers support the standard translations, while the all-zero totalizations use explicit Atlas conventions and elementary local proofs.

Do not bury the witness maps or the zero case in a long `statement` string. Add these optional edge fields and render them inside the existing disclosure:

- `source_scope`
- `witness_translation: { forward, reverse, result }`
- `local_boundary_case: { case, adopted_conventions, argument, result, evidence_basis }`
- `notation_boundaries`
- `curation_record`

Require the full set on the four admitted edges. `evidence_basis` for each zero case must be the literal `atlas_local_definition_and_proof`.

## Required concepts

Seven nodes are sufficient:

1. `boolean-relation-matrix`
2. `boolean-rank`
3. `one-support-rectangle-cover`
4. `fixed-bipartition-biclique-cover`
5. `nondeterministic-communication-s2`
6. `local-boolean-rank`
7. `local-biclique-cover`

The last two must be nodes rather than phrases embedded only in R4. Their objectives are maximum participation per row/column and per vertex. They are different from total cover size and from witness multiplicity per cell or edge.

Use two new source records:

- Javadi, Maleki and Omoomi, *Local Clique Covering of Graphs*, arXiv:1210.6965v1, Introduction, printed pp. 2-3.
- Karchmer, Newman, Saks and Wigderson, *Non-deterministic Communication Complexity with Few Witnesses*, Sections 2.1-2.3, printed pp. 3-5, especially Proposition 3 and its proof.

The proposed wording paraphrases the sources and preserves their reuse limitations. The Karchmer PDF's title page is dated February 11, 2003; the Javadi paper is the pinned 2012 arXiv version.

## Relationship projection

- **R1:** `boolean-rank -> one-support-rectangle-cover`, `r_B(A)=rc_1(A)`. Retain Boolean OR-AND arithmetic, unrestricted overlap, `k=0` and empty OR. A factorization with `k` factors yields at most `k` nonempty rectangles after empty factors are omitted; a cover with `t` rectangles yields exactly `t` factors. These two inequalities prove equality of the minima.
- **R2:** `one-support-rectangle-cover -> fixed-bipartition-biclique-cover`, `rc_1(A_G)=bc(G)`. Retain the fixed labeled nonempty sides and rectangular biadjacency matrix. The forward and reverse maps preserve cover cardinality cell-for-edge.
- **R3:** `one-support-rectangle-cover -> nondeterministic-communication-s2`. State the cited formula only for nonempty 1-support, define `M_f[x,y]=f(x,y)`, map Atlas `N^1_S2` to source `n(f)`, and then show the Atlas-local zero totalization separately. Do not identify it with `n_1(f)` or deterministic complexity.
- **R4:** `local-boolean-rank -> local-biclique-cover`, `lr_B(A_G)=lbc(G)`. The witness maps preserve each row/column or vertex incidence, not per-cell multiplicity.

Supporting definition edges connect the matrix to its cover, each total-cover parameter to its local-load version, and the Boolean biadjacency representation to the existing adjacency-matrix node through an explicit `distinguishes_representation` edge. That final edge is a boundary, not an equality; it also satisfies the existing all-pairs navigation requirement without inventing a transfer theorem.

## Beginner path and practical question

Use the journey **From a yes/no table to a communication certificate**:

1. Mark accepted pairs in a finite table.
2. Group accepted pairs into all-one rectangles.
3. Read each rectangle as one Boolean factor.
4. With fixed graph sides, read it as one biclique.
5. Ask how many branch bits identify a compatible rectangle under the cited nondeterministic protocol model.

The final prompt may use the concrete setting "one machine knows `x`, another knows `y`, and both use a public acceptance table." It must immediately say that the formula does not measure deterministic cost, privacy, latency or deployed-system performance. This gives a recognizable computer-science question while accurately presenting established mathematics.

The separately reported 3-by-3 overlap illustration could later sit after steps 2-3 if its own independent audit passes. The current graph-specific example validator cannot accept it without a kind-specific artifact rule. This assessment did not inspect or certify that example.

## Files and tests

The implementation touches `data/atlas.json`, `lib/atlas.ts`, `components/atlas-map.tsx`, `app/page.tsx`, `scripts/validate_atlas.py`, `scripts/check-atlas.ts`, `docs/data-model.md`, a new bridge explanation, coverage/reuse documentation and a retained evidence projection. `/api/atlas`, lexical search and `connectionPath` need no algorithm change.

The map does not use corpus `x/y` metadata: it places the selected concept and only its direct neighbors on a fixed radial layout. The proposed node of highest degree has five neighbors, below the current maximum of eight, so this addition alone does not require changing the `840 x 660` viewBox. Check finite coordinates, label baselines and cluster colors functionally. No visual-quality claim is part of this packet.

The exact design adds 7 nodes, 8 edges, 2 sources and 2 journeys to the pinned 33-node/44-edge/9-source/4-journey corpus. Tests should cover structural shape, exact R1-R4 projection, negative convention mutations, lexical discovery, journey references, all-pairs navigation, API preservation, typecheck, lint, build and existing feature regressions. The implementer must not self-certify the final source/projection gate.

No solver, matrix census, application benchmark or performance experiment is needed for this integration. All four relationships are known; the value is preserving their assumptions and translating them clearly, not claiming a new equivalence or measured practical impact.
