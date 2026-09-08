# Uniform sources and uncertain destination demand

Frozen 2026-09-09. Base 6f3c6996a3929d5ce3f098609d25a7a5b9fec2d4,
completed draft PR15 on codex/kemeny-strength-comparison. Root owns shared
writes; agents use separate D stages. Use uv for all Python, including the
outer process-tree-aware logger and child, with D-local environments/cache.
The selected subset remains random walks and network edge design.

## Model and outcome

For a finite connected undirected loopless graph with positive conductances,
n>=3, choose one allowed absent pair and a fixed added conductance t>=0 before
theta is known. The allowed set is finite and nonempty. All t=0 labels are one
physical no action. A request starts uniformly, independently of its destination
law (1-theta)Uniform+theta delta_q, for 0<=l<=theta<=h<1. Hitting counts actual
discrete-time steps and is zero at an equal source/destination. Minimize maximum
relative regret against an oracle with the SAME edges and strength continuum.
Retain the changing total conductance m+t. The graph remains undirected even
though directed hitting times need not be symmetric.

Deliver the independently audited analytic characterization and a separate
importable exact rational-input solver. Do not change the prior iid-mixture API.
The source distribution is fixed uniform here; no arbitrary-source, multiple-edge,
adaptive, randomized, monetary-cost or finite-budget API is promised.

## Analytic requirements

Derive H_ij=(Md)_i-(Md)_j+2m(M_jj-M_ij) from first-step equations, with M=L^+
and d the weighted degrees. Uniform source averaging gives F_q=2mM_qq-(Md)_q.
Thus U_theta=(1-theta)2m tr(M)/n+theta F_q. Do not use iid commute symmetry or
cancel an iid (1-theta) factor. With v=e_i-e_j, w=e_i+e_j, z=Mv and r=v^TMv,
insertions update M_t=M-tzz^T/(1+rt) and d_t=d+tw. Verify all coefficients of
the resulting quadratic-over-linear objective (a0+a1*t+a2*t^2)/(1+rt).

Use the positive uniform component h<1 and the accepted PSD rank argument to
prove positive coercivity uniformly over the fixed finite edge set, attained
positive oracles and a2/r>0. Positive affine objective ratios reduce the
continuum worst regret to workload endpoints. Curvature can be negative:
the weighted path 0--1--2 with weights 1,2, focus1 and theta99/100 must reproduce
U''=-199/[225(3t+2)^3]. Theta98/101 is the affine boundary. Both are increasing
and select no action; strict convexity must not be asserted generally.

Instead prove strict quasiconvexity and unique PER-EDGE strength: nonpositive
curvature implies strict increase because the limiting derivative is positive;
positive curvature implies strict convexity. The maximum of two positively
normalized strictly quasiconvex functions remains strictly quasiconvex. Global
location ties remain possible. Complete candidates are zero, positive endpoint
stationary roots and positive roots of the quadratic equality of normalized
endpoint objectives. Handle identically zero, constant, linear, nonreal,
repeated, zero, negative and duplicate roots, collapsed intervals and all ties.

Include the independently checked boundary counterexample with FIXED source1
on the same weighted path and target law uniform-plus-focus1. Its objective is
(1-theta)(1+8/[3(3t+2)]), strictly decreasing to a positive unattained infimum
1-theta for theta<1. A finite cap makes its upper boundary optimal. State this
changed source assumption clearly; it does not contradict the uniform-source
theorem and does not establish a calibrated physical cost or capacity limit.

## Implementation, evidence and validation

Package source_target_minimax.py, verify_source_target.py, exact_support.py and
three pinned environment files in a new experiment directory. exact_support.py
is the immutable prior module hash
0057aae1dc61cfcb69c43bd2fcb5b43674e66a252c409a857b71a069eef82980;
import only its rational,
comparison, minimum, encoding and error utilities. Never call its iid solver.
Exact inputs, roots, interval signs and zero certification cannot use tolerance
ties or executable evidence strings. Unresolved comparisons are explicit
InconclusiveError/CLI exit3; symbolic simplification can remain expensive.

The frozen portable checker must reproduce four declared cases: weighted path
focus1 at collapsed99/100, collapsed98/101, interval[0,99/100], and collapsed
uniform four-cycle with both tied missing locations. Preserve its 30 direct
transition first-step hitting comparisons (every declared edge, strengths0,1/2,2,
both endpoints), three symbolic identities, seven abstract root cases and seven
malformed inputs. Its wide-path balancing winner is an observed certificate,
not an assumed oracle in the specification. Validate fresh output/exclusive
creation, explicit UTF-8 LF, all THREE module hashes and pinned runtime versions.

Root performs one fresh 90-second process-tree-aware canonical uv run; output
must match the worker and distinct replay byte-for-byte. Retain raw argv,
environment, stdout/stderr, statuses and every failed launcher. The theorem
review's initial missing-SymPy failure followed by authorized setup correction
must remain explicit; it was one successful mathematical run and two launchers.
Reuse unchanged distinct mathematical/code audits; finite checks do not replace
analytic first-step, PSD rank, coercivity, continuum endpoint or candidate proofs.

## Prior work and release

Attribute substantial partial overlap with Martinez et al., DOI10.1145/3744658:
directed recommendation walks, average reachability, rewiring, probability
optimization, rank-one greedy updates and SLSQP. Indexed primary publisher
passages and a failed direct DOI open must remain distinguished from a verified
full PDF. Do not infer novelty from missing literature. If using the newly
inspected author code, pin its immutable revision, exact normalization and
teleportation/intervention assumptions with a distinct source audit. No direct
theorem transfer to a general directed recommendation graph or reproduction of
its empirical gains follows. Keep public notes, locators, requests and raw
hashes; bulk third-party content stays local. Unverified reuse/data terms are
access gaps, not blanket claims that no license exists.

Freeze typed claims before result prose. Final independent four-check audit
allows at most two Critic/Resolve rounds; deterministic PASS is required before
promotion. Create a draft PR based on PR15. The local gate does not certify
hosted CI: inspect actual post-push workflow states, download both proof outputs
and obtain a distinct CI audit. Prior bundles remain immutable in historical
commit context. The broader goal, publication priority and measured practical
benefit remain unfinished.
