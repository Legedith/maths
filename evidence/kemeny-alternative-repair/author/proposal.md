# Next candidate: optimal alternate insertion when repair is forbidden

Status: author-derived full-domain comparison certificate; independent audit required. This is a NEXT discovery packet, not part of the currently frozen release. No public docs or prior packets were changed.

Let G=K_(a,b,c) join K1 with 3<=a<=b,c, let u be in A, let h be the original hub, and let H=G-uh. Forbid restoring uh. Candidate: the minimizing single missing-edge insertions are exactly the unordered pairs wholly in A minus {u}. Thus there is one optimal orbit, containing binomial(a-1,2) edges; a unique edge only when a=3. This stays strict against insertions within B or C even when b=a or c=a. No global priority or real-world impact claim.

## Reused proof inputs
The final-K rational expressions for uv, untouched_A, B and C are reused from ../astra-postfailure-design-work/batch2.json, whose SHA256 is frozen in input-hash.json and checked before this run. Their six-cell derivation and a=3 zero-size-cell boundary argument are in ../astra-postfailure-design-work/proposal.md. No unchanged determinant was recomputed. The prior candidate proves uv-minus-untouched_A>0. This next packet supplies the only missing comparisons: B-minus-untouched_A and C-minus-untouched_A.

The admissible missing-edge orbits, once uh is forbidden, are uv, untouched_A, B, C. Hence strict domination of the other three orbits establishes the stated exact set of optima. This conclusion depends on independent acceptance of the reused rational graph formulas and prior uv domination, as well as this new subtraction certificate.

## Exact certificate
For T=B,C, compute R_T=K(H+edge_in_T)-K(H+untouched_A_pair) by exact symbolic subtraction and factorization. Write R_T=N_T/D_T in the form returned by sympy.fraction of that factorization; result.json retains this rational expression and both complete exponent/coefficient lists after

  a=3+x, b=3+x+y, c=3+x+z.

This substitution exhausts the integer domain x,y,z>=0. For both comparisons the numerator has 104 nonzero terms, all strictly positive, minimum coefficient 2 and constant coefficient 39690. Every nonzero denominator coefficient is positive, minimum 1 and constant 77157360. Therefore N_T>=39690>0 and D_T>=77157360>0 on the nonnegative orthant, so R_T>0 throughout the full graph domain, including x=0, y=0 or z=0. No division by a-b or a-c is used. Both tied-size boundaries are covered directly.

Numerical diagnostics are only evaluations of these reused rational formulas, not independent new full-matrix checks. At (3,3,3), both B and C are worse than untouched_A by exactly 1/1944. At (3,3,7), the B gap is 1/7040; at (4,4,6), it is 1/9100. These refute an intact-graph-style equality assumption for equal part sizes. All five declared tuples and both comparison values are retained in result.json.

## Elimination ledger
H1 untouched_A strictly beats B/C: survives diagnostics and has the above full-domain sign certificate candidate.
H2 b=a implies equal B and untouched_A changes: REJECTED at (3,3,3), positive gap 1/1944 (also explicit unequal-c witnesses above).
H3 direct nonnegative-domain polynomial certificate exists: obtained for both comparisons.
H4 B-vs-C ordering: deliberately not tested; outside needed conclusion.

## Execution/provenance boundary
One bounded batch ran; no second batch, retry, failure, extra range or wider research. plan.md preceded execution. batch1.py pins its input, constructs the two differences exactly with SymPy 1.14.0, evaluates the five frozen tuples, and writes all coefficients. argv.json, stdout.txt, stderr.txt and rc.txt retain the uv isolated run, D-drive cache, and rc=0. Original quotient methods are known (Hu--Kirkland and Breen et al. section 3); the candidate is the particular optimality/sign conclusion, not a new quotient algorithm.

Typed claims: numerical coefficient facts and diagnostic fractions -> result.json and stdout.txt; methodological exact reuse/subtraction -> input-hash.json, batch1.py and argv.json; conclusion -> reused graph/formula proof plus prior uv comparison and this full-domain positive-polynomial argument. Independent verification must check pinned formula provenance and reconstruct these comparisons before promotion. No author self-certification.

Conditional interpretation: when the failed hub edge cannot be restored and all remaining eligible insertions have equal cost, connect two unaffected vertices of the damaged minimum part. This is a theorem candidate for the ideal unweighted simple-random-walk objective, not demonstrated improvement in a measured network. No safety or cost model is silently substituted, and current-release scope stays unchanged.
