# Mathematical bridge to Conjecture3.4.7

## Typed dependencies

SOURCE S1: Hu and Kirkland, Complete multipartite graphs and Braess edges (2019), pinned hu-kirkland-2019.pdf SHA256 c896d263c6bec602274f84a29c30492f99e85e3bde654f3e61dcf5aa10718c77. Page3 defines a Braess graph by strict increase for EVERY nonedge. Page19 Remark2 and Conjecture3.4.7 correspond to page-marked text lines1177-1229. Page18 equation12 provides a consistency check on equation13. Existing independent visual notes identify equation13 as malformed; this review newly reads extracted primary text, not a new PDF rendering.

ACCEPTED PROOF P1: project/evidence/kemeny-multipartite/general-review/report.md SHA256 85b165206fd017efbd2d26feee1d50ec438f8c1531ff5900e47d765f174a3e39, especially sections2-3. Exact certificate project/experiments/kemeny-multipartite-proof/certificate.json SHA256 b264e53aa98bb9171fcb327cb82cd01ec31e4c67eecbf30af6752545c078804c. This distinct original mathematical audit reconstructs all1777 coefficients and proves arbitrary gap-count extension. It is reused without a new evaluator.

ACCEPTED PROOF P2: project/evidence/kemeny-multipartite/ranking-review/review.md SHA256 9142b6e6d2d761e86ffefa60d430c37a1aafa67a6e542f889a4a0797c76e4039. Actual-change ranking, including tied sizes, is separately audited.

CONCLUSION C1 below follows from S1+P1; P2 strengthens the decision rule but is NOT needed to close the previously conjectural branch. Publication priority is outside this logical implication.

## Exact graph-theoretic conclusion

Let r>=2, p>=1 and k_i>=3 be integers, and G=K_(k_1,...,k_r) join K_p. Then G is a Braess graph if and only if r=2 and inserting an edge in a smallest non-singleton part strictly increases Kemeny's constant. In the two-part case this is precisely the graph-theoretic condition established in source Remark2. Thus P1 resolves every r>=3 case left conjectural by Conjecture3.4.7; combined with the already-proved two-part characterization it establishes the intended full graph characterization.

Proof: if r>=3, choose any minimum part. It contains a missing pair because its size is at least3. P1 gives Delta=K(G+edge)-K(G)<0 for this pair, contradicting the requirement that every nonedge have positive Delta. Indeed P1 proves the stronger statement for every pair in every tied minimum part. If r=2, Remark2 gives exactly the equivalence above. Alternatively P2 orders the actual changes, so positivity in the minimum part is equivalent to positivity in both parts. No other missing edges exist: the p clique vertices are p singleton parts, adjacent to everything, and all cross-part edges are already present. This proves both directions and all ties. A zero change does not count as Braess; the criterion must remain strict.

The source writes p in N in its dominating-vertex section. Our theorem uses p>=1 explicitly. If N were interpreted to include0, the p=0 case is separately covered by the source's no-dominating-vertex Theorem3.3.3; it must not be silently assigned to the positive-p certificate. Here r counts non-singleton parts, whereas the general source update formula counts all r+p parts. The minimum restriction3 excludes the source's separate size2 case.

## Equation13 issue and safe claim

The extracted p^2 coefficient begins '-18 k_2^3(-8 k_1-50)k_2^2', with no addition sign between the cubic term and the following quadratic term. Read literally this is a product, not the expected sum. The natural additive reading is

    -18 k_2^3 + (-8 k_1-50)k_2^2
    + (30 k_1^2-94 k_1+24)k_2 + 8 k_1^3-24 k_1^2+12 k_1.

At k_1=k_2=k, this gives (by collecting terms) 12k^3-168k^2+36k, exactly the p^2 coefficient in equation12. The literal product cannot do so: it introduces higher-degree terms. This local check diagnoses the missing separator; it is NOT a fresh independent reconstruction of every coefficient of equation13. The all-r proof uses the clean Theorem3.2.3 six-term formula, not equation13.

Safe publication wording: 'We prove the r>=3 assertion of Hu-Kirkland Conjecture3.4.7, and hence its graph-theoretic characterization together with their Remark2. Equation13 in the inspected source has a malformed separator; the proof and sign criterion are expressed using Theorem3.2.3.' Do not claim the literal malformed printed polynomial is proved. A corrected full polynomial should be independently reconstructed before publishing it as a replacement formula.

## Scope verdict

Analytic implication: supported. Coverage of previously conjectural r>=3 cases: complete, including unequal sizes and arbitrary positive p. Full intended characterization: supported with the equation13 qualification above. Ranking: stronger optimal-insertion statement, logically optional. Priority/current open status: NOT assessed. No new evaluator, no finite grid, no new source search, no implementation or release certification.
