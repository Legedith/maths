# Safe upgrades and optimal repair after one link fails

We now have two design guarantees for an infinite family of networks:
a chosen upgrade remains beneficial after any one existing link fails,
and, for a specified hub-link failure, restoring that link is the best
single-edge intervention. We also disproved the idea that the previously
chosen upgrade stays optimal after damage.

Both theorems have independent exact mathematical checks. They concern
random-walk exploration in a structured graph family. Publication
originality and benefit on an actual network or workload remain unresolved.
The calculation methods are established tools; the potential contribution
is the full-domain sign and optimality guarantees.

## Model and results

Let G=K_(a,b,c) join K_1, for integers a,b,c>=3 with a<=b,c. Vertices in
each of three groups have no internal links and connect to every vertex
in the other groups. A hub h connects to everyone. Choose distinct u,v in
the minimum group A. Every edge has weight one. K is the stationary-target
Kemeny constant of the simple random walk P=D^(-1)A, with zero hitting
time when the starting vertex is the target.

**Theorem 1 (one-failure tolerance).** For every original edge f of G,

    K(G-f+uv) < K(G-f).

The result includes every pair u,v in any original minimum group, tied
minima, and every possible incidence of f with u or v. It covers exactly
one deleted original edge, three groups of size at least three, and one
hub. It does not extend the arbitrary-part-count intact-graph theorem to
arbitrary-part-count damaged graphs.

**Theorem 2 (optimal hub-link repair).** Set H=G-uh. Among all graphs H+e
obtained by adding a single missing unit-weight edge e, the unique minimum
of K occurs at e=uh. Thus restoring the hub link beats every alternate
new edge, assuming restoration is allowed in the intervention budget.

**Strict domination.** For distinct v,w in A other than u,

    K(H+vw) < K(H+uv).

This last comparison rejects the candidate rule that an insertion incident
to the damaged vertex is the best alternative to restoration. It does not
yet establish vw as the best alternative among all groups. Combining
Theorems 1 and 2 also proves K(G)<K(H), so the optimal restoration improves
on doing nothing.

## Proof of one-failure tolerance

Write r for an A vertex other than u,v, j for a B vertex and k for a C
vertex. The complete list of deletion categories is

    uB, uC, rB, rC, BC, uh, rh, Bh, Ch.

Here uB includes deletion from either u or v to B. Permutations within
parts and swapping u,v preserve the proposed insertion. Interchanging B
and C reduces the list to six representative formulas: uB,rB,BC,uh,rh,Bh.
The parameters b,c have identical lower bounds; no assumption b<=c is made.

For each representative split out u,v,h and any other deleted-edge
endpoints as singleton cells. Retain the remaining vertices of each part
as one independent twin cell. Define its neighbor-count matrix R directly
from cross-part adjacency, remove the selected edge, and optionally add
uv. Set D=diag(R1), L=D-R, and let m be the number of cells.

The cell-constant subspace is invariant under the full transition matrix.
Each zero-sum subspace on an independent twin cell has transition
eigenvalue zero. These subspaces give a direct decomposition of the full
space, so

    K(full graph) = n-m + q2/q1,
    q1=[t]det(L+tD),  q2=[t^2]det(L+tD).

The coefficient ratio follows from
det(L+tD)=det(D)t product_i(t+mu_i), where the nonzero normalized
Laplacian eigenvalues mu_i are positive. Connectivity holds after each
single deletion because a third original part supplies an alternate path.

When a=3 and r is split out, the residual A cell has size zero. Retaining
it formally leaves its column in Q=D^(-1)R zero and adds exactly one
transition eigenvalue zero to the physical quotient. The resulting extra
unit in q2/q1 cancels the extra subtraction in n-m. Its row degree remains
positive. This handles the boundary without treating an empty set as a
physical cell. No other residual cell is empty in the admitted domain.

For each case the resulting rational difference is N/D0. The frozen
certificates expand -N and D0 after a=3+x,b=3+x+y,c=3+x+z. Every nonzero
coefficient is a positive integer and both constants are positive:

| Deletion representative | Terms of -N | Terms of D0 | Constant of -N | Constant of D0 |
| --- | ---: | ---: | ---: | ---: |
| uB | 275 | 431 | 656032608 | 30692188800 |
| rB | 160 | 272 | 11235924 | 577886400 |
| BC | 157 | 266 | 11085984 | 577886400 |
| uh | 163 | 278 | 12749400 | 674956800 |
| rh | 118 | 212 | 1701000 | 85730400 |
| Bh | 115 | 206 | 1656900 | 85730400 |

Thus N<0 and D0>0 throughout the required domain. The full coefficient
dictionaries are in [the six certificates](../experiments/kemeny-one-deletion-proof/all-deletions).
The portable checker reconstructs each determinant and verifies the
rational identity by exact cross-multiplication; it does not trust the
author's canceled expression or its summary flags. The orbit argument
then proves Theorem 1. The earlier [specific hub-deletion proof](kemeny-one-deletion.md)
is retained as a separately checked intermediate result.

