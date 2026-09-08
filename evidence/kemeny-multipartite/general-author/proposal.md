# Candidate: all numbers of non-singleton parts

Status: author-derived universal proof candidate; NOT independently certified. Root must commission separate verification before promotion.

## Proposed theorem
For integers r>=3, p>=1, and q_1,...,q_r>=3, let G=K_{q_1,...,q_r} join K_p. Every missing edge in every minimum-size non-singleton part strictly decreases the simple-random-walk Kemeny constant (zero diagonal hitting-time convention).

## Source and exact numerator
The accepted package's Hu--Kirkland Theorem 3.2.3 formula applies to arbitrary complete multipartite graphs when selected size x>=3. The accepted three-part proposal and independent source-domain audit were read before use. Retain p singleton parts.

Select x=min q_i, let k=r-1, and write remaining sizes x+u_i, i=1,...,k, with u_i>=0. Set U=sum u_i, V=sum u_i^2, W=sum u_i^3. Then

n=(k+1)x+U+p,
a=n-x,
T2=(k+1)x^2+2xU+V+p,
T3=(k+1)x^3+3x^2 U+3xV+W+p,
g=n^2-T2,
S0=g-xa,
S1=n^3-2nT2+T3-xa^2.

Here T2 and T3 include every singleton. The corrected +p in T3 is essential.

The cited six-term formula gives Delta=2B/(g+2), with D B=M, D=2an(a+2)g, and

M=-g*n*(a+2)*g+(x-2)*a*n*(a+2)*g+2*S1*a*(a+2)
  +(x-2)*S0*a*n*(a+2)+(n-2)*S0^2*(a+2)+2*(g-a)*n*g.

All D and g+2 factors are positive on the theorem's domain. It suffices to show -M>0.

## Stable symmetric-polynomial certificate
Substitute x=3+A,k=2+R,p=1+P. Thus A,R,P>=0 covers all admitted sizes, part counts, and singleton counts. Expand Q=-M after the power-sum substitutions. Q has total degree at most five in gaps. This bound is visible from the aggregate expansion: Q is a sum C(U)+L(U)V-2(x-2)V^2-2(U+kx+p)(U+kx+p+2)W, where deg C<=5 and deg L<=2. aggregate.txt retains the original expansion with C requiring correction by -2p(U+kx+p)(U+kx+p+2); the other terms were unaffected by the original missing singleton cube.

For a gap monomial with support size s<=5, its coefficient in k variables equals its coefficient using five formal variables, with extra variables set to zero and k left as an independent scalar. This follows by restricting all variables outside that monomial's support to zero in the power-sum expression; no other variable can contribute to that monomial. Gap monomials of support >5 cannot occur because the total gap degree is at most five. When k<5 simply pad with zero gaps. Therefore coefficient positivity in five formal gap variables proves coefficient positivity for arbitrary k>=2.

The corrected exact expansion batch2.py produces certificate.json, all 1777 nonzero coefficients strictly positive in A,R,P,u1,...,u5, constant 60948. Equivalently symmetric-coefficients.json gives 18 coefficient polynomials indexed by gap exponent partitions; every displayed scalar coefficient is positive. The missing partition [5] has coefficient zero. For every k, Q equals the sum of these coefficient polynomials times the monomial symmetric polynomials m_lambda(u_1,...,u_k), with each distinct monomial counted once. Partitions longer than k contribute zero. Consequently Q>=60948>0 for nonnegative parameters. This gives Delta<0. Tied minima and all within-part pairs follow by relabelling and vertex-permutation symmetry exactly as in the accepted proof.

This is a symbolic full-domain argument, not an inference from the numerical sweep. The finite sweep is diagnostic only.

## Hypotheses and eliminations
H1 (minimum-edge rule for all r>=3) survives, with the above proof candidate.
H2 (extend to r=2) is refuted: q=(9,9),p=1, Delta=229/627000>0. Thus r>=3 is a sharp universal boundary under the specified sizes and p domain.
H3 (positive-coefficient gap expansion for all r>=3) survives via the stable five-variable argument.
The initial symbolic S1 expression omitted +p in T3; its outputs are INVALID and retained separately. The exact numerical batch1 formula explicitly included p*(n-1)^2 and is unaffected. The error was detected by comparing the constant to the accepted 60948, corrected without changing the declared domain, and rerun within batch2.

## Finite diagnostic range
Batch1 exhaustively evaluated sorted q_i in [3,9], p in [1,8], r in [2,7], with exact fractions. All 27,168 tuples with r>=3 had strict negative minimum-edge Delta. r=2 had 224 tuples and explicit positive examples. This does not establish the universal result.

## Prospective application and novelty boundary
For a network modeled exactly as a complete multipartite graph with a dominating clique, the proposed theorem gives a simple edge placement rule: add a link within a smallest non-singleton group to guarantee a decrease in mean stationary-target hitting time, independently of all group sizes. Selection requires only group sizes; no matrix inverse is needed.
Real impact would require evidence that this graph/walk model fits a use case, that stationary-target hitting time is the relevant cost, and that a feasible same-group link preserves the assumptions. No real-world performance claim is made.

The retained independent source audit identifies Hu--Kirkland Theorem 3.3.1 (p=0), Theorem 3.4.2 (minimum size 2), Theorem 3.4.3 (sufficiently large p), Corollary 3.4.5 (equal sizes), and Conjecture 3.4.7 (r>=3 existential conclusion). Conditional on primary-source rechecking, this candidate strengthens that conjectural existential conclusion to a strict minimum-edge rule for all r>=3. No fresh global literature search was undertaken by this branch; publication novelty/current openness remain unestablished.

## Independent verification requested
Re-derive arbitrary-r moments from the actual source; reconstruct M independently; verify stable coefficient argument for arbitrary gap counts; check all 18 coefficient polynomials or independently expand; validate at least the r=2 counterexample and an r>=6 diagnostic with the exact matrix evaluator; compare primary-source scope. Do not accept merely because this author's script passes.
