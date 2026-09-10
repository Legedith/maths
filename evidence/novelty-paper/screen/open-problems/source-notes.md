# Typed source assessment, 10 September 2026

## B1: explicit question, poor selection candidate

PRIMARY: Jang, Kempton, Kim, Knudson, Madras and Song, *Kemeny's constant and enumerating Braess edges in trees*, arXiv:2309.02977v1, 6 September 2023, https://arxiv.org/pdf/2309.02977. PDF p16, lines2351-2365 in retained raw-04: an unnumbered question asks for tree families whose number B of nonedges that strictly increase Kemeny's constant is asymptotic to a prescribed divergent function f(n)<=n²/2. The immediately following Theorem4.10 constructs a common-center mixture of b1 length-one and b2 length-two arms, with B=binomial(b1,2). Earlier methods are cut-vertex moment and spanning-forest identities, Proposition2.1 and Theorem4.1.

INFERENCE, not independently audited: this stated asymptotic question appears to follow routinely from that same theorem. The order is n=1+b1+2b2. Choose b1 of parity n-1 nearest sqrt(2f(n)), capped at n-3, and b2=(n-1-b1)/2. For sufficiently large n, b1>=1 and b2>=1; b1 differs from sqrt(2f(n)) by O(1), including the cap because sqrt(2f(n))<=n. Since f diverges, binomial(b1,2)/f(n) tends to one. This makes the literal asymptotic question unsuitable as a substantive new result without a stronger, genuinely separate formulation. No claim is made that the authors intended the question to remain unresolved after their theorem.

## B2: exact edge-change extremizers already studied

PRIMARY: Kirkland, Li, McAlister and Zhang, *Edge Addition and the Change in Kemeny's Constant*, arXiv:2306.04005, https://arxiv.org/pdf/2306.04005, retained raw-03. Search metadata identifies 2025 journal publication. The paper studies extremal change on adding an edge to trees. The retained find calls found no occurrence of 'conject' or 'open'. This is not a theorem-level absence certificate and supplies no selected open problem.

## B3: latest derivative paper is a different perturbation convention

PRIMARY: Bini, Meini and Poloni, *The derivative of Kemeny's constant as a centrality measure in undirected graphs*, IMA Journal of Numerical Analysis, DOI10.1093/imanum/drag050, published18 August2026, https://academic.oup.com/imajna/advance-article/doi/10.1093/imanum/drag050/8762920. Retained raw-06 lines260-274, Section3 equations3.1-3.2, decrease edge weight while adding compensating endpoint loops, preserving degrees. Thus positivity of this directional centrality cannot be transferred to ordinary edge insertion/removal. No explicit conjecture was identified by the retained targeted text checks; this is a method-boundary warning, not an open-problem candidate.

## B4: completion lead not selected

PRIMARY: Kirkland, *Completion Problems and Sparsity for Kemeny's Constant*, arXiv:2308.10259, https://arxiv.org/pdf/2308.10259, retained raw-06. No numbered conjecture was identified in the bounded checks. General stochastic completion is a different feasible set and is not proposed as a new edge-design result.

## Search scope and decision

Six search queries and six primary opens were used; two opens failed404. Raw structured requests/results are retained except call02, whose visible failures are explicitly transcribed in failure-02.md. Four followup queries returned substantial unrelated rank-aggregation noise; those hits support no scientific claim here. No evaluator or external code was run. No later resolution was identified for B1, but the local inference above makes that negative search immaterial. Branch B recommends NO candidate for promotion: the only precisely located question appears routine from the adjacent published construction. Root's independent Hu-Kirkland direction is not duplicated. A distinct source audit is still required for any use of these notes.
