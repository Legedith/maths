# Candidate complete continuum-strength minimax reduction

Author exploration, independent audit required. H1 and H2 are proved analytically below; the sole declared344 interval[0,1/10] refutes H3 that endpoint-optimal strengths suffice. No current release is changed. The methods are elementary inverse-update, calculus and minimax reasoning, not a generic novelty claim.

## Model and positive attained oracle

For a fixed connected H in the stated multipartite damaged family, let M=L_H+,m>0 and n>=10. Actions are every missing edge e assigned a fixed real t>=0 before the workload is known; all t0 labels are the same no-action graph. Workload is the same iid hub mixture on a closed[l,h] subset[0,1). Put v=e_i-e_j,r=v^TMv>0,z=Mv,

    T_theta=tr(M)+n*theta*M_hh,
    s_theta=||z||^2+n*theta*z_h^2,
    B_theta=r*T_theta-s_theta,
    f_e,theta(t)=(m+t)[T_theta-t*s_theta/(1+rt)].

Actual hitting objective is2(1-theta)f/n. Thus volumes m+t remain inside f; they cannot be canceled across differing strengths. All denominators are positive.

On1-perp M is positive definite. rM-Mvv^TM is PSD by Cauchy-Schwarz, with rank n-2>0 on that space. Its trace against the positive definite workload matrix I+n*theta*e_h e_h^T is B_theta>0. Also s_theta>0. Rewriting gives

    f(t)=(m+t)[B_theta/r+s_theta/(r(1+rt))] >= m*B_theta/r>0.

Since B_theta is continuous and strictly positive on the compact workload interval, and there are finitely many edges, a common positive lower bound exists. Likewise f(t)/t tends to B_theta/r uniformly on that interval (the rational remainder is bounded). Thus objectives are uniformly coercive for t tending to infinity, including the positive lower bound on1-theta. The oracle infimum over edges and strength is strictly positive and attained at a finite strength. This proves the needed graph conditions rather than assuming them. No point-mass theta1 or disconnected action is included.

For each FIXED action(e,t), dividing U by1-theta gives a positive affine function of theta, despite action-dependent volumes. The endpoint argument extends from finite to continuum actions: U_action/U_oracle is the supremum of pairwise positive-affine ratios, each bounded by its endpoint maximum. Supremum over actions commutes with the maximum of the two endpoints. Therefore every chosen action's worst relative regret is attained at l or h. Attainment of the oracle makes the ratio literal; the pairwise bound itself does not need a finite oracle action set. Workload-dependent oracle changes cause no exception.

## Exact finite candidate characterization

First compute the two oracle values O_l=min_e,t f_e,l(t), O_h=min_e,t f_e,h(t). For each edge and endpoint define A_theta=T_theta-m*s_theta. The derivative of f is

    [A_theta+B_theta(2t+rt^2)]/(1+rt)^2.

The numerator strictly increases on t>=0 because B_theta,r>0. If A_theta>=0, the unique endpoint minimum is t0. If A_theta<0, the unique positive endpoint minimizer is

    t_theta=(sqrt(s_theta*(mr-1)/B_theta)-1)/r.

Here A<0 and B>0 imply mr>1 and the radicand>1. Its minimum value is

    [B_theta*(mr-1)+s_theta+2sqrt(B_theta*s_theta*(mr-1))]/r^2.

No infinity candidate is necessary by coercivity. Thus each endpoint oracle is computed by finitely many exact rational/radical comparisons.

For each edge minimize max{f_e,l(t)/O_l-1,f_e,h(t)/O_h-1}. It suffices, and retains every minimizing strength, to evaluate:

1. t0;
2. each positive endpoint stationary strength just described;
3. the positive equal-regret crossing, if it exists.

In this model the crossing is at most ONE, not quadratic: cancel the common positive(m+t)/(1+rt) to obtain

    (T_l+B_l*t)/O_l=(T_h+B_h*t)/O_h,
    t_balance=(T_h*O_l-T_l*O_h)/(B_l*O_h-B_h*O_l).

If the denominator is zero and numerator nonzero, no crossing exists. If both vanish, the two normalized endpoint functions coincide identically, so their endpoint stationary candidates already suffice. A zero crossing is t0; negative crossings are omitted. If l=h, the same identical-function case applies. Duplicate candidates and duplicate physical edge classes can be merged computationally but all minimizer labels must be restored; t0 labels represent one no-action choice.

Completeness: an interior minimizer of the maximum either lies where the functions are equal or has a neighborhood with only one strictly active differentiable function, whose derivative must vanish. The boundary is t0. Identical-function pieces reduce to one function. No interval of stationary minima occurs because each derivative numerator strictly increases; hence the candidate set includes ALL minimizers. Each per-edge objective is continuous/coercive, so a minimizer exists; finite edge comparison gives the global deterministic minimax set. Positivity of both oracle values justifies every normalization. No assumption that a fixed graph family's location envelope has only two orbits is used.

## Exact344 balancing witness

Only(3,4,4), interval[0,1/10] was evaluated. A direct centered inverse of the12vertex graph verifies LM=I-J/n and reconstructs all16missing incidence actions, grouped by exactly equal(r,s_l,s_h). The four classes have multiplicities2incident,1restore,1untouched_A,12B/C. m50,T_l985/792,T_h10657/7920. Exact endpoint oracles are

    O_l=sqrt(112079)/33+5144/99,
    O_h=sqrt(10081666)/250+162923/3000.

The globally minimizing action is restoration alone at its balancing strength t_balance as above, using

    r=5/22,s_l=51/1936,s_h=753/19360,
    B_l=r*T_l-s_l,B_h=r*T_h-s_h.

This expression is retained in full in result.json. The evaluator obtains exact rational square-root enclosures with100 bisections and propagates rational interval arithmetic through every expression, refusing any sign decision whose interval contains zero. It checks both endpoint oracle minima strictly against all other classes. It then evaluates every candidate from the complete characterization, including t0, all per-edge endpoint stationary strengths and every positive balancing strength. Strict disjoint worst-regret bounds show this restoration balance uniquely beats every other candidate, including ALL edges' endpoint-stationary choices, not only the endpoint oracle choices. The approximate regret0.0014261174620597283 is display only; all decisions use retained rational bounds. The winning strength is positive and finite by its certified interval; no decimal root solver is used.

Thus H3 is false even in the declared graph family. Selecting an endpoint's optimal strength can miss the minimax solution. The example illustrates the finite characterization, not a graph/workload grid or universal best-location assertion. Result files retain all endpoint regrets, radical expressions, rational bounds, candidate strengths and physical winner labels.

## Execution, provenance and limits

One exact evaluator, rc0,5.313seconds under60second cap; no failures, second run or expanded graph/workload search. run.json/stdout.bin/stderr.bin retain argv, environment and streams; stderr includes successful uv setup/index messages. SymPy1.14.0/Python3.12.11, D isolation. The script's sole float conversion prints an approximate final regret after all exact assertions; it has no role in selection. Input hashes pin accepted inverse/strength and endpoint audits. No external source query, shared write, Git change, generic-method novelty or physical-impact claim occurred. A distinct independent reviewer must audit the analytic globality, interval implementation and exact witness before promotion.
