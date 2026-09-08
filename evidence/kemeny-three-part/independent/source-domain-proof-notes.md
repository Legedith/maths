# Independent source, domain, and sign audit

## Primary-source identity and conventions

The inspected manuscript is Yuxiang Hu and Steve Kirkland, *Complete Multipartite Graphs and Braess Edges* (2019), local SHA256 `c896d263c6bec602274f84a29c30492f99e85e3bde654f3e61dcf5aa10718c77`, retrieved from the URL frozen in `contract-v1.md`.

- PDF page 2 defines the Markov-chain transition matrix and writes Kemeny's constant as `kappa(T)=sum_{i=2}^n 1/(1-lambda_i)`. Its random-target expression is `kappa+1` because the manuscript's diagonal mean-first-passage entries are return times. Replacing the diagonal by zero hitting times subtracts exactly one, so the contract's zero-hitting-time Kemeny constant is the manuscript's `kappa`.
- PDF page 3 specializes to the simple random walk `T=D^{-1}A` on a connected undirected graph. It defines a Braess edge by strict increase and a non-Braess edge by weak nonincrease.
- PDF page 10 treats a complete multipartite graph with independent sets `S_1,...,S_r` of sizes `k_1,...,k_r`, assumes `k_1>=2`, adds the edge between vertices 1 and 2 of `S_1`, and defines `n=sum_j k_j`, `alpha_j=n-k_j`, and `gamma=sum_j k_j alpha_j`. Case 1 is `k_1>=3`.
- PDF page 12, Theorem 3.2.3, gives exactly the brace transcribed in the frozen contract. The total number of parts is the page-10 `r`; for `K_{a,b,c} join K_p` it is therefore `3+p`, because the `p` dominating vertices are `p` singleton parts.

The visual comparison found no missing factor, index, summation endpoint, or sign in the frozen transcription. Theorem 3.2.5 is the separate `k_1=2` case and does not apply. The malformed displayed equation (13) on page 19 is not used.

## Exact reduction of Theorem 3.2.3

Fix one minimum-size non-singleton part and relabel it as the first part. Write its size as `x` and the other two sizes as `y,z`, so `x>=3` and `y,z>=x`. With `p>=1`, put

```
n = x+y+z+p,
alpha = n-x = y+z+p,
gamma = x(n-x)+y(n-y)+z(n-z)+p(n-1),
S0 = y(n-y)+z(n-z)+p(n-1) = gamma-x*alpha,
S1 = y(n-y)^2+z(n-z)^2+p(n-1)^2.
```

The factors `p(n-1)` and `p(n-1)^2` are the sums of the `p` separate singleton contributions. Distributing the source's outer `1/gamma` gives the six-term brace

```
B = -gamma/(2*alpha)
    +(x-2)/2
    +S1/(gamma*n)
    +(x-2)*S0/(2*gamma)
    +(n-2)*S0^2/(2*gamma*n*alpha)
    +(gamma-alpha)/(alpha*(alpha+2)).
```

Every cleared denominator is positive on the full domain:

```
n >= 10,
alpha = y+z+p >= 7,
alpha+2 >= 9,
gamma = 2xy+2xz+2yz+2p(x+y+z)+p(p-1) > 0.
```

Hence `D=2*alpha*n*(alpha+2)*gamma>0`, and the theorem's prefactor `2/(gamma+2)` is positive. Clearing the six terms separately yields

```
M = -gamma*n*(alpha+2)*gamma
    +(x-2)*alpha*n*(alpha+2)*gamma
    +2*S1*alpha*(alpha+2)
    +(x-2)*S0*alpha*n*(alpha+2)
    +(n-2)*S0^2*(alpha+2)
    +2*(gamma-alpha)*n*gamma,
```

with the exact identity `D*B=M`.

## Domain and positive polynomial

Set

```
A=x-3,  u=y-x,  v=z-x,  P=p-1.
```

