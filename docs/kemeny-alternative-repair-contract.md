# Optimal alternate insertion release contract

Freeze: 2026-09-08, after independent acceptance of the mathematical packet.
This is an incremental addition to PR #8, whose previous release commit is
addc03ed0f4b4eff84e5d065d868b3fbcd9e5944. Preserve its original proof inputs,
code, logs and audit reports. Its evidence bundle describes that historical
commit; this new bundle will cover the changed documentation and theorem.

For integer 3<=a<=b,c let H=(K_(a,b,c) join K1)-uh, u in its minimum part
A, h the original hub. Exactly one missing unit-weight edge may be added,
but restoration uh is forbidden. Prove the exact minimizing edge set for
stationary-target simple-random-walk Kemeny's constant with zero initial
target hitting time. The selected theorem says that set is all unordered
pairs in A excluding u. There are binomial(a-1,2) optimal edges, so the
edge is unique exactly at a=3. Cover tied minima, all endpoint choices and
the empty-cell boundary. Do not confuse a unique orbit with a unique edge.

Reuse the already independently audited K formulas and uv-minus-untouched_A
strict comparison, pinned by exact input hashes. New certificates are the
two differences B-minus-untouched_A and C-minus-untouched_A in the frozen
astra-alternative-repair-work/result.json. Both complete numerator and
denominator dictionaries must match independently reconstructed ratios.
Positive coefficients with positive constants supply the full-domain sign;
finite diagnostics alone do not.

The portable implementation reuses unchanged singleton-endpoint subset
determinants, K-n=q2/q1-m, and exact sparse integer arithmetic. It pins the
new certificate and its input provenance, reconstructs the two new ratios,
and also checks the prior uv strict comparison from its pinned certificate.
Record all source hashes and raw outputs. Canonical command:

    uv run --project experiments/kemeny-one-deletion-proof --frozen python experiments/kemeny-one-deletion-proof/verify_alternative_repair.py --certificate experiments/kemeny-one-deletion-proof/alternative-repair.json --prior-certificate experiments/kemeny-one-deletion-proof/optimal-repair.json --output work/kemeny-alternative-repair/check-01.json

Use a fresh output name on subsequent runs. Pin Python 3.12.11, no package
dependencies, uv, isolated D-drive cache/env. An independent Astra reviewer
must check changed implementation, final prose and typed evidence against
the already completed mathematical audit; reuse unchanged verified work.
Root/author may not self-certify semantic checks. Limit the release review
to two Ground/Critic/Resolve rounds. Preserve failed runs and require all
four checks plus deterministic gate PASS, then inspect actual CI outputs.

The result is about this graph-dependent stationary-target objective. It
makes no assertion for fixed target/start distributions, unequal costs,
other failure types, weighted walks, or multiple insertions. Publication
priority and practical benefit require separate evidence.
