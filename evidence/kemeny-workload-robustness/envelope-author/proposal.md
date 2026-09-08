# Candidate common-strength hub-workload envelope

Author analytic packet; independent audit required. H1 score identities, H2 two-line envelope and H3 strict threshold decrease are established below. Generic inverse/update and covariance methods are inherited known machinery, not claimed new. No parameter grid was run.

## Domain and scores

For integers3<=a<=b<=c, H=(K_a,b,c join K1)-uh has unit old conductances. Choose exactly one missing edge of COMMON conductance t>0. The iid endpoint law is p=(1-theta)Uniform+theta delta_h,0<=theta<1, with zero diagonal hitting time. Define
 n=a+b+c+1, d=n-a, e=n-c,
 k=(n-1)(d-1)/(nd), W=[n(n-1)+d(d-1)]/(n^2 d^2),
 D_R=k+t(1-k), D_U=d^2 k+t(2dk+1).
All denominators below are positive;0<k<1.

The relative improvement in the covariance trace, after canceling common positive t(1-theta)/n, is an affine line. Restoration has
 R_t=W/(k D_R), lambda_R=1/(n k D_R).
Incident-u A pairs have
 U_t=(2k+2/d+W/k)/D_U, lambda_U=1/(n k D_U).
Each untouched part of size q has constant score2/[(n-q)(n-q+2t)]; the largest-part score is C_t=2/[e(e+2t)]. Candidate total conductance m+t is common, so maximizing these lines minimizes actual iid expected hitting time.

Derivation: reuse accepted M=L_H^+ and the intact/deletion inverse action. Restore has r=(1-k)/k, s=W/k^2, z_h=-1/(nk). Incident-u has r=2/d+1/(d^2 k), s=2/d^2+2/(d^3 k)+W/(d^2 k^2), z_h=-1/(ndk). The score is s/(1+tr)+theta*n*z_h^2/(1+tr), giving the formulas above. Untouched contrasts are orthogonal to the deletion image and have zero hub coordinate. D_U-D_R=k[d^2-1+t(2d+1)]>0, so restoration has strictly larger slope. At t=1 these definitions reduce to the accepted unit-strength formulas (D_R=1,D_U=Z).

## Unequal family: only largest parts and restoration

If c>a, let j=d-e=c-a>=1. The accepted common-positive-strength uniform theorem gives C_t>U_t>R_t. Define tau_t=(C_t-R_t)/lambda_R. At the restore/C crossing, incident-u lies strictly below iff
 E_t=(D_U-D_R)C_t-D_U U_t+D_R R_t>0.
Independent symbolic simplification gives
 E_t=2[k*((d^2-1+t(2d+1))/(e(e+2t))-1)-1/d].
Put N=d^2-e^2-1+t(2d+1-2e). Then
 d E_t/2=((n-1)/n)(d-1)N/[e(e+2t)]-1.
For d>=e+1, N>=2e+3t, d-1>=e, and all factors are positive. Hence
 d E_t/2 >= [(n-2)e+(n-3)t]/[n(e+2t)]>0.
Thus incident-u lies below the constant C_t up to tau_t, and below the steeper restoration line thereafter. Other untouched scores are strictly smaller unless their part is also largest. The complete envelope consists of all largest-part internal edges (both B,C if b=c) and restoration only.

The exact positive threshold is
 tau_t=2 n k D_R/[e(e+2t)]-n W.
If tau_t<1, largest-part edges win below, tie with restoration exactly at tau_t, and restoration uniquely wins above. If tau_t>=1, largest-part edges win for every admitted theta. The case tau_t=1 is not an actual two-orbit tie at theta1: all actual objectives there are zero.

## Equal family

If a=b=c, the accepted common-t uniform theorem puts incident-u strictly above every untouched edge and restoration at theta0. Its positive slope keeps untouched edges excluded. Only incident-u versus restoration can win. Their crossing is
 tau_eq_t=2n(k+1/d)D_R/[d^2-1+t(2d+1)]-nW
 =(a-2)[20a^3+8a^2 t+4a^2-a t-t]/[(2a+1)^2(3a+1)(4a^2+4at+4a+3t)].
