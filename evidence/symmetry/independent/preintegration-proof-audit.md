# Independent proof and assumption audit (pre-integration)

Date: 2026-09-08.  Scope: the frozen `discovery-contract.md` and
`symmetry-contract.md`, and the unchanged `project/src/atlas_engine` baseline.
This note does not certify candidate code or performance; neither was available
for integration audit when this proof pass began.

## Exact statement that can be supported

Let an admitted input be a connected simple undirected unweighted graph
`G=(V,E)` with `2 <= |V| <= 6`, together with distinct ordered terminals
`(s,t)`.  Let two inputs be equivalent when a graph isomorphism maps the
*unordered* set `{s,t}` onto the other unordered terminal set.  Encode a
labelled graph injectively by its complete upper-triangle edge bit vector and
choose the least encoding over the two terminal orders and every permutation
of the other vertices.

Assume a cache miss invokes the unchanged `analyze_graph` on that canonical
graph with source `0` and target `1`.  The complete baseline result for every
equivalent caller is recovered exactly by:

* permuting both Laplacian indices;
* permuting potentials when the caller source maps to `0`;
* using `R - p` after permutation when the caller source maps to `1`;
* swapping the two directional hitting times in that reversed case;
* preserving scalar invariants, tree counts, applicability, and checks; and
* returning the caller's validated normalized edges and ordered terminals.

This is a correctness statement for the complete admitted implementation
domain.  Its proof is algebraic/combinatorial.  The finite audit is corroborating
evidence and is not being used to infer an unrestricted theorem.

## Proof obligations

### Canonical keys classify precisely the required equivalence

Each eligible relabelling is a bijection `f: V -> {0,...,n-1}` with
`{f(s),f(t)}={0,1}`.  The edge encoding is injective for fixed `n`.  If two
inputs have the same minimum encoded graph, their minimizing bijections compose
to a graph isomorphism that carries one unordered terminal pair to the other.
Conversely, composing any eligible relabelling with such an isomorphism gives
the same set of candidate encodings, hence the same minimum.  The key must
include `n`; the bit integer alone is not the stated canonical identifier.

The implementation proof therefore depends on four concrete facts: all and
only the eligible bijections are enumerated, the edge order is fixed, the
encoding is injective, and `n` is in the key.

### Laplacian transport

For a caller-to-canonical bijection `f`, adjacency and degrees are preserved,
so

`L_G[x,y] = L_H[f(x),f(y)]`.

Both matrix indices must be permuted.  This also proves that row-sum and all
other label-independent Laplacian statements survive transport.

### Unique grounded voltage and endpoint reversal

For canonical source `0`, target `1`, the baseline vector `p` solves

`L_H p = e_0 - e_1`, with `p[1]=0`,

and `R=p[0]`.  The grounded solution is unique.  Indeed, for a vector `z`
grounded at the target,

`z^T L z = sum_{uv in E} (z[u]-z[v])^2`.

If the reduced homogeneous system vanishes, connectedness makes `z` constant,
and grounding makes that constant zero.  Thus the reduced Laplacian is
nonsingular.

If the caller source maps to `1` and target to `0`, define

`q[x] = R - p[f(x)]`.

Laplacian row sums are zero, so the constant `R` disappears and

`L_G q = e_s - e_t`.

Also `q[t]=R-p[0]=0`; hence uniqueness makes `q` exactly the caller's grounded
baseline potential.  Plain negation is wrong because it leaves the wrong
gauge.  On `K2`, canonical `p=[1,0]`; reversal requires `[0,1]`, whereas `-p`
would give `[-1,0]` under the identity vertex map.

### Directional Markov values

The first-step system for destination `t` is

`h[t]=0`, and `h[v]=1+average(h[w] : w adjacent to v)` for `v != t`.

It is unique on a finite connected graph.  The difference of two solutions is
harmonic off `t` and zero at `t`; the discrete maximum/minimum principle forces
that difference to zero.  A graph isomorphism therefore transports a hitting
function to the corresponding hitting function.  When orientation reverses,
the caller's forward value is the canonical `1 -> 0` value and its backward
value is canonical `0 -> 1`; the two scalars must be exchanged.

They are not generally equal.  For the three-vertex graph with edges
`{0-1,0-2}`, the audit found `H(0,1)=3` and `H(1,0)=1`.

### Spanning trees and nonedge applicability

Relabelling maps edge subsets bijectively.  It preserves connectedness and
cardinality, hence maps spanning trees bijectively.  If `{s,t}` is an edge,
trees containing it correspond exactly to canonical trees containing `{0,1}`.
If `{s,t}` is not an edge, `{0,1}` is not an edge either.  Therefore total tree
count, selected-edge count, and their ratio are invariant where applicable;
for a nonedge, `tree_edge_count` and `edge_probability` remain `null`, and the
conditional edge-probability check must remain absent.

