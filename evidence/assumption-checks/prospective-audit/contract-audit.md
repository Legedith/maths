# Prospective structured-transfer checker audit

Auditor: `/root/sol_atlas_audit` (independent read-only verifier)  
Audit time: 2026-09-08T01:52:15Z  
Scope: the prospective mathematical and schema contract only. No implementation existed in this audit scope, and this report does not certify implementation behavior, retrieval quality, natural-language interpretation, browser behavior, originality, or real-world error rates.

## Snapshot reviewed

| Artifact | SHA-256 |
|---|---|
| `project/docs/assumption-check-contract.md` | `6eaf5f003b0cf6f34b7b416edc229072079244ff0008cf53a208abc8b40a8e20` |
| `project/docs/assumption-check-interface.md` | `63bea7e1be12ef64e172508d235d1f1ff5cbca137d461c51d849c1ef160a26bf` |
| `project/fixtures/retrieval-study-v1.json` | `848ac3e25222af20cf86429b9648d9c282275a437f69401f51f300e9279ff224` |

## Prospective verdict

**CONDITIONAL PASS for implementation after the accepted clarifications below are made normative.** The central mathematical conventions are coherent. The frozen interface, read literally without the clarifications, leaves several cases with more than one defensible output. Those ambiguities would make an independent exact evaluator unfair. Root accepted all items before dependent implementation work and stated that an addendum will record them.

## Normative clarifications required by the evaluator

1. Top-level `source` and `target` are terminal vertex identifiers: non-boolean integers in `[0,n)`, and distinct. The term `source` here is electrical/Markov orientation, not literature provenance.
2. Integer conductances and all rational constants receive the same 12-digit numerator/denominator bound. A denominator is a positive nonzero integer. Input fractions may have an optional numerator sign and leading zeros and are reduced to a canonical `p/q` form with positive denominator; conductances must normalize to a strictly positive value. Booleans never count as integers.
3. Boolean literals admit both JSON `true` and `false`.
4. Missing/extra/wrong-typed fields, unknown expression kinds/operators, invalid indices, and total AST limit violations are `invalid_input`. A syntactically valid quantity node whose name is not supported is an evaluability failure and therefore `abstain`.
5. Verdict precedence is deterministic: validate the whole input structure first; then apply provenance-interpretation abstention; then evaluate recorded assumptions. Any exactly false assumption yields `not_applicable`, even if another assumption is undefined. If none is false but one is undefined, yield `abstain`. Only then evaluate the claim (`undefined` -> `abstain`, false -> `counterexample`, true -> `no_counterexample_in_instance`).
6. Boolean `and` and `or` use strict evaluation with undefined propagation. They do not hide an undefined operand through short-circuiting.
7. The 300-node budget is the total across every assumption and the claim; each expression root has depth 1 and maximum depth 20.
8. `hit_forward = E_source[tau_target]`, `hit_backward = E_target[tau_source]`, and `commute` is their sum. For connected graphs, `potentials` is the unique solution of `L v = e_source - e_target` with `v_target = 0`; `resistance = v_source - v_target`.
9. `stationary_distribution` is the degree-normalized stationary vector selected by the interface. On a disconnected graph with no isolates it is stationary but generally not unique and does not imply convergence from arbitrary initial distributions. Referenced quantities are computed lazily; an unrelated undefined catalog quantity cannot force abstention.
10. A `period` trace includes a checkable structural certificate: a complete bipartition for period 2, or an explicit odd cycle for period 1. A finite transition prefix is not a certificate.
11. The frozen name `total_conductance` means graph volume `sum_v d_v = 2 sum_e c_e`. Every trace must expose both equal forms. It must never silently mean `sum_e c_e`.

## Checked mathematical conventions and traps

