# Candidate uniform-source / mixed-target strength theorem

Exploratory author packet requiring distinct independent audit. This is a proposed random-walk model, not a validated P2P workload or a novelty/release claim. Fixed connected positive weighted loopless undirected G, n>=3, focus q, nonempty finite allowed absent-edge set. Source is uniform, independently target is (1-theta)Uniform+theta delta_q,0<=l<=theta<=h<1. One edge and strength t>=0 are selected before theta. Self hitting is zero; all t0labels denote one no-action graph. Oracle has the same allowed edges and strengths.

## Directed hitting identity, derived without iid symmetry

Let d be the weighted-degree vector, m=sum_edges c, M=L^+, and H_ij the expected number of steps from i to j. The first-step equations give (L H_.j)_i=d_i for i!=j. Since column sums of L vanish, the remaining component is d_j-2m. Thus L H_.j=d-2m e_j. Applying M and imposing H_jj=0 gives

 H_ij=(Md)_i-(Md)_j+2m(M_jj-M_ij).

The graph is connected, so the grounded system is invertible and this solution is the hitting-time solution. Averaging only the source uniformly uses M1=0 and gives

 F_j=mean_i H_ij=2m M_jj-(Md)_j.

Uniformly averaging targets additionally gives U_unif=2m tr(M)/n. Therefore the new objective is

 U_theta=(1-theta)*2m tr(M)/n +theta*[2m M_qq-(Md)_q].

The directed degree correction is essential. It cannot be removed by the symmetric iid commute/covariance formula. There is no common1-theta factor for this new model; even theta1 generally has a positive uniform-source hitting objective.

## Exact rank-one strength formula

For an absent pair i,j let v=e_i-e_j, w=e_i+e_j, z=Mv, r=v^TMv>0, D=1+rt, s=z^Tz, T=tr(M). Adding conductance t gives d_t=d+tw and M_t=M-tzz^T/D. These identities follow from the Laplacian rank-one inverse on1-perp and the degree update. Define

 Uu(t)=2(m+t)/n*[T-ts/D],
 Fq(t)=2(m+t)M_qq-(Md)_q-t(Mw)_q
       +[t*z_q*(z^Td-2m*z_q)+t^2*z_q*(z^Tw-2z_q)]/D.

Then U_theta(t)=(1-theta)Uu(t)+theta Fq(t), exactly. Each actual objective is affine in theta and quadratic-over-linear in t. All volumes m+t are retained.

For an explicit coefficient representation U_theta=(a0+a1*t+a2*t^2)/D, the uniform coefficients are

 u0=2mT/n, u1=2[T+mrT-ms]/n, u2=2(rT-s)/n.

Set F0=2mM_qq-(Md)_q, F1=2M_qq-(Mw)_q,
 P1=z_q*(z^Td-2m*z_q), P2=z_q*(z^Tw-2z_q).
The focus coefficients are f0=F0,f1=rF0+F1+P1,f2=rF1+P2.
Use ak=(1-theta)uk+theta fk. No directed hitting time is assumed symmetric.

## What survives and what fails

H1 AFFINITY: proved directly above. H2 ENDPOINT REGRET: survives. Every fixed action has a positive affine line in theta; the oracle ratio is the supremum of ratios to all fixed actions. Every positive-affine ratio is monotone or constant, so sup over actions commutes with maximum over l,h. Thus worst relative regret is at an endpoint even with the continuum oracle. There is no need for an iid common-factor cancellation.

Positivity and coercivity are also available on h<1. Focus hitting times are nonnegative, so U_theta(t)>=(1-h)Uu(t). On1-perp the PSD matrix rM-Mvv^TM has rank n-2>0, giving B=rT-s>0 and Uu(t)>=2(m+t)B/(nr). For a fixed graph and finite allowed edges this is a common positive linear lower bound. The oracle is positive and attained, and every fixed-edge minimax problem has an attained finite minimum. These are fixed-graph constants, not a uniform varying-graph performance claim.

H3 STRICT CONVEXITY: false. For U=(a0+a1*t+a2*t^2)/(1+rt),

 U'=[a1-r*a0+2a2*t+r*a2*t^2]/D^2,
 U''=2[a2-r*a1+r^2*a0]/D^3.

