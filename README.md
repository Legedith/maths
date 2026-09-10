# Optimal Edge Insertion and a Multipartite Braess Conjecture

*Mathematics Atlas project · Research note · 10 September 2026*

[Read the paper](https://legedith.github.io/maths/) · [Exact certificate](experiments/kemeny-multipartite-proof/certificate.json) · [Proof and evidence](evidence/novelty-paper/README.md)

## Abstract

Adding a link can increase the average search time of a random walk. We prove
that this cannot happen for a link placed within a smallest non-singleton part
of $K_{q_1,\ldots,q_r}\vee K_p$, when $r\ge3$, $p\ge1$, and every $q_i\ge3$.
The result resolves the $r\ge3$ assertion of Hu and Kirkland's Conjecture 3.4.7
and strengthens its existence claim to an explicit choice of edge. We also
prove that single-edge changes in Kemeny's constant are strictly ordered by
part size, for comparisons between parts of size at least three. Together,
these results identify every optimal single-edge location in the stated family.
The universal sign proof has an exact certificate of 1,777 positive integer
coefficients; a finite-support argument extends it to arbitrarily many parts.
Independent algebraic reconstruction, integer-arithmetic checkers and raw
verification records accompany the proofs.

## 1. Problem and contribution

Consider a simple random walk: at each step, choose a neighboring vertex with
equal probability. Kemeny's constant measures the expected time to reach a
target sampled from the stationary distribution. When an edge is added, both
the walk and that target distribution change. Consequently, a denser graph
need not have a smaller constant.

A complete multipartite graph has groups with no internal edges and all
possible edges between different groups. The join with $K_p$ adds $p$ mutually
adjacent vertices connected to every group. These are also singleton parts of
the multipartite graph. The design question is where to place one missing edge
to minimize the resulting Kemeny constant.

Hu and Kirkland's [2019 paper](https://doi.org/10.1016/j.laa.2019.05.035)
provides the general edge-update identity and several special cases.
Conjecture 3.4.7, on page 19 of the
[institutional manuscript](https://mspace.lib.umanitoba.ca/server/api/core/bitstreams/04a4246d-2b67-4e4c-9c4b-60f0c5417031/content),
asserts, in particular, that graphs in our $r\ge3$ family cannot have every
missing edge increase the constant. Our first theorem proves a stronger,
constructive statement. The second compares the actual changes between parts.
The source identity is an ingredient; these sign and ordering results are the
contribution studied here.

## 2. Definitions and theorems

All graphs in the main results are finite, connected, simple, undirected and
unweighted. Let $T=D^{-1}A$ be the transition matrix and
$\pi_v=d_v/(2m)$ its stationary distribution. Write $H_{uv}$ for the mean
first hitting time, with $H_{uu}=0$. We use

$$K(G)=\sum_v\pi_v H_{uv}.$$

This value is independent of the starting vertex $u$. For a missing edge $e$,
define $\Delta_e=K(G+e)-K(G)$. An improving edge has $\Delta_e<0$.
Following the strict convention in the 2019 source, a Braess graph has
$\Delta_e>0$ for every missing edge. Zero is not positive.

**Theorem 1 (minimum-part improvement).** Let $r\ge3$, $p\ge1$, and
$q_1,\ldots,q_r\ge3$ be integers. For
$G=K_{q_1,\ldots,q_r}\vee K_p$, every missing edge in every smallest
non-singleton part satisfies $\Delta_e<0$.

**Theorem 2 (strict part-size ranking).** In any connected complete multipartite
graph, let $\Delta_x$ and $\Delta_y$ be the changes for edges inserted within
two parts of sizes $x,y\ge3$. Then

$$\operatorname{sign}(\Delta_x-\Delta_y)=\operatorname{sign}(x-y).$$

Other parts may have any positive integer sizes. This theorem does not compare
an insertion inside a part of size two.

**Corollary 3 (optimal insertion and conjecture).** In Theorem 1's family,
the optimal missing edges are exactly the pairs within smallest non-singleton
parts. Every such insertion improves $K$. In particular, the graph is not a
Braess graph, proving every $r\ge3$, $p\ge1$ case of Conjecture 3.4.7.

All cross-part edges already exist, and singleton parts have no internal
pairs. Theorems 1 and 2 therefore exhaust the admissible locations, including
all ties. The source's two-part case is treated in its Remark 2. Our claim
about the conjecture explicitly concerns the $r\ge3$ assertion; it does not
reproduce the malformed separator in its printed equation (13).

## 3. Exact update and proof of Theorem 1

Choose a part of size $x\ge3$. In this section $(q_j)$ denotes the full part
list $(q_1,\ldots,q_r,1,\ldots,1)$, including every singleton in the sums:

$$n=\sum_j q_j,\quad a=n-x,\quad g=\sum_j q_j(n-q_j),$$
$$S_0=g-xa,\qquad S_1=\sum_{j\ne\mathrm{selected}}q_j(n-q_j)^2.$$

Theorem 3.2.3 of Hu and Kirkland, manuscript page 12, gives

$$\Delta_x=\frac{2B(x)}{g+2},$$
$$B(x)=-\frac{g}{2a}+\frac{x-2}{2}+\frac{S_1}{gn}
+\frac{(x-2)S_0}{2g}+\frac{(n-2)S_0^2}{2gna}
+\frac{g-a}{a(a+2)}.$$

Relabel a smallest part as $x$. Put $k=r-1$ and write the remaining
non-singleton sizes as $x+u_i$, where $u_i\ge0$. With
$U=\sum_i u_i$, $V=\sum_i u_i^2$, and $W=\sum_i u_i^3$, their moments,
including the $p$ singleton parts, are

$$t_1=kx+U+p,\quad t_2=kx^2+2xU+V+p,$$
$$t_3=kx^3+3x^2U+3xV+W+p.$$

Thus $n=x+t_1$, $a=t_1$, $S_0=nt_1-t_2$,
$S_1=n^2t_1-2nt_2+t_3$, and $g=xa+S_0$.
Every singleton contributes one to every moment, including the cubic moment.
The denominator $D_*=2an(a+2)g$ is positive throughout this domain.

Set $Q=-D_*B(x)$ and substitute
$x=3+A$, $k=2+R$, $p=1+P$.
Before introducing individual gaps, the independently reconstructed aggregate
has weighted degree at most five in $U,V,W$, with respective weights $1,2,3$.
This bounds total gap degree independently of how many gaps are substituted.
The [frozen certificate](experiments/kemeny-multipartite-proof/certificate.json)
expands this polynomial with five formal gap variables. It has 1,777 nonzero
integer coefficients, all positive, with constant coefficient 60,948. It is
symmetric in the gaps and has total gap degree at most five.

To justify arbitrarily many parts, regard $k$ as a scalar independent of the
number $s$ of formal gaps. Define $F_s$ using the same expression in $U,V,W$.
Setting a gap to zero gives $F_{s-1}$ without changing $k$. Hence a monomial's
coefficient remains unchanged when unused variables are added or removed.
Symmetry moves any support into the first positions. Since degree at most five
bounds the number of variables in any monomial by five, the five-gap expansion
supplies every possible coefficient for every $s$. For fewer gaps, pad with
zeros. Finally set $s=k$, the actual number of gaps.

All actual parameters $A,R,P,u_i$ are nonnegative. Therefore
$Q\ge60948>0$, and

$$\Delta_x=-\frac{2Q}{D_*(g+2)}<0.$$

Any tied smallest part can be selected. Permutations within a part make all
its unordered pairs equivalent, proving the full edge quantifier. The
[independent proof audit](evidence/kemeny-multipartite/general-review/report.md)
reconstructs the polynomial separately and checks the finite-support argument.
A finite sweep of graphs is not used to infer the universal assertion.

## 4. Proof of Theorem 2

For two eligible part sizes set $a=n-x$, $b=n-y$, and
$H=\sum_j q_j(n-q_j)^2$. Substitute $S_1=H-xa^2$ in the update formula.
For $x\ne y$, exact subtraction gives

$$\frac{B(x)-B(y)}{x-y}=\frac{N}{nab(a+2)(b+2)},$$
$$N=g[(n-2)(a+b+2)-ab]+ab[2(a+2)(b+2)-n].$$

Here $a,b\ge3$, $n\ge a+3$, $n\ge b+3$, and $n\le a+b$.
The first bracket is the sum of
$a^2+b^2-ab+a+b+2(n-2)>0$ and
$a(n-a-3)+b(n-b-3)\ge0$.
The second is $2ab+3a+3b+8+(a+b-n)>0$.
Thus the fraction is positive. Multiplication by $2/(g+2)$ preserves its
sign. Equal part sizes give equal changes directly. A
[separate ranking audit](evidence/kemeny-multipartite/ranking-review/review.md)
checks the identity, inequalities and ties.

## 5. Relation to prior work and scope of novelty

The central contribution is the constructive all-size resolution of the named
conjectural clause. Strict ranking of actual edge changes is a separately
proved strengthening; we do not claim its short algebraic identity alone as
a substantial novelty result.
The [source comparison](evidence/novelty-paper/sources/root/comparison-notes.md)
and [follow-up investigation](evidence/novelty-paper/sources/followups/source-notes.md)
record the inspected versions, closest statements and search limitations.
No earlier proof of these exact assertions was identified in that reviewed
literature. This supports a scoped contribution claim; it is not an exhaustive
certificate of priority across all published or unpublished mathematics.

The [additional overlap check](evidence/novelty-paper/sources/completion/source-notes.md)
compares stochastic-matrix completion and tree edge-addition results. Neither
inspected theorem supplies the coupled one-edge sign guarantee proved here.

Breen, deBlieck and Vander Meulen's
[2026 preprint](https://arxiv.org/html/2608.04150v1), Theorem 3.5, supplies a
general twin-clique update and Theorem 4.7 specializes to complete bipartite
graphs. Those formulas and the phenomenon that individual-edge signs can
differ from a clique's sign are already known. They are not our novelty claim.

The restriction $r\ge3$ matters. For $K_{9,9}\vee K_1$, adding an edge in
either non-singleton part instead gives $\Delta=229/627000>0$, as independently
reproduced in the improvement audit. The $p=0$ case belongs to the earlier
source's results; our positive-$p$ certificate does not silently cover it.

## 6. A separately verified correction

In arXiv:2608.04150v1, the displayed simplification in the proof of Theorem 4.7
has a denominator inconsistent with Theorem 3.5. For a clique of order $k$
inserted in the $a$-side of $K_{a,b}$, the corrected expression is

$$\Delta(k)=\frac{k(k-1)(4a-3b+2-5k)}
{2[2ab+k(k-1)](b+k)}.$$

The positive denominator correction preserves the strict sign threshold.
It changes Example 4.8's maximization: for $K_{90,10}$, the unique maximum
over all integers $2\le k\le90$ occurs at $k=28$, not the stated $33$.
The exact increases are $1008/1349$ and $3674/5117$, respectively, with gap
$201710/6902833>0$.

The [calculation and proof](evidence/novelty-paper/clique/author/proposal.md)
derive $K$ independently from an equitable transition quotient and all omitted
eigenmodes, including the empty-cell boundary. All 89 exact values are retained
and independently reproduced. This version-specific correction is subsidiary
to the conjecture result; it does not by itself establish a broad new theory.

## 7. Reproducibility

From the repository root, run the following commands with uv, using fresh
output paths if these files already exist. Python 3.12.11
is pinned; the two main checkers use integer arithmetic without a symbolic
algebra dependency.

```text
uv run --project experiments/kemeny-multipartite-proof --frozen python experiments/kemeny-multipartite-proof/verify_certificate.py --certificate experiments/kemeny-multipartite-proof/certificate.json --output work/kemeny-multipartite-proof/check.json
uv run --project experiments/kemeny-multipartite-proof --frozen python experiments/kemeny-multipartite-proof/verify_ranking.py --output work/kemeny-multipartite-proof/ranking.json
```

The [evidence index](evidence/novelty-paper/README.md) links canonical output,
commands, environment pins, raw logs, the correction evaluator and distinct
mathematical/source reviews. The
[typed release bundle](.codex/evidence/runs/novelty-investigation-v1/bundle.json)
binds the promoted claims to hashes and locators. These are computer-assisted
proofs with mathematical audits; they are not Lean formalizations or journal
peer review.

## 8. Interpretation and limitations

Given the partition, one scan of its sizes identifies an optimal new link.
This is an exact decision guarantee for an infinite graph family, and a
constructive answer to a published mathematical conjecture. It gives researchers
a proved case against which more general edge-design methods can be checked.

Measured improvements in communication networks, biology or physical transport
have not been established here. Those require a justified workload and network
model. Weighted, sparse, congested and approximately multipartite networks are
outside the theorem. After one insertion the graph generally leaves the class,
so repeatedly applying the rule is not justified.

The earlier source-target optimization study, atlas and learning tools remain
available in the [previous paper](docs/robust-link-design-paper.md) and
[project overview](docs/atlas-overview.md). The present paper concentrates on the
conjecture result and its proof.
