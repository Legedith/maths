# Independent foundation audit

Auditor: `/root/sol_atlas_audit`  
Scope: the Mathematics Atlas foundation and the Loogle formal-library adapter in the final pre-commit snapshot. The separately staged symmetry/discovery optimization is outside this audit, except that the full test suite may import its modules. No browser screenshots, DOM inspection, visual/responsive QA, deployment, or WebMCP runtime certification was performed here.

## Gate verdicts

| Gate | Verdict | Basis |
|---|---|---|
| Source verification | **PASS** | All 31 curated nodes and all 40 material edges were reviewed by source cluster. Their current paraphrases, assumptions, and locators are conservatively entailed by seven authoritative sources. The three Spielman items are first-party lecture notes; the other four are research papers. The Grady and Klein local downloads failed TLS, so the audit used their primary author/journal web passages. Reuse-document claims were checked against official Loogle, TheoremGraph, zbMATH Open KG, MathGloss, and original-paper pages. No current entry claims novelty, exhaustive coverage, Lean verification, empirical segmentation accuracy, or chemical-property prediction. |
| Specification compliance | **PASS** | The delivered scope implements typed corpus records, assumptions and locators, real-data lexical search, relation inspection, 961-pair navigation, three learning journeys, five contribution tasks, seven finite examples, programmatic validation, exact bounded computation, and explicit novelty/coverage limits. Three complete `coe_explorer` final events were recovered and verified against the original rollout; each addresses cross-domain value, source quality, tractable validation, and beginner usefulness, and all precede implementation. The original encrypted prompt bodies prevent checking word-for-word prompt identity. Final bundle assembly plus Git commit/push remain root-owned post-audit operations. |
| Implementation alignment | **PASS** | Python validation enforces the frozen graph domain. Resistance, Markov first-step equations, and tree enumeration are composed through separate modules and share only the generic exact solver where allowed. The browser port uses BigInt fractions and reproduces every public output. Search normalizes punctuation and requires every term; the 31-node graph is connected for all 961 ordered pairs. Corpus validation rejects malformed collections, unsupported statuses, dangling evidence, unresolved or escaping formal artifacts, duplicate example IDs, and missing fixtures. The formal adapter fixes the upstream host, quotes name-fragment queries, caps the response at 512,000 bytes, validates returned modules, marks results untrusted/external, and never promotes them to the curated graph. Typecheck and lint passed. |
| Reproduction | **PASS** | `pytest` passed 75 tests. A fresh evaluator produced 772 deterministic records: connected labeled graphs 1/4/38/728 for n=2/3/4/5 plus one named six-cycle, with zero failures, seven valid fixtures, ten rejected invalid fixtures, and no sampling. Fresh records are byte-for-byte equal to the retained baseline, SHA-256 `b05d83051ba0f92713c87ced4742d1a902297b998d6f221250bef0f80890dd8c`; summaries agree after removing the absolute output path. Three transparent post-freeze six-vertex cases passed. Node v24.12.0 matched all fields for 772 baseline and three supplemental records plus the valid/invalid fixtures. The live quoted Loogle query returned HTTP 200, 23 declarations, and `SimpleGraph.lapMatrix`; its Mathlib documentation URL returned 200. |

## Source assessment

The detailed matrix is in `source-matrix.md` and `source-matrix.json`. The corpus edge distribution is 5 Laplacian-note edges, 14 resistance-note edges, 6 tree-note edges, 4 commute-paper edges, 4 sparsification-paper edges, 5 segmentation-paper edges, and 2 resistance-sum-paper edges, totaling 40. The most assumption-sensitive claims were checked directly:

