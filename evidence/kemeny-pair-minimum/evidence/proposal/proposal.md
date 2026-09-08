# Proposal: minimum order of a jointly Braess edge pair

**Status:** exploratory proposal only. No graph enumeration, matrix evaluation, or study-case computation was run for this artifact.

## The exact question

For a connected simple undirected graph `G`, let `e` and `f` be distinct nonedges and write

```text
delta_e  = K(G + e)     - K(G)
delta_f  = K(G + f)     - K(G)
delta_ef = K(G + e + f) - K(G).
```

Find the minimum order `n` for which some `(G,{e,f})` satisfies

```text
delta_e <= 0,  delta_f <= 0,  and  delta_ef > 0.
```

Here `K` is Kemeny's constant for the simple random walk with row transition matrix `P = D^-1 A`. The inequalities follow Definition 4.1 of Faught, Kempton, and Knudson: a Braess edge or set requires a **strict** increase. Exact zero differences must be reported separately so that the result can also be read under papers that use a non-strict edge convention.

The closest known witness in the reviewed sources is the naturally labelled path `P7`, with `e={1,3}` and `f={5,7}`. The cited paper states that the pair is Braess while neither singleton is Braess. It does not state that order 7 is minimum. Thus the known witness supplies an upper bound; the only finite search needed for minimum order is over orders 2 through 6.

## Proposed delta over known work

The 2021/2022 paper defines Braess sets and supplies the `P7` example. The 2026 follow-on studies clique-shaped sets and proves constructions illustrating interactions between individual edges and whole cliques. The proposed output is narrower: an exact, independently replayable minimum-order certificate for a two-nonedge set, or a smaller counterexample to the apparent order-7 upper bound.

This is not a proposal for another general solver. It reuses a complete non-isomorphic graph source and existing exact linear algebra. The computation method itself is standard. The candidate added result is the minimum-order fact, if it survives independent verification and a broader novelty review.

## Bounded experiment

1. Freeze the exact nauty version or the official graph6 files before implementation. Enumerate every connected simple graph of orders 2 through 6. Require the per-order counts `1, 2, 6, 21, 112` (142 total), matching the official nauty catalogue.
2. For each graph representative, enumerate every unordered pair of distinct nonedges. Checking all such pairs on one representative covers every marked choice; automorphic duplicates may be retained because they cannot create a false existence result.
3. Evaluate all four graph states (`G`, `G+e`, `G+f`, `G+e+f`) using exact rational arithmetic. The primary route is the resistance identity `K(G)=d^T R d/(4m)`, with resistances obtained by exact grounded-Laplacian solves. Floating-point comparisons are forbidden.
4. Independently replay every qualifying case and the published `P7` case through the spectral route. If `mu_2,...,mu_n` are the nonzero eigenvalues of `I-P` and `q(x)=det(xI-(I-P))/x`, then `K(G)=sum_i 1/mu_i=-q_1/q_0`, where `q_0` and `q_1` are the constant and linear coefficients. This coefficient computation remains rational and avoids numerical eigenvalue decisions.
5. Retain the pinned inputs, source and environment hashes, exact command records, graph counts, number of nonedge pairs examined, a full sign ledger, and for every witness: graph6, an explicit edge list, `{e,f}`, all four exact `K` values, and the three reduced rational differences.
6. Have a separate verifier regenerate or independently parse the 142 graph classes and run the second formula without access to author-produced verdicts. Any count mismatch, omitted candidate, formula disagreement, or nonzero process error invalidates the result.

The run gets a predeclared 30-minute process limit and no automatic expansion past order 6. The official class count and matrices of order at most 7 make local feasibility plausible, but this proposal contains no runtime measurement.

## Outcomes and stop rules

- If a qualifying graph occurs at order at most 6, the result is a smaller exact witness than the one identified in the reviewed paper. Search all lower orders before describing it as minimum.
- If none occurs through order 6 and the `P7` replay passes, the finite certificate establishes minimum order 7 within connected simple undirected graphs under the pinned strict-increase definition.
- If the `P7` replay fails, or equality changes its classification, stop and resolve the semantic or source discrepancy before interpreting the census.
- If either exact route disagrees, or independent verification cannot reproduce the complete input and candidate counts, report an invalid experiment rather than a mathematical result.
- Before implementation, run a targeted broader literature check. If it finds the same minimum theorem or a published exhaustive census, stop: the proposed novelty value has been falsified even though the replay may remain a useful test.
- If the run only reproduces `P7` without a complete no-smaller certificate, it adds no discovery value and should not be promoted.

## Novelty boundary

The Braess-set definition, the `P7` witness, resistance formulas, spectral formulas, and non-isomorphic graph generation are known. A three-source review cannot establish that nobody has already computed the minimum. A successful result should initially be called a **candidate exact minimum-order computation**. Publication-level novelty requires a wider literature search and expert review after the result is frozen; search absence alone is not evidence of novelty.

If the exhaustive certificate passes, its mathematical scope is precise: connected, finite, simple, undirected, unweighted graphs and unordered pairs of distinct nonedges, with strict increase defining a Braess set. It says nothing about directed or weighted networks, larger edge sets, frequency in graph families, or a new general algorithm.

## Primary sources

1. Faught, Kempton, and Knudson, [A 1-Separation Formula for the Graph Kemeny Constant and Braess Edges](https://arxiv.org/abs/2108.01061), especially Definition 4.1, Lemma 1.1, and the example after Corollary 4.3.
2. Breen, deBlieck, and Vander Meulen, [Kemeny's constant and Braess cliques in graphs](https://arxiv.org/abs/2608.04150), especially Theorem 2.1, Proposition 2.2, Section 5, and the concluding notes.
3. McKay and Piperno's official [nauty and Traces site](https://users.cecs.anu.edu.au/~bdm/nauty/) and McKay's official [connected graph catalogue](https://users.cecs.anu.edu.au/~bdm/data/graphs.html).
