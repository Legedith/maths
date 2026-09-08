# Weighted insertion release contract

Freeze: 2026-09-08. Previous goal turn made progress by publishing audited
PR8/PR9 results and independently verifying the following weighted extension.
This release starts at 286aff954c0369f1cdff9680c75cfd5724f0b2af. Preserve
previous bundles, certificates, code and raw failures as historical records.

Let H=(K_(a,b,c) join K1)-uh, integer 3<=a<=b,c, u in A and h the hub.
All old conductances equal one. The objective U is the mean first hitting
time for independent uniform start/target, with zero self-hit and transitions
proportional to conductance. First prescribe one common new-edge conductance
t>0 for every candidate missing edge. Prove the exact optimal edge set is
unchanged for every such t: all u-incident A pairs if a=b=c; otherwise all
internal pairs in each largest original part. Restoration permission does
not change this set. Do not claim the entire suboptimal ordering is fixed.

Then allow one missing edge and any conductance t>=0, with t=0 representing
no action and no monetary penalty. Prove the same edge set with its unique
positive finite strength t*=(sqrt(s(mr-1)/(rT-s))-1)/r is exactly the joint
global optimum, where r=v'L_H^+v, s=v'(L_H^+)^2v, T=trace(L_H^+), m=edges(H).
Cover tied maxima, all endpoint categories, a=3 and integer substitutions,
both boundary t=0 and t tending to infinity, and equivalent edges sharing
r,s. Do not claim t*<1 universally or that t*=1 never occurs.

Reuse the independently audited weighted and strength mathematical packets.
Six complete positive coefficient certificates prove the intercept/slope
signs of pairwise comparisons of s/(1+tr). Three unchanged unit no-op
certificates establish the strict improvement premise for the calculus
corollary. The latter requires a documented analytic derivative/sign and
global-order argument; finite examples cannot establish it.

Portable implementation requirements: reconstruct r,s,T,m in exact sparse
integer rational arithmetic, pin the weighted and prior no-op certificates,
verify all six weighted coefficient identities and all three no-op identities,
positive denominators and constants, and emit input/dependency hashes.
Never execute expression strings from certificates. Reuse unchanged audited
integer polynomial arithmetic, documenting its fourth exponent truncation
and using only the first three variables for these identities. Include
exact rational evidence for the (4,4,6) suboptimal crossing at t=12 and the
(3,3,3) strength radical if practical, with finite scope clearly marked.
The graph reduction, edge-set completeness, generic calculus and joint
global-optimum argument remain explicit independently audited proof bridges.

Canonical command from project root, fresh output name:

    uv run --project experiments/kemeny-one-deletion-proof --frozen python experiments/kemeny-one-deletion-proof/verify_weighted_repair.py --weighted-certificate experiments/kemeny-one-deletion-proof/uniform-weighted.json --noop-certificate experiments/kemeny-one-deletion-proof/uniform-noop.json --output work/kemeny-weighted-repair/check-01.json

Use pinned Python3.12.11 and no new package dependencies, isolated D-drive
environment/cache. Implementation worker owns a separate stage; root alone
integrates shared files. Freeze at least three falsifiable checks and at most
two bounded implementation attempts, retaining all original failures.
An agent who did not implement the checker must audit the changed code and
fresh replay. Final prose/typed evidence needs an independent gate, at most
two final Critic/Resolve rounds, followed by deterministic gate and actual CI.

Attribute the known commute, multipartite inverse, Kirchhoff edge scoring,
join-formula overlap and normalized conductance-optimization framework from
primary sources. Do not claim a novel generic optimization algorithm or
infer originality from missing search results. Publication priority and
measured application benefit remain unresolved. Later strength-vs-one
classification research is excluded from this frozen release.
