# Independent exact method

For a connected graph, let `M = I - D^-1 A`. Its eigenvalues are
`0, mu_2, ..., mu_n`, with zero simple. Write

`p(x) = det(xI-M) = x q(x)`.

If `q_0` is the constant coefficient of `q` and `q_1` is its coefficient
of `x`, then

`q_0 = (-1)^(n-1) product_i mu_i`

and

`q_1 = (-1)^(n-2) sum_j product_(i != j) mu_i`.

Consequently,

`-q_1/q_0 = sum_i 1/mu_i = K(G)`.

The evaluator computes the descending coefficients of `p` with the exact
Faddeev-LeVerrier recurrence. Starting with `B_0=I`, for `k=1,...,n`,

`c_k = -trace(M B_(k-1))/k`,

`B_k = M B_(k-1) + c_k I`.

This yields

`p(x) = x^n + c_1 x^(n-1) + ... + c_n`.

It verifies `c_n=0` and `c_(n-1)!=0` for every graph state, then returns
`-c_(n-2)/c_(n-1)`. All matrix entries and coefficients use the standard
library's `fractions.Fraction`; no floating-point value is constructed.

The graph6 decoder consumes the six-bit payload in graph6 order
`(0,1),(0,2),(1,2),(0,3),...`, while the internal graph mask uses a
separate lexicographic edge order. Input completeness is checked by comparing
the actual union of every representative's full vertex-permutation orbit with
an independently generated set of every connected labelled graph mask.
