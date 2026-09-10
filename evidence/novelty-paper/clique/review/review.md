# Independent scoped audit

All four scoped gates PASS. This is an example/formula correction certificate, not substantive novelty or release approval. No source contact was made.

## Reproduction

One frozen evaluator invocation, cap60s, actual elapsed10.211662s, rc0, empty child stderr, no retry. logs/attempt-review01.json retains explicit uv child argv, environment, times and stream hashes. Outer command was uv run --frozen python D:/CodexWorkspaces/mathematics-atlas/project/experiments/kemeny-three-part-proof/run_logged.py --attempt-id review01 --timeout-seconds 60 --log-dir logs -- uv run --frozen python check.py, from this stage with UV_CACHE_DIR=this-stage/uv-cache and UV_PROJECT_ENVIRONMENT=this-stage/.venv. Outer setup created the isolated environment and installed two packages; this startup precedes the timed child. Pins copied bytewise from project/experiments/kemeny-workload-proof. Runtime Python3.12.11 and SymPy1.14.0 asserted.

Independent full100x100 adjacency/transition fundamental inverses at k28 and33 give K=267769/2698 and1015397/10234. Their exact gap is201710/6902833>0. Separate characteristic-polynomial reconstruction of the equitable quotient at each integer k2..90 gives unique maximizing k28. This uses no source expression for computing K; the corrected source expression is compared afterward. result.json retains all89 values, full-matrix checks and code hash. Author manifest entries were freshly hash-checked and all matched.

## Mathematical specification

The quotient is valid because each cell has constant degree and constant total transition probability to every other cell. Zero-sum vectors within clique C have eigenvalue -1/(b+k-1); within the remaining independent cell and B they have eigenvalue0. Dimensions are3+(k-1)+(a-k-1)+(b-1)=a+b for k<a. At k=a the empty cell is removed, giving2+(a-1)+(b-1)=a+b. This accounts for all modes, including singleton residual cells and the endpoint. Reversibility ensures the eigenvalue interpretation; connectivity gives precisely one stationary mode. For charpoly det(zI-(I-Q)), the reciprocal sum of nonzero roots is minus its z² coefficient divided by its z coefficient, valid for both quotient dimensions used. The base K90,10 has spectrum1,-1,0 with multiplicities1,1,98 and K=197/2.

The algebra (4a-3k)(b+k)-2(2ab+k(k-1))=k(4a-3b+2-5k) proves the corrected denominator b+k. All denominators are positive. The source's strict sign threshold survives this denominator correction; this audit does not certify other rewritten non-strict inequalities. Pair/clique choices within a part are isomorphic, so enumerating clique sizes suffices for the claimed90-part example. No arbitrary graph or all-parameter optimum is claimed.

## Primary source entailment

Retained primary raw-02.json SHA5453711dd4089f86e3cd2c78d428368a59db2c0ef9761a9c61f17a9e604bdd8e identifies https://arxiv.org/html/2608.04150v1, Breen/deBlieck/Vander Meulen, displayed date24August2026. Theorem4.7 proof lines491-492 has n-ell+k in the unsimplified expression and n+k-1 in the next expression. Example4.8 lines508-510 explicitly asserts largest increase at33 for K90,10. The retained source therefore entails the specific discrepancy claim. Our exact28-versus33 comparison directly falsifies that maximum assertion under its stated simple-random-walk convention. No inference is made about author intent or figure-generation process, later corrected versions, or publication priority.

## Implementation alignment

Author code independently inspected: exact Fraction quotient principal minors, correct omitted modes, k90 branch, all89 comparisons. Our evaluator instead uses quotient characteristic coefficients plus two full fundamental-matrix inverses. Both align with the claimed finite scope. The author result's unique printed-formula maximizer33 is secondary diagnostic evidence, not needed for falsification. The reviewed proposal SHA is d206fe6ec171cd49cdd6d5b108cee7abd4aaf7f73eae870bbb1ca0d452cca130; result SHA3bf79f4e7a36fc9e3fffd55f3097fb9ba618dfb5331e4a9a3b4bcbbb19901643. No correction requested within this scope.
