# Exact Robust Link Design for Random-Walk Search

## Abstract

We give a finite exact characterization of a robust link-design problem on a weighted undirected graph. A request starts at a uniformly chosen vertex and independently chooses a destination from a mixture of uniform demand and demand concentrated at one focus vertex. The mixture weight is unknown within a prescribed interval. Before it is known, the designer chooses one missing edge and any nonnegative conductance, including zero for no action. Performance is expected discrete-time hitting time; the objective is worst relative regret against an oracle with the same available interventions. We prove that the worst workload occurs at an interval endpoint and that each edge has a unique optimal conductance, found among boundary, stationary and quadratic balance candidates. Strict convexity is unnecessary and can fail. An audited rational-input implementation retains exact certificates and all location ties. An analytic supplement classifies the exceptional fixed-source graphs where finite attainment fails and extends the characterization to infimum oracles. These are mathematical results, not measured improvements in a deployed search system.

## 1. Problem and main result

Let (G) be a finite connected loopless undirected graph with (n\ge3), positive edge conductances and a finite nonempty set \(\mathcal E\) of allowed missing edges. Parallel conductances, if supplied, are combined. An action is \((e,t)\), where \(e\in\mathcal E\) and \(0\le t<\infty\) is the conductance inserted at that edge. All labels with \(t=0\) describe the same physical no-action graph.

The walk chooses its next neighbor in proportion to incident conductance. Write \(H_{ab}\) for its expected number of steps from source \(a\) to target \(b\), with \(H_{aa}=0\). The source is uniform. Independently, the target follows

\[
\nu_\theta=(1-\theta)\operatorname{Uniform}+\theta\delta_q,
\qquad 0\le l\le\theta\le h<1.
\]

The graph, focus \(q\), interval and allowed edges are fixed before the action. Let \(U_e(t,\theta)\) be the resulting expected hitting time. Define the same-action-set oracle and regret by

\[
O(\theta)=\min_{e\in\mathcal E,\,t\ge0}U_e(t,\theta),
\qquad R_e(t)=\max_{\theta\in[l,h]}
\left(\frac{U_e(t,\theta)}{O(\theta)}-1\right).
\]

**Main theorem.** Under these assumptions, the oracle is positive and attained. For every action, worst regret occurs at \(l\) or \(h\). Each allowed edge has exactly one minimizing strength. Its strength belongs to a finite list consisting of zero, positive stationary strengths for either endpoint, and positive roots of an equation of degree at most two equating normalized endpoint objectives. Comparing these per-edge minima gives every globally optimal location, including ties.

This is a deterministic decision made before the workload is known. It does not allow several insertions, adaptive choices, randomization or a separate monetary cost. The source and target conventions are essential: expected hitting time can change when either distribution changes.

## 2. Directed hitting times and exact coefficients

Let \(L\) be the weighted Laplacian, \(M=L^+\), \(d\) the weighted-degree vector and \(m\) total undirected conductance. First-step equations for a fixed target \(b\) give

\[
LH_{\cdot b}=d-2m e_b.
\]

Solving with \(H_{bb}=0\) yields

\[
H_{ab}=(Md)_a-(Md)_b+2m(M_{bb}-M_{ab}).
\]

Uniform source averaging therefore gives \(F_b=2mM_{bb}-(Md)_b\), and

\[
U_\theta=(1-\theta)\frac{2m}{n}\operatorname{tr}M
+\theta F_q.
\]

The degree correction cannot be omitted: directed hitting times need not be symmetric even though the graph is undirected.

For an inserted pair \(i,j\), set \(v=e_i-e_j\), \(w=e_i+e_j\), \(z=Mv\), \(r=v^TMv>0\), and \(D=1+rt\). The inverse update on the subspace perpendicular to the constant vector is

\[
M_t=M-\frac{tzz^T}{D},\qquad d_t=d+tw.
\]

Consequently

\[
U_e(t,\theta)=\frac{a_0(\theta)+a_1(\theta)t+a_2(\theta)t^2}{1+rt},
\]

where the coefficients are affine in \(\theta\). For explicit reconstruction, write \(T=\operatorname{tr}M\), \(s=z^Tz\). The uniform-target coefficients are

\[
(u_0,u_1,u_2)=\frac2n(mT,\ T+mrT-ms,\ rT-s).
\]

Set \(F_0=2mM_{qq}-(Md)_q\), \(F_1=2M_{qq}-(Mw)_q\), \(P_1=z_q(z^Td-2mz_q)\), and \(P_2=z_q(z^Tw-2z_q)\). The focused coefficients are \((f_0,f_1,f_2)=(F_0,rF_0+F_1+P_1,rF_1+P_2)\); finally \(a_k=(1-\theta)u_k+\theta f_k\). Actual conductance volume is always \(m+t\).

