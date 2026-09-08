# Choosing a repair when traffic and link weights change

The best network repair can depend on where journeys start and finish. We prove
a complete decision rule for one damaged family of graphs, including every
positive prescribed strength of the new link. We also certify a finite set of
repairs against any change of up to 10% in one existing link, and give exact
counterexamples when several links change together.

In everyday terms: reconnecting a broken hub link can be best when enough
journeys involve the hub. With more evenly distributed journeys, a link within
one of the groups can be better. The theorem identifies the precise dividing
line. This offers a testable model for recommendation systems used in network
repair; it is not a measurement of a deployed network or a claim that real
traffic follows a random walk.

The mathematical arguments and portable checks have separate independent
audits in the [evidence packet](../evidence/kemeny-workload-robustness/README.md).
Publication originality remains unresolved. The general electrical,
inverse-update and optimization techniques are established prior work.

## Model and complete decision rule

Let

\[
 H=(K_{a,b,c}\vee K_1)-uh,\qquad 3\le a\le b\le c,
\]

where the part sizes are integers, the hub is \(h\), and the failed link joins
\(h\) to \(u\in A\). All remaining links have conductance 1. Add exactly one
missing link of a **common prescribed conductance** \(t>0\). The walk chooses
a neighbor in proportion to conductance. Source and destination are independent
with the same fixed law

\[
 p=(1-\theta)\operatorname{Uniform}+\theta\delta_h,
 \qquad 0\le\theta<1.
\]

Self-hitting time is zero. Minimize the expected number of walk steps
\(U_p=\sum_{i,j}p_i p_j H_{ij}\). This is a fixed workload objective; the
destination law is not changed to each candidate graph's stationary law.

Define

\[
\begin{aligned}
n&=a+b+c+1,&d&=n-a,&e&=n-c,\\
k&=\frac{(n-1)(d-1)}{nd},&
W&=\frac{n(n-1)+d(d-1)}{n^2d^2},\\
D_R&=k+t(1-k),&D_I&=d^2k+t(2dk+1).
\end{aligned}
\]

All displayed denominators are positive and \(0<k<1\).

**Equal parts, \(a=b=c\).** Set

\[
\tau_{=}(t)=
\frac{(a-2)(20a^3+8a^2t+4a^2-at-t)}
 {(2a+1)^2(3a+1)(4a^2+4at+4a+3t)}.
\]

This threshold is strictly between 0 and 1. Below it, precisely all pairs
\(\{u,v\}\), \(v\in A\setminus\{u\}\), are optimal. Above it, restoring
\(uh\) is uniquely optimal. At the threshold, the union of those sets is
optimal. The incident-pair choice is an entire tied set, not a unique edge.

**Unequal parts, \(c>a\).** Set

\[
 \tau_{\ne}(t)=\frac{2nkD_R}{e(e+2t)}-nW>0.
\]

Below this threshold, precisely all internal pairs in every largest part are
optimal. If \(b=c\), include both parts. Above it, restoration is uniquely
optimal, provided the threshold is below 1. At an admitted crossing, the
optimal set is the union. If \(\tau_{\ne}(t)\ge1\), largest-part pairs remain
optimal for all admitted workloads; restoration never wins there.

Both thresholds strictly decrease with \(t\) and have strictly positive limits.
Increasing the new link's strength does not drive the threshold to zero.
This theorem chooses the location at a common strength. It does not optimize
different strengths for different candidates or compare against doing nothing.

## Why the rule follows

Write \(M=L_H^+\), \(C_p=\operatorname{diag}(p)-pp^T\), and let \(m\) be the
sum of old conductances. The established weighted commute identity gives

\[
 U_p=2m\operatorname{tr}(M C_p),\qquad
 \operatorname{tr}(M C_p)=\frac{1-\theta}{n}
       \bigl(\operatorname{tr}M+n\theta M_{hh}\bigr).
\]

