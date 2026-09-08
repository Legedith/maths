# Directed simultaneous perturbation screen

The prescribed first-order sign pattern produces3outside-set winners among eight10percent cases, and none among eight1percent cases. Every one of the16targeted Q margins decreases. Thus H2 is refuted, H1 survives only this specific finite adversary screen, and H3 holds for these16patterns only.

All failures have theta1/10 and epsilon1/10:

| Parts | New unique winning edge | Qrunner-Qrestore after perturbation |
|---|---|---|
|334|C vertices6,7|-1237797931957837/7791858666372791417|
|345|C vertices7,8|-73321/173420000|
|446|C vertices8,9|-27446561/89464689000|

Indices are zero-based, with A first, then B,C, and hub last; u=0. In all16nominal cases restoration was independently confirmed as unique optimum by evaluating every missing edge. The runner was selected by exact objective then lexicographic endpoint order, not assumed to be a representative.

The lexicographically first failure is334,theta1/10,epsilon1/10. Its nominal targeted gap is919/1694000. Perturbed old total conductance is218/5. Exact Urestore=8286027872520913257/908367355347833150, Uwinner=29313964633299551/3218584043663450. Its entire missing-edge objective vector and unique winner were independently recomputed via full fundamental-matrix first hitting times in batch2; every value agrees exactly. This is a cross-formulation reproduction by the explorer, not an independent-agent final gate.

## Construction and exact scope

For each candidate insertion e, the baseline post-insertion inverse M_e is obtained from an independently constructed full baseline Laplacian. The workload covariance is fixed. For an old-edge incidence f, differentiation gives dQ_e/dw_f=-(M_e f)^T Cov_p(M_e f). Thus the targeted gap gradient is -s_runner,f+s_restore,f. Each old edge receives weight1-epsilon*sign(gradient), with zero gradients unchanged. This is a deterministic box-feasible first-order direction; it is not an exact minimizer of the nonlinear gap or a worst-case adversary.

All16perturbed weighted Laplacians are rebuilt and inverted exactly. Every missing unit insertion is evaluated, and actual U uses2*(perturbed_old_volume+1)*Q. This common positive factor cancels for ranking candidates at a fixed perturbation, but its actual value is retained in all reported objectives. The gradient is deliberately for Qrunner-Qrestore, not an asserted gradient-optimality certificate for U or an optimizer over the whole box.

result.json /rows retains all old-edge weights/gradients, original candidate Q values, runner choice, perturbed U for every missing edge, current optimizer sets, targeted gaps and flags. The first_counterexample duplicates the first failure for deterministic reproduction. direct-result.json retains every direct hitting-time U for that one authorized second-batch instance.

Exactly two <=60second logged batches, rc0/rc0, empty stderr, about2.4seconds and2.5seconds. Python3.12.11/SymPy1.14.0, uv isolated D cache/interpreter; explicit UTF-8/ASCII text. No failures, retries, new graphs/workloads/weights, random search or literature queries. Prior stages/repository unchanged.

The earlier single-old-edge10percent screen and these simultaneous failures have different perturbation sets, so they do not conflict. Similarly, small sufficient simultaneous radii do not predict a failure at1percent; this screen's unsuccessful1percent adversaries do not prove robustness. At10percent these three exact feasible assignments do prove failure of universal containment for their fixed graph/workload boxes. No measured physical benefit, method novelty or global worst-case threshold is claimed.

Typed numerical claims -> result.json summary/rows and direct-result.json; methodology -> check.py, check2.py and frozen plans; conclusions -> feasible exact weight assignments plus exhaustive missing-edge comparisons. This author packet requires independent review before promotion.
