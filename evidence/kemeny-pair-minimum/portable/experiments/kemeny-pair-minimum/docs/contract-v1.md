# Contract v1: minimum order of a jointly Braess pair

Status: selected for exact evaluation after independent source/method review and the five-text bounded prior-art review, including the explicit 2306.04005 citation lead. This task supports the larger mathematics atlas goal without redefining that goal. A successful finite result is neither a complete map nor proof of publication novelty.

## Question and scope

For a finite connected simple undirected unweighted graph G and distinct missing edges e and f, let P = D^-1 A be the transition matrix of its simple random walk. Define K(G) = sum of reciprocals of the nonzero eigenvalues of I-P. This definition includes periodic connected graphs. It uses no extra additive return-time constant.

Determine the minimum number n of vertices permitting

    K(G+e) <= K(G), K(G+f) <= K(G), K(G+e+f) > K(G).

Equal single-edge values count as non-Braess under this explicitly strict-increase convention. Retain equalities separately from decreases. The two nonedges may share a vertex. Graphs of order at most one have fewer than two distinct nonedges and cannot qualify. All graphs, edges, and additions retain explicit labelled vertex identities.

The selected proposal cites the naturally labelled P7 with missing edges {1,3} and {5,7} as a known published example. That example supplies an upper bound only after a source check and exact replay. It must never be presented as newly discovered here.

## Input freeze and enumeration

Use exactly the five official connected graph6 files for orders 2 through 6, retrieved in kemeny-input-work and pinned by source-manifest.json. Their advertised class counts are 1, 2, 6, 21, 112. Preserve the original files byte for byte. No data file or candidate may be replaced after results are observed without a new versioned specification and retained invalidated run.

For each representative in source order, enumerate every unordered pair of distinct nonedges in lexicographic order. Retain automorphic duplicates. An early positive result does not stop the census: all orders 2 through 6 and all marked pairs must be evaluated. Record graphs with fewer than two missing edges as having zero pairs. The graph's full degree vector, edge count, and random-walk matrix must be recomputed after each addition.

Independently establish input completeness by generating the permutation orbit of every supplied representative and comparing its union with the set of all connected labelled graphs on the same vertex set. Verify disjoint representative orbits and connectivity, graph6 decoding, no duplicate source records, exact per-order counts, and full labelled coverage. Do not treat agreement with the five advertised counts alone as a completeness proof.

## Author evaluator

Use an isolated uv environment with pinned Python and SymPy versions. Use exact integers and rationals only. For each graph state compute its grounded Laplacian inverse, all effective resistances, and

    K(G) = d^T R d / (4m).

A cache keyed by the full labelled graph state is allowed and must be disclosed. There is no speedup or algorithm-novelty claim. Every pair requires the base, each single addition, and joint addition values. Store each rational as a reduced numerator/positive-denominator pair, including exact zero. Floating-point values must not decide signs or witness status.

The canonical run must first replay the known P7 example. If the source interpretation or exact values fail to yield the specified inequalities, terminate with an invalid run and retain all output before any census interpretation. Tests on other study graphs before the canonical run are prohibited. Syntax checks and fixed input-hash checks are allowed.

Retain a graph-state value table, the complete marked-pair ledger, per-order sign and witness counts, every qualifying witness with explicit edge lists and graph6 identifier, the P7 replay, and a machine-readable summary. Minimum-order conclusions require both a positive witness and complete exclusion of every smaller order. Do not infer novelty, general prevalence, real-network performance, or human-time benefit.

## Independent evaluator

A separate agent must implement its own decoder, graph-state representation and evaluator without importing the author's mathematical code. Use standard-library Fraction arithmetic and the characteristic polynomial of I-P. If q(x) = det(xI-(I-P))/x, compute K = -q_1/q_0 from its linear and constant coefficients. Faddeev-LeVerrier is an allowed exact coefficient method. Verify the zero constant term and nonzero q_0 explicitly.

The verifier must compute its own full pair census and P7 replay before reading author verdicts or ledgers. Record a timestamped hash of those independent outputs before the comparison. Compare all exact graph-state values and every pair's classification, not only positive cases. Independently verify the permutation-orbit coverage described above. Formula agreement without complete candidate coverage is insufficient.

## Execution and failure records

Keep root as the only writer to the shared project. Author and independent verifier own separate D-drive staging directories. All Python execution uses uv and isolated environments; keep the uv cache on D. Record source and environment hashes, exact argv, working directory, start/end UTC timestamps, return code, timeout status, raw stdout and stderr, and a chronological attempt log. Preserve failed attempts and unchanged prior inputs.

