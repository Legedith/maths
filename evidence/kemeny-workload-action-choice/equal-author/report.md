# Candidate no-action comparison: equal-family theorem and bounded unequal evidence

Author packet; independent review required. The requested full unequal-family theorem remains OPEN in this packet. All twelve frozen diagnostic rows improve under the best unit insertion. A complete analytic proof is obtained for every all-equal graph a=b=c>=3 and every0<=theta<1. No diagnostic pass is promoted to the unresolved unequal domain.

## Correct objective and proof approaches

For candidate score alpha_e+theta beta_e in the accepted unit workload convention, let B(theta)=T/n+theta M_hh. Baseline objective is2m(1-theta)B(theta), while inserted objective is2(m+1)(1-theta)[B(theta)-alpha_e-theta beta_e]. Hence baseline minus insertion equals
 2(1-theta)[(m+1)(alpha_e+theta beta_e)-B(theta)].
The volume change cannot be canceled in this comparison.

A1, resistance decrease alone: REJECTED as a proof approach because it omits the larger final volume. A2, retain the uniform-optimal edge throughout: REJECTED, already within the frozen333theta9/10 row. There U_uv=3247929/2170000 exceeds baseline3337/2250 although restoration improves. A3, use the complete optimum envelope and test affine improvement at its switch/endpoints: VALID approach and successful for the equal family below. Its unequal switch inequality is not established here.

## Full all-equal theorem

Set a=b=c>=3, n=3a+1,d=2a+1,m=3a^2+3a-1 and reuse accepted k,W,R=W/k,Z=d(d+2)k+1,U=(2k+2/d+R)/Z. Let
 T=3(a-1)/d+3/n+R,
 h=(n-1)/n^2+1/(n^2 k).
Define the scaled improvement margins
 F_R(theta)=(m+1)R-T+theta[(m+1)/(nk)-nh],
 F_U(theta)=(m+1)U-T+theta[(m+1)/(nkZ)-nh].
Actual improvement is2(1-theta)F/n. The accepted oracle selects uv up to tau=(a-2)(10a^2+a-1)/[(2a+1)^2(2a+3)(3a+1)], then restoration. Both tie at tau, and0<tau<1.

Independent symbolic simplification gives the same margin for both at tau:
 F_R(tau)=F_U(tau)
 =[18a^6+531a^5+306a^4+39a^3-15a^2-8a-1]
 /[3a^2(2a+1)^2(2a+3)(3a+1)^2]>0.
For a>=1,15a^2+8a+1<=24a^3<39a^3; thus the numerator is strictly positive without an unreported coefficient search.

The uv slope is
 -(216a^6+342a^5+105a^4+51a^3+12a^2+5a+1)
 /[6a^2(3a+1)(12a^3+18a^2+3a+1)]<0.
The restore slope is
 (18a^4+15a^3+12a^2-2a-1)/[6a^2(3a+1)]>0;
indeed2a+1<=3a^2<12a^2 for a>=1. Therefore the selected uv margin is minimized at tau on[0,tau], and the selected restoration margin is minimized at tau on[tau,1). Both are strictly positive. This proves the best required unit insertion strictly beats no action for every equal-family member and every admitted workload. Ties inside the incident-u class and at the switch do not affect the objective proof. At theta1 all actual objectives are zero, so strict improvement does not extend to that endpoint.

## Frozen diagnostics and rejected hypotheses

Exactly333,334,33100 at theta0,1/10,1/2,9/10 were evaluated, all five missing-edge classes each time. All twelve best-improves flags are true; result.json retains every baseline/candidate value and improvement. No new graph rows were added.

H1, best unit improves for the whole sorted family: PROVED for a=b=c only; twelve diagnostics support but do not settle the unequal family. H2, restoration alone always improves: REFUTED by33100 at all four declared workloads. At theta0, U_restore=15219215/80143 exceeds baseline308161495107/1625002366, while C insertion improves. H3, the optimal-envelope switch margin is always positive: PROVED for equal family, OPEN for unequal family.

In an unequal graph, the accepted oracle is C then restore if tau<1, or C throughout if tau>=1. The remaining proof obligations are explicit: with F_C(theta)=(m+1)C-T-theta*n*M_hh, show F_C(tau)>0 when tau<1 and show F_C(1)>=0 (with sufficient strictness before1) when tau>=1, together with the restoration slope sign. Those inequalities are not asserted solved here. Uniform theta0 improvement is independently known; it cannot alone settle the whole interval.

## Evidence, bounds and limits

Batch1: exact Fraction12row calculation, rc0, empty stderr,0.72s. Batch2: frozen symbolic equal-switch/slope factorization, rc0, empty stderr,1.75s. Both timeout60s, uv isolated/D cache; batch2 uses SymPy1.14.0. Raw argv/cwd/status/streams and scripts/results retained. There were exactly two evaluator attempts, no retry or expanded grid. A preliminary read-only filename lookup for report.md in the old uniform no-op stage failed because the file is proposal.md; this was not an evaluator or lost run.

Accepted inverse/unit-workload envelope and uniform no-op review are reused with input hashes. The new no-action identity and equal-family proof above are not inferred solely from those prior results. Typed numerical claims resolve to result.json /rows; symbolic identities to batch2.json/check2.py; universal equal conclusion to the sign argument and accepted envelope. This packet is excluded from currentPR11 and requires another agent's audit before promotion. No physical benefit, monetary decision optimum, generic-method novelty or full unequal-family conclusion is claimed.
