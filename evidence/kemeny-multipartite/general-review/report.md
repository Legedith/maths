# Independent four-gate review

Verdict: PASS for the selected mathematical theorem and frozen certificate. The new portable checker has not been supplied and is outside this verdict. No novelty or practical-impact certification.

Auditor: /root/astra_general_proof_verifier, independent of candidate authors. Frozen evaluator: evaluator-contract.md, established before evaluate.py execution. Canonical execution: .venv/Scripts/python.exe evaluate.py; run.py retains actual argv, cwd, stdout, stderr, and returncode for environment creation, dependency installation, and evaluator execution in run-0.json through run-2.json. All returncodes are zero. Python environment and uv cache are on D:. No author code was executed or read.

## 1. Reproduction: PASS

The evaluator reconstructs the source six rational terms, clears each denominator separately, and expands the independently aggregated moments with SymPy 1.14.0. The exact dictionary agrees with every entry of the frozen certificate: 1777 nonzero terms, minimum scalar coefficient 2, constant 60948. Adjacent gap-variable transpositions preserve the dictionary. The aggregate has weighted degree 5 with weights (1,2,3) on (U,V,W). Raw output: result.json and run-2.json; independently derived aggregate: independent-aggregate.txt.

Exact adjacency/transition matrices, with K=trace((I-T+1*pi)^(-1))-1, give Delta=229/627000 for q=(9,9),p=1 and Delta=-302125/100216116 for q=(3,3,4,4,5,6),p=2. Both match the six-term source formula exactly. These are bridge diagnostics, not the universal proof.

## 2. Specification compliance and proof: PASS

For k=r-1, every nonselected size is x+u_i. Summing cubes over all non-singleton parts gives (k+1)x^3+3x^2 U+3xV+W. Every singleton contributes 1, hence +p is mandatory in T3; similarly T2 has +p. Expanding sum_j q_j(n-q_j)^2 gives n^3-2nT2+T3, and removing the selected contribution gives S1. Thus the corrected moment is exactly the source sum, not an empirical correction.

The complements to the six denominators, in order, are n(a+2)g, an(a+2)g, 2a(a+2), an(a+2), a+2, and 2ng. Multiplying the six numerators gives exactly the proposed M. On the domain n>=10, a>=7, g=sum_j q_j(n-q_j)>0, so D=2an(a+2)g and g+2 are strictly positive.

The universal-variable step is valid. Treat k as a scalar indeterminate independent of the number m of formal gap variables, and write F_m=F(sum u_i,sum u_i^2,sum u_i^3;k,x,p). Setting one variable to zero gives F_(m-1) exactly, with k unchanged. Therefore the coefficient of any particular monomial is unchanged when unused variables are removed or added. Symmetry transports any support of size s to the first s variables. Weighted aggregate degree <=5 implies every occurring gap monomial has support <=5. Accordingly the five-variable dictionary supplies every possible coefficient for any m, even m>5. Setting m=k only at final evaluation is legitimate; it is not necessary or correct to set k=5 during certification. For k<5, padding by zero gives the required expression. Substitution k=2+R preserves this restriction property because R is a separate scalar variable. There is no missing variable-count dependence: all such dependence is already carried by k.

The dictionary's strictly positive scalar coefficients and constant 60948 prove Q>=60948 on the nonnegative orthant, including every actual number of gaps. Parameters A=x-3, R=r-3, P=p-1 and u_i=q_i-x are nonnegative integers for any selected minimum part. Conversely choosing these integers and exactly k=R+2 gaps constructs every relabelled admitted graph. Therefore Delta=-2Q/(D(g+2))<0 universally.

Every tied minimum can independently be relabelled as selected x. Permutations within a part act transitively on its unordered vertex pairs and preserve the original graph; edge-added graphs are isomorphic. Thus every pair in every minimum part is covered. No uniqueness-of-minimum assumption is hidden.

## 3. Source verification: PASS, bounded priority only

Read the pinned Hu--Kirkland page-marked primary text, particularly PDF page 10 (general part count, n, alpha, gamma, selected size >=3), page 12 Theorem 3.2.3 (six-term formula), page 18 Corollary 3.4.5 (equal parts), and page 19 Conjecture 3.4.7. Pinned PDF SHA256 c896d263c6bec602274f84a29c30492f99e85e3bde654f3e61dcf5aa10718c77 matches the previously visually verified source notes at project/evidence/kemeny-three-part/independent/source-domain-proof-notes.md. Current review used extracted primary text plus those existing visual notes; it did not newly render the PDF. Source section 3.2 permits arbitrary total part count; its total count includes the p singletons. The source's page-19 r instead counts non-singleton parts.

The general edge-update formula is known. The audited all-r strict minimum-part sign result strengthens the r>=3 non-Braess existence branch of that historical conjecture. This review does not establish global priority, that the conjecture remained open in 2026, or real-world impact. The two-part counterexample establishes failure of the unrestricted r=2 extension, not failure for every two-part graph. No finite sweep was needed or recertified here.

## 4. Implementation alignment: PASS for frozen mathematical certificate

Selection SHA256 29543de7f639db23fed0bdc8bdccb024b5c8b2c29e301f41455520b8e0694a8e and proposal SHA256 0cd623573884161cbc6dbfb28381b716ed63b5fff8104063c337a2117be73bf9 were checked. Evaluator asserts certificate SHA256 b264e53aa98bb9171fcb327cb82cd01ec31e4c67eecbf30af6752545c078804c, variable ordering, absence of duplicate exponent entries, and full dictionary equality. This closes the mathematical proof/certificate alignment independently. It does not audit an unspecified portable checker, nor does it promote the original invalid singleton-cube artifacts. The certificate's sufficiency is tied to this frozen source/proof interpretation; it is not a provenance schema on its own.
