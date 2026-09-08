# Network repair with uniform sources and uneven destination demand

For the stated random-walk model, we can find a best missing link and its
conductance by comparing finitely many exact candidates. A source is chosen
uniformly; independently, the destination mixes a uniform draw with a fixed
focus vertex. Uncertainty concerns the mixture weight. The method keeps all
tied link locations and the option to do nothing.

This is a mathematical algorithm with an audited rational-input implementation.
It is not yet an established publication-priority or practical-gain result.

| Model | What is established |
| --- | --- |
| Source and destination iid from one mixture | The earlier [iid study](kemeny-strength-minimax.md) gives strict convexity and a finite optimum. |
| Uniform source; independent mixed destination | This study gives a finite optimum and unique strength per link, even when curvature is negative. |
| Fixed source at the middle of the weighted path below | The best value can be approached forever without a finite optimizing strength. |

## Exact objective and finite characterization

Let m be the total undirected conductance, d the weighted-degree vector and
M=L^+. First-step equations with H_jj=0 give

    H_ij=(Md)_i-(Md)_j+2m(M_jj-M_ij).

Uniform source averaging gives F_q=2mM_qq-(Md)_q. Hence

    U_theta=(1-theta)*2m*tr(M)/n + theta*F_q.

This degree correction matters: directed hitting times are not generally
symmetric, even on our undirected graph. For an allowed absent edge i,j,
write v=e_i-e_j, w=e_i+e_j, z=Mv, r=v^TMv and D=1+rt. Then

    M_t=M-t*z*z^T/D,  d_t=d+t*w,
    U_theta(t)=(a0+a1*t+a2*t^2)/D.

For T=tr(M), s=z^Tz, the uniform coefficients are

    u0=2mT/n, u1=2(T+mrT-ms)/n, u2=2(rT-s)/n.

Set F0=2mM_qq-(Md)_q, F1=2M_qq-(Mw)_q,
P1=z_q(z^Td-2mz_q), P2=z_q(z^Tw-2z_q). The focus coefficients are
f0=F0, f1=rF0+F1+P1, f2=rF1+P2, and ak=(1-theta)uk+theta*fk.
Every insertion retains actual volume m+t.

The assumptions are a fixed finite connected loopless undirected weighted graph,
n>=3, a nonempty finite allowed absent-edge set and 0<=l<=theta<=h<1. The
positive uniform component and the accepted PSD rank argument give a positive
linear lower bound as t grows. Endpoint oracles are positive and attained.
Every fixed action's objective is a positive affine function of theta, so its
worst relative regret against the same continuum oracle occurs at l or h.

For one endpoint quotient,

    U'=(a1-ra0+2a2*t+ra2*t^2)/(1+rt)^2,
    U''=2(a2-ra1+r^2*a0)/(1+rt)^3.

Coercivity gives a2/r>0. With nonpositive curvature the derivative is at least
its positive limiting value, so the objective strictly increases. With positive
curvature it is strictly convex. Both cases are strictly quasiconvex: an interior
point between distinct strengths has value below the larger endpoint value.
The maximum of the two normalized endpoint functions preserves this property,
giving one minimizing strength per link. Different link locations may tie.

Compute each endpoint oracle from zero and positive stationary roots. Then for
each link compare zero, positive stationary roots for either endpoint, and
positive roots of

    O_h*(a0_l+a1_l*t+a2_l*t^2)-O_l*(a0_h+a1_h*t+a2_h*t^2)=0.

The equation is at most quadratic. Identical branches reduce to one function;
constant/linear/nonreal/repeated/zero/negative and duplicate-root cases are
handled explicitly. At an interior optimum an active branch is stationary or
the branches coincide. Coercivity excludes an optimum at infinity. The full
[author proof and distinct audit](../evidence/kemeny-source-target/README.md)
state the analytic steps that finite computations do not formalize in Lean.

## Counterexamples that define the boundary

On path0--1--2 with conductances1,2, add edge02 of strength t and use focus1.
With uniform sources,

    U_theta=[(4+8theta)t^2+(24+3theta)t+36-24theta]/(27t+18).