| Topic | Evaluator interpretation | Trap the implementation must avoid |
|---|---|---|
| Combinatorial Laplacian | `A_uv=c_uv`, `D=diag(sum_v c_uv)`, `L=D-A`; defined for all admitted graphs. | Treating a conductance as a resistance, or normalizing `L` accidentally. |
| Transition matrix | With no isolates, `P=D^-1 A`; row distributions use `mu P`, column functions use `P f`. | Mixing row and column conventions produces a transpose on irregular graphs. |
| Random-walk Laplacian | `L_rw=I-P=D^-1 L`; rational and generally nonsymmetric. Undefined as a whole-matrix quantity if any vertex is isolated. | Substituting the symmetric normalized Laplacian, which generally contains square roots. |
| Similarity | When `D` is invertible, `D^(1/2) L_rw D^(-1/2)=L_sym=D^(-1/2)L D^(-1/2)`. | Similar matrices share eigenvalues; they are not entrywise equal and do not share raw eigenvectors. |
| Stationarity | The degree vector is an unnormalized reversible measure. Its normalization by graph volume is stationary when `P` is defined. Connectedness gives uniqueness; aperiodicity is additionally needed for convergence from every start. | Calling stationarity, uniqueness, and convergence the same fact. A connected bipartite walk has the stationary vector but oscillates from a point mass. |
| Period | For a connected, loopless undirected graph with positive edge weights, support alone determines period: bipartite gives 2; an odd cycle gives 1. | Inferring nonconvergence from finitely many steps, or assigning one period to a disconnected chain. |
| Electrical quantities | Same-component terminals have finite resistance and hitting quantities, solved on that component. Different-component values are reported undefined under this interface. | Returning zero or an arbitrary finite pseudoinverse result across components. |
| Potentials | Global potentials are exposed only on a connected graph and use the target-zero gauge and source-to-target unit-current sign. | Comparing ungrounded potentials as if they were unique, or reversing the injection sign. |
| Hitting/commute | Hitting times are directed. On a connected weighted network, `commute = graph_volume * resistance`. | Assuming forward and backward hitting times are equal, or using `sum_e c_e` and losing a factor of 2. For same-component terminals in a disconnected graph, the component volume governs the componentwise identity; the sourced whole-network theorem instead fails its connectedness assumption. |
| Weighted spanning trees | `tree_mass=sum_T product_(e in T)c_e`; it is zero if disconnected. For connected graphs the product of nonzero combinatorial-Laplacian eigenvalues is `n*tree_mass`. | Counting trees without their weights, or dropping the factor `n`. |
| Edge inclusion | For an existing edge in a connected graph, `Pr[e in T]=c_e R_eff(e)` under product-of-conductance tree sampling. | Dropping `c_e`, or applying an edge theorem to a nonedge. The interface deliberately makes the edge mass/probability undefined for nonedges and disconnected graphs. |
| Random-walk spectral product | On a connected graph, the product of nonzero eigenvalues of `L_rw` is the coefficient equal to the sum of its principal `(n-1)`-minors. From similarity and Matrix Tree, it equals `tree_mass * graph_volume / product_v d_v`. | Reusing `n*tree_mass`, which is the combinatorial-Laplacian formula. |
| Rank and determinant | For positive weights, `rank(L)=n-components`; `det(L)=0` for every admitted graph. | Treating determinant zero as evidence that the graph is disconnected. |

## Remaining limitations after clarification

- `total_conductance` is a potentially misleading public name for graph volume. Version 1 can remain deterministic because the formula is explicit, but source annotations must quote or map the source convention rather than match names.
- The language has no infinity value. A source statement that explicitly assigns infinite cross-component hitting time or resistance cannot be translated as rational equality; it must be represented through a connectedness assumption/undefinedness or the translator must abstain.
- A disconnected graph with no isolates has many stationary distributions. Version 1 exposes one canonical degree-normalized vector but no quantity for uniqueness or convergence. These properties can only be checked through recorded structural assumptions (`connected`, `period`) and a source-faithful claim expressible in the grammar.
- The language has no terminal-component-volume quantity. The connected-network commute theorem remains checkable by recording `connected`; a componentwise variant on a disconnected whole graph is outside version 1.
- Exact structured checking says nothing about whether retrieved prose was translated correctly. That remains an independently annotated retrieval study.

## Source basis

Typed locators and local file hashes are in `source-locators.json` and `raw/source-hashes.json`. The key anchors are Masuda, Porter and Lambiotte (2017), eqs. (75)-(77) for `D^-1 L=I-P`; Spielman (2006), PDF pp.1-2 for the row-walk matrix and its similarity to the symmetric matrix; Levin and Peres with Wilmer (2017), book pp.7-10 and 52 for period, stationarity, and convergence; book pp.116-119 and 131-132 for weighted networks, voltage gauge, and commute time; and Spielman (2018), Theorems 14.5.1 and 14.6.1 for weighted tree mass and edge inclusion.
