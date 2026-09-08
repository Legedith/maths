# Explorer 3 proposal: the smallest part always supplies a strictly non-Braess edge

## Scope and claim

Let `p >= 1` and `a,b,c >= 3` be integers, and let

`G = K_{a,b,c} join K_p`.

Choose a smallest non-singleton part and call its size `x`; call the other two sizes `y,z`. Then adding any missing edge within the part of size `x` strictly decreases Kemeny's constant:

`K(G+e)-K(G) < 0`.

This proves the three-non-singleton-part branch requested by the frozen contract, and is stronger than the required existence of an edge with difference at most zero. The claim is only for `p >= 1` and three non-singleton parts of sizes at least 3. It does not establish a result for more non-singleton parts or a current publication-novelty claim.

## Source dependency

The sole mathematical source dependency is Hu and Kirkland (2019), *Complete multipartite graphs and Braess edges*, PDF page 12, Theorem 3.2.3, Case 1. Its Section 3.2 notation is on PDF page 10 and Conjecture 3.4.7 is on PDF page 19. The pinned PDF SHA-256 is `c896d263c6bec602274f84a29c30492f99e85e3bde654f3e61dcf5aa10718c77`.

The derivation uses the displayed Theorem 3.2.3 formula, not the malformed expanded equation (13), and does not use Theorem 3.2.5. The theorem's total number of parts is `R=3+p`; every singleton is retained in every sum.

## Reduction of the sourced formula

Permuting part labels is a graph isomorphism, so relabel a minimum of `a,b,c` as `x`. Then `x <= y,z`. Put

`q=(x,y,z,1,...,1)` with `p` singleton entries,

`n=x+y+z+p`, and `alpha=n-x=y+z+p`.

The source quantity `gamma=sum_j q_j(n-q_j)` becomes

`gamma=n^2-(x^2+y^2+z^2+p)`

`=2xy+2xz+2yz+2p(x+y+z)+p(p-1)`.

For the sum over all parts other than the selected part, define

`S0=y(n-y)+z(n-z)+p(n-1)=gamma-x*alpha`,

`S1=y(n-y)^2+z(n-z)^2+p(n-1)^2`.

The `p(n-1)` and `p(n-1)^2` terms are the combined contributions of all `p` singleton parts. Collecting the terms in Theorem 3.2.3 gives

```
B = -gamma/(2*alpha)
    +(x-2)/2
    +S1/(gamma*n)
    +(x-2)*S0/(2*gamma)
    +(n-2)*S0^2/(2*gamma*n*alpha)
    +(gamma-alpha)/(alpha*(alpha+2)),
```

where the desired difference is

`Delta = 2*B/(gamma+2)`.

All sign-clearing factors are strictly positive. Indeed, `n >= 10`, `alpha >= 7`, `alpha+2 >= 9`, and the displayed positive decomposition of `gamma` has `2xy > 0`. Therefore

`D=2*alpha*n*(alpha+2)*gamma > 0`

and `gamma+2 > 0`.

Direct denominator clearing, without cancellation, gives `D*B=M`, where

```
M = -gamma*n*(alpha+2)*gamma
    +(x-2)*alpha*n*(alpha+2)*gamma
    +2*S1*alpha*(alpha+2)
    +(x-2)*S0*alpha*n*(alpha+2)
    +(n-2)*S0^2*(alpha+2)
    +2*(gamma-alpha)*n*gamma.
```

## Positive-coefficient certificate

Set

`A=x-3`, `u=y-x`, `v=z-x`, and `P=p-1`.

This substitution covers the whole domain after the minimum part is relabeled: `A,u,v,P` are nonnegative integers, and conversely `x=3+A`, `y=x+u`, `z=x+v`, `p=1+P` produces every such ordered choice.

Expanding the preceding expression gives the exact identity

`M=-Q(A,u,v,P)`.

For `i>j`, write `s_ij=u^i v^j+u^j v^i`, and for `i=j`, write `s_ii=u^i v^i`. Then the 124-monomial polynomial has the shorter grouped form

```
Q = 6*s_41
  + 6*(2*A+P+7)*s_40
  + 18*s_32
  + 4*(19*A+9*P+70)*s_31
  + 2*(2*A+P+7)*(20*A+9*P+77)*s_30
  + 12*(10*A+5*P+39)*s_22
  + 4*F21*s_21
  + 2*F20*s_20
  + 4*F11*s_11
  + 2*F10*s_10
  + 2*F00,
```

with