Its curvature has a constant sign for each theta, but need not be positive. The exact counterexample below establishes strict negative curvature inside the admitted model.

Nevertheless per-edge uniqueness SURVIVES by a different proof. Coercivity implies a2/r>0 (the linear asymptotic slope). If curvature is negative, U' decreases to that strictly positive slope, so U is strictly increasing on t>=0. If curvature is zero it is affine with positive slope, also strictly increasing. If curvature is positive, U is strictly convex, with its derivative increasing to a positive limit; its unique minimum is either0or the unique positive stationary root. Each case is strictly quasiconvex: at a strict convex combination of two distinct strengths its value is strictly below the larger endpoint value. Division by a positive fixed oracle constant preserves this property. The maximum of the two normalized endpoint functions is strictly quasiconvex: choose a function active at the intermediate point and bound it strictly by its own endpoint maximum, hence by the endpoint maximum of both functions. Attainment therefore gives exactly one minimizing strength for each edge, without claiming convexity of its robust objective. Different edge locations can still tie.

H4 FINITE CANDIDATES: survives with an amended balance equation. Let O_l,O_h be minima of the actual endpoint objectives over all allowed edges/strengths. Each endpoint oracle is found by comparing t0and positive roots of

 a1-r*a0+2a2*t+r*a2*t^2=0.

For each fixed edge, compare0, its positive endpoint-stationary roots and its positive balance roots. Unlike the iid formula, balance generally does not cancel(m+t): it is

 O_h*(a0_l+a1_l*t+a2_l*t^2)
 -O_l*(a0_h+a1_h*t+a2_h*t^2)=0.

This polynomial has degree at most2. If it vanishes identically the normalized functions coincide and endpoint stationary/boundary candidates suffice. Otherwise retain all positive real roots, including a repeated root; zero roots are already included and negative roots excluded. At any interior robust minimum either one endpoint is strictly active locally and stationary, or both are equal. Coercivity excludes infinity. This proves finite candidate completeness, and strict quasiconvexity proves the unique per-edge selected strength. Deduplicate algebraically equal roots and t0labels, retain every tied positive physical edge. A collapsed workload interval is the identical-function case. This is a mathematical finite characterization, not an implemented general solver or complexity claim.

## Sole exact diagnostic and explicit counterexample

Graph: path0--1--2 with conductances1and2; missing pair(0,2) has strength t. All three focus vertices were predeclared. The evaluator derives each focus objective from its own full grounded hitting equations and checks the rank-one directed formula exactly. It uses no iid covariance substitution for the directed target law.

For focus q=1,

 Uu(t)=(4t^2+24t+36)/(27t+18),
 F1(t)=(4t^2+9t+4)/(9t+6),
 U_theta(t)=[(4+8theta)t^2+(24+3theta)t+36-24theta]/(27t+18),
 U_theta''(t)=-4(101theta-98)/[9(3t+2)^3].

Choose collapsed interval l=h=99/100. Its objective is strictly concave for every t>=0, with U''=-199/[225(3t+2)^3]<0. It remains strictly increasing/coercive, so its unique optimum is0. Thus the iid strict-convexity theorem cannot be transferred even to a connected three-vertex weighted path and an admitted theta<1. At theta98/101 the objective is affine; this is another exact symbolic boundary, not an extra evaluator. Focus0and2curvatures in result.json are positive on[0,1), so no alternative successful example was selected after a grid.

## Evidence and hypothesis ledger

plan.md preceded the sole run. check.py/result.json and logs/attempt-path.* retain the exact formulas, all three focus rows and raw argv/streams/rc. The process-tree-aware established logger ran uv Python3.12.11/SymPy1.14.0 with D cache/environment. It returned0 without timeout in4.144437seconds under60seconds; stderr30bytes is successful package setup. No second evaluator, graph grid, retrieval, Git or shared write occurred. H1/H2 accepted by analytic derivation; H3refuted by the declared exact path; H4accepted with quadratic rather than iid-linear balancing. The inherited PSD/rank positivity ingredient is unchanged from the distinct accepted graph-general review; the new directed identity, curvature counterexample and quasiconvexity argument require independent review.

The model closes one mathematical source/target mismatch only. It does not establish a real P2P traffic law, symmetric routing-control feasibility, novelty, measured benefit or release approval.
