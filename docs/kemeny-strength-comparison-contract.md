# Exact endpoint comparison regression

Frozen 2026-09-09. Base commit 06e2be9dcc0633bb855cd9eedbbe8ddd2b6a6b6d,
draft PR14, branch codex/kemeny-strength-minimax. Stay within the existing
one-missing-edge conductance minimax model and its rational-input API.

Implement the independently audited candidate that changes only endpoint
maximum selection inside solve. For the SAME edge and strength, remove the
positive factor (m+t)/[(1+rt)O0O1] and compare the affine cross-product
N(t)=(T0+B0*t)O1-(T1+B1*t)O0. At a certified positive balance, or coincident
branches, use the algebraically established equality and preserve first-endpoint
tie selection. Other candidates use the unchanged exact comparator on N.
General comparison, graph validation, candidate generation, global location
ties, no-action representation and inconclusive outcomes must remain unchanged.

Preserve the four prior API certificate subtrees exactly as parsed inert JSON,
including all exact expression strings and rational enclosures. Package the
checker dependency baseline/result.json with the frozen PR14 result hash
734c9f73753f2ab07232ab8dbf2a1583b42565e88623f9b50d7779aba904665b.
The importable solver must not depend on that baseline. Never evaluate evidence
expressions. Keep the original 80 grounded-objective comparisons, seven invalid
inputs, five abstract degeneracy cases, and three symbolic identities. Add two
cross-product identities and 64 grounded comparisons for the admitted graph
(K_3,4,4 joined to a hub) minus edge (0,11), all 16 absent pairs, theta in
[0,9/10]. This regression verifies per-edge B/C no action, not global no action.

Use uv for both outer process-tree-aware logger and child, with D-local cache
and isolated environments on this host. One root canonical run with a fresh
output and 90-second cap must match the final worker result and distinct replay
byte-for-byte. Retain both worker attempts separately, the existing-output
rejection, all raw statuses/streams, implementation hashes and runtime versions.
Re-use unchanged mathematical premises and independent audits. Finite regression
checks do not prove the graph-general characterization or Lean formalization.

Retain the earlier timeout and later abnormal instrumented profile as distinct
historical observations. The latter sampled endpoint comparison but establishes
neither crash cause nor the complete cause of the earlier timeout. Disclose its
direct-Python outer logger as a historical uv convention deviation; do not alter
its bytes or represent it as compliant. New invocations must comply. Do not
rerun those failures, claim a controlled speedup, guarantee crash prevention or
all-input termination, or claim mathematical priority or measured application
benefit. The partial exact general comparator can still be expensive.

Root alone writes the repository. Independent agents use separate D stages and
may not self-certify their authored implementation. Keep old bundles immutable
in their historical commit context. Build typed claims before the result note,
then require a distinct final four-check audit (at most two Critic/Resolve
rounds) and deterministic PASS before promotion. The local release gate does
not certify hosted CI: create a draft PR based on PR14, inspect the actual
commit's CI, download and independently compare the two exact proof artifacts.
The broader discovery and mathematics-map goal remains active.