For an insertion incidence vector \(b_f\), put \(z=M b_f\),
\(r=b_f^TMb_f\), \(s=\|z\|^2\). The rank-one inverse update reduces the
covariance trace by

\[
 \frac{t(1-\theta)}n\,
 \frac{s+n\theta z_h^2}{1+tr}.
\]

Every candidate has the same final total conductance \(m+t\). After canceling
the common positive factors, maximizing the following scores minimizes the
actual hitting objective:

| Missing link | Score |
|---|---|
| Restore \(uh\) | \(R_t+\theta\lambda_R\), where \(R_t=W/(kD_R)\), \(\lambda_R=1/(nkD_R)\) |
| Join \(u\) to another vertex in \(A\) | \(I_t+\theta\lambda_I\), where \(I_t=(2k+2/d+W/k)/D_I\), \(\lambda_I=1/(nkD_I)\) |
| Pair avoiding \(u\) inside a part of size \(q\) | \(2/[(n-q)(n-q+2t)]\) |

The last row covers unaffected pairs in \(A\) and all pairs in \(B,C\).
The inverse action, candidate coverage and workload reduction are independently
checked in the [full theorem review](../evidence/kemeny-workload-robustness/envelope-review/review.md).
The [earlier common-strength uniform theorem](kemeny-weighted-repair.md) supplies
the strict intercept ordering at \(\theta=0\). Also

\[
 D_I-D_R=k[d^2-1+t(2d+1)]>0,
\]

so restoration has the greater slope. In the equal family, the incident score
starts above every untouched score and increases, leaving just its crossing
with restoration.

In the unequal family put \(C_t=2/[e(e+2t)]\). The uniform ordering is
\(C_t>I_t>R_t\). To exclude the incident score from the upper envelope, evaluate
it at the restoration/largest-part crossing. The required strict gap is

\[
 E_t=(D_I-D_R)C_t-D_I I_t+D_R R_t
 =2\left[k\left(\frac{d^2-1+t(2d+1)}{e(e+2t)}-1\right)-\frac1d\right].
\]

Since \(d-e=c-a\ge1\),
\(N=d^2-e^2-1+t(2d+1-2e)\ge2e+3t\) and \(d-1\ge e\). Consequently

\[
 \frac{dE_t}{2}
 =\frac{n-1}{n}\frac{(d-1)N}{e(e+2t)}-1
 \ge\frac{(n-2)e+(n-3)t}{n(e+2t)}>0.
\]

Before the crossing the incident score stays below the largest-part score;
afterward the steeper restoration score stays above it. All other untouched
scores are smaller unless their part is also largest. This proves the complete
sets, including boundaries and ties, for every admitted integer triple and
positive real \(t\); no parameter grid is used to infer the theorem.

## Strength dependence and endpoints

Direct differentiation gives

\[
 \tau_{\ne}'(t)=\frac{2nk[e-k(e+2)]}{e(e+2t)^2}<0,
 \qquad e-k(e+2)\le-\frac{(a-1)(d-1)}{nd}.
\]

Its limits are
\(\tau_{\ne}(0^+)=2nk^2/e^2-nW\) and
\(\tau_{\ne}(\infty)=nk(1-k)/e-nW\ge(a-1)(d-1)/(d^2n)>0\).
These expressions do not classify every integer instance with threshold 1.

For equal parts, the derivative sign reduces to
\((d^2-1)-kd(d+2)=-(d-1)(a-2)/n<0\). The limits are

\[
 \tau_{=}(0^+)=\frac{a(a-2)(5a+1)}{(a+1)(2a+1)^2(3a+1)},\quad
 \tau_{=}(\infty)=\frac{(a-2)(8a^2-a-1)}{(2a+1)^2(3a+1)(4a+3)}.
\]