At theta99/100, U''=-199/[225(3t+2)^3]<0. The function still increases and
selects no action. Theta98/101 gives an affine increasing objective. Thus a
strict-convexity proof cannot be carried over from the iid model.
On [0,99/100] the exact robust strength instead is

    t=(-10617+3*sqrt(24368421))/13934,

the positive balance of the endpoint regrets. The full certificate retains its
exact enclosing rational bounds and all competitors.

Now change the source to FIXED vertex1 while keeping the mixed destination.
First-step equations instead give

    H10=5(t+2)/(3t+2), H12=4(t+1)/(3t+2),
    U_theta=(1-theta)*(1+8/[3(3t+2)]).

For theta<1 this strictly decreases toward the positive value1-theta, never
attaining it at finite t. It is even strictly convex: convexity does not supply
attainment. If an oracle is defined by this infimum, regret is8/[3(3t+2)] with
unattained infimum zero. An oracle required to be an attained minimum does not
exist in this changed model. A prescribed finite cap0<=t<=Tmax restores
attainment and selects Tmax in this example. This is a mathematical remedy,
without a claimed physical calibration of capacity or cost.

## Connection to computer-science prior work

Martinez, Cinus, Bonchi and Vitria study directed recommendation-walk reachability,
rewiring and probability optimization, using rank-one greedy updates and SLSQP.
These are substantial related objectives and methods, not newly claimed here.
[Publisher DOI](https://doi.org/10.1145/3744658).

We also inspected two files at author revision
20f35f4c28da3f40049f5b10caa64a3371905cb8. On the SAME valid transition matrix P,
the selected code's score is G=U_0/(n-1)=C/n, where C conditions on different
source and target. It uses P=.985X+.015J/n under feasible row constraints,
introducing teleportation and self transitions, with directed probability
changes across multiple rows. Those interventions differ from our one symmetric
conductance insertion. A consistent positive rescaling preserves rankings and
regret; changing the chain or action set does not. This is a static alignment,
not a paper-error finding or optimizer/empirical validation. [Pinned objective](https://github.com/alexmartinezmiguel/reachability/blob/20f35f4c28da3f40049f5b10caa64a3371905cb8/compute_SLSQP_rewirings-reweighting.py).

The [source notes and audits](../evidence/kemeny-source-target/README.md) retain
exact locators, primary requests and hashes. Indexed publisher text is
distinguished from the failed direct/full-PDF access. Code/data reuse terms
remain unverified in the inspected material. No complete-literature absence,
novelty or reproduced empirical improvement follows.

## Use, validation and human contribution

The separate [solver README](../experiments/kemeny-source-target-proof/README.md)
gives the API and exact replay command. Its checker performs30direct grounded
first-step comparisons at strengths0,1/2,2 over four declared cases,3symbolic
identities,7abstract root cases and7invalid inputs. Worker, distinct reviewer
and root outputs are byte-identical. A symmetric cycle checks location ties;
all zero-strength labels are one no action. Fresh-output rejection preserves
existing bytes. The theorem review transparently retains an initial missing-
SymPy setup failure and its authorized correction, followed by one successful
mathematical replay. The fixed-source counterexample has a separate analytic
audit; it is not falsely described as a second machine replay.

The exact comparison implementation can be inconclusive or expensive. Use an
external process-tree-aware cap; no general runtime or polynomial-time guarantee
is offered. Sources are uniform in the API. Multiple interventions, arbitrary
source laws, adaptive/randomized decisions and costs are excluded.

Useful human work is now specific: assess the exact characterization against
prior literature, validate source/destination and routing assumptions with a
real workload, and define common feasible actions before benchmarking against
the recommender work. Mathematical validity is audited; publication priority
and practical value are still unresolved. The local [evidence bundle](../.codex/evidence/runs/kemeny-source-target-v1/bundle.json)
and [contract](kemeny-source-target-contract.md) are separate from actual hosted
CI for the eventual pushed commit.