All incident-u A pairs win below it, tie with restoration at it, and restoration alone wins above it. Positivity and the upper bound1 for every t>0 follow from the strict decrease and limits proved next. No individual incident-u edge is uniquely selected.

## Strength dependence and nonzero limits

Unequal threshold derivative is
 tau_t'=2nk[e-k(e+2)]/[e(e+2t)^2].
Since1-k>0 and e<=d-1,
 e-k(e+2)<=(d-1)-k(d+1)=-(a-1)(d-1)/(nd)<0.
Therefore tau_t strictly decreases. Its limits are
 tau_0=2nk^2/e^2-nW,
 tau_infinity=nk(1-k)/e-nW.
Using e<=d-1 and k(1-k)>0,
 tau_infinity>=nk(1-k)/(d-1)-nW=(a-1)(d-1)/(d^2 n)>0.
Thus all finite thresholds are positive and decrease toward a strictly positive limit, not toward zero. These limits do not classify which integer triples have tau_t=1.

For the equal threshold, differentiation gives the positive prefactor2n(k+1/d) divided by[d^2-1+t(2d+1)]^2 times
 (d^2-1)-k d(d+2)=-(d-1)(a-2)/n<0.
Therefore it too strictly decreases. Its exact limits are
 tau_eq_0=a(a-2)(5a+1)/[(a+1)(2a+1)^2(3a+1)],
 tau_eq_infinity=(a-2)(8a^2-a-1)/[(2a+1)^2(3a+1)(4a+3)].
Both are positive for a>=3. Moreover
 1-tau_eq_0=(12a^4+23a^3+32a^2+10a+1)/[(a+1)(2a+1)^2(3a+1)]>0.
Consequently0<tau_eq_infinity<tau_eq_t<tau_eq_0<1 for every finite t>0. At t=1 the threshold simplifies exactly to the accepted(a-2)(10a^2+a-1)/[(2a+1)^2(2a+3)(3a+1)].

At t=0 all actual insertion interventions coincide with no addition; limiting normalized score rankings are not actual distinctions there. At theta=1 every actual iid objective is zero. Both endpoints are excluded from the strict ranking theorem. Infinite t is only a limit, not a finite admissible intervention in this statement.

## Uniform old-weight scaling interpretation

If all old weights are multiplied by q>0 while the new edge remains unit, dividing all final conductances by q leaves random-walk transitions and hitting times unchanged. This is equivalent to unit old weights and common new strength t=1/q, with the SAME fixed iid endpoint law. Thus this theorem directly provides a conditional location rule for uniform old-weight scaling. At theta0 the old common-t optimizer is invariant. For nonuniform workloads the choice can change: in any equal family choose theta strictly between tau_eq_infinity and tau_eq_0. Strict monotonicity and continuity give a unique positive t crossing, changing the optimum between incident-u and restoration. This is an analytic existence inference, not a perturbation-grid observation or claim for every theta.

## Provenance, execution and limits

Accepted inputs: ../astra-uniform-weight-review-work/review.md (common-t uniform optimizer and inverse scores); ../astra-workload-family-review-work/report.md and ../astra-next-screen-summary-review-work/workload-attestation.md (unit workload envelope); ../astra-workload-screen-review-work/result.json (accepted workload convention evidence). Input byte hashes are retained separately. No old file was changed.

Batch1 check.py/result.json validates score/slope/E identities, lower-bound algebra, threshold derivatives and equal limits/unit specialization. Batch2-plan.md froze the remaining unequal limit-sign simplification and derivative checks; check2.py/batch2.json provides exact positive lower and negative upper bounds after n=d+a. This refines the original planned endpoint-sign task, without new graphs or a numeric grid. Both short logged symbolic batches returned rc0, empty stderr (about3.10s and1.72s; each timeout60s), uv isolated/SymPy1.14.0/D cache. Raw argv/cwd/status/streams retained. No failed mathematical hypothesis or execution was hidden. The optional numeric diagnostics were not needed.

Typed claims: score/threshold identities are symbolic result claims linked to the two scripts/results; universal envelope and sign conclusions are analytic claims linked to the positive factored bounds and accepted uniform theorem; scaling is an inference from invariant transition probabilities. This is a complete conditional location rule, not joint strength optimization, a no-action rule, global integer endpoint classification, generic-method novelty or measured practical benefit. Independent audit remains required.
