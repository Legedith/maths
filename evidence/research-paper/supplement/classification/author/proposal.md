# Sharp zero-growth classification and exceptional nonattainment

Author theorem candidate, requiring distinct audit. Zero evaluators were needed; all arguments below are symbolic proofs, not machine-certified results. No novelty, physical interpretation, release approval, or change to an accepted API is claimed.

## Model and precise contraction convention

Let G be a finite connected positive weighted loopless undirected graph, with absent pair {i,j}. Thus n>=3. Combine any parallel conductances before speaking of the underlying simple adjacency graph. Add conductance t>=0 to that pair. Source a is fixed, and the target law has a positive uniform floor, in particular nu_theta=(1-theta)Uniform+theta*delta_q on 0<=l<=theta<=h<1. All hitting times are actual discrete-time steps and H_aa=0.

Contract i,j to a vertex z and combine parallel conductances. The phrase 'contracted graph is a simple path' means its underlying simple adjacency graph is a path. Literal multigraph simplicity would be false in the exceptional case: edges wi and wj become parallel wz edges. Their sum does not change the connectivity criterion.

## H1: exact structural classification

The averaged linear growth coefficient for source a is zero if and only if:

1. a is outside {i,j}; and
2. the underlying contracted graph is a path with distinct endpoints a and z.

Equivalently, G consists exactly of a path from a to w, followed by two leaves i,j each attached only to w. The a-to-w path may have length zero, giving the n=3 two-prong path with a=w. All existing edge weights may be arbitrary positive numbers.

Proof. The accepted growth criterion says a source in the inserted pair has positive slope for any outside target. For a outside the pair, zero averaged slope is equivalent to every b outside {a,i,j} separating a from the pair. The uniform target floor makes every such target relevant. In the contracted graph this says every vertex other than a,z separates a from z.

Choose any simple a-to-z path P. Every other vertex must lie on P: otherwise P avoids it, contradicting its separating property. There can be no nonconsecutive chord of P, because such a chord produces an a-to-z route skipping an internal vertex of P. Hence the underlying contracted graph is exactly P. Conversely a path with endpoints a,z has the required separating property. This also proves the case of two contracted vertices, where there are no internal separators.

Since z is a path endpoint, its only neighbor is w. In the original graph both i,j therefore have neighbors only in {w}; connectedness and their absence as a pair force each to have precisely that neighbor. Edges among all remaining vertices are exactly the a-to-w path edges. This proves the forked-path equivalence. Positive weights have no bearing on these support/connectivity arguments.

## H2: two supported source vertices restore coercivity

For any fixed inserted pair, at most one source has zero growth. If the contracted graph is a path, it is the unique endpoint other than z; otherwise there is none. Pair endpoints themselves have positive growth.

Therefore any fixed source probability law with support of size at least two gives positive averaged linear growth for every absent pair, under a target uniform floor. This holds for real probabilities, not only rational ones: at least one supported source contributes a strictly positive slope and every other contribution is nonnegative. For a finite nonempty allowed edge set, the accepted growth/coercivity result supplies a common positive asymptotic lower bound on the compact theta interval, hence attained positive endpoint oracles and robust optima. This conclusion does not claim strict convexity or uniqueness of the resulting general-source optimization problem.

## H3: the exceptional fixed-source family strictly decreases

In the exceptional graph let p=c_wi>0 and q=c_wj>0. Write d_tail for the sole edge weight from w toward a if the tail is nonempty. Let B=H_aw, which does not depend on t. If the tail is nonempty, let v be w's neighbor toward a and set E=d_tail*(1+H_vw); this is finite and positive, and H_vw is independent of t because the walk stops on its first arrival at w. For a=w (empty tail), put B=E=0. No formula for E in terms of tail weights is needed.

Set D=p*q+(p+q)*t>0. At target i, first-step decomposition at w and j, with excursions into the tail, yields

    (p+q)*H_wi = p+q+E + q*H_ji,
    H_ji = 1 + q*H_wi/(q+t).

Therefore

    H_ai = B + (p+2*q+E)*(q+t)/D.

Exchanging p and q gives

    H_aj = B + (2*p+q+E)*(p+t)/D.

Differentiating these rational functions gives

    dH_ai/dt = -(p+2*q+E)*q^2/D^2 < 0,
    dH_aj/dt = -(2*p+q+E)*p^2/D^2 < 0.

For every other target b, the walk from endpoint a must hit b before it can reach w and then either prong (or b=a and the time is zero). Thus H_ab is independent of t. Strong Markov decomposition justifies adding B to the prong hitting times. This includes b=w, the empty tail, and arbitrary tail lengths/weights; no directed-hitting symmetry is assumed.

The exact prong limits are

    H_ai(infinity)=B+(p+2*q+E)/(p+q),
    H_aj(infinity)=B+(2*p+q+E)/(p+q).

Their finite gaps above these limits are respectively

    (p+2*q+E)*q^2/((p+q)*D),
    (2*p+q+E)*p^2/((p+q)*D).

Both are strictly positive at every finite t. Averaging against any fixed target law assigning positive mass to the prongs, in particular every law with the specified uniform floor, gives a strictly decreasing objective with a positive finite limit and no finite minimizer on this edge ray. The limit is positive because the source is outside the pair and the prong targets have positive mass. The formula is valid at t=0 as well as all positive t.

Thus, in this specific positive-uniform-floor model, the graph classification strengthens the generic warning 'zero slope alone does not decide attainment': after establishing the exceptional structure, zero slope DOES imply nonattainment along that edge. This is a new consequence of the structural and first-step arguments, not an inference from zero slope in arbitrary models. If other edge locations are allowed, one must still compare their attainable values against this edge's limiting value; no unconditional global nonattainment across all locations is asserted.

## Evidence and limits

plan.md was frozen before proof development. No graph was selected for execution and neither optional evaluation was used. The only reused mathematical premise is astra-hitting-growth-explore-work/proposal.md with its distinct review astra-hitting-growth-review-work/review.md, both hash-pinned. The present author did review that premise but did not author it; the new classification and consequences require another independent audit. No external literature attribution was introduced. There is no raw experiment stream because no evaluator or third-party code ran.
