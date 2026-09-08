# Optimal repair when destinations stay fixed

The best repair depends on the question asked. Kemeny's constant weights
destinations by each candidate network's degrees. Here every vertex is an
equally likely start and destination, with that workload held fixed across
repairs. For this objective we obtain a different, complete decision rule.

Consider three groups with every connection between different groups,
no connections within a group, and a hub connected to everyone. One
vertex u in a smallest group loses its hub connection. If the groups all
have equal sizes, connect u to another member of its group. Otherwise,
connect two members of a largest group. This recommended insertion also
beats leaving the damaged graph alone.

## Exact objective and theorem

Let G=K_(a,b,c) join K1, with integer 3<=a<=b,c. Let A be the a-part,
u in A, h the hub, and H=G-uh. For a connected graph J on n vertices put

    U(J) = (1/n^2) sum_(i,j) E_i[T_j],    E_j[T_j]=0.

This is the mean number of discrete random-walk steps between independent
uniformly sampled vertices. Source and destination distributions stay
unchanged. Under a budget of at most one missing unit-weight edge:

- If a=b=c, the minimizing insertions are exactly {u,v} for v in A\{u}.
  There are a-1 optimal edges.
- Otherwise, the minimizing insertions are exactly the internal pairs in
  every original part of size max(b,c). The number is the sum of
  binomial(q,2) over those largest parts, including both when b=c>a.
- Leaving H unchanged is strictly worse than these choices. Allowing or forbidding
  restoration of uh does not change the minimizing set.

All ties refer to sets of edges. There is no unique optimal edge under the
admitted a>=3 domain. The result concerns this random-walk objective and
one unit insertion; it does not include monetary costs.

## Known electrical tools and the new comparisons

Write L for the ordinary combinatorial Laplacian and L^+ for its
pseudoinverse. The classical commute identity gives
E_i[T_j]+E_j[T_i]=2m R_ij. Summing unordered pairs, using zero self-hit and
sum_(i<j)R_ij=n tr(L^+), gives

    U(J) = (2m_J/n) tr(L_J^+).

