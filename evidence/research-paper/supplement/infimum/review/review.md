# Independent general-source infimum audit

Auditor astra_damage_symbolic. Four scoped gates PASS; no required correction. Target proposal SHA256 fdfaedabe166af618fdff39149755819b294a5e17a302094a4583d7ccef3971f. Zero evaluators or new browsing; no unresolved equation required a machine check. The graph, source and target laws are fixed independently of the action; target probabilities entail 0<=l<=h<1. Source priority, implementation, release and physical validation are outside scope.

## Premise separation and provenance

All five author manifest entries match actual bytes (input-hash-check.json). Growth is used through the accepted independent review 4a46cdd108cae41e737d6c164e02fbbac795d37f9659bf3bf397e387814033f6. The classification authored by this reviewer is used ONLY through the distinct general review cd94730bfdd553565c86992256efd9093e4630bb9ebf8255e5d9d9eab9a3655a, freshly read. This is not self-certification of that classification. The new general-source synthesis is authored by general and reviewed independently here.

## General source formula and positivity

For target b, first-step equations are (L_b+t*v_b*v_b^T)h=d_b+t*w_b, with the other endpoint the sole degree increment if b belongs to the pair. The inverse update therefore yields exactly the proposed mu_b-weighted expression. Source mass at b contributes zero, without renormalizing remaining mu masses. r is the effective resistance between inserted endpoints, invariant under grounding: potentials differ only by an additive constant, so their endpoint difference is unchanged.

For explicit coefficient verification, write alpha=mu_b^T*K*d, beta=mu_b^T*K*w, c=mu_b^T*K*v, dstar=v^T*K*d, estar=v^T*K*w. Then the numerator is alpha+(r*alpha+beta-c*dstar)*t+(r*beta-c*estar)*t^2. This follows by multiplying the displayed rank-one formula by 1+r*t. Summing these coefficients with nu_theta gives affine coefficients in theta. Both actual degree increments and the fixed source masses are preserved.

For every finite action U>=1-sum_a mu_a*nu_a. Because nu has uniform mass 1-theta, this is at least (1-theta)*(n-1)/n, hence at least (1-h)*(n-1)/n>0. This bound remains true for all infima and limits. It does not require rational source probabilities.

The accepted classification exhausts all edge rays: positive asymptotic coefficient uniformly on the compact workload interval, or the exceptional fixed-source forked path with strict decrease and positive finite limit. For a fixed source, there is at most one exceptional absent pair. If n=3 it is the two leaves with middle source. If n>=4, the forked path has a unique degree-three vertex and three leaves; the source must be its tail-end leaf, so the remaining two leaves uniquely determine the pair. Combining parallel conductances before computing adjacency degrees is essential and correctly stated.

## Infimum oracle and endpoint reduction

On coercive rays continuity gives a finite endpoint minimum. The derivative numerator is a1-r*a0+2*a2*t+r*a2*t^2, verifying the stationary list. Exceptional rays contribute their unattained limit, approached by finite strengths. The minimum over the finite collection of ray infima equals the infimum over the union of legal rays, with no assumption that it is attained. A finite endpoint minimizer tied at that value establishes attainment; a tied limit label alone does not.

For positive objective values, U_x/O=sup_y U_x/U_y even if the oracle is only an infimum. For each fixed legal x,y the numerator and denominator are positive affine functions of theta, whose ratio has constant-sign derivative (or is constant). Consequently its supremum is at l or h. Supremum over y commutes with that finite endpoint maximum. This proves the endpoint formula without requiring compactness of the action set or an oracle optimizer. Collapsed intervals cause no change.

## Completeness, ties and nonattainment

On each coercive ray U' tends to a2/r>0 and U''=2*(a2-r*a1+r^2*a0)/(1+r*t)^3. If curvature is nonpositive, U' is nonincreasing to a positive limit and hence is strictly positive throughout. If curvature is positive, U is strictly convex. Both cases are strictly quasiconvex. Dividing by a positive endpoint oracle and subtracting one preserves this property. The maximum of finitely many such branches is strictly quasiconvex: at any interior convex combination each branch is strictly below the maximum of its own endpoint values, hence below the maximum across all branches and endpoints. Therefore the continuous coercive ray objective has exactly one minimizer.

At an interior minimizer with only one locally active branch, that branch is stationary. If distinct branches tie, the displayed equality polynomial supplies the point, because both use the same denominator 1+r*t. Coincident branches reduce to a single branch and its stationary candidates; a nonzero constant yields no equality root. Boundary zero, repeated positive roots, linear cases, collapsed intervals and absent positive roots are all correctly handled. Including inactive stationary/equality points is harmless when candidate values are compared.

On the exceptional ray both endpoint branches strictly decrease. Their finite maximum also strictly decreases: select a maximizing branch at the later strength and compare it to its earlier value. Its infimum is the maximum of its two limiting values and is not attained on that ray. There is no legal infinity action. The global comparison is therefore exactly all attained coercive-ray minima plus the possible exceptional limit. If a finite value ties the least limit, the global infimum is attained by that finite action; otherwise a uniquely winning limit means nonattainment. All equal finite ray minima are retained, and all zero-strength labels are one physical action. An allowed set consisting solely of the exceptional pair is included: the finite physical list is empty, but the infimum value is still defined. Endpoint-limit ties and robust-limit ties are separate records and need not coincide.

For rational inputs, stationary and equality equations and their endpoint coefficients yield algebraic candidates and values; exact real-algebraic comparison is possible in principle. Arbitrary real source masses yield a mathematical characterization, not an effective exact algorithm without a representation oracle. No runtime, rational-only API support, generic convexity, or global uniqueness across locations is claimed.

## Four scoped gates

Specification compliance PASS: general fixed source law, finite action set of edge rays, finite strengths and positive uniform target floor retained.
Mathematical integrity PASS: explicit coefficients, positive denominator bound, endpoint-infimum identity, complete candidate/tie/attainment argument verified.
Methodological integrity PASS: analytic audit with distinct accepted classification review and all frozen input hashes; no evaluator substituted for universal proof.
Conclusion integrity PASS: infinity remains nonphysical; general real-input characterization distinguished from exact implementation; no source originality, application or release claim.
