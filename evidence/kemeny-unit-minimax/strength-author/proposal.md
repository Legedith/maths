# Counterexample to the all-strength forbidden-restoration conjecture

Author packet, independent review required. The proposed extension is FALSE. Take(a,b,c)=(3,3,4), prescribed common insertion strength t=16, and theta=9147/9152. Restoration is forbidden. Precisely the two incident-u A edges win, strictly beating every largest-part pair.

Using the accepted full common-strength inverse/covariance formulas, n11,d8,e7,k70/88 and W166/(121*64). Put D=d^2k+t(2dk+1), I=(2k+2/d+W/k)/D, lambda=1/(nkD), C=2/[e(e+2t)]. Exact calculation gives

    C-I-lambda=-1/2166528,
    sigma=(C-I)/lambda=4571/4576,
    theta=(sigma+1)/2=9147/9152.

Thus0<sigma<theta<1 is admitted. Scores at this theta are incident_A4535/619008, untouched_A1/160, B1/160 and C2/273. The incident-minus-C gap is1/4333056>0; C also exceeds1/160. All remaining missing edges are covered: two incident A edges, one untouched A edge, three B pairs and six C pairs. With labels A0,1,2, B3,4,5, C6,7,8,9 and hub10, the complete optimal set is{0,1},{0,2}. This is a tied edge class, not a unique edge.

The score comparison translates to the actual fixed iid hitting objective because all candidates have the same positive final volume m+16 and the canceled factor16(1-theta)/n is positive. There is no comparison to no action or optimization over different strengths. Theta1 would make actual objectives zero, but the chosen theta is strictly smaller. This does not contradict the prior unit-strength domination theorem.

## Discovery and failed conjecture

The first symbolic evaluator established the cleared endpoint numerator is affine in t. Its constant coefficient is positive in both exhaustive unequal orthants, but the proposed slope positivity fails. At the first orthant origin334 the numerator is28910-1820t; hence its endpoint sign becomes negative above t2891/182. The first run wrote full coefficients then failed its assertion with rc1. That output is exploratory failure evidence, not a universal positivity certificate.

The separately frozen second evaluator selected t16 at that exact boundary, computed the rational crossing and its midpoint with1, and compared all remaining classes. It returned0. No grid, additional graph or third run occurred. Both60second capped calls, raw streams, argv, elapsed and statuses are retained. Batch1 stderr includes uv setup and its AssertionError; batch2 stderr is empty. result.json preserves the failed coefficient proposal and batch2.json the successful exact counterexample. No shared files, Git or current release changed.

Known generic score machinery is reused from the accepted common-strength analytic review. This packet refutes the all-t endpoint and location conjectures; it does not classify the full forbidden-restoration envelope, prove novelty or physical benefit, or provide a final independent evidence gate.
