# Single-failure network-design release contract

Freeze 2026-09-08, after completion of three author packets. This release
supersedes the narrower pending release in kemeny-one-deletion-contract.md,
whose task and results remain retained as the first proof component. The
broader mathematics-atlas goal remains active; no site expansion is included.

Use connected simple unweighted undirected graphs and stationary-target
Kemeny's constant with zero initial-target hitting time. For integers
3<=a<=b,c let G=K_(a,b,c) join K1. Fix distinct u,v in its a-part A and
write h for the hub. The selected claims are:

1. For every original edge f, K(G-f+uv)<K(G-f). Cover all nine deletion
   endpoint categories, using six formulas under B/C relabelling.
2. For H=G-uh, restoring uh uniquely minimizes K(H+e) over all missing
   edges e of H. Restoration is an admissible unit-weight insertion.
3. In that same H, inserting an edge between two vertices of A other than
   u strictly beats inserting uv. This does not rank it against B/C.

Every quantifier includes tied minima, endpoint relabellings and a=3.
Prove any formal empty-cell correction. No multi-deletion, arbitrary part
count, p>1, practical benefit, or global originality claim is in scope.

Frozen candidate inputs are the specified one-deletion symbolic.json,
six astra-all-deletions-recovery-work case JSON files, and
astra-postfailure-design-work/batch2.json. Pin exact bytes in the portable
package and evidence manifest. Retain each author plan, raw attempts,
failures, and the explicit extra-execution amendment for the all-deletions
serialization repair. Do not silently reset attempt counts.

Root alone implements shared files. Portable checks use integer subset
determinants modulo t^3 and exact cross-products against all full coefficient
dictionaries. For the optimal-repair checker, split inserted pair endpoints
into singleton cells; independent residual cells give K=n-m+q2/q1 even
when the number of cells m differs between interventions. Mathematical
auditors must independently verify this alternative to the author's merged
pair correction. The author or root cannot self-certify semantic gates.

Canonical commands, from the repo, using fresh output names:

    uv run --project experiments/kemeny-one-deletion-proof --frozen python experiments/kemeny-one-deletion-proof/verify_certificate.py --certificate experiments/kemeny-one-deletion-proof/symbolic.json --output work/kemeny-one-deletion-proof/check-01.json
    uv run --project experiments/kemeny-one-deletion-proof --frozen python experiments/kemeny-one-deletion-proof/verify_all_deletions.py --certificates experiments/kemeny-one-deletion-proof/all-deletions --output work/kemeny-one-deletion-proof/all-deletions-01.json
    uv run --project experiments/kemeny-one-deletion-proof --frozen python experiments/kemeny-one-deletion-proof/verify_optimal_repair.py --certificate experiments/kemeny-one-deletion-proof/optimal-repair.json --output work/kemeny-one-deletion-proof/optimal-repair-01.json

Retain raw argv/stdout/stderr, runtime/exit status, and exact outputs. Use
uv, Python 3.12.11, no package dependencies, and isolated D-drive env/cache.
Add these three checks to the existing proof CI and retain its actual
results. Reuse unchanged previously reviewed arithmetic and source facts.

Independent Astra reviewers audit reproduction, full specification, source
entailment and implementation alignment. Final publication prose and the
assembled evidence bundle also require independent review; limit the
Ground/Critic/Resolve release pass to two rounds. Promote only with all four
checks and deterministic gate PASS. Record unresolved novelty and impact.