For the relabelled minimum-part domain these are nonnegative integers. Conversely, every `A,u,v,P>=0` gives `x=3+A`, `y=x+u`, `z=x+v`, `p=1+P`, so the substitution is exhaustive and reversible.

The frozen independent evaluator `scripts/independent_polynomial_audit.py` was written before opening the selected checker. It reconstructs the source sum directly, checks all six denominator complements against `D`, and expands both the 124-term certificate and the proposal's eleven grouped terms. Its canonical result proves the polynomial identity

```
M = -Q(A,u,v,P),
```

where all 124 coefficients of `Q` are strictly positive: minimum 2, maximum 73722, and constant coefficient 60948. Thus `Q>=60948>0` on the entire nonnegative orthant, so `M<0`, `B<0`, and

```
kappa(G+e)-kappa(G) = 2*B/(gamma+2) < 0.
```

## Every tied minimum and every within-part edge

The preceding relabelling can be performed separately for each part whose size equals `min{a,b,c}`. For each such choice the two remaining sizes are at least `x`, so the same exhaustive substitution applies. This covers one, two, or three tied minimum parts without assuming a unique minimum.

Every pair of distinct vertices in a multipartite part is a missing edge. Because `x>=3`, such pairs exist and Theorem 3.2.3 is in its `k_1>=3` case. The symmetric group on the vertices of a fixed part acts transitively on its unordered pairs while preserving the base graph. Therefore adding any two within-part pairs gives isomorphic graphs, and Kemeny's constant is invariant under the corresponding permutation similarity. The strict sign holds for every missing edge in every minimum-size non-singleton part.

The exact matrix diagnostic independently checked all 30 within-minimum-part pairs in four finite graphs, including two-way and three-way minimum ties. Those examples validate the graph/source bridge but are not used for the universal conclusion.

## Closest-source comparison and priority boundary

Independent visual inspection of Hu--Kirkland pages 13--19 confirms the following boundaries.

- Theorem 3.3.1 proves a minimum-part strict decrease when there are no singleton parts (`p=0`), outside the audited domain.
- Theorem 3.4.2 handles minimum part size 2 for `p>=1`.
- Theorem 3.4.3 guarantees a non-Braess edge only for sufficiently large `p` when all non-singleton sizes are at least 3.
- Corollary 3.4.5 covers the equal-size family with at least three equal non-singleton parts for every `p>=1`; its displayed proof is strictly negative. Thus the `a=b=c` subfamily is already published.
- Conjecture 3.4.7 leaves the `r>=3` existential non-Braess conclusion conjectural. Here its `r` counts non-singleton parts, unlike Section 3.2's total part count.

The closest located later source is Breen, deBlieck, and Vander Meulen, *Kemeny's constant and Braess cliques in graphs* (2026), local SHA256 `69037b759b6c7948fba80c77c4e50823c4d051658ff93eedf1113d7c21a3d660`. Its Theorem 3.5 on PDF pages 11--12 supplies a general accessibility-index formula for turning an independent twin set into a clique; pages 16--17 specialize it to complete bipartite graphs. These passages do not state or prove the all-`p` unequal three-non-singleton-part sign theorem.

Accordingly, the exact update formula is published, the equal-size subfamily is published, and the independently verified contribution is the remaining all-`p` sign analysis for three non-singleton parts, with the stronger location and strictness conclusion. The corrected prior-art packet is only a bounded source lead because its investigator also authored proposal branch 2. No global publication-priority, novelty, current-openness, four-or-more-part, all-edge-sign, or practical-impact claim is certified here.

## Checker boundary

The preserved selected checker and certificate are mathematically aligned with the proof and reject coefficient corruption, a wrong exponent count, duplicate exponents, a missing schema tag, and a wrong variable order. The checker nevertheless accepts certificates whose `source_formula` is missing, whose target identity is reversed, whose written domain says `x=2+A`, or which add an unknown top-level field. It therefore checks the core polynomial mathematics but is not a complete provenance-schema validator. The independent evaluator closes those source/domain checks for the exact frozen certificate hash; this limitation must remain visible if the checker is distributed as a standalone validator.
