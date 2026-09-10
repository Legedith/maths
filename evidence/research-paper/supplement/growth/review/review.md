# Independent analytic audit of hitting-growth criterion

Auditor: astra_damage_symbolic. Four scoped gates PASS. No required correction. Scope is the stated finite connected positive weighted undirected loopless graph, a fixed absent edge, and fixed independent source/target laws. Source priority, physical interpretation, and release approval are excluded.

## Grounded identity and exact sign criterion

With target b removed, first-step equations are L_b h=d_b: degree multiplies the unit-step term. For b outside the inserted pair, the updated system is (L_b+t*v*v^T)h=d_b+t*w. Sherman-Morrison is valid for all t>=0 because L_b is positive definite and r=v^T*K*v>0. Dividing by t and taking the limit yields C*w, C=K-K*v*v^T*K/r. Since C*v=0 and w=e_i+e_j, this equals 2*C*e_i=2*C*e_j. The factor two and the degree update are necessary and correct.

Let E map contracted potentials to equal original i,j potentials. Its image is exactly ker(v^T), and E^T*L_b*E is positive definite. For any forcing f, minimizing x^T*L_b*x/2-f^T*x subject to v^T*x=0 yields both C*f (Lagrange multiplier) and E*(E^T*L_b*E)^(-1)*E^T*f (reduced coordinates). This proves the contraction identity, including parallel conductances induced by contraction.

Deleting ground from the contracted graph gives block-diagonal grounded Laplacians. Each component block has nonnegative inverse, with strictly positive entries within that block. One elementary justification is its killed-walk series: each component has a route to the ground because the original contracted graph is connected, so spectral radius is below one; nonnegative powers give positivity exactly along component paths. Entries between blocks vanish. Thus C_ai>0 precisely when source a lies in a component attached to either i or j before contraction in G-b. Contraction cannot connect another component except through the merged pair. This is equivalent to a path from a to the pair avoiding b, as claimed.

All boundary cases are sound. For a=b, the actual hitting time is identically zero and no grounded source coordinate is used. When b is i or j, both the grounded update vector and the sole degree increment are the other endpoint's basis vector; C*w=0, so every source has zero linear slope. For a in the pair and b outside, a zero-length path makes the slope strictly positive. There is no assumed symmetry of H_ab and H_ba.

## Averaging and attainment

For any fixed probability vector mu (including irrational entries), finite sums commute with the limits. Every pair slope is nonnegative. For a target mixture on 0<=l<=h<1, each target weight is at least (1-h)/n. Therefore one supported source and one distinct outside target satisfying the path condition give a strictly positive uniform lower bound on the averaged slope. Conversely, absence of every such pair forces every weighted slope to zero. This equivalence includes collapsed intervals and arbitrary focus q.

Each hitting objective is quadratic over the same positive linear denominator 1+r*t for a fixed edge. Affine dependence on theta and compactness imply a uniform bounded remainder after subtracting its linear asymptote. A positive lower bound on slope thus gives uniform coercivity. If every edge in a finite allowed set satisfies the condition, taking the minimum over their positive bounds gives a common coercive tail. Continuity then gives attained endpoint oracles and minimizers of the robust objective. Positivity is especially direct: E[H]>=P(source!=target)>=(1-h)*(n-1)/n for every legal finite action. Relative-regret denominators are therefore bounded away from zero; the robust objective is continuous and coercive as well.

When slope is zero, the quadratic numerator's leading coefficient vanishes and the objective has a finite limit. This does not decide whether its minimum is finite or unattained. The proposal explicitly preserves this distinction. One failing edge blocks the blanket all-edge coercivity argument, but does not by itself prove failure of the global optimum. Uniform source supplies supported a=i and an outside target for any allowed edge with n>=3, confirming that special case without extrapolation from examples.

## Independent bounded exact verification

plan.md froze only the two declared four-vertex trees. The independent check.py constructs transition probabilities and solves directed first-step equations, unlike the author's grounded inverse calculation. All eight rational source-to-target functions and all eight limiting slopes match the frozen result exactly. Star source 3 has slopes (0,0,0,0); path source 1 has (0,0,0,2). No new graph or second run occurred. These checks support the diagnostics, not the universal proof in place of the preceding argument.

Every author manifest hash and raw stream hash/size passed; assigned proposal/result/manifest hashes match. The logger hash was preflighted and checked inside the evaluator. Own frozen environment uses Python 3.12.11/SymPy 1.14.0, D environment/cache and uv both outer and child. logs/attempt-review01.json records rc0, no timeout, empty stderr, 6.638646 seconds under a 60-second cap. Author run is rc0, no timeout, empty stderr, 2.890622 seconds. Input hashes, code hash, exact reconstructions and raw output are retained locally.

## Scoped gate record

Specification compliance PASS: analytic generality stated precisely; only two authorized diagnostics.
Mathematical/numerical integrity PASS: contraction proof, complete boundary cases, averaged coercivity and exact functions verified.
Methodological integrity PASS: distinct first-step reconstruction with immutable inputs and raw bounded execution.
Conclusion integrity PASS: zero slope not equated to nonattainment; no finite-to-universal inference, novelty, application or release claim.
