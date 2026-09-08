# Choosing a repair when the traffic mix is uncertain

Choosing a link for the middle of an expected traffic range can give a worse
worst-case guarantee. In the ten-vertex example below, that choice restores
the damaged link. A different repair has smaller maximum relative regret.

For the specified family of random-walk networks, we can classify every best
deterministic unit repair over any closed traffic interval below 1. Only two
types of repair need consideration, and two endpoint products decide between
them. The reduction depends on a strict domination proof; keeping only actions
that sometimes win is insufficient in a general minimax problem.

This is a result about a mathematical model. Robust regret optimization and
the underlying electrical and inverse-matrix methods are established ideas.
Priority of this precise family classification and measured benefit in a real
network remain unresolved. The independently audited results and portable
checker are recorded in the [evidence bundle](../.codex/evidence/runs/kemeny-unit-minimax-v1/bundle.json).

## Decision being made

Let H=(K_(a,b,c) join K1)-uh, with integers 3 <= a <= b <= c, hub h and u in
part A. All remaining conductances are 1. Walk transitions are proportional
to conductance. Source and target are independent with common law

    p_theta = (1-theta) Uniform + theta delta_h,

and self-hitting time is zero. Choose exactly one missing UNIT link, including
the option of restoring uh, before theta is known. The uncertainty interval
is [l,h], with 0 <= l <= h < 1; in interval notation h denotes its upper
endpoint, rather than the hub vertex. Doing nothing, choosing the strength,
randomized choices and decisions made after observing theta are outside this
classification. The [previous action-choice study](kemeny-workload-action-choice.md)
handles the distinction between insertion and no action separately.

For a candidate e let U_e(theta) be its expected number of walk steps. Its
relative regret compares it with the best repair for that same theta:

    rho_e(theta) = U_e(theta) / min_j U_j(theta) - 1.

We minimize max_{theta in [l,h]} rho_e(theta), retaining every tied physical
edge. This objective expresses protection against a bad traffic estimate;
it is not a claim about measured internet routing or intervention cost.

## Why endpoints suffice, and when actions can be removed

For any finite set of fixed connected graph interventions on the same n >= 2
vertices, write M_e for the Laplacian pseudoinverse and m_e for total undirected
conductance. The iid commute/covariance identity gives

    U_e(theta) = (1-theta) L_e(theta),
    L_e(theta) = alpha_e + theta beta_e,
    alpha_e = 2 m_e tr(M_e)/n, beta_e = 2 m_e (M_e)_hh.

These reduced lines are positive. Different fixed volumes belong inside each
candidate's coefficients; they cannot be cancelled individually. The common
factor 1-theta cancels from relative regret for theta < 1. At theta=1 all
objectives vanish and the stated ratio is undefined.

For positive affine lines,

    1 + rho_e(theta) = max_j L_e(theta)/L_j(theta).

The derivative of (A+B theta)/(C+D theta) is
(BC-AD)/(C+D theta)^2, with constant sign. Each pairwise ratio attains its
maximum at an interval endpoint. Taking the finite maximum over j proves
that rho_e does too, even if the oracle changes inside the interval.
This elementary argument is not claimed as a new general optimization method.

Removing a weakly dominated action preserves the minimax value and at least
one minimizer, but can remove tied minimizers. On [0,1/2], take the positive
affine lines A=1+2 theta, B=2-2 theta and C=3/2+theta. Although A <= C,
all three have worst relative regret 1. Conversely, with C=3/2 constant,
C never beats the pointwise oracle min(A,B), but has worst regret 1/2;
A and B each have worst regret 1. These are abstract affine examples, not
asserted graph realizations.

For the graph family we prove a stronger property: every removed action is
strictly dominated at both endpoints by one fixed retained action X. At an
endpoint maximizing X's regret, the removed action's regret is strictly
larger. It therefore cannot be a minimax tie.

## Two surviving repair types

Define

    n = a+b+c+1, d = n-a, e = n-c,
    m = ab+ac+bc+a+b+c-1,
    k = (n-1)(d-1)/(nd),
    W = [n(n-1)+d(d-1)]/(n^2 d^2), Z = d(d+2)k+1,
    T = sum_{q in (a,b,c)} (q-1)/(n-q) + 3/n + W/k,
    Hh = (n-1)/n^2 + 1/(n^2 k),
    R = W/k, lambda_R = 1/(nk),
    I = (2k+2/d+W/k)/Z, lambda_I = 1/(nkZ),
    C = 2/[e(e+2)].

The restoration set Rset contains only uh. Define Xset and (J,lambda_X) by:

| Part sizes | Xset | J | lambda_X |
|---|---|---|---|
| a=b=c | Every pair {u,v} with v in A and v != u | I | lambda_I |
| c>a | Every internal pair in every largest part | C | 0 |

If b=c>a, include all pairs in both B and C. The two reduced objective lines
are

    A(theta) = T-J + theta(nHh-lambda_X),
    B(theta) = T-R + theta(nHh-lambda_R).

Their actual objectives are 2(m+1)(1-theta)/n times A or B, respectively.
All other unit insertions are strictly dominated by each fixed Xset action.
For equal parts, this follows from the independently accepted
[workload envelope](kemeny-workload-robustness.md).

