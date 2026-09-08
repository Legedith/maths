# Choosing link strength when traffic is uncertain

A repair decision includes both where to add a link and how strong to make it.
In the exact example below, every strength optimized for either traffic extreme
loses to a strength that balances the two extremes. Doing nothing is included
in the comparison.

The underlying characterization applies to any fixed connected weighted graph
under the stated iid traffic model. For each allowed missing link, there is
exactly one best robust strength. A finite list of stationary and balancing
strengths contains that optimum, and comparing the links retains every tied
best location. The graph need not have the symmetry or universal hub of our
[earlier examples](kemeny-unit-minimax.md).

The circuit bounds, inverse updates and general robust-optimization ideas are
established mathematics. The deductions and exact example here have distinct
mathematical audits; publication priority and measured physical benefit remain
unresolved. The [contract](kemeny-strength-minimax-contract.md) and
[evidence bundle](../.codex/evidence/runs/kemeny-strength-minimax-v1/bundle.json)
state what is proved and what the implementation checks.

## Graph, traffic and decision

Let G be a finite connected loopless undirected graph on n>=3 vertices, with
positive conductance on each present edge. Parallel edges may be merged by
summing conductances. Let E be a finite nonempty set of allowed absent pairs.
Choose one pair and its conductance t>=0 before knowing theta. Every t=0
label represents the same no-action graph.

Fix a focus vertex q. Source and destination are independent with common law

    p_theta = (1-theta) Uniform + theta delta_q,
    0 <= l <= theta <= h < 1.

Self-hitting time is zero and transitions are proportional to conductance.
The focus vertex may be any vertex. The workload law is the same for every
candidate. For expected walk steps U_(e,t)(theta), minimize

    max_{theta in [l,h]} [U_(e,t)(theta) / min_(j,s>=0) U_(j,s)(theta) - 1],

where j ranges over the same E. The oracle may choose its edge and strength
for each theta; our chosen intervention is fixed. Randomization, adaptive
decisions, costs and multiple-edge additions are different problems. Theta=1
is excluded because every actual objective vanishes and this ratio becomes
undefined.

## A classical resistance bound and its equality case

Let m be total undirected conductance, d_i,d_j weighted degrees and r the
effective resistance between a missing pair i,j. Shorting all other vertices
into one gives two series links of conductances d_i and d_j. Classical
shorting monotonicity therefore gives

    r >= 1/d_i + 1/d_j >= 4/(d_i+d_j) >= 4/m.

