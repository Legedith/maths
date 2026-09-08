# Safe and optimal edge insertion in complete multipartite networks

Research note, 8 September 2026. Both the improvement theorem and the ranking
theorem below have separate independent mathematical reviews. Their exact
algebra is machine checked. They are not Lean formalizations. The results go
beyond the closest published cases inspected; publication priority and
real-world benefit remain unestablished.

## Results

Let K(G) denote Kemeny's constant of the simple random walk on a finite,
connected, simple, undirected, unweighted graph. We use transition matrix
T=D^(-1)A and stationary-target hitting time with zero hitting time when the
initial vertex is the target.

**Improvement theorem.** Let r>=3, p>=1, and q_1,...,q_r>=3 be integers. In
G=K_(q_1,...,q_r) join K_p, adding any missing edge within any minimum-size
non-singleton part strictly decreases K(G). This includes every tie for the
minimum size and every pair in each minimum part.

**Ranking theorem.** In any connected complete multipartite graph, compare
two parts of sizes x,y>=3. If Delta_x and Delta_y are the changes caused by
adding one edge inside the respective parts, then

```text
sign(Delta_x - Delta_y) = sign(x - y).
```

Other parts may have any positive integer sizes. This theorem makes no
comparison with an insertion in a part of size two.

**Combined consequence.** For the graph family in the improvement theorem,
choosing any pair in any smallest non-singleton part is globally optimal
among all single missing-edge insertions, and it strictly improves K.

## Why it might be useful

If a network and its workload really fit this model, its group sizes suffice
to choose a best new link. With the partition supplied, finding a smallest
group uses a linear number of comparisons in the number of groups. It avoids
evaluating every vertex pair. This is a mathematical decision guarantee, not
a measured runtime improvement, a graph-recognition algorithm, or a guarantee
for weighted, sparse, congested, or approximately multipartite networks.

The first insertion changes the graph class. Repeating the rule greedily is
not justified by these theorems. Small experiments on damaged networks suggest
further robustness questions, but neither deletion robustness nor arbitrary
multi-edge insertion is established here.

## Sourced update formula

