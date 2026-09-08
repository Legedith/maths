# When the best unit repair is worse than doing nothing

In one 12-vertex network, every possible unit-strength addition makes the
modeled journeys slower for a precisely identified range of traffic mixes.
Doing nothing is best among those actions. Yet, at a workload inside that
range, a half-strength link helps, and we can prove the exact best strength
and location across all possible new links.

This is a decision about a mathematical random-walk model. It illustrates why
an optimizer should include both the option to do nothing and the strength of
an intervention. It does not measure the effect of installing a physical link.
The general phenomenon of harmful additions and the electrical/optimization
methods are known; publication originality of these specific results remains
unresolved.

Three results have separate independent mathematical audits and a portable
exact checker:

| Scope | Result |
|---|---|
| Every equal-part graph in the specified family, every admitted hub-mixture workload | The best unit insertion strictly improves on no action. |
| Parts(3,4,4), unit insertion or no action | An exact interval of workloads makes no action uniquely best. |
| Parts(3,4,4), workload parameter14/405, variable insertion strength | All12internal B/C pairs at one exact subunit strength are globally optimal. |

## Model and the volume term

Let \(H=(K_{a,b,c}\vee K_1)-uh\), with integers \(3\le a\le b\le c\), hub
\(h\), and \(u\) in part \(A\). Remaining conductances are 1. Walk transitions
are proportional to conductance. Source and destination are independent with
the same fixed law

\[
 p=(1-\theta)\operatorname{Uniform}+\theta\delta_h,
 \qquad 0\le\theta<1.
\]

Self-hitting time is zero. Minimize \(U_p=\sum_{i,j}p_i p_j H_{ij}\), the
expected number of steps. This is not a candidate-dependent stationary-target
Kemeny objective. The action set is first no action or one missing unit link;
the final example additionally permits choosing that link's strength.

Write \(n=a+b+c+1\), \(m=ab+ac+bc+a+b+c-1\), \(M=L_H^+\),
\(T=\operatorname{tr}M\), and \(h_0=M_{hh}\). The known weighted commute
identity and iid covariance reduction give

\[
 U_p(H)=2m(1-\theta)(T/n+\theta h_0).
\]

If a unit candidate reduces the covariance-scaled quantity \(T/n+\theta h_0\)
by \(\alpha_f+\theta\beta_f\), then

\[
 U_p(H)-U_p(H+f)
 =2(1-\theta)\bigl[(m+1)(\alpha_f+\theta\beta_f)-(T/n+\theta h_0)\bigr]
 =\frac{2(1-\theta)}n F_f(\theta).
\]

The factor \(2(1-\theta)/n\) is positive on the stated domain. Candidate
comparisons share final volume \(m+1\); comparison with no action does not.
Resistance decrease alone therefore does not prove improvement in walk steps.
The [previous workload envelope](kemeny-workload-robustness.md) identifies the
best insertion. Here we compare that best insertion against the baseline.

## Complete equal-family improvement theorem

Suppose \(a=b=c\ge3\). Set

\[
\begin{aligned}
n&=3a+1,&d&=2a+1,&m&=3a^2+3a-1,\\
k&=\frac{(n-1)(d-1)}{nd},&
W&=\frac{n(n-1)+d(d-1)}{n^2d^2},&Z&=d(d+2)k+1,\\
R&=W/k,&I&=\frac{2k+2/d+R}{Z},\\
T&=\frac{3(a-1)}d+\frac3n+R,&
h_0&=\frac{n-1}{n^2}+\frac1{n^2k}.
\end{aligned}
\]

Restoration and an incident pair \(\{u,v\}\), \(v\in A\setminus\{u\}\), have
scaled improvement margins

\[
\begin{aligned}
F_R(\theta)&=(m+1)R-T+\theta[(m+1)/(nk)-nh_0],\\
F_I(\theta)&=(m+1)I-T+\theta[(m+1)/(nkZ)-nh_0].
\end{aligned}
\]

The accepted insertion rule selects all incident pairs below

\[
 \tau=\frac{(a-2)(10a^2+a-1)}{(2a+1)^2(2a+3)(3a+1)}\in(0,1),
\]

and restoration above, with their union at the crossing. The incident margin
has strictly negative slope and the restoration margin strictly positive
slope. Their shared minimum on their selected branches is