## 3. Proof of the finite characterization

**Positivity and attainment.** On the nonconstant subspace, \(rM-Mvv^TM\) is positive semidefinite of rank \(n-2\). Hence \(B=rT-s>0\). Nonnegative focused hitting times and the uniform target component imply

\[
U_e(t,\theta)\ge(1-h)\frac{2(m+t)B}{nr}>0.
\]

Finitely many allowed edges give a common coercive bound. Continuity supplies finite oracle minima. In particular, each endpoint quotient has positive asymptotic slope \(a_2/r\).

**Endpoint reduction.** For fixed actions \(x,y\), \(U_x(\theta)/U_y(\theta)\) is a ratio of positive affine functions, so it is monotone or constant on the interval. Moreover, \(U_x/O=\sup_y U_x/U_y\). Exchanging this supremum with the maximum over the two endpoints proves the asserted reduction. The comparator need not be the same oracle action at both endpoints.

**Uniqueness without convexity.** For an endpoint quotient \(f(t)=(a_0+a_1t+a_2t^2)/(1+rt)\),

\[
f'(t)=\frac{a_1-ra_0+2a_2t+ra_2t^2}{(1+rt)^2},\qquad
f''(t)=\frac{2(a_2-ra_1+r^2a_0)}{(1+rt)^3}.
\]

If curvature is nonpositive, the derivative is at least its positive limiting value, so \(f\) strictly increases. Otherwise it is strictly convex. Both cases are strictly quasiconvex: at an interior point between distinct strengths, the value is below the larger endpoint value. Positive normalization preserves this property. A finite maximum also preserves it: choose a branch active at the interior point and apply its strict inequality. Thus the robust objective has a unique minimizing strength on each edge.

**Candidates.** First compute endpoint oracles from zero and positive roots of the displayed derivative numerator. Then include the positive roots of

\[
O_h(a_{0,l}+a_{1,l}t+a_{2,l}t^2)
-O_l(a_{0,h}+a_{1,h}t+a_{2,h}t^2)=0.
\]

An interior minimum either has a locally active stationary branch or equal active branches. Identical branches reduce to one function; nonzero constant, linear, repeated-root and nonreal-root cases are handled explicitly. Zero is already a boundary candidate. Algebraically equal strengths are deduplicated. Coercivity excludes infinity, completing the proof.

## 4. Exact weighted-path example

Take the path \(0-1-2\) with conductances \(1,2\), focus \(1\), and insert the missing edge \(0,2\). Direct first-step equations give

\[
U_\theta(t)=\frac{(4+8\theta)t^2+(24+3\theta)t+36-24\theta}{27t+18}.
\]

On \([0,99/100]\), the certified robust optimum is the positive balance strength

\[
\boxed{t^*=\frac{-10617+3\sqrt{24368421}}{13934}}.
\]

The existing certificate records its exact rational enclosing bounds and every competing candidate. This value is not selected from a sampled strength grid.

At the collapsed workload \(\theta=99/100\), however,

\[
U''_\theta(t)=-\frac{199}{225(3t+2)^3}<0.
\]

The objective remains strictly increasing, so no action is optimal. At \(98/101\) it is affine and increasing. These cases demonstrate why the uniqueness proof uses strict quasiconvexity rather than importing a strict-convexity theorem from the different iid-demand model.

## 5. Implementation and reproducibility

The [separate rational-input solver](experiments/kemeny-source-target-proof/README.md) implements this model. It returns endpoint oracles, all candidate classifications, actual objectives and conductance volumes, unique strength per edge, and all global location ties. Zero-strength labels collapse once. Exact algebraic comparisons use certified rational intervals and exact identities; unresolved comparisons raise an explicit inconclusive error instead of returning an approximate winner.

From the repository root, choose a fresh output:

```sh
uv run --project experiments/kemeny-source-target-proof --frozen python experiments/kemeny-source-target-proof/verify_source_target.py --output source-target-replay.json
```

Python 3.12.11 and SymPy 1.14.0 are pinned. The [evidence guide](evidence/kemeny-source-target/README.md) records independent audits and canonical artifacts. Validation includes 30 direct grounded first-step comparisons at strengths \(0,1/2,2\), three symbolic identities, seven abstract root cases and seven malformed inputs. A symmetric four-cycle checks location ties. Existing-output rejection protects prior certificates. Worker, independent reviewer and integration outputs agree byte-for-byte.

These checks support the implementation; the universal proof also needs the analytic arguments above. Neither the main result nor the supplement is claimed to be formalized in Lean. Symbolic comparison may be expensive, so the documented process-tree-aware logger supplies an external time limit. No all-input termination or polynomial-time guarantee is asserted.

## 6. Analytic supplement: arbitrary sources and nonattainment