Use Hu and Kirkland, *Complete multipartite graphs and Braess edges*,
[Theorem 3.2.3, PDF page 12](https://mspace.lib.umanitoba.ca/server/api/core/bitstreams/04a4246d-2b67-4e4c-9c4b-60f0c5417031/content)
(2019, [DOI](https://doi.org/10.1016/j.laa.2019.05.035)). Select a part of
size x>=3 and set

```text
n = sum_j q_j, a = n-x, g = sum_j q_j(n-q_j),
S0 = sum_(j != selected) q_j(n-q_j) = g-xa,
S1 = sum_(j != selected) q_j(n-q_j)^2.

Delta_x = 2 B(x)/(g+2),
B(x) = -g/(2a) + (x-2)/2 + S1/(gn)
       + (x-2)S0/(2g) + (n-2)S0^2/(2gna)
       + (g-a)/(a(a+2)).
```

Every singleton is included in these sums. The general update identity is
prior work. The sign and ranking arguments below are the contributions
checked in this project.

## Proof of improvement

Relabel any minimum part as x. Write the other k=r-1 non-singleton sizes
as x+u_i, with u_i>=0, and retain all p singleton parts. Let
U=sum u_i, V=sum u_i^2, W=sum u_i^3. The moments of the other parts are

```text
t1 = kx + U + p,
t2 = kx^2 + 2xU + V + p,
t3 = kx^3 + 3x^2 U + 3xV + W + p.
```

In particular every singleton contributes one to the cubic moment. Then
n=x+t1, a=t1, S0=nt1-t2, S1=n^2 t1-2nt2+t3, and g=xa+S0.
Multiplying the six terms in B by the positive denominator
D=2an(a+2)g gives M=D B. Here n>=10, a>=7, and
g=sum_j q_j(n-q_j)>0. Thus the sign of Delta is the sign of M.

Substitute x=3+A, k=2+R, p=1+P. These parameters are nonnegative and,
with exactly k gaps, cover the whole relabelled domain. Put Q=-M.
The retained exact certificate expands Q using five formal gaps and finds
1,777 positive integer coefficients, a positive constant 60,948, symmetry
in all gaps, and total gap degree at most five.

Five formal gaps suffice even when the actual number is different. For any
number m of formal gaps, define F_m by the same expression in U,V,W, keeping
k as an independent scalar. Setting one gap to zero gives F_(m-1) with k
unchanged. Consequently a monomial's coefficient does not change when unused
variables are added or removed. Symmetry allows any support to occupy the
first positions. Degree at most five bounds each monomial's support by five.
The five-gap calculation therefore supplies every possible coefficient for
every m; for m<5, pad with zero gaps. Finally choose m=k.

All coefficients remain nonnegative for A,R,P>=0 and the constant remains
positive. Hence Q>=60948>0, M<0, and Delta<0. Each tied minimum may be
relabelled separately. Within-part vertex permutations make all unordered
pairs equivalent, proving the full edge quantifier.

The [independent improvement audit](../evidence/kemeny-multipartite/general-review/report.md)
reconstructs the source expression separately and justifies this finite
support argument. Finite graph tests are diagnostics, not the proof of the
universal quantifier.

## Proof of ranking

Fix two eligible part sizes x,y and write a=n-x, b=n-y, and
H=sum_j q_j(n-q_j)^2. In the source formula use S1=H-xa^2.
For x!=y, exact subtraction yields

```text
(B(x)-B(y))/(x-y) = N / [n a b (a+2)(b+2)],
N = g[(n-2)(a+b+2)-ab] + ab[2(a+2)(b+2)-n].
```

Because x,y>=3 and the parts are distinct, a,b>=3,
n>=a+3, n>=b+3, and n<=a+b. The first bracket is positive: its difference
from a^2+b^2-ab+a+b+2(n-2) is
a(n-a-3)+b(n-b-3)>=0, while a^2+b^2-ab=(a-b)^2+ab>0.
The second bracket is at least 2ab+3a+3b+8>0; their difference is a+b-n>=0.
Both the numerator and denominator are positive. Multiplication by 2/(g+2)
preserves the sign. Equal sizes give equal B directly.

The [independent ranking audit](../evidence/kemeny-multipartite/ranking-review/review.md)
checks the rational identity, inequalities, and scope using separate code.

## Existing work, boundaries, and reproduction

Hu and Kirkland already establish the no-dominating-vertex case, a
minimum-size-two case, a sufficiently-large-p result, and the equal-size
subfamily. Their Conjecture 3.4.7 contains the r>=3 existence claim strengthened
here. Their two-part comparison orders cleared sign numerators; the ranking
proof above compares actual changes. The r=2 extension is false in general:
K_(9,9) join K_1 has Delta=229/627000>0, independently reproduced.

The [bounded literature comparison](../evidence/kemeny-multipartite/source-comparison.json)
also records later related work. It does not prove global novelty or that the
historical conjecture remained open when this note was written.

Run the dependency-free polynomial checker from the repository root, using
uv and a fresh output path:

```text
uv run --project experiments/kemeny-multipartite-proof --frozen python experiments/kemeny-multipartite-proof/verify_certificate.py --certificate experiments/kemeny-multipartite-proof/certificate.json --output work/kemeny-multipartite-proof/check.json
uv run --project experiments/kemeny-multipartite-proof --frozen python experiments/kemeny-multipartite-proof/verify_ranking.py --output work/kemeny-multipartite-proof/ranking.json
```

Python 3.12.11 is pinned. The checker verifies the exact frozen certificate,
reconstructs the six source terms with integer arithmetic, and checks their
denominators, symmetry, degree, and coefficients. The source interpretation,
arbitrary-variable argument, and graph quantifiers additionally require the
mathematical proof and independent audit. The second command checks the
ranking identity and positivity decompositions by exact cross multiplication.
The ranking audit's separate symbolic evaluator is also retained with its
original command and outputs.

The [release evidence](../.codex/evidence/runs/kemeny-network-design-v1/bundle.json)
records the promoted files and checks. Source papers stay external; recorded
source hashes and locators identify the reviewed versions.