Both are positive. The complement of the first has numerator
\(12a^4+23a^3+32a^2+10a+1>0\) over the same positive denominator. Hence
\(0<\tau_{=}(\infty)<\tau_{=}(t)<\tau_{=}(0^+)<1\).
The checker retains the full positive coefficient lists after \(a=x+3\).

At \(t=0\), all insertion actions actually coincide. At \(\theta=1\), all
actual objectives are zero. Neither endpoint is classified by the scaled
strict-score rule. Infinite strength is a limit only.

If all old weights are instead multiplied by \(q>0\) and the new link is unit,
divide every final weight by \(q\). Transition probabilities stay unchanged,
giving exactly the model above with \(t=1/q\) and the same workload. Uniform
workloads retain the earlier strength-independent optimal location. For every
equal family, choosing \(\theta\) strictly between the two threshold limits
gives a unique finite strength crossing, so a nonuniform workload can change
the recommendation under common old-weight scaling. This is an existence
result for that interval of workloads, not a switch for every fixed workload.

## What is certified when one old link changes

This separate certificate fixes part sizes \((3,3,3),(3,3,4),(3,4,5),(4,4,6)\),
workloads \(\theta=0,1/10,1/2\), and unit insertion. Change any one existing
conductance to \(1+\delta\), for **every real** \(\delta\in[-1/10,1/10]\).

Let \(M_f\) be the nominal inverse after candidate insertion \(f\), and \(b\)
the old link's incidence vector. Set
\(T_f=\operatorname{tr}M_f+n\theta(M_f)_{hh}\),
\(r_f=b^TM_f b\), and
\(s_f=\|M_f b\|^2+n\theta[(M_f b)_h]^2\). The scaled trace is

\[
 Q_f(\delta)=T_f-\frac{\delta s_f}{1+\delta r_f}.
\]

An existing unit link gives \(0<r_f\le1\); both comparison denominators are
at least \(9/10\). For nominal optimum \(i\) and outsider \(j\), the
numerator of \(Q_j-Q_i\) is quadratic, with coefficients

\[
 D,\quad D(r_j+r_i)-s_j+s_i,\quad Dr_jr_i-s_jr_i+s_ir_j,
 \qquad D=T_j-T_i.
\]

Check both endpoints and an interior vertex if the quadratic is convex and its
vertex lies in the interval. Original graph/workload symmetries give eight
existing-edge types; after perturbing a representative, the program evaluates
**every actual missing insertion**, not just nominal insertion orbits.

The exact computation covers **96 contexts and 3,896 comparisons**, all strictly
positive. No interior convex vertex occurs in this data, although the checker
handles it. Independent reconstruction checks 71 full nominal candidate
inverses and four direct perturbed inverses. Therefore every nominal optimum
beats every nominal outsider throughout the interval: the new optimal set is
contained in the old set. Ties within the old set may break. The certificate
does not cover arbitrary part sizes or simultaneous changes.

## Simultaneous changes: a bound and counterexamples

For any connected positive-weight baseline, fixed iid law with at least two
positive probabilities, and a finite nonempty set of unit insertions, let
\(Q_f=\operatorname{tr}(L_f^+C_p)\), \(Q_*\) its minimum and \(Q_o\) the
smallest value outside the complete nominal optimal set. Apply the same
relative old-weight perturbation \(|\delta_g|\le\epsilon<1\) to all candidates.
The elementary Loewner bound gives

\[
 (1-\epsilon)L_f\preceq L_f'\preceq(1+\epsilon)L_f,
 \qquad \frac{Q_f}{1+\epsilon}\le Q_f'\le\frac{Q_f}{1-\epsilon}.
\]

Every nominal optimum strictly beats every outsider whenever

\[
 \epsilon<\frac{Q_o-Q_*}{Q_o+Q_*}.
\]

The common final conductance cancels once. At equality these bounds provide
only weak separation, not an actual tie or failure. If there are no outsiders,
containment is automatic for \(\epsilon<1\); a point-mass workload makes all
objectives zero. The bound is sufficient and generally conservative, not an
exact failure radius. Uniform-workload invariance under common old scaling
already refutes a general claim of sharpness along that scaling direction.