The unchanged baseline's tree oracle is independent in the required sense: it
uses only `(n-1)`-edge subset enumeration and connectivity, not the Laplacian,
determinants, resistance, or Markov values.  The verifier cross-checked it with
a separate fraction-free matrix-tree determinant and, for selected edges, the
contraction identity `tau_e(G)=tau(G/e)` while retaining parallel-edge
multiplicity after contraction.

### Tied canonical minimizers

Suppose eligible minimizers `f` and `g` produce the same canonical labelled
graph `H`.  Then `a = g composed with inverse(f)` is an automorphism of `H`
preserving `{0,1}` as a set.  It may fix or exchange the endpoints.  If it fixes
them, uniqueness makes the canonical voltage and hitting solutions invariant
under `a`.  If it exchanges them, uniqueness gives the voltage relation
`p[a(v)] = R-p[v]`, and graph isomorphism gives `H(0,1)=H(1,0)`.  The transport
orientation changes at the same time, so either minimizer produces the same
caller output.  Laplacian and spanning-tree claims are already automorphism
invariant.

Equivalently, each tied transport independently solves the same uniquely
specified caller equations and returns the same caller-labelled graph data, so
the two outputs must agree.  A deterministic tie-break remains desirable for
diagnostics and reproducibility but is not a correctness assumption.

## Independent finite corroboration

Command (uv cache fixed as required):

`$env:UV_CACHE_DIR='D:\CodexWorkspaces\mathematics-atlas\uv-cache'; uv run --project 'D:\CodexWorkspaces\mathematics-atlas\project' python 'D:\CodexWorkspaces\mathematics-atlas\symmetry-audit-work\preintegration_audit.py' --output 'D:\CodexWorkspaces\mathematics-atlas\symmetry-audit-work\preintegration_audit.json'`

The standalone verifier enumerated every labelled connected simple graph on
2..5 vertices and every ordered distinct terminal pair.  Results:

* graph counts: `1, 4, 38, 728`, total `771`;
* ordered pair counts: `2, 24, 456, 14560`, total `15042`;
* ordered existing-edge pairs: `8588`;
* ordered nonedge pairs: `6454`;
* unordered-terminal canonical classes: `118 = 69 edge + 49 nonedge`;
* frozen 771-input first-edge benchmark classes: `69`;
* inputs with minimum-label ties spanning both endpoint orientations: `3142`;
* exact full-result transport mismatches: `0`;
* tied-minimizer transport mismatches: `0`;
* independent tree-oracle mismatches: `0`;
* nonedge applicability mismatches: `0`.

This bounded run tests the formulas and supplies independent expected counts.
It does not replace the proof above and does not audit candidate code.

A separate all-terminal run over the five frozen six-vertex boundary families
checked 150 ordered pairs (`76` edges, `74` nonedges) and found zero transport,
tie, determinant/contraction-tree, or applicability mismatches.  It found 20
canonical classes across the families and 100 instances with minimizing maps in
both terminal orientations.  Per-family class counts were: `P6=9`, `C6=3`,
`K1,5=2`, `K6=1`, and two triangles joined by a bridge `=5`.

## Concrete implementation hazards to reject later

1. Canonicalizing the graph without constraining the distinguished terminal
   set merges inequivalent questions.  In path `P3`, an adjacent pair has
   resistance `1` while the two endpoints have resistance `2`.
2. Caching only the key and orientation is insufficient for caller-labelled
   potentials and Laplacian; each call needs its caller-to-canonical bijection.
3. Reversal by `-p` violates the grounded gauge; use `R-p`.
4. Commute symmetry does not make directional hitting times equal; swap them.
5. Validation must finish before lookup.  Otherwise duplicate or reversed
   duplicate edges can collapse onto a warm valid key and return a result for an
   invalid payload.  Exceptions must never be cached.
6. `n` must be part of the key, and bit ordering must be fixed and injective.
7. The canonical core must be produced by unchanged `analyze_graph(H,0,1)` so
   its independent resistance, Markov, and subset-tree cross-checks remain in
   force.
8. Every returned nested list and mapping must be fresh.  A shallow outer copy
   is not enough to protect cached edges, Laplacian rows, potentials, or checks.
9. The cache must be instance-local and bounded.  The eviction policy and
   `clear()`/diagnostic semantics need explicit tests and documentation.
10. For a fresh capacity large enough to retain the frozen benchmark's 69
    classes, expected diagnostics are exactly `69` misses/core calls and `702`
    hits.  Other counts require an explained eviction-capacity effect.

## Scope conclusion

The mathematical transport is valid for the frozen admitted inputs under the
listed assumptions.  It is an application of established graph
canonicalization, automorphism, electrical-network, Markov, and spanning-tree
facts.  At most, the deliverable can support a new project-specific assembly and
measured optimization for this exact workload.  It cannot support a new graph
theorem, globally novel algorithm, unrestricted-domain result, or demonstrated
scientific/real-world impact.
