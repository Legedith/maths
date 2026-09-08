# Independent ranking review

Reviewer: separate GPT-6 Astra review branch; 2026-09-08. Scope frozen in freeze.md; own exact evaluator check.py was hashed before execution.

## Four gates
- Reproduction: PASS for selected mathematical claim. Independent symbolic subtraction of source-form brace has zero residual against candidate identity. Four exact matrix updates on the two frozen partitions agree. stdout.txt, stderr.txt, rc.txt and argv.json retain the invocation and results; rc=0. stderr includes uv no-project warning (PowerShell formats it as NativeCommandError despite successful native return).
- Specification compliance: PASS. Distinct parts x,y>=3, arbitrary other positive integer parts, connected complete multipartite graph, one missing edge, zero-diagonal hitting-time K. No comparison with an insertion in size 2. Diagnostics explicitly include another size-2 part and a singleton. Equal part sizes give equal B directly. If eligible parts are absent, selection is undefined; selection language should say when a missing edge exists.
- Source verification: PASS. Read pinned Hu--Kirkland page-marked text, Theorem 3.2.3 lines 699-714 and Remark 2 page 19 lines 1177-1224; compared independent source-domain-proof-notes.md. Source brace is -g/(2a)+[(x-2)g/2+sum_{j!=i}q_j a_j(a_j/n+(x-2)/2+(n-2)(g-xa)/(2na))]/g+(g-a)/(a(a+2)). Substituting sum q_j a_j=g-xa and sum q_j a_j^2=H-xa^2 yields precisely proposed B. This attribution supports the formula, not publication priority.
- Implementation alignment: PASS for the proposed formula, ranking proof, and operation-count claim checked here. Independent script reconstructs source brace, uses exact symbolic and matrix rational arithmetic, and does not rely on candidate checker or grid. Author's 3640-case and 37-coefficient historical claims were not rerun/certified in this bounded review; neither is needed for theorem.

## Positivity, independently resolved
Write a=n-x,b=n-y. Then a,b>=3; n-a-3=x-3>=0; n-b-3=y-3>=0; a+b-n=sum(other parts)>=0; g>0. Let C=(n-2)(a+b+2)-ab and L=a^2+b^2-ab+a+b+2(n-2). Exact gap C-L=a(n-a-3)+b(n-b-3)>=0. L>0 since a^2+b^2-ab=(a-b)^2+ab>0. The second displayed inequality has exact gap a+b-n>=0. Both summands of N are therefore strictly positive, and denominator n*a*b*(a+2)*(b+2)>0. Since Delta difference has additional positive factor 2/(g+2), sign(Delta_x-Delta_y)=sign(x-y), with tied sizes handled directly. No concrete mathematical defect found.

## Published comparison and practical scope
Remark 2 concerns K_{k1,k2} join K_p and establishes ordering of cleared sign polynomials f(k1,k2), f(k2,k1). These are multiplied by part-dependent positive factors; their ordering alone does not entail ordering of actual updates. The candidate supplies that separate rational difference identity in a larger domain. This is a bounded source distinction only; novelty remains unresolved.

For an already supplied partition list, one pass computes n, sum q^2, sum q^3, and smallest eligible size. Then g=n^2-sum q^2 and H=n^3-2n sum q^2+sum q^3; evaluating B takes constant further arithmetic operations. Thus O(r) is arithmetic/comparison operation count, not graph recognition, bit complexity, measured runtime, or producing every pair of endpoints. All-part global optimality needs no size-2 parts and at least one missing edge. In graphs containing size-2 parts the theorem optimizes only among parts of size >=3. No guaranteed decrease is supplied by ranking alone.

## Typed provenance
citation: source brace and Remark 2 -> pinned text locators above and source-domain-proof-notes.md.
numerical: symbolic residual zero, four exact matrix matches -> check.py, pre-run-hash.json, argv.json, stdout.txt, stderr.txt, rc.txt.
methodological: exact rational independent evaluator -> check.py and argv.json; known-partition O(r) -> displayed aggregate reconstruction and proposal.md.
conclusion: universal ranking -> source brace, zero symbolic residual, full-domain positivity argument above. Source/proposal/evaluator hashes retained in hashes.json.