The factors follow the unordered Kirchhoff-index convention. See
[Chandra et al., Theorem 2.1](https://homes.cs.washington.edu/~ruzzo/papers/resist.pdf).
For a unit insertion vector v=e_i-e_j, the rank-one inverse update on
the subspace orthogonal to the all-ones vector gives trace reduction

    S(v) = v^T(L_H^+)^2 v / (1+v^T L_H^+ v).

Every candidate insertion has the same final edge count, so larger S
means smaller U. Exact Kirchhoff edge scoring and optimal insertion are
already published in [Monnig and Meyer, Theorem 2 and section 8.1](https://arxiv.org/pdf/1605.01091).
Their ordered resistance sum is twice the usual Kirchhoff index; this
constant does not affect the ranking.

Put n=a+b+c+1, d=n-a, k=(n-1)(d-1)/(nd), and
W=[n(n-1)+d(d-1)]/(n^2 d^2). The intact graph has within-part eigenvalues
n-q and three remaining nonconstant eigenvalues n. Its inverse and trace
are established complete-multipartite formulas; see
[Bapat, Karimi and Liu, sections 2-3](https://arxiv.org/pdf/1611.09457).

For completeness, if P=I-11^T/n and E_q projects onto the zero-sum vectors
inside a part of size q, then
L_G=nP-sum_q qE_q and L_G^+=P/n+sum_q q/[n(n-q)]E_q.
For y=e_u-e_h and w=L_G^+y, the entries are
w_u=(n-1)/(nd), w_v=-1/(nd) for v in A\{u}, w_h=-1/n,
and zero elsewhere. Thus ||w||^2=W and 1-y^T L_G^+y=k>0.
Deleting uh gives L_H^+=L_G^++ww^T/k.

The missing edges have five types: uh, an A pair incident to u, an A pair
excluding u, a B pair, or a C pair. Part-preserving permutations fixing
u,h preserve the workload and are transitive on each type. Their scores are

    S_restore = W/k
    S_uv = [2/d^2 + 2/(d^3 k) + W/(d^2 k^2)]
           / [1 + 2/d + 1/(d^2 k)]
    S_q = 2/[(n-q)(n-q+2)]   for an untouched pair in part q.

Every denominator is positive. S_q strictly increases with q, so larger
parts beat smaller parts among untouched pairs. Three exact sign
comparisons settle the remaining choices:

| Positive difference | Substitution, variables nonnegative | Numerator terms | Positive constant |
|---|---|---:|---:|
| S_uv-S_restore | a=3+x, b=3+x+y, c=3+x+z | 16 | 92 |
| S_uv-S_a | same | 20 | 1404 |
| S_b-S_uv | a=3+x, b=4+x+y, c=3+x+z | 77 | 71442 |

The complete numerator and denominator lists are in
[uniform-ranking.json](../experiments/kemeny-one-deletion-proof/uniform-ranking.json).
Every listed coefficient and each constant is positive. The checker
reconstructs the rational differences and checks full polynomial
identities, so these are full-domain signs rather than sampled estimates.
The third substitution covers b>a because part sizes are integers;
exchanging B,C covers c>a. Combining these signs with monotonic S_q
proves both necessity and sufficiency of the minimizing sets.

## Why the best action also beats no action

Let m=ab+ac+bc+a+b+c-1 be the number of edges in H and let

    T = tr(L_H^+)
      = 3/n + (a-1)/(n-a) + (b-1)/(n-b) + (c-1)/(n-c) + W/k.

Although every insertion reduces T, it also increases the edge-count
factor in U. In fact

    U(H+e)-U(H) = (2/n)[T-(m+1)S_e].

We prove (m+1)S_best-T>0 in three exhaustive cases, using B/C exchange
to assume b>=c where needed:

| Case | Substitution | Best score | Numerator terms | Positive constant |
|---|---|---|---:|---:|
| All equal | a=b=c=3+x | S_uv | 6 | 100288 |
| One larger | a=c=3+x, b=4+x+y | S_b | 26 | 53102 |
| Both larger | a=3+x, c=4+x+z, b=4+x+z+y | S_b | 117 | 190464 |

Again all complete numerator/denominator coefficients and constants are
positive, and exact cross-products match
[uniform-noop.json](../experiments/kemeny-one-deletion-proof/uniform-noop.json).
The substitutions include a=3 and tied maxima. Thus the best insertion
strictly reduces U throughout the admitted integer domain, proving the
at-most-one-edge statement.

## An exact example that eliminates a misleading rule

At (a,b,c)=(3,3,3), full graph equations give:

| Action | U after the action | Change from H |
|---|---:|---:|
| Do nothing | 751/90 | 0 |
| Restore uh | 1458/175 | -41/3150 |
| Insert an A pair incident to u | 90189/10850 | -1567/48825 |
| Insert any untouched A/B/C pair | 1462/175 | +31/3150 |

Every insertion lowers electrical resistance, but the last choice makes
this fixed-workload mean worse. The untouched-A choices in that last row
are the optimal alternate insertions for the
[stationary-target Kemeny objective](kemeny-alternative-repair.md).
The two objectives therefore lead to different decisions on the same graph.

Weight also matters for improvement over no action. If that last edge has
conductance t instead of 1, write r=v^T L_H^+v and s=v^T(L_H^+)^2v. Then

    Delta U(t) = (2t/n)[(T-ms)+t(rT-s)]/(1+tr).

In this example r=2/7, s=2/49, T=751/630 and m=35. Improvement occurs
exactly for 0<t<1043/1322; the endpoint gives equality. Thus a sufficiently
weak link helps and a unit link worsens U. This is an illustration of the
known update formula, not a claimed weighted optimizer. The independent
review clarifies the author's phrase "maximum improving weight" as an
upper threshold for strictly improving weights.

## Reproduction, independence and contribution boundary

From the repository root:

```powershell
$env:UV_CACHE_DIR = 'D:/CodexWorkspaces/mathematics-atlas/uv-cache'
uv run --project experiments/kemeny-one-deletion-proof --frozen python experiments/kemeny-one-deletion-proof/verify_uniform_repair.py --ranking-certificate experiments/kemeny-one-deletion-proof/uniform-ranking.json --noop-certificate experiments/kemeny-one-deletion-proof/uniform-noop.json --output work/kemeny-uniform-repair/check-01.json
```

Use a fresh output name on repeat runs; other hosts may use another cache
directory. Python 3.12.11 is pinned and no Python packages are required.
The checker verifies six complete rational identities with exact integer
arithmetic, pins certificate bytes, and never executes stored expression
strings. A separate reviewer derived the ranking from grounded graph
equations, checked the no-op result, and independently replayed the
portable implementation. Exact witnesses, finite diagnostics, original
reviewer invocation failure, corrected rejection test, and raw evidence
are retained in the [evidence index](../evidence/kemeny-uniform-repair/README.md).

Our potential contribution is the specific full-domain ordering and
no-op guarantee. The inverse formulas, electrical interpretation and
generic edge-scoring method are established work. The
[independent source notes](../evidence/kemeny-uniform-repair/source/source-notes.md)
record close prior work and unresolved fulltext leads; bounded searching
does not establish publication originality.

U measures random-walk steps under a uniform workload. It is not a
measurement of routed traffic latency, throughput, or deployed benefit.
Nonuniform workloads and other failure models require their own tests.
The work remains an algorithmically checked and independently audited
mathematical result, without Lean formalization.
