# Independent forbidden-restoration endpoint review

All four scoped gates PASS. No correction required. Scope is the frozen unequal integer family3<=a<=b<=c,c>a, one required missing UNIT insertion, unit old conductances, fixed iid hub mixture0<=theta<1, and restoration forbidden. This is not a public-code or publication gate and is excluded from the current action-choice release.

## Reproduction

Verified target proposal161f3b82f41ba7ada806fa1d2779bbee18066b31aaa29ce6ef1cb586e96094bf and result12373b7f62ccb631da09b31840ab3b337eb1a7f424c4dfb8d78a0a66feafe681. All author/input manifest references match their byte hashes. One independent symbolic batch returned0, empty stderr,2.71s, timeout60s, uv isolated/SymPy1.14.0/D cache. No retry, grid or extra evaluator.

The reconstruction starts from accepted inverse-action quantities r_I=2/d+1/(d^2 k),s_I=2/d^2+2/(d^3 k)+W/(d^2 k^2),z_h=-1/(ndk), using I=s_I/(1+r_I),lambda=n*z_h^2/(1+r_I), and C=(2/e^2)/(1+2/e). It does not copy the author's compact I formula or gap polynomial. After cancellation and each substitution, I reconstructed the entire author numerator/denominator from every exponent/coefficient record and asserted exact polynomial equality to the independently derived expressions. Duplicate exponents, missing nonzero monomials, or extra terms would fail. Missing monomials are zero; they cannot hide a negative term because full polynomial equality is checked.

Case b=a: numerator27 terms,degree6,constant27090; denominator42 terms,degree8,constant25084080. Case b>a: numerator83 terms,degree6,constant50240; denominator161 terms,degree8,constant62092800. Every nonzero coefficient is positive. Full dictionaries agree, not merely constants or selected signs. Raw argv/cwd/status/streams and result.json retain these findings.

## Domain, denominators and boundaries

Case1 a=x+3,b=a,c=a+1+z covers exactly b=a,c>a, including x=0,z=0; y is absent. Case2 a=x+3,b=a+1+y,c=b+z covers exactly b>a,c>=b, including y=0,z=0 and hence b=c. Integer gaps make these disjoint cases exhaustive. Equal a=b=c is explicitly excluded and must not use this conclusion.

Every original score denominator is positive: n>=11,d>=8,e>=7,k>0,Z=d(d+2)k+1>0 and1+r_I>0. There is no cancellation across a pole on the domain. The reconstructed denominator polynomials have positive constants and nonnegative coefficients, so their evaluated values are strictly positive even on the orthant boundaries. Positive numerator constants likewise prove strict G=C-I-lambda>0 throughout both orthants; no finite-grid extrapolation or boundary limit assumption is used.

## Workload envelope and ties

With restoration unavailable, missing edges comprise incident-u A pairs, untouched A pairs, internal B and internal C pairs. All are nonempty because a>=3. Untouched scores2/[(n-q)(n-q+2)] increase strictly with part size q. In the unequal domain A cannot be largest, so largest scores belong to C alone when c>b, or to both B and C when b=c. Every actual internal pair of each largest part ties; no individual-edge uniqueness is asserted.

Lambda is positive, and for all theta<1,
 C-I-theta*lambda=G+(1-theta)*lambda>0.
Therefore incident-u can never join the optimum. The formal crossing sigma=(C-I)/lambda=1+G/lambda is strictly greater than1, closing the prior conditional unit-insertion question on this domain. The common final volume m+1 and positive workload normalization factor preserve ranking among these required unit insertions. No-action has a different volume and is outside the assertion.

At theta1, actual iid source and target both equal h, so every action objective is zero. Strict positivity of the scaled endpoint gap does not imply an actual strict ranking or only a two-orbit tie there. No arbitrary-strength extension follows from this unit proof.

## Four gates and provenance boundary

Reproduction PASS: exact independent score-to-polynomial reconstruction and raw successful run.
Specification compliance PASS: exhaustive integer cases, full non-restoration candidate set, a3/b=a/b=c boundaries and theta endpoint convention.
Source verification PASS for accepted generic inverse/covariance machinery and prior independently reviewed envelope only. The pinned common-strength review is distinct from its author's proposal, and no new priority claim is introduced. No source search or generic-method novelty is certified.
Implementation alignment PASS: author code cancels the same rational gap and emits all actual nonzero terms. Its positivity assertion plus recorded positive constants matches the proof; the independent checker additionally verifies full equality and denominator constants. Author's single6.16s rc0 run and its setup-containing stderr are not misreported as multiple runs or empty output.

This independent acknowledgment covers the mathematical research packet only. It makes no physical benefit, no-action improvement, equal-family conclusion, arbitrary strength claim or public implementation approval.