The last step uses nonadjacency: the terminal incident-edge sets are disjoint.
This is an immediate application of a known circuit principle, rather than a
new resistance technique. The weighted convention and shorting law appear in
[Aldous and Fill, section 3.3](https://www.stat.berkeley.edu/~aldous/RWG/Book_Ralph/Ch3.S3.html).

For a direct equality argument, fix potentials V_i=1,V_j=0 and set every
interior potential to 1/2. Its Dirichlet energy is (d_i+d_j)/4 <= m/4, an
upper bound on the minimum energy 1/r. Equality mr=4 requires no edges between
interior vertices and requires this trial potential to be harmonic. For each
interior vertex v, the latter condition says c_iv=c_jv. Connectedness makes
both positive. Conversely, these conditions achieve equality.

Thus equality at mr=4 holds precisely for a weighted K_(2,n-2), with i,j in
the size-two part and equal conductances on the two edges of each branch.
Different branches can have different weights. Equality in the intermediate
degree bound alone is weaker: edges between equipotential interior vertices
can remain. The mr=4 equality additionally removes their contribution to m.
An existing edge or a self-loop convention must not be silently substituted
for the absent-pair model.

## The objective and its strict convexity

Write M=L_G^+, v=e_i-e_j, z=Mv and

    r = v^T M v,
    T_theta = tr(M) + n theta M_qq,
    s_theta = ||z||^2 + n theta z_q^2,
    B_theta = r T_theta - s_theta.

The known weighted commute/covariance formula and rank-one inverse update give

    U_(e,t)(theta) = 2(1-theta) f_(e,theta)(t)/n,
    f_(e,theta)(t) = (m+t)[T_theta - t s_theta/(1+rt)].

The volume m+t remains inside f. Comparing resistance decreases alone would
discard part of the hitting-time objective.

On 1-perp, M is positive definite. The matrix K=rM-Mvv^TM is positive
semidefinite by Cauchy-Schwarz, with rank n-2>0. Hence

    B_theta = tr(K) + n theta K_qq >= tr(K) > 0,

and s_theta>0. Moreover,

    f(t) = (m+t)[B_theta/r + s_theta/(r(1+rt))]
         >= (m+t) B_0/r.

For a fixed graph and finite allowed edge set this provides a common positive
lower bound and growth to infinity, uniformly over the traffic interval.
The extra factor 2(1-theta)/n stays bounded away from zero. The oracle is
therefore positive and attained at a finite strength.

Differentiate with respect to t:

    f'(t) = [T_theta-m s_theta+B_theta(2t+rt^2)]/(1+rt)^2,
    f''(t) = 2s_theta(mr-1)/(1+rt)^3 > 0.

The resistance bound mr>=4 makes strict convexity explicit. Dividing by a
positive endpoint oracle preserves it, as does taking the maximum of the two
normalized endpoint functions. Growth at infinity ensures attainment. Each
fixed edge therefore has exactly one optimal robust strength. This conclusion
permits ties between different edge locations.

## From infinitely many traffic values and strengths to finite candidates

For any fixed action (e,t), U/(1-theta) is positive and affine in theta.
Regret plus one is the supremum of its ratios to every fixed oracle action.
Each positive-denominator affine ratio is monotone or constant, so its maximum
is at l or h. A supremum over actions commutes with a maximum over these two
endpoints. Consequently every chosen action's worst relative regret is
attained at an endpoint, despite the continuum of available oracle strengths.

Let O_l and O_h be the endpoint minima in the f normalization. For each edge
and each endpoint, set A_theta=T_theta-m s_theta. The endpoint minimizing
strength is

    t_theta = 0                                      if A_theta >= 0,
    t_theta = [sqrt(s_theta(mr-1)/B_theta)-1]/r        if A_theta < 0.

In the second case the radicand exceeds 1. The exact minimum is

    [B_theta(mr-1)+s_theta+2sqrt(B_theta s_theta(mr-1))]/r^2.

Finite comparisons over the allowed edges determine O_l,O_h. Then each edge
needs only the following candidate strengths:

1. Zero.
2. Its positive stationary strength at either endpoint.
3. Its positive balancing strength, if one exists:

       t_balance = (T_h O_l-T_l O_h)/(B_l O_h-B_h O_l).

The equality equation is linear after cancelling the positive common factor
(m+t)/(1+rt). A zero denominator with nonzero numerator means no crossing;
both zero means identical normalized functions. Zero crossings are already
included, negative crossings are inadmissible, and a collapsed traffic
interval has identical endpoint functions. Duplicate algebraic expressions
represent one strength.

An interior optimum either balances the two active functions or is stationary
for its single locally active function. Zero is the only finite boundary,
and growth at infinity rules out an infinite-strength optimum. Thus the list
contains every minimizer. Strict convexity makes the selected strength unique
for each edge; comparison across edges retains all location ties. This is a
finite characterization, without a claimed bit-complexity bound.

## Exact balancing example

Take the damaged graph (K_(3,4,4) join K1)-uq with unit old conductances and
traffic interval [0,1/10]. All16 missing pairs are allowed. They form four
classes: two pairs incident to u inside its part, one restoration, one
untouched pair inside that part, and twelve internal pairs in the two largest
parts. Total old conductance is 50.

The exact endpoint oracles in the f normalization are

    O_l = sqrt(112079)/33 + 5144/99,
    O_h = sqrt(10081666)/250 + 162923/3000.

Restoration alone is globally minimax at its positive balancing strength.
For that link,

    r = 5/22,
    T_l = 985/792, T_h = 10657/7920,
    s_l = 51/1936, s_h = 753/19360,
    B_l = r T_l-s_l, B_h = r T_h-s_h.

Substituting these quantities into t_balance specifies the strength exactly.
Its maximum relative regret is approximately 0.0014261174620597283; this
decimal is for display only. Rational bounds enclosing the radicals strictly
separate its value from all ten other declared candidate entries, including
every endpoint-stationary choice and zero. The two original reconstructions
use different graph inverse constructions and different radical enclosures.

This refutes the idea that an endpoint-optimal strength always suffices.
It does not say restoration is optimal in every graph or uncertainty interval.

## Attribution and implementation boundary

[Stochastic p-Robust Location Problems](https://optimization-online.org/wp-content/uploads/2004/08/921.pdf)
uses scenario-relative regret in location design. The inspected July2004
technical report defines that regret in Definition1 and constrains it while
optimizing expected cost. Its scenario probabilities and later assignment
decisions do not establish randomized repair timing.

[Optimal Weight Allocation of Dynamic Distribution Networks](https://arxiv.org/html/1803.05640)
studies robust conductance allocation through an induced H-infinity objective
and a fixed-total-weight semidefinite program. Those are useful connections,
with different uncertainty and loss from the hitting-time ratio here.
[Ghosh, Boyd and Saberi](https://www.web.stanford.edu/~boyd/papers/eff_res.html)
provide established resistance-convexity context. Multiplying by changing
total volume requires the separate derivative calculation above.

The source packets preserve unresolved access and attribution questions.
In particular, the Springer DOI10.1007/s00186-020-00712-y remains a substantive
source gap; no theorem or timing model is attributed to it. The nearby
unweighted Sylvester degree bound is not cited as the weighted nonadjacent
inequality. Bounded non-identification does not prove originality.

The portable solver targets rational graph conductances and rational traffic
endpoints. The theorem allows positive real conductances. An unresolved exact
comparison must be reported as inconclusive, never converted into a tolerance
tie or uncertified recommendation. The checker and distinct implementation
review record the actual supported interface and its resource limits.
One later exploratory invocation on344,[0,9/10] exceeded a60-second limit
without producing its diagnostic result. Its raw record is retained; the
log does not localize the delay. General runtime reliability is unproved.

The analytic Dirichlet equality, covariance/inverse reduction, rank trace,
uniform coercivity, continuum endpoint interchange and completeness arguments
remain separately audited bridges. Finite API examples do not enumerate all
graphs, and this is not a Lean formalization. Implementation reproduction and
actual hosted CI require their own evidence before a release is promoted.

The [solver README](../experiments/kemeny-workload-proof/README-strength-minimax.md)
contains the importable interface, exact comparison limits and replay command.
