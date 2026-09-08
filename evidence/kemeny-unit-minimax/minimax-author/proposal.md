# Candidate complete deterministic unit-repair minimax rule

Author analytic packet, pending distinct independent audit. Domain: H=(K_(a,b,c) joinK1)-uh, integers3<=a<=b<=c, unit old edges, and exactly one missing UNIT insertion with restoration allowed. No action is NOT an admissible action. The fixed iid hub-mixture workload is unknown in a closed interval[l,h] with0<=l<=h<1. This is not optimization over strength, randomization or theta-adaptive actions, and is excluded from PR12.

## Positive lines and the two surviving sets

Let n=a+b+c+1,d=n-a,e=n-c,k=(n-1)(d-1)/(nd),W=[n(n-1)+d(d-1)]/(n^2d^2),Z=d(d+2)k+1. Set

    T=sum_{q=a,b,c}(q-1)/(n-q)+3/n+W/k,
    Hh=(n-1)/n^2+1/(n^2 k),
    R=W/k, lambda_R=1/(nk),
    I=(2k+2/d+W/k)/Z, lambda_I=1/(nkZ), C=2/[e(e+2)].

Restoration is the singleton action set Rset={uh}. Define Xset and its score parameters(J,lambda_X) as follows:

- If a=b=c, Xset is every{u,v},v in A excluding u; J=I,lambda_X=lambda_I.
- If c>a, Xset is every internal pair in every largest part; J=C,lambda_X=0. If b=c both parts contribute all pairs.

For these two sets define positive reduced objective lines

    A(theta)=T-J+theta*(nHh-lambda_X),
    B(theta)=T-R+theta*(nHh-lambda_R).

The actual objective is U_X=2(m+1)(1-theta)A(theta)/n or U_R=2(m+1)(1-theta)B(theta)/n, respectively, where m=ab+ac+bc+a+b+c-1. Positivity of these lines follows from the connected candidate graph's positive covariance trace for theta<1. Their slopes need not be assumed positive for the endpoint method. Common normalization cancels in relative regret only because every admissible action inserts the same unit strength and uses the same workload law.

Every other insertion is strictly pointwise dominated in actual objective by each member of Xset throughout theta<1. In the equal family, accepted uniform ordering gives I strictly above every untouched score, and its positive workload slope preserves that strict score advantage. In the unequal family, the distinct accepted forbidden-restoration audit proves C-I-lambda_I>0; hence C-I-theta*lambda_I>0. Every nonlargest untouched score is also strictly smaller. These are FIXED-action dominations, not merely absence from a changing oracle envelope.

This eliminates every other insertion from the COMPLETE minimax set: its regret is strictly larger than an X action's regret at both interval endpoints. At an endpoint attaining X's worst regret, the excluded action has strictly larger regret, hence strictly larger maximum. This also holds when l=h. Tied labels inside Xset remain tied at every workload and cannot be removed when reporting all actions. There are exactly two surviving objective orbits before minimax selection.

## Complete rule

The unique formal crossing tau is

    equal: (a-2)(10a^2+a-1)/[(2a+1)^2(2a+3)(3a+1)],
    unequal: nkC-nW.

Accepted envelope results give tau>0, equal tau<1, A<B below tau and B<A above it. Unequal tau may be at least1.

If l=h, choose Xset when l<tau, Rset when l>tau, and their union when l=tau. The minimum worst relative regret is zero; excluded dominated actions remain strictly suboptimal.

For a nondegenerate interval l<h:

1. If h<=tau, precisely Xset is minimax, with worst regret zero. This includes crossing only at h and every admitted interval when tau>=1.
2. If l>=tau, precisely Rset is minimax, with worst regret zero. This includes crossing only at l.
3. If l<tau<h, compare P_X=A(l)A(h) with P_R=B(l)B(h). If P_X<P_R choose precisely Xset; if P_X>P_R choose precisely Rset; if equal choose their union. There are no additional minimizers.

In the interior-crossing case the exact orbit regrets are

    r_X=A(h)/B(h)-1, r_R=B(l)/A(l)-1.

The minimax value is their minimum. X's unique worst workload is h and restoration's is l. In the one-sided cases the winning orbit is oracle everywhere, hence every workload attains its zero regret. Endpoint-only crossing does not add the other orbit to the minimax set on a nondegenerate interval: that orbit has strictly positive regret at the other endpoint. At theta1 all actual objectives vanish and relative regret is0/0, so no rule above extends there.

The independently accepted endpoint lemma proves worst regret is attained at an endpoint, even with oracle changes: L_e/min_j L_j=max_j L_e/L_j, and each positive-denominator affine ratio is monotone or constant. The two-action product comparison follows by multiplying positive A(l)B(h). This elementary robust linear-fractional method is known/inference, not a generic novelty claim. The new proposed scope is its combination with strict full-family domination and complete physical-action ties.

## Sole declared midpoint diagnostic

For333 and interval[0,21/500], midpoint21/1000 exceeds tau46/2205. Reduced lines are

    A(theta)=10021/8680+(2547/2480)theta,
    B(theta)=81/70+(9/10)theta.

At the midpoint A=20416409/17360000 and B=82323/70000, so midpoint optimization selects restoration. Yet the worst relative regrets are r_X=23305/10372104 and r_R=23/10021, with r_X<r_R. Thus precisely the two incident-u A edges are minimax. result.json retains exact endpoint products as an independent rational check of the comparison. The one predeclared diagnostic passed; no alternate interval or graph was tried.

## Provenance and limits

One Fraction-only evaluator returned0 with empty stderr under a60second uv/D cap; run.json/stdout.bin/stderr.bin retain exact execution. No failures, second evaluator or numerical grid. Main theorem reasoning is analytic and depends on independently accepted unit domination, equal-envelope ordering and endpoint lemma, all pinned in input-hashes.json. The complete minimax set is not inferred from the diagnostic. No no-action, variable-strength, general demand, physical benefit, priority or current-release approval is asserted. A distinct reviewer must verify this proposal before promotion.
