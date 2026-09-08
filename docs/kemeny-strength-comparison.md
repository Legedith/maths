# Exact endpoint comparison in the conductance solver

The solver now completes the previously difficult (3,4,4), [0,9/10] input
within the declared local cap. Its four original API certificates are preserved
exactly as parsed data, including expressions and rational bounds. This is a
targeted implementation improvement within the [existing model](kemeny-strength-minimax.md).

For one edge and strength t, the difference between endpoint regrets is

    (m+t) * N(t) / [(1+r*t)*O0*O1],
    N(t)=(T0+B0*t)*O1-(T1+B1*t)*O0.

The removed factor is positive. Comparing N therefore selects the same endpoint.
At a certified balancing candidate N=0 follows from its construction; coincident
branches also establish equality directly. Both preserve first-endpoint tie
selection. Other candidates still use the exact comparator on N. General
comparison, candidate generation, location ties and no action are unchanged.

The root run, final worker run and distinct replay produce byte-identical JSON.
There are 144 direct grounded-objective comparisons: the original 80 plus 64
for all 16 allowed edges of the wide-interval input at strengths 0 and 1/2 and
both workload endpoints. Five symbolic identities, seven invalid-input cases
and five explicitly abstract balance cases also pass. The new example verifies
a B/C edge's optimum is no action despite a negative derivative at the inactive
endpoint; it does not assert global no action. The general analytic theorem
continues to rely on its separately audited proof.

The [checker](../experiments/kemeny-workload-proof/verify_strength_minimax.py)
requires the packaged inert baseline/result.json. The importable solver does
not. No baseline expressions are executed. See the [API README](../experiments/kemeny-workload-proof/README-strength-minimax.md)
for an example and fresh-output invocation.

Two worker attempts are retained separately; only the second is the final
consolidated checker output. The distinct reviewer also tested existing-output
rejection without changing its bytes. Root performed one fresh canonical run
with a 90-second process-tree-aware cap and explicit uv outer and child calls.

The earlier timeout and later abnormal instrumented profile remain historical
failed attempts. The profile sampled endpoint comparison but did not establish
the crash cause, runtime share or complete cause of the earlier timeout. Its
direct-Python outer logger is a recorded historical uv convention deviation.
It has not been rewritten as compliant. New worker, reviewer and root calls use
uv for both logger and child.

This was not a controlled speed experiment. Other symbolic comparisons can
still be expensive or inconclusive; no general termination or crash-prevention
guarantee follows. Mathematical priority and measured application benefit
remain unresolved. The local evidence gate is separate from hosted CI for the
eventual pushed commit.

The [contract](kemeny-strength-comparison-contract.md), [bundle](../.codex/evidence/runs/kemeny-strength-comparison-v1/bundle.json)
and [raw evidence guide](../evidence/kemeny-strength-comparison/README.md) identify
the exact inputs, distinct audits and remaining limits. Prior releases reproduce
in their historical commit context; their frozen bundles are unchanged.
