# Candidate complete rule when restoration is forbidden

Author proposal, pending independent review. The endpoint conjecture is TRUE with strict inequality on the full unequal integer domain. For unit old conductances, one required missing UNIT insertion, fixed iid hub mixture0<=theta<1, and restoration forbidden, the complete optimal set consists of every internal pair in every largest original part. If b=c, include both B and C. There is no incident-u takeover. This is not a no-action or strength-optimization statement and is excluded from the current action-choice release.

Write n=a+b+c+1,d=n-a,e=n-c,k=(n-1)(d-1)/(nd),W=[n(n-1)+d(d-1)]/(n^2d^2),Z=d(d+2)k+1. Accepted inverse and covariance formulas give the scaled incident score I+theta*lambda, where I=(2k+2/d+W/k)/Z and lambda=1/(nkZ)>0. Largest-part pairs have constant score C=2/[e(e+2)]. All other untouched pairs have strictly smaller constant scores unless their part is also largest.

The exact certificate establishes G=C-I-lambda>0. Therefore C-I-theta*lambda=G+(1-theta)*lambda>0 for every admitted theta. In particular the formal incident/C crossing sigma=(C-I)/lambda is strictly greater than1 everywhere in this domain. No unresolved conditional crossing remains for unit insertion with restoration forbidden.

## Full-domain positivity certificate

The evaluator cancels G exactly in the independent symbols n,d,e, then substitutes two exhaustive disjoint integer cases:

1. a=x+3,b=a,c=a+1+z, x,z>=0 (formal y unused).
2. a=x+3,b=a+1+y,c=b+z, x,y,z>=0.

Every sorted integer triple with3<=a<=b<=c and c>a lies in exactly one case: either b=a so c>=a+1, or b>=a+1. In each case the canceled numerator and denominator have only strictly positive nonzero coefficients. Every coefficient and exponent triple is retained in result.json, including positive constants. Case1 constants are27090 and25084080; case2 constants are50240 and62092800. Thus neither numerator nor denominator can vanish anywhere on its nonnegative orthant, including a=3 and b=c boundaries. This proves strict positivity throughout the integer domain (and throughout these stronger real orthants). Missing monomials have coefficient zero, not negative; the constant term guarantees strictness.

Positive k,Z and the accepted graph score normalization justify all denominators. The same final conductance m+1 and positive factor1-theta make score maximization equivalent to minimizing actual iid hitting steps among the required unit insertions. No comparison to baseline is made. At theta1 all actual objectives vanish, so the positive limiting scaled gap does not classify actual action ties there. Equal parts are explicitly outside this proposal.

## Evidence and limits

One evaluator, timeout60seconds, rc0; run.json records exact argv, elapsed and D isolation variables. stdout.bin/stderr.bin preserve raw streams. Stderr includes successful uv setup/index messages. No second evaluator, failure, grid, counterexample search or shared write occurred. check.py and full result.json form the rational coefficient certificate. Input hashes pin the accepted full common-strength analytic review and original unit-envelope independent attestation. The proof is the explicit orthant coverage and coefficient-sign argument, not a finite graph experiment.

The generic covariance/inverse methods are known. This closes the stated family-specific unit endpoint question but establishes no novelty, physical benefit, no-action improvement, arbitrary insertion-strength extension or publication gate. A distinct reviewer must independently verify the exact identity and source/graph bridges before promotion.
