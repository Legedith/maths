# Exact counterexample to the clique-size numerical example

Author triage, requiring independent audit. This identifies a displayed formula and numerical-example discrepancy in arXiv:2608.04150v1, not a new central network-design theorem or a completed novelty goal. No author contact or shared changes.

## Primary statement compared

Root's retained novelty-multipartite-work/raw-02.json contains primary HTML returns from https://arxiv.org/html/2608.04150v1. Theorem 3.5 line 343 has final denominator r+k. In Theorem 4.7 the first equality at line 491 substitutes r=n-ell, so its last denominator is n-ell+k. The next displayed simplification, line 492, instead has n+k-1. Example 4.8 lines 508-510 states that K90,10 has its largest increase at clique order 33. No new source opens were used here.

Write a=ell, b=n-ell and D=2ab+k(k-1). Direct algebra in Theorem 3.5 gives

    Delta = (k-1)(4a-3k)/(2D) - (k-1)/(b+k)
          = k(k-1)(4a-3b+2-5k)/(2D(b+k)).

The numerator expansion uses (4a-3k)(b+k)-2D=k(4a-3b+2-5k). Thus b+k is the correct denominator in that simplification. Replacing it by n+k-1 changes the magnitude when a!=1. Both denominators are positive on the present domain, so this discrepancy alone does not refute the strict sign threshold in Theorem 4.7. No separate assessment of its non-strict rewritten inequalities is made here.

## Independent full-spectrum calculation

For K_a,b with a clique on k vertices of the a-part, partition into clique C, remaining a-part A0, and B. For k<a the transition quotient is

    Q = [[(k-1)/(b+k-1), 0, b/(b+k-1)],
         [0,                 0,           1],
         [k/a,          (a-k)/a,           0]].

Functions constant on each cell form an invariant three-dimensional subspace. On zero-sum differences inside C the transition eigenvalue is -1/(b+k-1), multiplicity k-1; inside A0 and B it is zero, multiplicities a-k-1 and b-1. These subspaces give the full dimension a+b and therefore account for every eigenmode. The chain is reversible, so the quotient eigenvalues are real and include the single stationary eigenvalue 1. Kemeny's constant is the sum of 1/(1-lambda) over the remaining modes.

Let M=I-Q. Its two nonzero eigenvalues have sum trace(M) and product equal to the sum of its principal 2x2 minors. Their reciprocal sum is trace(M) divided by that minor sum. Adding (k-1)(b+k-1)/(b+k)+(a-k-1)+(b-1) gives exact K, independently of Theorem 3.5. At k=a the empty A0 cell is removed: Q is the 2x2 matrix with rows ((k-1)/(b+k-1),b/(b+k-1)) and (1,0), whose nonstationary reciprocal contribution is 1/trace(I-Q). Only clique and B difference modes remain. No empty-cell eigenmode is invented.

## Finite exact certificate

The frozen evaluator fixes a=90,b=10 and computes every integer 2<=k<=90 (89 choices). Each quotient value matches the unsimplified Theorem 3.5 specialization and the corrected formula above. All 89 disagree with the printed n+k-1 simplification. The exact unique maximum is

    k=28: Delta=1008/1349, K=267769/2698.
    k=33: Delta=3674/5117, K=1015397/10234.
    Delta(28)-Delta(33)=201710/6902833 > 0.

The displayed erroneous formula, evaluated over the same 89 choices, has unique maximizer 33. This explains the numerical agreement between that expression and the stated example, without inferring how the authors generated their figure. result.json retains every quotient, omitted-mode contribution, total K, all three formula values, and exact maxima. The positive 28-versus-33 gap alone falsifies the example's maximum assertion; exhaustive finite comparison additionally establishes the unique maximum 28 for its specified K90,10 family.

## Execution and limits

plan.md was frozen first. One Fraction-only evaluator, Python3.12.11 in a new D venv, uv outer and child, preflighted process-tree-aware logger; cap60, rc0, no timeout, elapsed0.155128s. stderr59bytes is uv's warning that --no-project was supplied when no project was found; preserved, not hidden as empty. Outer invocation emitted the same warning. No second evaluator or graph extension. A later PowerShell display attempt failed because K and k keys collide in default ConvertFrom-Json; reading with -AsHashtable succeeded. This was an output-inspection issue, not an evaluator rerun or changed result.

The code uses only standard-library exact arithmetic and no third-party source implementation. Full primary returns remain in their frozen local root packet and are hash-pinned, not copied publicly. This finite source-error certificate requires a distinct mathematical/source audit before any public correction statement. It does not establish broader priority, physical benefit, or a nontrivial novel central theorem.
