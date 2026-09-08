# Postfailure one-edge design: candidate proof and elimination ledger

Author-derived discovery, not independently certified. Scope: G=K_(a,b,c) join K1 with 3<=a<=b,c; H=G-uh, u in A and h the hub. All graphs are connected simple undirected unweighted, K is stationary-target simple-random-walk hitting time with zero initial-target time. Known quotient and exact polynomial methods are reused; novelty and practical impact unresolved.

## Strongest surviving claim
Restoring uh uniquely minimizes K(H+e) among every missing edge e of H. In addition, adding an untouched pair in A strictly beats adding a pair incident with u in A. This does not establish the untouched pair as the best alternative if restoration is forbidden; that comparison with B/C was not symbolically tested.

The only missing-edge orbits of H are: uh; u-v with v in A minus u; v-w with distinct v,w in A minus u; a pair in B; a pair in C. All exist since a,b,c>=3. Part-preserving permutations fixing u,h are transitive within each listed orbit; merging equal-size B/C is harmless. Thus strict comparison of all four alternate representatives with restoration is sufficient for a unique edge optimum.

## Exact derivation
Known equitable/twin quotient reduction is attributed to Breen et al., arXiv:2608.04150v1 section 3, and Hu--Kirkland's earlier approach. batch2.py builds neighbor-count matrices R from cell sizes and original part labels, removes uh except for restoration, and inserts the target edge. The four six-cell partitions are:

restore and uv: (u,v,A-rest,B,C,h), sizes (1,1,a-2,b,c,1).
untouched_A: (u,{v,w},A-rest,B,C,h), sizes (1,2,a-3,b,c,1).
B: (u,A-rest,{s,t},B-rest,C,h), sizes (1,a-1,2,b-2,c,1).
C follows from the B expression by simultaneous b/c interchange.

Initially R_ij=size_j for different original parts and zero otherwise. Removal sets R_uh=R_hu=0. The uv insertion sets R_uv=R_vu=1. For a merged inserted pair, its diagonal entry is 1. D=diag(R*1), L=D-R and Q=D^-1 R. All cell degrees are positive on the domain.

With positive cell sizes, cell-constant vectors form an invariant subspace of the full transition matrix. Independent twin-cell zero-sum subspaces have eigenvalue zero. The merged adjacent pair has one zero-sum eigenvalue -1/d_pair. These invariant spaces span the full vertex space. Hence for restore/uv:
K=n-6+K(Q).
For untouched_A/B/C:
K=n-6+K(Q)-1/(d_pair+1).
Here K(Q)=sum_(i=2)^6 1/(1-lambda_i(Q)). The correction replaces one otherwise unit contribution by d_pair/(d_pair+1).

Let F(t)=det(L+tD). Its linear and quadratic coefficients q1,q2 satisfy K(Q)=q2/q1 by factorization det(D)*t*product_(i=2)^6(t+1-lambda_i). batch2.py computes each coefficient by the finite principal-minor formula:
q_k=sum_(|S|=k) product_(i in S)d_i * det L[S^c,S^c], k=1,2.
No floating-point arithmetic is used.

Boundary a=3 for untouched_A: the A-rest cell has size zero. Its column in Q is zero and it has zero diagonal. Removing its row/column leaves the actual five-cell quotient; the six-cell matrix has that quotient's eigenvalues plus an extra zero. Thus K(Q6)=K(Q5)+1, and n-6+K(Q6)-1/(d_pair+1) equals n-5+K(Q5)-1/(d_pair+1), exactly the physical five-cell formula. This handles the boundary without interpreting zero vertices as an actual cell. All other quotient partitions have positive sizes throughout the domain.

## Full-domain coefficient evidence
For each difference below, batch2.py uses exact cancellation/factorization then substitutes a=3+x,b=3+x+y,c=3+x+z. This substitution covers exactly 3<=a<=b,c for integer x,y,z>=0. The numerator and denominator are expanded as integer polynomials; every stored nonzero coefficient is positive, and both constants are positive. Complete exponent/coefficient lists and original rational differences are in batch2.json. Therefore each difference is strictly positive on the entire domain.

Comparison | numerator monomials | minimum numerator coefficient | numerator constant | minimum denominator coefficient | denominator constant
uv minus restore | 30 | 2 | 3316 | 2 | 357120
untouched_A minus restore | 48 | 2 | 20412 | 2 | 2449440
B minus restore | 53 | 2 | 21672 | 2 | 2449440
C minus restore | 53 | 2 | 21672 | 2 | 2449440
uv minus untouched_A | 84 | 2 | 115668 | 2 | 121492224

These are differences between final graph K values. Subtracting the common K(H) does not change their signs. This establishes the claimed ordering provided the construction and stored exact identities pass independent review. It does not itself prove restoration decreases K(H); the minimum comparison stands regardless. Combining with the separately audited-or-pending uv strict-decrease theorem would give that sign as a separate consequence.

## Elimination ledger and exact witnesses
H1 restoration always best: survived all five exact diagnostic tuples; full-domain coefficient proof candidate obtained.
H2 untouched-A always beats uv: survived all five; full-domain coefficient proof candidate obtained.
H3 uv best among non-restoration insertions: REJECTED. At (3,3,3), deltas relative to H are restore=-71/2520, untouched_A=-5/252, B=C=-263/13608, uv=-787/41664. Untouched_A beats uv by 17/17856. Thus a safe insertion incident to the damaged vertex is strictly dominated even when restoration is excluded.
Additional recorded warning: in (3,3,7), C insertion has positive Delta=2287/524160, while restoration and the other listed insertions have negative Delta. No blanket all-part improvement claim is supported.

## Execution history and limits
Batch1 frozen tuples: (3,3,3),(3,4,5),(4,4,6),(3,3,7),(4,5,5). Direct full adjacency matrices and exact fundamental matrix compute all five deltas. Original run finished calculations but failed serializing SymPy BooleanTrue for H2; original code, argv, stderr and rc=1 retained. Only converting that value to Python bool was changed; identical-range retry succeeded rc=0. batch1.json stores every result. This retry is a retained serialization correction, not a new hypothesis or range.
Batch2 frozen five symbolic comparisons: exactly those above. rc=0. Two predefined tuples (3,3,3),(3,4,5) compare all four alternate-minus-restore expressions with batch1 exact matrix values and agree. No extra grid, symbolic retry, or third hypothesis batch. Raw argv/stdout/stderr/rc files retained for both batches. uv runs isolated SymPy 1.14.0 environments with D-drive cache. No benchmark performed.

Typed claims: numerical diagnostics -> batch1.json plus retry logs; source/method -> cited quotient source and batch2.py; exact coefficient claims -> batch2.json complete dictionaries plus batch2 logs; universal conclusion -> orbit coverage, quotient spectrum argument including zero-cell boundary, polynomial sign proof. Independent verifier must reconstruct source-to-quotient and exact comparisons before promotion; this author does not self-certify.

Practical interpretation is conditional: with one unit-cost edge intervention and restoration allowed, this idealized failure model favors repair over every alternate new edge. If restoration is prohibited or costs differ, the current optimum theorem is not the relevant objective. No measured network/workload benefit or global publication originality has been shown.
