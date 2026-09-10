# Graph criterion for linear hitting-time growth

Author theorem candidate requiring independent audit. Fixed connected positive weighted loopless undirected graph; absent pair i,j gains conductance t>=0. Source a and target b are fixed independently of t. H_bb=0. No novelty or physical interpretation beyond the discrete-time random walk is claimed.

If b is outside {i,j}, let K=(L with row/column b removed)^(-1), v=e_i-e_j and w=e_i+e_j in grounded coordinates. The grounded degree vector is d. First-step equations give

    h(t)=(K-t*K*v*v^T*K/(1+r*t))*(d+t*w), r=v^T*K*v>0.

Consequently the exact linear growth vector is

    lim h(t)/t = C*w,
    C=K-K*v*v^T*K/r,
    C*w=2*C*e_i=2*C*e_j.

The factor two comes from the two endpoint degree increments. This calculation includes the degree update, not merely the resistance change.

To interpret C, identify i and j in the grounded network. Let E duplicate the single merged coordinate into their two original coordinates. Then

    C=E*(E^T*L_b*E)^(-1)*E^T.

Indeed this is the inverse of the quadratic energy restricted to v^T*x=0, obtained also by the displayed rank-one projection. The grounded contracted Laplacian is positive definite. Its inverse is entrywise nonnegative; an entry is strictly positive exactly when its two vertices lie in the same connected component after the ground is deleted. This follows componentwise from the irreducible grounded Laplacian's inverse (equivalently its convergent killed-walk Green series). Thus C_ai>0 exactly when a can reach either i or j in G without visiting b: contraction joins their components but does not create another route from a to the pair.

Therefore for a!=b and b outside {i,j}, the linear coefficient is positive IF AND ONLY IF that target-avoiding path exists. Otherwise it is zero. This proves root's proposed graph criterion. For a=b it is zero by self hitting. If b is one endpoint, the other endpoint has grounded update v=w=e_j. The leading coefficient is K*w-K*v*(v^T*K*w)/r=0, so every source has zero linear growth. All statements include sources in the inserted pair, interpreted as zero-length reachability to the pair.

## Averaged laws, coercivity and its limits

For a fixed source probability law mu and target law nu_theta=(1-theta)Uniform+theta*delta_q, the leading coefficient is the nonnegative sum

    c(theta)=sum_a,b mu_a*nu_theta,b*c_ab.

For theta in a closed [l,h], h<1, every target has mass at least (1-h)/n. Hence c(theta)>0 throughout the interval, with a uniform positive lower bound, exactly when SOME supported source a and some target b outside the pair, b!=a, admit a target-avoiding path from a to the pair. If no such pair exists then c(theta)=0 for every theta. This classifies the sign of a2/r in the quadratic-over-linear averaged objective, without assuming rational source probabilities.

If this positive-growth condition holds for each edge in a finite allowed set, continuity and the common positive asymptotic slope give uniform coercivity and attained positive endpoint oracles and robust optima. Positivity follows from at least one nonself target having positive mass. If the condition fails, the corresponding edge objectives are bounded at infinity; their quadratic coefficient is zero. Finite attainment may hold or fail and needs separate analysis. Zero slope alone is not a nonattainment proof, and one noncoercive edge prevents using the blanket finite-set coercivity argument.

Uniform source satisfies the condition for n>=3: choose a=i and any b outside the pair. General fixed sources need not, even n>=4.

## Two frozen exact diagnostics

Unit star center1, leaves0,2,3, source3, inserted pair02: for outside target1 every path from3 to the pair visits1; outside target3 is self. Both pair targets also have zero coefficient. The exact first-step evaluator confirms all four slopes zero. This refutes the inference that n>=4 by itself restores coercivity.

Unit path0-1-2-3, source1, inserted pair02: target3 can be avoided while reaching the pair, so its coefficient is positive; the evaluator gives 2. All other target slopes are zero. Thus any target law with a positive uniform component makes this source's averaged slope positive.

The sole evaluator uses full grounded first-step matrices and degree vectors; result.json retains every source-to-target rational function and linear limit. Two graphs were frozen in plan.md, no prior three-path replay and no extra grid. One invocation rc0, empty stderr, 2.890622 seconds under60 seconds, both uv layers with verified pins and process-tree-aware logging. The analytic contracted-Green proof is not replaced by these finite checks. Independent review and source attribution remain necessary before promotion.
