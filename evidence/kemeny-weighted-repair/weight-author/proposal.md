# Candidate: optimal edge location is invariant under common positive conductance

NEXT author-derived result; independent audit required. H=K_(a,b,c) join K1-uh,3<=a<=b,c, fixed uniform source/target, zero diagonal hitting time. Choose exactly one missing edge, with a prescribed common conductance t>0 for every candidate. Current unit release and prior proof packets are unchanged.

## Full-domain candidate
For every t>0, if a=b=c the optimal edges are exactly uv with v in A minus u; otherwise they are exactly internal pairs of largest original parts B/C, with both when tied. Restoration is never optimal, so allowing or forbidding it does not change the optimal set. There is NO phase transition of optimal orbit as the common weight varies. This is not an optimization over choosing t or no-op; those have different volume/budget constraints.

## Derivation and exact certificate
Known fixed-uniform bridge and rank-one update give U(H+t e)=2(m+t)/n * [T-t s_e/(1+t r_e)], where r_e=v_e^TL_H+v_e and s_e=v_e^T(L_H+)^2v_e. Thus for fixed t one maximizes s_e/(1+t r_e). For two edges i,j the difference has positive denominator and affine numerator
(s_i-s_j)+t(s_i r_j-s_j r_i).
This generic comparison identity is not claimed new.

Use the previously derived graph inverse. Put n=a+b+c+1,d=n-a,k=(n-1)(d-1)/(nd),W=[n(n-1)+d(d-1)]/(n^2 d^2). Then
r_restore=(1-k)/k, s_restore=W/k^2;
r_uv=2/d+1/(d^2 k), s_uv=2/d^2+2/(d^3 k)+W/(d^2 k^2);
r_q=2/(n-q),s_q=2/(n-q)^2 for untouched pairs in part q.
Input values from ../astra-uniform-noop-work/batch1.json are hash-pinned in input-hash.json and checked in batch1 before reuse. The inverse derivation is in ../astra-uniform-repair-design-work/proposal.md. Batch2 verifies all these r/s expressions against every pinned input case before its symbolic comparisons.

For uv>restore and uv>untouched_A, substitute a=3+x,b=3+x+y,c=3+x+z. For B>uv, substitute a=3+x,b=4+x+y,c=3+x+z. These exhaust the base domain and b>=a+1,c>=a respectively. Both the intercept and slope are strictly positive rational functions: every nonzero shifted numerator/denominator coefficient is positive, with positive constants. Full original expressions and coefficient lists are in batch2.json.

Comparison component | numerator terms | numerator constant | denominator constant
uv>restore intercept | 7 | 16 | 3969
uv>restore slope | 16 | 68 | 142884
uv>untouched_A intercept | 20 | 1212 | 142884
uv>untouched_A slope | 10 | 192 | 142884
B>uv intercept | 77 | 63406 | 15366400
B>uv slope | 50 | 8036 | 15366400
All numerator minimum coefficients are 2; all denominator minimum coefficients are 1. Thus each affine numerator stays strictly positive for every t>0, not merely sampled weights. b/c symmetry supplies C>uv whenever c>a.

Among untouched parts, s_q/(1+t r_q)=2/[(n-q)(n-q+2t)], strictly increasing with q for every t>0. Five missing-edge orbits exhaust H. Consequently in the equal case uv beats every other orbit, and in the unequal case the largest untouched part beats uv, restoration and smaller untouched parts. Integer part sizes make b>a equivalent to b>=a+1, which is essential to the second domain shift. No real-valued part-size extension is asserted.

## Ledger and boundary mechanism
H1 unit-optimal orbit remains optimal for all t>0: full-domain certificate candidate obtained.
H2 restoration never optimal: full-domain strict uv dominance candidate obtained.
H3 some optimal uv/largest-part phase change occurs: REJECTED throughout the full domain, conditional on independent acceptance of this certificate.

Suboptimal order CAN change: at (4,4,6), restoration and untouched_A (also B) cross at exactly t=12. C remains strictly best on both sides and at the crossing. Therefore neither 'no pairwise crossings' nor invariance of the entire ranking is claimed. The mechanism supported by this algebra is only stability of the maximizing orbit: both the small-weight intercept and the affine slope of each necessary comparison have the same strict sign.

## Execution
Batch1 plan fixed five tuples from the pinned no-op packet: (3,3,3),(3,3,4),(3,4,5),(3,3,7),(4,4,6), five weights 1/100,1/10,1,10,100, all five missing-edge orbits. It also computed all positive pairwise crossing weights for those tuples. Complete scores/ties/crossings retained.
Batch2 separately froze the six symbolic coefficient comparisons and independent full weighted hitting-matrix checks at exactly (4,4,6),weights1/10,12,100,all five orbits. All 15 full-matrix fixed-uniform values match derived inverse scores; exact values are in batch2.json. These are author cross-formulation checks, not independent-agent review. Both runs rc0, no failures/retries/extra ranges/third batch. uv isolated SymPy1.14.0, D-drive cache, raw argv/stdout/stderr/rc retained; hashes.json seals the packet.

Typed claims: finite scores/crossings -> batch1.json; symbolic positivity -> batch2.json complete lists, batch2.py/logs; methodological derivation -> preceding identities, input hash and frozen prior inverse; universal optimality -> exhaustive domain substitutions, affine positivity, untouched-score monotonicity and missing-edge orbits. Separate reviewer must verify proof/source alignment and complete coefficient equality before promotion.

No generic-method novelty, global publication priority, deployed-network performance, multi-edge guarantee, or choice-of-budget optimum claimed. Prescribed-weight location invariance does not imply every weight improves U versus no-op; the prior no-op packet shows excessive weight can worsen that objective.