Each canonical evaluator process has a 30-minute hard limit. No automatic expansion past order 6 is permitted; the separate fixed P7 replay is the only order-7 evaluation. A timeout or mismatch invalidates that attempt and is not evidence of absence. A corrected rerun requires an explicit documented correction, new source hash, and retained prior output. Do not optimize or change definitions after seeing results to obtain a preferred answer.

## Source and final gates

Before implementation, independent reviewers must verify the primary-source witness, both exact formulas, strict-increase convention, and finite search sufficiency, and perform the targeted broader prior-art check. If the exact minimum result or exhaustive classification is found already published, stop this proposed discovery experiment and record the reuse decision.

After both evaluators finish, create typed source, code, log, result and conclusion provenance. Require independent reproduction, specification compliance, source verification and implementation alignment gates. Freeze mathematical results before a follow-up literature search for the exact result. Search absence cannot establish global novelty. Any final description must distinguish an algorithmically verified finite fact, its relationship to inspected prior work, and unresolved publication-level novelty.

## Pinned execution details

Source-manifest SHA-256: e4a02bdeb62d8e6b0e68849b4aa3d65d9a37744578bebd48abe740fe94c52c7f. All five listed source hashes must match before execution. The independent completeness implementation must additionally check labelled connected counts for orders 2 through 6 equal 1, 4, 38, 728, 26704, and each representative's pair count equals choose(number of nonedges, 2).

The author owns D:/CodexWorkspaces/mathematics-atlas/kemeny-author-work. Use Python 3.12.11, SymPy 1.14.0, uv 0.8.19, and a frozen uv.lock. The independent evaluator owns D:/CodexWorkspaces/mathematics-atlas/kemeny-independent-work, uses Python 3.12.11 and the standard library only, and maintains its own frozen uv environment. Existing base interpreters may be reused; both virtual environments, experiment data, logs, and UV_CACHE_DIR remain on D.

Author evaluation argv (from the author directory):

    uv run --project . --frozen python census.py --input-dir D:/CodexWorkspaces/mathematics-atlas/kemeny-input-work --output-dir D:/CodexWorkspaces/mathematics-atlas/kemeny-author-work/run-01

Independent evaluation argv (from the independent directory):

    uv run --project . --frozen python verify_census.py --input-dir D:/CodexWorkspaces/mathematics-atlas/kemeny-input-work --output-dir D:/CodexWorkspaces/mathematics-atlas/kemeny-independent-work/run-01

Each process must be invoked by an audit-owned logging wrapper with a 1800-second timeout; the wrapper records its actual argv, UTC timestamps, process result, stdout and stderr. Before invoking the evaluator, seal its source, wrapper, .python-version, pyproject.toml, uv.lock, interpreter version, this contract, and all input hashes in an input-freeze manifest. Creating the lock and running syntax/hash checks does not evaluate study cases. Do not run unlogged study computations.

Required deterministic outputs are summary.json, graph-values.json, pairs.jsonl, witnesses.json, and published-p7.json. They may include additional fields, but must retain n, source line and graph6 for each representative; graph states identified by n plus the full sorted edge list; every pair of added edges; all four K values; all three deltas; signs and exact equality flags. Vertices in all public records are numbered 1 through n, and edges and edge pairs are lexicographically sorted. Reduced rational values are objects with integer numerator and positive integer denominator. Timing belongs in separate command logs, not mathematical values.

The independent evaluator must seal the hashes of its own deterministic outputs before any author-result comparison. Its graph-source completeness result is additionally retained as completeness.json. Author results must remain unread by the independent implementer until that seal exists. A separate final reviewer will inspect both raw runs, the comparison, and the typed evidence bundle.

Pre-execution source review: /root/sol_symmetry_audit verified the P7 witness, both K formulas, graph counts, all five input hashes, and the strengthened independent census/coverage obligations. Initial four-text prior-art review: source-notes.json SHA-256 eefafc33143c177442d35bfa123ddcb7a4232014b679f1211b73b98d19cf23f6. Supplementary primary text review: supplement-2306.04005.json SHA-256 5ed72f2385d33dbf082c0eff26fa8f9275865353151fecaaf45df51aed8a5827. These reviews found no exact-result blocker within their stated limits; they do not certify novelty.