```
F21 = 62*A^2 + 61*A*P + 486*A + 15*P^2 + 238*P + 940,

F20 = 84*A^3 + 123*A^2*P + 993*A^2 + 61*A*P^2
    + 970*A*P + 3861*A + 10*P^3 + 238*P^2 + 1881*P + 4947,

F11 = 76*A^3 + 115*A^2*P + 947*A^2 + 60*A*P^2
    + 953*A*P + 3833*A + 10*P^3 + 240*P^2 + 1908*P + 5062,

F10 = 64*A^4 + 132*A^3*P + 1138*A^3 + 110*A^2*P^2
    + 1760*A^2*P + 7248*A^2 + 40*A*P^3 + 937*A*P^2
    + 7409*A*P + 19850*A + 5*P^4 + 160*P^3 + 1899*P^2
    + 10005*P + 19871,

F00 = 12*A^5 + 36*A^4*P + 372*A^4 + 52*A^3*P^2
    + 850*A^3*P + 3750*A^3 + 35*A^2*P^3 + 789*A^2*P^2
    + 6217*A^2*P + 17127*A^2 + 10*A*P^4 + 307*A*P^3
    + 3531*A*P^2 + 18387*A*P + 36861*A + P^5 + 40*P^4
    + 630*P^3 + 4918*P^2 + 19249*P + 30474.
```

Every displayed summand of `Q` is nonnegative, and `2*F00 >= 60948`. Hence `Q>0`, so `M<0`, `B<0`, and finally `Delta<0` because `2/(gamma+2)>0`.

An edge exists within the selected part because `x>=3`. All choices within that part are equivalent under permutations of its vertices. Thus the chosen smallest part supplies a strictly non-Braess missing edge for every admitted parameter tuple.

## Exact reusable verification

`proof/verify_coefficient_certificate.py` is a dependency-free Python checker. It independently reconstructs the six sourced summands after denominator clearing using a sparse integer-polynomial implementation. It verifies:

- the domain variable order and certificate schema;
- the positive decomposition of `gamma`;
- exact equality between the reconstructed `-M`, the 124-term coefficient certificate, and the grouped display above;
- strict positivity of every expanded coefficient and the positive constant term;
- the reported coefficient extrema and term count.

The portable canonical check is:

```
uv run --no-project --python 3.12 python proof/verify_coefficient_certificate.py \
  --certificate proof/coefficient-certificate.json \
  --output proof/portable-certificate-check.json
```

The retained portable run exited zero. Its stdout is in `logs/certificate/attempt-portable-verify-01.stdout.bin`, and the structured result is `proof/portable-certificate-check.json`.

As a finite diagnostic only, `proof/exact_matrix_sanity.py` independently computed Kemeny's constant as `trace((I-P+1*pi)^-1)-1` with `fractions.Fraction`. For the five tuples `(3,3,3,1)`, `(3,3,6,1)`, `(3,5,8,2)`, `(4,7,5,4)`, and `(9,3,4,1)`, all 15 exact matrix differences matched Theorem 3.2.3, and every sampled minimum-part type was strictly negative. This does not establish the universal quantifier; the polynomial identity does.

## Retained failed and abandoned probes

- `symbolic-01` failed before its coefficient summary because SymPy Boolean objects were passed to Python `sum`; `symbolic-02` corrected only that probe and completed.
- `symmetric-01` failed because a simultaneous substitution left `a` in coefficients; `symmetric-02` corrected the substitution order.
- Replacing the two gaps by their elementary symmetric sum and product produced eight coefficients of the wrong sign, so that representation was not used as a positivity certificate.
- An equal-size baseline plus a monotonic-change expansion gave a valid but much larger 610-term negative-coefficient numerator. Weighted-sum alternatives were also larger. They were abandoned in favor of the direct minimum-part certificate.
- The exploratory grid over ordered sizes 3 through 10 and `p` from 1 through 8 found only sign patterns `---` and `--+`, with no all-positive tuple. It was used only to choose a symbolic route.
- A pairwise symbolic probe found that the theorem brace is increasing with selected part size, with a positive factored quotient. That observation is not needed by this proof and is not asserted as a separately certified theorem here.

## Limits and next independent gate

This branch authored the derivation and checker, so it does not self-certify the final mathematical gate. An independent reviewer should compare the reconstructed six-term expression against the actual PDF display, run the stdlib checker from a clean Python 3.12 environment, inspect the grouped identity, and if desired reproduce a subset with an independently written exact matrix method. A later primary-literature review is still required before describing this as new; absence from the frozen source packet is not novelty evidence.
