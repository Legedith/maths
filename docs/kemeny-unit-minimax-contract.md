# Deterministic unit-repair minimax contract

Frozen 2026-09-09. Base 24758065398e3b5e90d926d4376abbd8cc0fdbc5,
completed draft PR12. Root integrates the shared repository serially. D storage,
uv and isolated environments remain required. Stay within random walks and
network edge design; broader atlas and Site changes remain paused.

## Question and domain

Choose one missing UNIT edge before knowing a workload parameter theta in a
closed interval [l,h], where 0 <= l <= h < 1. The graph is
H=(K_(a,b,c) join K1)-uh, integers 3 <= a <= b <= c, unit old conductances,
u in A, hub h. Restoration is allowed and exactly one insertion is required.
No action, strength optimization, randomization and adaptive actions are
excluded from this release. Source and target are iid
p=(1-theta)Uniform+theta delta_h, zero self-hitting, and transition probabilities
are proportional to conductance. Minimize maximum RELATIVE regret
U_e(theta)/min_j U_j(theta)-1, using the same workload and full action set for
every comparison. Retain actual volumes before cancelling common factors.

## Accepted results to integrate

1. Reconstruct the full unequal-family strict certificate C-I-lambda_I > 0
   at unit insertion strength. Use the two exhaustive nonnegative integer
   shifts: a=x+3,b=a,c=a+1+z; and a=x+3,b=a+1+y,c=b+z. Retain every numerator
   and denominator coefficient, its exponent, positive constant, and the
   exact rational identity. Explain orthant coverage, positive denominators
   and the fixed-action strict domination argument. Equal-family ordering
   comes from the separately accepted workload envelope, with pinned evidence.
2. State and prove the finite-positive-affine endpoint lemma, allowing
   differing fixed candidate volumes. Show why pairwise ratios are monotone
   or constant and why finite maxima commute. Distinguish weak domination
   from strict exclusion of all tied minimizers; retain both abstract
   counterexamples from the accepted endpoint packet. Do not assert they
   are graph realizations. The generic method is elementary known context.
3. Integrate the complete family rule from the accepted full-unit minimax
   packet: equal-family X is all incident-u A pairs; unequal-family X is all
   internal pairs in every largest part; R is restoration. Strictly exclude
   every other action. Use reduced positive lines A,B and their crossing tau.
   Handle l=h, tau>=1, one-sided intervals, endpoint-only crossing, interior
   crossing and equal endpoint products, retaining every physical-action tie.
   For l<tau<h, compare A(l)A(h) with B(l)B(h) and report exact worst regrets.
   Theta=1 yields zero objectives and undefined relative regret, so is excluded.
4. Reproduce the declared 333,[0,21/500] midpoint counterexample from every
   candidate graph matrix. Midpoint selects restoration, minimax selects the
   two incident-u edges. Exact worst regrets are 23305/10372104 and 23/10021.
   The finite example illustrates, rather than proves, the full-family rule.
5. Preserve the failed arbitrary-strength extension and exact boundary
   counterexample 334,t=16,theta=9147/9152 with restoration forbidden.
   Independently reconstruct all twelve allowed candidates; the two incident
   edges win by score gap 1/4333056 and actual objective gap 145/6815897088
   over largest-part pairs. This is a scope counterexample, not optimization
   over strength or comparison to no action. Retain the failed first
   positivity evaluator and successful second evaluator unchanged.

## Reproduction and evidence

Use Python 3.12.11/SymPy 1.14.0 in the existing pinned uv proof project.
Provide a portable checker that constructs its own expressions, never evals
certificate strings, requires fresh output, keeps assertions enabled, and
writes deterministic UTF-8 LF JSON. Independently construct graph inverses
for both finite witnesses and keep exact rational objectives, candidate labels,
all winners and volumes. Explicitly name analytic bridges not formalized by
the symbolic/finite checker; do not call this a Lean proof or universal
enumeration. A checker policy interface should handle every stated boundary,
with exact illustrative cases chosen from the accepted formula, not a search
for favorable performance.

Keep typed claims and hashed source/code/log/result provenance before final
prose. Reuse unchanged mathematical audits with distinct authors and reviewers.
Implementation workers cannot self-certify their implementation or release.
Root runs one canonical replay through the raw logger with an explicit uv
child, fresh attempt and output paths. Preserve failures rather than overwrite.
Final independent Critic/Resolve is at most two rounds; promotion requires all
four independent gates and a deterministic PASS. Add CI replay and inspect
actual post-push outputs before claiming hosted verification. Use a new draft
PR based on codex/kemeny-workload-action-choice; do not mutate past bundles.

## Attribution and contribution boundary

Credit the known inverse/covariance machinery, robust network design,
relative regret and elementary endpoint/linear-fractional reasoning. The
bounded priority packet retains exact requests, source locators and access
failures; primary-source support must receive a distinct audit. No bounded
search can establish absence, priority or novelty. New claims are the scoped
family classification and exact counterexamples, conditional on these stated
models. Publication priority, measured real-network value and broader
mathematical mapping remain unresolved. The wider goal remains active.