| Parts | \(\theta\) | Sufficient strict radius | Certifies 1% |
|---|---|---|---|
| 3,3,3 | 1/10 | 1745/434753 | No |
| 3,3,3 | 1/2 | 2113/113713 | Yes |
| 3,3,4 | 1/10 | 919/359119 | No |
| 3,3,4 | 1/2 | 1451/93251 | Yes |
| 3,4,5 | 1/10 | 25/38113 | No |
| 3,4,5 | 1/2 | 545/49001 | Yes |
| 4,4,6 | 1/10 | 209/386721 | No |
| 4,4,6 | 1/2 | 913/98913 | No |

Only three of these eight instances receive a strict 1% guarantee from this
bound. A failed certificate does not establish instability.

A separate deterministic screen tested 16 assignments: the four graphs above,
\(\theta=1/10,1/2\), and \(\epsilon=1/100,1/10\). For each old link, choose
\(w_g=1-\epsilon\operatorname{sign}(\partial_g(Q_{runner}-Q_{restore}))\),
using the exact nominal runner with lexicographic tie breaking. This is a
feasible first-order direction, not a globally optimal nonlinear adversary.

Three 10% assignments, all at \(\theta=1/10\), switch the unique optimum:

| Parts | Winning pair | Exact perturbed \(Q_{runner}-Q_{restore}\) |
|---|---|---|
| 3,3,4 | {6,7} | -1237797931957837/7791858666372791417 |
| 3,4,5 | {7,8} | -73321/173420000 |
| 4,4,6 | {8,9} | -27446561/89464689000 |

Vertices are numbered from zero, with \(A,B,C\) in order, hub last and \(u=0\).
Every missing insertion was evaluated exactly. For the first witness, all 13
objectives were also reproduced through direct hitting equations by the author
and independently through fresh matrix construction by another agent.
The [full weights and objectives](../evidence/kemeny-workload-robustness/adversary-author/result.json)
make the counterexample reconstructible.

None of the eight tested 1% assignments switched the winner. This does not
prove robustness to the whole 1% box. The three successful 10% assignments do
disprove universal containment for their respective boxes, without conflicting
with the one-link certificate's different uncertainty set.

## Reproduction, prior work and remaining work

The [portable package](../experiments/kemeny-workload-proof/README.md) pins
Python 3.12.11 and SymPy 1.14.0 through uv. Its first checker reconstructs 33
symbolic identities and full positive coefficient lists. The second uses
exact rational arithmetic for all 3,896 comparisons. Neither checker alone
proves the graph reduction or analytic quantifiers: those have separate
independent audits. Ordinary Python assertions must remain enabled.

The integrated outputs match the reviewed replays byte for byte. An initial
logged child invocation failed to import SymPy; an explicit uv child invocation
recovered without changing proof code. Both attempts are retained. CI is
configured to reproduce the two checks and retain raw logs; actual post-push
execution is recorded separately and is not inferred from workflow text.

The [source assessment](../evidence/kemeny-workload-robustness/source/README.md)
credits the commute/resistance correspondence, multipartite inverse formulas,
rank-one updates, conductance optimization and nearby sensitivity work. An
uncertain-consensus stability margin is a different object from stability of
the best discrete repair. A close Kirchhoff-sensitivity paper remains only
partially accessible, and graph-join overlap remains unresolved. These limits
prevent claiming established publication novelty.

The candidate contribution is the complete family-specific workload/strength
decision rule and these precisely scoped robustness findings. Useful next
tests concern exact switching thresholds, reliable choices under uncertain
workloads, and sharper simultaneous certificates. This package does not claim
a physical-network improvement, a new generic inverse algorithm, Lean
verification, or completion of the mathematics map.