For unequal parts the new certificate proves G=C-I-lambda_I > 0. Consequently
C-I-theta lambda_I = G+(1-theta)lambda_I > 0 throughout the admitted range.
The incident-u pairs lose strictly to largest-part pairs, and every untouched
pair in a smaller part also loses strictly. This additionally classifies the
entire unit-insertion optimum when restoration is forbidden.

The positivity certificate covers two disjoint exhaustive cases:

| Nonnegative shifts | Numerator terms / constant | Denominator terms / constant |
|---|---|---|
| a=x+3, b=a, c=a+1+z | 27 / 27090 | 42 / 25084080 |
| a=x+3, b=a+1+y, c=b+z | 83 / 50240 | 161 / 62092800 |

Every nonzero coefficient is positive. The positive constants guarantee
strict positivity, including zero-shift boundaries. Every coefficient and
the exact rational identity are retained; this is a polynomial certificate
plus an analytic coverage argument, not an enumeration of a finite graph grid.

## Complete deterministic rule

The lines cross formally at

    tau = (a-2)(10a^2+a-1)/[(2a+1)^2(2a+3)(3a+1)]  if a=b=c,
    tau = nkC-nW                                     if c>a.

The accepted envelope proves tau>0, with A<B below tau and B<A above tau.
For unequal parts tau can be at least 1. For equal parts it is below 1.

If l=h, select Xset below tau, Rset above tau, and their union at tau. The
minimax regret is zero. On a nondegenerate interval l<h:

| Interval condition | Complete minimax set | Worst regret |
|---|---|---|
| h <= tau | Xset | 0 |
| l >= tau | Rset | 0 |
| l < tau < h and A(l)A(h) < B(l)B(h) | Xset | A(h)/B(h)-1 |
| l < tau < h and A(l)A(h) > B(l)B(h) | Rset | B(l)/A(l)-1 |
| l < tau < h and products equal | Xset union Rset | The common value |

For interior crossing, X's unique worst workload is h and restoration's is l.
Crossing only at an interval endpoint does not add the other repair type to
the minimax set: it has positive regret at the opposite endpoint. For the
winning zero-regret type, every workload attains the same zero regret.
If tau>=1, every admitted nondegenerate interval selects Xset.

The product rule follows from comparing the two endpoint ratios and multiplying
positive denominators. Strict domination makes this a complete classification
over every missing edge, rather than a two-action heuristic.

## Exact failure of the midpoint choice

For a=b=c=3 and interval [0,21/500], the midpoint 21/1000 exceeds
tau=46/2205. Here

    A(theta) = 10021/8680 + (2547/2480)theta,
    B(theta) = 81/70 + (9/10)theta.

At the midpoint A=20416409/17360000 and B=82323/70000, so restoration wins
that comparison. But its maximum relative regret is 23/10021, larger than
23305/10372104 for either of the two incident-u repairs. Those two repairs
are precisely the minimax set. All ten possible insertion matrices are
reconstructed independently; the finite witness illustrates the full theorem.

## A failed extension defines the strength boundary

The unequal-family location rule does not extend to every prescribed positive
strength. For (a,b,c)=(3,3,4), common inserted strength t=16,
theta=9147/9152 and restoration forbidden, precisely the two incident-u
pairs win. They beat each of the six largest-part pairs by score gap
1/4333056, corresponding to actual expected-step gap 145/6815897088.
Every one of the twelve allowed candidates is reconstructed, with final
conductance 58. This comparison does not optimize over strength or include
no action.

The first exploratory positivity assertion failed: the endpoint numerator at
the 334 origin is 28910-1820t. The second frozen experiment used that failure
to construct the exact counterexample. Both attempts and their raw outputs
remain evidence; the failed universal conjecture is not relabelled a theorem.

## Prior work, proof boundary and replay

[Kumar et al., AAAI 2016](https://ojs.aaai.org/index.php/AAAI/article/download/9908/9767)
already define absolute minimax regret for stochastic network design and prove
an endpoint property for uncertain cascade probabilities (printed pages
3858-3859, equations 3-5 and Propositions 1-2). Their model does not directly
provide this fixed-iid hitting-time ratio classification. The publisher abstract
for [Minimax Relative Regret Approach for Resilient Supply Chain Design](https://www.sciencedirect.com/science/article/pii/S2405896322019061)
also establishes prior use of relative regret in network design; its full-text
open failed. No equation or endpoint theorem is attributed from that abstract.
The [source notes and distinct audit](../evidence/kemeny-unit-minimax/README.md)
retain those limits and the unsuccessful textbook-passage retrieval.

The portable checker reconstructs polynomial identities, exact graph examples
and policy branches. The full-domain proof additionally uses separately
audited analytic bridges: the commute/covariance formula, graph reduction,
orthant coverage, equal-family envelope, affine endpoint lemma and strict
exclusion of all other minimizers. This is not a Lean formalization.

From the repository root, choose a fresh output in an existing directory:

```powershell
uv run --project experiments/kemeny-workload-proof --frozen python experiments/kemeny-workload-proof/verify_unit_minimax.py --output minimax-replay.json
```

See the [checker README](../experiments/kemeny-workload-proof/README-unit-minimax.md)
for exact versions and the logged canonical invocation. Assertions must remain
enabled. Local semantic verification and actual hosted CI have separate records;
a workflow definition alone is not evidence that a hosted run passed.