The following separately audited results extend the mathematics, not the implemented uniform-source API. Supplemental public evidence links are pending: **[SUPPLEMENT-GROWTH]**, **[SUPPLEMENT-CLASSIFICATION]**, **[SUPPLEMENT-INFIMUM]**.

Fix a source \(a\). When the target \(b\) lies outside an inserted pair \(i,j\), the coefficient of linear growth in \(H_{ab}(t)\) is positive exactly when \(a\ne b\) and \(a\) can reach the pair without visiting \(b\). It is zero for a target in the pair or a self target. Grounding \(b\), let \(K=L_b^{-1}\), \(v=e_i-e_j\), and \(w=e_i+e_j\). The coefficient is

\[
[Cw]_a=2C_{ai},\qquad C=K-\frac{Kvv^TK}{v^TKv}.
\]

The matrix \(C\) is the lifted Green matrix after identifying the pair. Its positive entries encode the stated target-avoiding connectivity; the factor two records both degree increments.

With a positive uniform target floor, zero averaged growth occurs precisely when the contracted underlying graph is a path with endpoints \(a\) and the merged pair. Equivalently, the original graph is a tail from \(a\) to a vertex \(w\), followed by two leaves \(i,j\) attached to \(w\). The tail may be empty. Parallel conductances created by contraction are combined. There is at most one exceptional source for a fixed pair, so any fixed source law supported on at least two vertices restores coercivity for every allowed edge.

For the exceptional fixed source, prong hitting times strictly decrease with strength and approach positive finite limits; other target times remain unchanged. Thus no finite strength attains the edge-ray infimum. This is not a contradiction of the uniform-source theorem. In the three-vertex example with source fixed at vertex \(1\),

\[
U_\theta(t)=(1-\theta)\left(1+\frac8{3(3t+2)}\right),
\]

whose infimum \(1-\theta\) is unattained.

For arbitrary fixed source laws, define the oracle by its **infimum**, preserving positive denominators. Endpoint reduction still holds. Coercive rays use the finite stationary/balance candidates; an exceptional ray contributes its limiting value, labelled infinity only as a certificate, never as a physical action. Compare all these values. The global infimum is attained exactly when a finite candidate ties the least value. A finite action may tie an exceptional limit; otherwise a uniquely winning limit means nonattainment. A fixed source has at most one exceptional pair. This characterization is algebraically effective for rational inputs, but arbitrary real probabilities require an appropriate exact representation. No new general-source implementation is claimed.

## 7. Related work and interpretation

Electrical-network methods provide established foundations. Palacios, Gomez and Del Rio give the conductance-weighted voltage identity in Theorem 2 and cutpoint, bridge and tree formulas in Corollaries 8–10 [1]. The growth supplement combines such ingredients with a limiting argument and separator classification; it is not presented as a novelty certificate.

Martinez and coauthors optimize directed recommendation-walk reachability through rewiring and probability adjustment [2]. Their objective is closely related, but their intervention set differs. Static inspection of a [pinned implementation](https://github.com/alexmartinezmiguel/reachability/blob/20f35f4c28da3f40049f5b10caa64a3371905cb8/compute_SLSQP_rewirings-reweighting.py) gives \(G=U_0/(n-1)=C/n\), where \(C\) averages over distinct source-target pairs. It also applies teleportation, \(P=0.985X+0.015J/n\), and changes directed probabilities across rows. A common positive rescaling preserves rankings and regret; a different transition matrix or action set does not.

Search and navigation systems motivate asking how link choices interact with uneven destination demand. The theorem supplies an exact answer for the specified walk and intervention model. It does not establish that real users walk this way, that conductance is a calibrated resource cost, or that a mathematical improvement produces deployment gains. Establishing those connections requires workload evidence and a common feasible set before empirical comparison. Publication priority and practical value remain separate questions.

The upper bound \(h<1\) ensures a positive uniform component throughout the workload interval. Removing that condition changes the proof obligations. Likewise, a finite conductance cap or an intervention cost defines a different optimization problem: a cap introduces an additional boundary candidate, while a cost requires its own objective and regularity analysis. These distinctions should be preserved when adapting the result to another search model.

## References

1. J. L. Palacios, E. Gomez and M. Del Rio. *Hitting Times of Walks on Graphs through Voltages*. Journal of Probability, article 852481, 2014. [Official full text](https://onlinelibrary.wiley.com/doi/pdf/10.1155/2014/852481).
2. A. Martinez, F. Cinus, F. Bonchi and J. Vitria. *Optimizing Reachability in Graph-Based Recommender Systems*. ACM Transactions on Intelligent Systems and Technology 16(4), article 93, 2025. [DOI](https://doi.org/10.1145/3744658).
3. [Main theorem, implementation and evidence](docs/kemeny-source-target.md); [repository research overview](docs/atlas-overview.md).
