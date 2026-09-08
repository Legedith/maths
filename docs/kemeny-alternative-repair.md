# Optimal insertion when direct repair is unavailable

For the same three-group-plus-hub model, we can now complete the optimal
decision rule. If the failed hub edge may be restored, restore it. If that
edge is forbidden, connect two unaffected vertices within the damaged
minimum group. This statement optimizes stationary-target Kemeny's
constant, with the current design's degree-proportional target weights.

## Exact theorem

Let a,b,c be integers with 3<=a<=b,c. In G=K_(a,b,c) join K1 choose u in
its a-part A and let h be the hub. Put H=G-uh. Among all single missing
unit-weight edges other than uh, the minimizing insertions are exactly
the unordered pairs contained in A excluding u.

There are binomial(a-1,2) such edges. They form one optimal orbit under
part-preserving permutations fixing u; there is a unique optimal edge
exactly when a=3. The comparison is strict against internal B/C edges
even when b=a or c=a. No ordering between B and C is asserted.

The objective is K for the simple random walk P=D^(-1)A, with zero hitting
time when the starting vertex is the sampled target. There is exactly one
insertion, with restoration forbidden. This theorem does not optimize a
fixed source-target workload or interventions with different costs.

## Proof from the complete comparison set

Once uh is forbidden, every missing edge belongs to one of four types:
a pair incident with u inside A, a pair in A excluding u, a pair inside B,
or a pair inside C. Each type is transitive under the relevant
part-preserving permutations. All types exist since a,b,c>=3.

The [previous independently audited comparison](kemeny-fault-tolerant-design.md)
proves that a pair in A excluding u strictly beats an A pair incident
with u. Only the B and C comparisons remained. Write J_A for the graph
after an untouched-A insertion, and J_T for one inside T=B,C. Exact
determinants give the differences K(J_T)-K(J_A)=N_T/D_T.

The [new certificate](../experiments/kemeny-one-deletion-proof/alternative-repair.json)
contains each complete numerator and denominator coefficient list after
a=3+x,b=3+x+y,c=3+x+z. In both comparisons the numerator has 104 nonzero
positive integer coefficients, minimum coefficient 2, and constant 39690.
Every nonzero denominator coefficient is positive, with minimum 1 and
constant 77157360. Thus N_T>0 and D_T>0 for all nonnegative x,y,z.
This substitution exhausts the admitted integer domain, including a=3
and all tied-size boundaries. No division by a-b or a-c occurs.

The portable checker independently reconstructs the full K ratios using
the previously audited singleton-endpoint partitions and integer subset
determinants. It checks each new ratio by exact cross-multiplication and
also rechecks the prior incident-A comparison against its byte-pinned
certificate. Its expression K-n=q2/q1-m retains the different numbers
of cells and the already proved formal empty-cell correction at a=3.
It never executes the symbolic expression strings in the author packets.

All three competing types are therefore strictly worse than J_A.
Transitivity makes every untouched-A pair equally good. This proves both
directions of the claimed exact optimum set; its cardinality follows by
choosing two vertices from the a-1 untouched vertices.

## An eliminated tie assumption

At a=b=c=3, exact full adjacency matrices give K(J_A)=497/60 and
K(J_B)=K(J_C)=80519/9720. Each B/C choice is worse by 1/1944.
Thus equal original part sizes do not imply equal post-failure insertion
quality. The independent review reused its already checked full matrices
and verified their hashes; no new full-matrix run is claimed.

## Reproduction and interpretation

From the repository root with uv installed:

```powershell
$env:UV_CACHE_DIR = 'D:/CodexWorkspaces/mathematics-atlas/uv-cache'
uv run --project experiments/kemeny-one-deletion-proof --frozen python experiments/kemeny-one-deletion-proof/verify_alternative_repair.py --certificate experiments/kemeny-one-deletion-proof/alternative-repair.json --prior-certificate experiments/kemeny-one-deletion-proof/optimal-repair.json --output work/kemeny-alternative-repair/check-01.json
```

Use a fresh output name on repeat runs. The package pins Python 3.12.11
and has no Python package dependencies. Other hosts may use another cache
directory. A separate agent independently audited the mathematics, then
replayed and checked the portable implementation. Exact result dictionaries,
raw successful and rejected-input runs, and scope are retained in the
[incremental evidence index](../evidence/kemeny-alternative-repair/README.md).

The quotient and edge-update methods remain established tools. The
potential contribution is this specific full-domain ordering and exact
optimum set. Publication priority and measured practical benefit remain
unresolved; this is not a Lean formalization.

Each design uses its own stationary target probabilities. If every
candidate adds one edge to H and the resulting edge count is M, then
pi_j=(degree_H(j)+1_{j is an inserted endpoint})/(2M). Thus even equal-cost,
equal-edge-count candidates weight destinations differently. A design rule
for an unchanged traffic or target workload needs separate evidence.
