# Frozen symbolic implementation plan

Scope: standalone common-strength workload-envelope identity checker, Python==3.12.11, SymPy==1.14.0. Required --output PATH and exclusive UTF-8 creation. No external/D-specific source inputs in CLI, no graph/grid change, no raw expression execution.

Falsifiable checks: (1) all restore/incident/untouched scores and slopes agree with r,s,hub coordinates; (2) D_U-D_R, E_t, and shifted N lower-bound identities vanish exactly; (3) both threshold derivatives and n=d+a sign bounds agree; (4) equal closed form, unit reduction, zero/infinity limits and full shifted positive numerator/denominator coefficient lists agree. Any residual or nonpositive coefficient fails.

Use cancellation and early parameter substitution, no blind multivariate expansion. Emit exact formulas, named checks, all univariate coefficients, interpreter/library/code hash and required analytic bridges. At most2 implementation evaluator attempts, each capped60s; retain failures. uv lock/sync are setup, not numerical batches. One canonical fresh-output run planned. Independent math and changed-code review required; author does not self-certify. No shared repo/integration writes.
