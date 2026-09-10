# General-source minimax infimum and attainment characterization

Author analytic candidate; independent audit required. Fixed finite connected positive weighted loopless undirected graph n>=3; finite nonempty set E of absent pairs; fixed source probability law mu, independent of target and intervention; target nu_theta=(1-theta)Uniform+theta*delta_q on closed [l,h], h<1. Legal actions are one pair e and finite t>=0, with all t=0 labels one physical no action. No infinity action is admitted.

Define O(theta)=inf over legal actions U(theta), and relative regret U_x(theta)/O(theta)-1. This explicitly uses infimum oracles; it is distinct from the minimum-oracle formulation when a minimum does not exist. The characterization below reports attainment rather than silently assuming it.

## Objective and edge classification

For each target b use the grounded first-step system. Write K_b=L_b^(-1), grounded incidence v_b for the inserted pair, and grounded degree increment w_b (both endpoints if b outside the pair, otherwise its other endpoint). The resistance r=v_b^T*K_b*v_b>0 is the same effective resistance for every ground b. Let mu_b retain source masses except b; its omitted self contribution is zero. Then

    F_mu,b(t)=mu_b^T*[K_b-t*K_b*v_b*v_b^T*K_b/(1+r*t)]*(d_b+t*w_b).

This includes both transition-degree increments. Summing against nu_theta gives U_e,theta(t)=(a0(theta)+a1(theta)t+a2(theta)t^2)/(1+r*t), with coefficients affine in theta. It applies also to source mass at b because that mass contributes zero hitting time.

Reuse the distinctly audited growth and sharp classification. If mu has at least two supported vertices, every ray is coercive. For point source a, a ray is exceptional exactly when a is outside the pair and G is a tail from a to w followed by two leaves i,j attached to w; empty tail permitted for n=3. Every nonexceptional ray has a2(theta)>0 uniformly across the workload interval. Each exceptional ray has a2(theta)=0 and is strictly decreasing, with a positive finite limit L_e(theta); the uniform target floor gives positive mass to both strictly decreasing prong hitting terms. No other zero-growth case occurs in this model.

There is at most one exceptional pair for a fixed source a. For n=3 the exceptional graph is the two-edge path and the pair is its unique two leaves, with a the middle. For n>=4 an exceptional graph has exactly one vertex of degree3, w, and no other branching vertex; it has three leaves. The source a is the leaf at one end of the tail and the pair is the other two leaves. Thus its pair is uniquely determined. Underlying adjacency degrees are used after parallel conductances merge. This proves H3 without assuming a particular allowed set.

## Positivity and endpoint infimum oracles

For every legal action, H_ab>=1 for a!=b. Therefore U(theta)>=Pr(source!=target)>= (1-h)(n-1)/n>0, including arbitrary real source probabilities. Infima and exceptional limits satisfy the same bound.

At each endpoint j in {l,h}, compute the infimum on each ray. Nonexceptional rays attain it among zero and positive stationary roots of

    a1-r*a0+2*a2*t+r*a2*t^2=0.

Exceptional rays have endpoint infimum L_e(j), unattained on that ray. O_j is the minimum of this finite collection of values. It is an infimum of the SAME legal finite-strength action set because every limit is approached by legal strengths. Record all finite endpoint minimizers, and separately any exceptional limit certificates tied at O_j; an endpoint oracle is attained iff its finite list is nonempty.

For any legal x, regret plus one is sup over legal y of U_x(theta)/U_y(theta), even without an attained oracle, by positivity. Each ratio of positive affine functions is monotone or constant. Commuting the supremum with the two-endpoint maximum gives

    sup_theta regret_x(theta)=max_j [U_x(j)/O_j-1].

A collapsed interval is a single endpoint. No endpoint oracle minimizer is assumed in this argument.

## Finite robust candidate list and attainment

On a nonexceptional ray, each endpoint branch has a2>0. Its curvature has constant sign; nonpositive curvature implies strict increase since the derivative tends to a2/r>0, and positive curvature gives strict convexity. Thus each normalized branch is strictly quasiconvex. Their finite maximum is strictly quasiconvex, coercive and continuous, and has one finite minimizing strength. A complete candidate list is zero, all positive endpoint stationary roots, and all positive real roots of the pairwise endpoint equality polynomial

    O_h*(a0_l+a1_l*t+a2_l*t^2)-O_l*(a0_h+a1_h*t+a2_h*t^2).

It has degree at most two. Identically zero means coincident branches; nonzero constant gives no roots; linear and quadratic cases retain positive real roots including repetitions before deduplication. Zero is already a boundary, negative/nonreal roots are excluded. If only one distinct branch is active at an interior minimum it is stationary; otherwise equality supplies a root. This covers all degeneracies and l=h.

On an exceptional ray both normalized endpoint branches strictly decrease, so their maximum strictly decreases as well. Its infimum is

    R_e,infinity=max_j[L_e(j)/O_j-1],

approached but never attained at finite t. Infinity is a certificate label for this limit only. No stationary/balance point on that ray can be its robust minimizer. This reduces the robust comparison to finitely many attained nonexceptional ray minima and at most one exceptional limit value.

Let Rstar be the least of those values. Report all finite ray minimizers equal to Rstar as physical global actions, deduplicating no action once. Record every tied exceptional limit separately. The global infimum is attained IF AND ONLY IF the physical list is nonempty. If only the exceptional limit wins, the answer is nonattainment with that approaching ray; if a finite ray ties the limit, attainment is true but infinity remains nonphysical. Coercive rays whose minima exceed Rstar contribute nothing. This is a complete deterministic minimax infimum/attainment characterization, preserving all edge-location ties.

## Exactness and limits

For rational conductances, source probabilities and workload endpoints, coefficients are rational, endpoint infima and candidate strengths are algebraic, and finite comparisons can in principle be certified by exact real-algebraic methods, with polynomial root isolation and unsquared-sign checks as needed. For arbitrary real mu the same mathematical characterization holds but is not an effective exact algorithm without a representation/comparison oracle. No rational-input implementation, bit-complexity bound, all-input runtime guarantee or extension of the current solver API is claimed.

Zero evaluators: the argument uses previously independently audited graph premises and the explicit algebra above. No new diagnostic graph, failed experiment, literature assertion, shared write, novelty or application claim. A distinct review is required before promotion.