- effective resistance as unit-flow voltage drop, its squared-Euclidean representation, series/parallel behavior, Schur complements, and the triangle inequality;
- commute time `C_st = 2m R_st` only for the stated connected unweighted undirected setting;
- weighted random-spanning-tree edge marginal `w_e R_e`, reducing to `R_e` for unit weights;
- Spielman-Srivastava sampling with its `n`, epsilon, sample-count, and success-probability conditions, without claiming strict edge reduction for every input;
- Grady's seeded first-hit-probability/Dirichlet segmentation formulation without an accuracy guarantee;
- Klein's resistance-distance sum rules as graph descriptors without a chemical-property guarantee.

The reused TheoremSearch normalization example was also checked against arXiv:1807.07167v1 §2.2 and Proposition 2.4. Its exact theorem body uses an unnormalized reversible conductance measure; the generated slogan's phrase “stationary probabilities” loses that convention. The retained K2 witness separates the two readings exactly, while making no error claim about the original paper or prevalence claim about the service.

## Raw reproduction paths

- Evaluator console: `console/evaluator.txt`
- Fresh canonical JSONL: `canonical/records.jsonl`
- Fresh evaluator summary: `canonical/summary.json`
- Baseline comparison: `reproduction-comparison.json`
- Full Python tests: `console/pytest.txt`
- Browser-port agreement: `console/browser-engine.txt` and `evidence/browser-engine/summary.json`
- Supplemental six-vertex run: `console/supplemental.txt` and `evidence/supplemental/records.jsonl`
- Corpus validation: `console/corpus-validation.txt` and `corpus-validation.json`
- Search/path check: `console/check-atlas.txt` and `evidence/corpus/search-and-paths.json`
- Formal adapter boundary check: `console/check-formal-search.txt` and `evidence/reuse/adapter-tests.json`
- Live formal adapter check: `console/formal-live.txt`, `formal-live-audit.json`, `formal-live-response.json`, and `formal-live-headers.txt`
- Normalization witness: `console/normalization-case.txt` and `evidence/reuse/normalization-witness.json`
- Selection provenance: `console/exploration-provenance.txt` and `exploration-provenance-check.json`
- Snapshot, commands, versions, hashes, and Git state: `snapshot-manifest.json`
- TypeScript and lint: `console/tsc.txt` and `console/lint.txt`

## Limits and required finalization

- Explorer task names, roles, times, full outputs, and ordering are verified. Their original prompt message fields are encrypted, so textual prompt identity is unavailable.
- The JavaScript runtime cannot distinguish a JSON number lexically written as `1.0` from `1`; Python rejects a native float object. This documented language-boundary difference does not affect JSON values after parsing.
- Cross-language agreement is strong reproduction evidence, but both implementations use the same mathematical decomposition; the separate Markov construction and combinatorial tree oracle supply the stronger internal checks.
- Loogle's official documentation says the JSON format is unstable, and its index may update every six hours. The live result is timestamp-specific and not a pinned Lean proof run.
- This audit makes no browser UI or WebMCP runtime claim. It inspected code and direct tool/library behavior only.
- The checked snapshot was uncommitted at Git HEAD `324a4f33c7015a32c4838176968325bc81d0d1f0`; `snapshot-manifest.json` hashes the reviewed files. Root must assemble the evidence bundle, commit, and push without changing audited core files, or request a delta review for any such change.
- The pre-assembly evidence-gate run is retained at `console/evidence-gate-preassembly.txt`; it failed solely because the bundle still had zero claims and four pending checks. That expected bookkeeping state must be replaced with this audit evidence and verified again before promotion.
- The finite foundation does not complete the enduring mapping or verified-discovery objective. The symmetry/discovery extension requires its own audit.
- After the core snapshot checks, `tests/test_symmetry.py:15` received a test-only portability correction from `parents[2]/project/fixtures` to `parents[1]/fixtures` (SHA-256 `f63405a6e57fc3ba6854df66f8e5ee80386191585ecddb8e27d123b81539746d`, case-insensitive). Root's retained `logs/integration-pytest-04.*` reports the unchanged 75-test pass. This did not alter the frontend, corpus, baseline engine, fixtures, or any gate conclusion here; the symmetry implementation remains outside this audit.

