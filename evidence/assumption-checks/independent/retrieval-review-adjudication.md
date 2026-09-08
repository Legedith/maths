# Blinded source-review comparison and adjudication

Two independent source-only reviews were frozen before either was opened. Reviewer A and reviewer B agreed on 21 of 24 fixed prospective retrieval results. The three disagreements were resolved from the exact-version original PDFs. Both original review files remain unchanged.

The adjudicated labels are descriptive for these 24 purposively chosen results only: 12 supported, 9 refuted, and 3 insufficient. They are not a service error rate or population estimate.

## Resolved disagreements

- **Theorem 19685900 (Q02 rank 1): insufficient.** The original theorem is recorded in a normalized-Laplacian context that uses positive degrees and a single distinguished zero eigenvalue. The slogan quantifies over a generic graph without retaining the connected/no-isolate convention. The identity may extend under a chosen normalized-Laplacian convention, so the omission is narrower-source ambiguity rather than a decisive counterexample. Locator: 2009.04139v1, PDF pp. 1-3: normalized-Laplacian definition and spectrum convention; Theorem 2.5.

- **Theorem 18165234 (Q03 rank 2): refuted.** The paper explicitly reserves UST for the unweighted law and 'weighted UST' for the product-of-weights law. The slogan says uniformly random spanning tree while retaining nonunit edge weights. On a triangle with conductances (2,1,1), the weight-2 edge has weighted inclusion probability 4/5 but ordinary uniform inclusion probability 2/3. Locator: 2410.16830v3, PDF p. 2, distinction between UST and weighted UST; PDF p. 8, Theorem 2.1.

- **Theorem 26077729 (Q09 rank 2): refuted.** The source globally defines a resistor network as connected and its conductance matrix as irreducible. The slogan drops this material hypothesis while claiming uniqueness modulo one global constant for any balanced current. A disconnected network has one gauge constant per component, and a globally balanced current can still be unbalanced on individual components and unsolvable. Locator: 2502.19720v2, PDF p. 5, connected-network/irreducible-conductance setup and Lemma 2.1.

## Complete accounting

| Query | Rank | Theorem | Paper | A | B | Final | Structured round two |
|---|---:|---:|---|---|---|---|---|
| Q01 | 1 | 23150070 | 0802.2576v2 | refuted | refuted | refuted | eligible |
| Q01 | 2 | 21091970 | 1612.07898v1 | refuted | refuted | refuted | ineligible |
| Q02 | 1 | 19685900 | 2009.04139v1 | insufficient | supported | insufficient | eligible |
| Q02 | 2 | 18276974 | 2302.07170v2 | refuted | refuted | refuted | eligible |
| Q03 | 1 | 18134454 | 2410.16836v3 | supported | supported | supported | eligible |
| Q03 | 2 | 18165234 | 2410.16830v3 | refuted | supported | refuted | ineligible |
| Q04 | 1 | 24585048 | 2109.13394v2 | supported | supported | supported | eligible |
| Q04 | 2 | 22467127 | 1206.0937v3 | supported | supported | supported | eligible |
| Q05 | 1 | 26329144 | 2101.07103v2 | insufficient | insufficient | insufficient | eligible |
| Q05 | 2 | 23740032 | 2104.06052v3 | supported | supported | supported | ineligible |
| Q06 | 1 | 25939467 | 2210.07869v7 | refuted | refuted | refuted | ineligible |
| Q06 | 2 | 21595533 | 1506.03343v1 | supported | supported | supported | ineligible |
| Q07 | 1 | 25306126 | 1202.5569v1 | supported | supported | supported | ineligible |
| Q07 | 2 | 22481653 | 1206.4162v1 | supported | supported | supported | ineligible |
| Q08 | 1 | 18458194 | 2405.09102v1 | supported | supported | supported | ineligible |
| Q08 | 2 | 17464638 | 2510.14165v1 | supported | supported | supported | eligible |
| Q09 | 1 | 22536602 | 1203.4045v1 | supported | supported | supported | ineligible |
| Q09 | 2 | 26077729 | 2502.19720v2 | refuted | supported | refuted | ineligible |
| Q10 | 1 | 20655858 | 1803.09144v1 | supported | supported | supported | ineligible |
| Q10 | 2 | 17584187 | 2508.21506v1 | refuted | refuted | refuted | ineligible |
| Q11 | 1 | 24648249 | 2010.01530v1 | supported | supported | supported | ineligible |
| Q11 | 2 | 20314933 | 1902.01110v2 | insufficient | insufficient | insufficient | ineligible |
| Q12 | 1 | 23832572 | 2109.01324v2 | refuted | refuted | refuted | ineligible |
| Q12 | 2 | 20258646 | 1904.07766v1 | refuted | refuted | refuted | ineligible |

Eight theorem IDs are eligible for separately recorded structured instance annotations. Sixteen are ineligible because at least one material object is absent from the grammar; every row's reason is retained in the machine-readable adjudication. Eligibility does not mean that the checker can prove the theorem or judge the generated prose. In particular, the two disconnected spectral separating instances are expected to produce `abstain` because the checker deliberately exposes those spectrum products only for connected graphs.

## Evidence boundary

The structured checker outputs remain separate from the source-only judgments and cannot revise them. A successful finite instance is not a theorem proof. The study makes no natural-language guarantee, timing or productivity claim, service-population inference, or novelty claim.

Machine-readable record: `retrieval-review-adjudication.json` (SHA-256 `1b64837ccce001b3bbe5996b594a8d820bcbcab0a87e1831f8e6fb2441311fb9`).
