# Candidate simultaneous-link recommendation certificate

Author proposal, independent audit pending. H1 is proved below; H2 is refuted by exact reused scores; H3 is refuted analytically as a general sharpness claim. Generic Loewner/inverse perturbation machinery is known. This is not a new algorithm or a measured network-benefit claim.

## Domain and certificate

Let H be the connected damaged multipartite graph with unit existing edges, and let E be its finite nonempty missing-edge candidate set (restoration allowed). The argument also applies to any connected positive-weight baseline with a fixed finite set of unit insertions. All existing weights change simultaneously to w_f(1+delta_f), |delta_f|<=epsilon<1. The SAME perturbation is used when comparing candidates; every new edge remains unit. Fix a probability law p independently of weights and candidate choice; endpoints are iid and diagonal hitting time is zero. Write C=diag(p)-p*p^T and Q_e=tr(L_e^+ C), where L_e is the unperturbed post-insertion Laplacian.

Let O be the COMPLETE old optimal set, Qstar=min_e Q_e. If outsiders exist, define Qoutside=min_{e not in O} Q_e and
 radius=(Qoutside-Qstar)/(Qoutside+Qstar).
If p has at least two positive entries, C is nonzero positive semidefinite on1-perp, all Q_e>0, and0<radius<1. For every0<=epsilon<radius, EVERY edge in O strictly beats EVERY outsider after every allowed simultaneous perturbation. Ties may break inside O: the conclusion is containment of the new optimum in O, not preservation of all old optimal ties.

## Proof and exact endpoints

Let B_e=v_e*v_e^T and L_e=L_H+B_e. Since each old edge Laplacian is positive semidefinite,
 (1-epsilon)L_H <= L_H(delta) <= (1+epsilon)L_H.
Adding B_e and using epsilon B_e>=0 gives
 (1-epsilon)L_e <= L_e(delta) <= (1+epsilon)L_e.
All operators are positive definite on1-perp because H stays connected for epsilon<1. Inverse order on this subspace, extended by zero on constants, yields
 L_e^+/(1+epsilon) <= L_e(delta)^+ <= L_e^+/(1-epsilon).
Taking traces against C preserves order, so Q_e/(1+epsilon)<=Q_e(delta)<=Q_e/(1-epsilon).

For any i in O and j outside O,
 Q_i(delta)<=Qstar/(1-epsilon)<Qoutside/(1+epsilon)<=Q_j(delta)
precisely when epsilon<radius. The actual iid hitting objective is2(m_delta+1)Q_e(delta). This factor is positive and COMMON to all candidates for the same perturbation, so it cancels. There is no squared volume-condition factor. Comparing with doing nothing would have different volume and is not covered.

At epsilon=radius these bounds give only non-strict separation Q_i(delta)<=Q_j(delta); they do not establish strict separation or an actual tie/failure. Above radius they give no ranking conclusion. At epsilon=0 the old strict gap to outsiders is recovered. Epsilon=1 is excluded because existing edges may vanish and connectedness may be lost.

If there are no outsiders (including a singleton candidate set), the stated separation is vacuous and the new optimizer is automatically in O for every epsilon<1. Report the certificate supremum as1 or 'no outside comparison', not radius0 or an undefined0/0. If p is a point mass, C=0 and all objectives are zero for every connected candidate; O=E and the same vacuous case applies. In the hub-mixture workload all theta<1 have full support; theta=1 is the degenerate point mass and is not a strict-ranking regime.

## Frozen eight-instance radii

At unperturbed unit insertion all candidates have common volume, so the radius computed from recorded U values equals the Q radius exactly. No matrix or perturbed graph was recomputed. The accepted effect result contains every missing edge, and the script minimizes over EVERY outsider, not merely a chosen competing orbit.

| Parts | theta | Exact strict epsilon radius | Radius >=1/100 |
|---|---|---|---|
|3,3,3|1/10|1745/434753|no|
|3,3,3|1/2|2113/113713|yes|
|3,3,4|1/10|919/359119|no|
|3,3,4|1/2|1451/93251|yes|
|3,4,5|1/10|25/38113|no|
|3,4,5|1/2|545/49001|yes|
|4,4,6|1/10|209/386721|no|
|4,4,6|1/2|913/98913|no|

All eight old optima are unique restoration. H2 (all radii at least1%) is false; five exact failures are retained. In the three yes cases the inequality is strictly greater, hence epsilon=1% itself is certified. In the five no cases this certificate cannot establish1% stability; it does NOT establish instability. None of these numbers is an actual perturbation failure threshold.

## H3: uniform-scaling sharpness is false in general

This claim is tested analytically, not numerically. Take any admitted graph with uniform iid workload (theta=0), such as the all-equal333 graph. Scale every existing conductance by q>0 and keep the new edge unit. Dividing EVERY final conductance by q leaves conductance-proportional transition probabilities, hence hitting times, unchanged. The equivalent graph has unit old edges and one new edge of strength1/q. The accepted independently audited common-positive-strength theorem says its optimal edge SET is independent of that positive strength. Thus uniform scaling never changes the optimizer for ANY q>0 in this uniform-workload subfamily.

The certificate nevertheless has radius strictly below1: the uniform theorem has outsiders with a strict gap and positive Qstar. Taking any epsilon between that radius and1, and q=1+epsilon, exceeds the certificate while preserving the exact optimizer. This disproves the general assertion that the certificate is a sharp uniform-scaling threshold. It does not prove conservativeness for every nonuniform instance or rule out worst-case nonuniform perturbations at the bound.

## Typed provenance and execution

H1 [analytic/methodological]: Loewner inequalities, inverse order and trace argument above, with the accepted iid commute bridge. H2 [exact finite numerical]: check.py/result.json records all optimum/nearest-outside edges, exact objectives/radii and all failed1% flags. Source result SHA256 f7de3722c44e98b2205f0aadc48329640d9688a79c081d3176c95fce07faa64e; independent effect review SHA2569988c53d13c275d8dd00a4c987cc89aea972014697d55efaa51239d5ebbb8d65; both verified before computation. H3 [analytic inference]: the scale invariance argument plus ../astra-uniform-weight-review-work/review.md SHA256221338dfce7a9e799c8689c806381598f8237fbc38ecee6a60d4d2c3db74a137, read as accepted prior theorem, no new proof replay.

One frozen exact Fraction batch, uv isolated/D cache, rc0, empty stderr,0.37s,60s timeout. run.json retains actual argv/cwd/status; stdout.bin/stderr.bin retain raw streams. No second batch, new matrices, scaling sweep, or unbounded search. New text is explicit UTF-8 with ASCII content. Prior stages and repository remain unchanged. This author packet does not self-certify the independent evidence gate.

## Three further falsifiable ideas, not executed

1. At least one of the five instances with radius below1% nevertheless preserves restoration under EVERY allowed simultaneous1% perturbation; prove or exhibit a violating assignment.
2. For the eight declared instances, the first loss of restoration under common old-edge scaling occurs strictly beyond this sufficient radius (or no such loss occurs). The uniform-workload argument above does not settle these positive-theta instances.
3. At an exact workload crossing with multiple old optima, arbitrarily small symmetry-breaking existing-edge perturbations can break their internal tie while all outsiders remain excluded by the positive outside-gap certificate.