## Proof of optimal repair and strict domination

In H the complete set of missing edges splits into five orbits:
the unique restoration uh, edges uv incident with u inside A, edges vw
between untouched A vertices, and internal edges of B and of C. All
orbits exist because every part has size at least three. Part-preserving
permutations fixing u and h are transitive within each orbit. Therefore
four strict comparisons against restoration establish a unique optimum.

For every intervention, split each newly inserted endpoint into a
singleton cell. The remaining cells are independent twins. The same
determinant argument gives K=n-m+q2/q1, with m=6 for restore/uv and m=7
for untouched-A/B/C insertions. The empty A cell at a=3 is handled as
above. When comparing interventions with different m, the difference in
the n-m terms must be retained; the checker computes K-n=q2/q1-m.

The author used a different quotient: merge an inserted adjacent pair
into one cell. Its omitted zero-sum mode has transition eigenvalue -1/d,
where d is the pair's common degree, and contributes d/(d+1). This gives
the author's correction K=n-6+q2/q1-1/(d+1). The independent review and
portable checker keep the pair split and verify that the resulting full
K values and differences match the author's formulas exactly.

After the same x,y,z substitution, all numerator and denominator
coefficients for these comparisons are positive, with positive constants:

| Final-graph K difference | Numerator terms | Numerator constant | Denominator constant |
| --- | ---: | ---: | ---: |
| uv minus restore | 30 | 3316 | 357120 |
| untouched A minus restore | 48 | 20412 | 2449440 |
| B minus restore | 53 | 21672 | 2449440 |
| C minus restore | 53 | 21672 | 2449440 |
| uv minus untouched A | 84 | 115668 | 121492224 |

The [complete comparison certificate](../experiments/kemeny-one-deletion-proof/optimal-repair.json)
and exact determinant identities therefore prove all five differences
strictly positive on the full domain. The first four prove Theorem 2;
the fifth proves strict domination. Relabelling covers all choices and
tied minima. No empirical extrapolation enters either proof.

## An eliminated idea

At a=b=c=3, independent full adjacency matrices give these changes relative
to the damaged graph H:

| One-edge intervention | Change in K |
| --- | ---: |
| Restore uh | -71/2520 |
| Add an untouched A pair | -5/252 |
| Add an internal B or C pair | -263/13608 |
| Add uv | -787/41664 |

Lower is better. The untouched A pair beats uv by exactly 17/17856. This
is a counterexample to uv optimality, even though Theorem 1 proves uv
safe. The full-domain domination proof shows this is systematic in the
specified hub-failure model. The exact values are implementation
diagnostics as well as a concrete rejected-hypothesis witness.

## Existing work, verification, and limits

The spectral expression for K and ordinary edge-deletion updates are
established in [Altafini et al., Corollaries 2.2-2.3 and Theorem 3.1](https://arpi.unipi.it/bitstream/11568/1170026/2/Poloni_1170026.pdf).
Equitable and twin quotient reductions are established tools, including
[Breen, deBlieck and Vander Meulen, Section 3](https://arxiv.org/html/2608.04150v1).
The [intact-network note](kemeny-network-design.md) also records the
Hu-Kirkland multipartite update formula and the source comparisons behind
our earlier sign and ranking results. After deletion of uh, u and v have
different neighborhoods, so those twin-insertion results cannot be applied
directly to that pair.

The bounded source investigation did not identify a result settling these
particular damaged-family guarantees. Additional searches for relocation,
switching and rewiring mostly returned unrelated models and weak retrieval;
those results provide no evidence of originality. A paper still needs a
stronger priority assessment. No new generic quotient algorithm, edge-update
formula, measured speedup, or deployed-network benefit is claimed.

The two mathematical audits independently reconstructed all relevant
symbolic identities. The robustness audit also repeated the 36 full-matrix
checks at the three declared tuples, including the zero-cell boundary.
The optimality audit independently checked full matrices at (3,3,3).
The dependency-free portable checks use integer arithmetic, and run in
the pinned Python 3.12.11 uv project. Full commands and evidence are in
the [evidence index](../evidence/kemeny-one-deletion/README.md) and
[frozen release contract](kemeny-single-failure-contract.md).

The historical failures remain retained: author type/serialization errors,
an explicitly authorized extra serialization-recovery execution, and
reviewer execution/parsing corrections. Their failed return codes are
preserved. They are not reported as successful attempts.

These theorems distinguish a safe upgrade from an optimal repair in an
idealized random-walk model. They do not establish routing latency,
throughput, or user benefit. Extending the result to multiple failures,
unequal costs, more groups, or a fixed application workload requires new
evidence. If restoration is unavailable, the best alternate insertion
remains a separate research question.