\[
 F_I(\tau)=F_R(\tau)=
 \frac{18a^6+531a^5+306a^4+39a^3-15a^2-8a-1}
 {3a^2(2a+1)^2(2a+3)(3a+1)^2}>0.
\]

For \(a\ge1\), \(15a^2+8a+1\le24a^3<39a^3\), proving numerator positivity.
The slopes are

\[
 F_R'=\frac{18a^4+15a^3+12a^2-2a-1}{6a^2(3a+1)}>0,
\]

\[
 F_I'=-\frac{216a^6+342a^5+105a^4+51a^3+12a^2+5a+1}
 {6a^2(3a+1)(12a^3+18a^2+3a+1)}<0.
\]

The positive sign in the first follows from \(2a+1\le3a^2<12a^2\). All
denominators are positive. Thus the selected improvement is strictly positive
throughout \(0\le\theta<1\), including the crossing and all tied incident
edges. The checker also reconstructs complete positive coefficient lists after
\(a=x+3\), covering \(x=0\). At \(\theta=1\), every actual objective is zero;
strict improvement does not extend there.

This is a theorem for all equal sizes, not an inference from the separately
retained twelve diagnostic rows. The [independent review](../evidence/kemeny-workload-action-choice/equal-review/review.md)
checks the inverse formulas, actual normalization and full-domain sign proof.

## An unequal counterexample and the full no-action interval

For \((a,b,c)=(3,4,4)\), label \(A=\{0,1,2\}\),
\(B=\{3,4,5,6\}\), \(C=\{7,8,9,10\}\), \(h=11\), \(u=0\).
There are 50 existing links and 16 possible insertions. Direct inverse
reconstruction gives

\[
 T=985/792,\quad h_0=269/3168,\quad
 F_C(\theta)=31/990-(269/264)\theta,\quad
 F_R(\theta)=-59/396+(277/66)\theta.
\]

Here \(F_C\) applies to all twelve internal pairs in \(B,C\). The insertion
envelope switches from those pairs to restoration at \(\tau=14/405\); all
three \(A\)-pairs are strictly worse than the envelope. Define

\[
 L=124/4035,\qquad R_0=59/1662,
 \qquad 0<L<14/405<R_0<1.
\]

These are exactly the zeros of \(F_C,F_R\). The complete policy allowing no
action is:

| Workload parameter | Complete optimal action set |
|---|---|
| \(0\le\theta<L\) | All12internal B/C pairs |
| \(\theta=L\) | Those pairs and no action |
| \(L<\theta<R_0\) | No action only |
| \(\theta=R_0\) | Restoration and no action |
| \(R_0<\theta<1\) | Restoration only |

This follows from exact affine signs and the complete insertion envelope.
The portable checker reconstructs the baseline plus all sixteen candidate
matrices and checks the competing affine margins at both ends of each
insertion-envelope interval. Affinity makes these comparisons valid throughout
the intervals; they are not sampled workload claims.

At \(\theta=14/405\), restoration and all twelve B/C pairs tie as best
insertions. Yet their margin is \(-19/4860\), giving

\[
 U_{\rm baseline}=53465731/5196312,\qquad
 U_{\rm best\ unit}=222787499/21651300,
\]

\[
 U_{\rm best\ unit}-U_{\rm baseline}=7429/11809800>0.
\]

Every unit insertion is therefore harmful in this model at that workload.
This refutes the proposed universal extension to unequal part sizes. The
[independent counterexample and interval audit](../evidence/kemeny-workload-action-choice/counter-review/review.md)
reconstructs all seventeen matrices and verifies every tie and endpoint.

## A weaker link improves the counterexample

Keep exactly this graph and \(\theta=14/405\), but allow one missing link of
any strength \(t\ge0\). At zero, all edge labels denote the same no-action
graph. For incidence vector \(v\), put

\[
 T_\theta=T+n\theta h_0=12431/9720,\quad
 r=v^TMv,\quad s_\theta=\|Mv\|^2+n\theta[(Mv)_h]^2.
\]

The actual objective is

\[
 U_f(t)=\frac{391}{2430}(50+t)
 \left(T_\theta-\frac{t s_\theta}{1+rt}\right).
\]

Write \(A=T_\theta-ms_\theta\), \(B=rT_\theta-s_\theta\). After removing
the common positive prefactor, the derivative numerator is
\(A+B(2t+rt^2)\), over \((1+rt)^2\). Here every \(r,B\) is positive.

| Edge class | Count | \(r\) | \(s_\theta\) | \(A\) | \(B\) |
|---|---|---|---|---|---|
| Incident-u A | 2 | 47/198 | 2027/71280 | -3821/26730 | 66191/240570 |
| Restoration | 1 | 5/22 | 27/880 | -6821/26730 | 2527/9720 |
| Untouched A | 1 | 2/9 | 2/81 | 431/9720 | 11351/43740 |
| Internal B/C | 12 | 1/4 | 1/32 | -5513/19440 | 701/2430 |

For \(A\ge0\), the edge is uniquely optimized at zero. For \(A<0\), the
derivative numerator strictly increases on \(t\ge0\), with a unique positive
root

\[
 t_*=(\sqrt{s_\theta(mr-1)/B}-1)/r.
\]

The objective decreases then increases. Its asymptotic positive slope is
\(B/r\) before the common prefactor, excluding an optimum at infinity.
The weighted positivity argument is valid: on the space perpendicular to
constants, \(rM-Mvv^TM\) is positive semidefinite and nonzero; taking its trace
against positive definite \(I+n\theta e_he_h^T\) gives \(B>0\).

Exact rational square-root enclosures compare every edge's global minimum,
using

\[
 \min_{t\ge0}(m+t)\left(T_\theta-\frac{ts_\theta}{1+rt}\right)
 =\frac{B(mr-1)+s_\theta+2\sqrt{Bs_\theta(mr-1)}}{r^2}
\]

for the improving classes. Strictly disjoint bounds prove that the complete
global optimum is **all twelve B/C pairs**, each at the same unique strength

\[
 \boxed{t_*=4\left(\sqrt{27945/22432}-1\right)\in(0,1).}
\]

Optimized restoration and every A pair are strictly inferior. Even the simple
choice \(t=1/2\) improves on no action by exactly
\(117691/11809800\) expected steps. The
[independent strength audit](../evidence/kemeny-workload-action-choice/strength-review/review.md)
reconstructs every candidate and proves the ordering with rational bounds.
This is a complete optimization for the one declared graph and workload,
not a general rule for arbitrary unequal graphs or traffic mixes.

## Experiments that changed the question

The initial diagnostics fixed parts333,334,33100 and workloads0,1/10,1/2,9/10.
All twelve best-unit choices improved on no action, but they did not settle
the unequal theorem. Two subsequent attempts at a universal unequal positivity
proof failed: one timed out and one failed a positivity assertion. Their raw
records are preserved. The344 counterexample was then derived by exact hand
arithmetic at a symbolic boundary, followed by independent reconstruction.
It is not recorded as a third successful run of the failed universal checker.

| Hypothesis | Outcome |
|---|---|
| Best unit insertion always improves throughout the whole family | False:344counterexample; equal-family theorem remains true. |
| Restoration alone always improves | False:33100in all four diagnostic workloads. |
| Keep the repair chosen for uniform traffic at every workload | False:333at9/10; that choice worsens the objective while restoration helps. |
| Optimizing restoration's strength makes it best in the344case | False: B/C pairs at their optimal strength are better. |
| No action remains best after allowing variable strength in that case | False: half-strength already improves it. |

These are mathematical model findings. No cost, capacity-to-conductance
calibration, or measured network benefit has been established.

## Reproduction and source limits

Use the [portable instructions](../experiments/kemeny-workload-proof/README-action-choice.md).
The checker pins Python3.12.11 and SymPy1.14.0 through uv, reconstructs full
coefficient lists, all finite matrices and exact radical bounds, and emits
the additional analytic bridges explicitly. The root canonical output matches
the implementation and distinct independent replay byte for byte. The
[evidence packet](../evidence/kemeny-workload-action-choice/README.md) retains
author/reviewer separation, failed attempts and exact command streams.

The [source notes](../evidence/kemeny-workload-action-choice/source/notes.md)
separate fixed-workload averages, stationary-target objectives, volume-sensitive
commute bounds and absorbing-group shortcut problems. Known inverse and
conductance-optimization techniques are credited. The inspected statements
do not directly give these results; this is not an exhaustive originality
check. Close-source fulltext and graph-join overlap remain unresolved.
No Lean formalization, new generic optimization method, physical deployment
benefit or completion of the mathematics map is claimed.
