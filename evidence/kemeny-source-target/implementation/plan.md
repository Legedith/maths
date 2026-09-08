# Frozen implementation contract

API solve(n,edges,focus,interval,allowed): rational positive undirected connected loopless graph n>=3, distinct absent pairs, rational 0<=l<=h<1. Parallel present edges merge. Model label is uniform-source-independent-mixed-target. Return exact endpoint coefficients/objectives, oracle actions, per-edge candidate classifications and unique optimum, all global location ties with no action once. No iid solver call; only unchanged pinned utility imports.

H1: directed rank-one coefficients agree with independent transition first-step matrices at t=0,1/2,2 for every declared edge and endpoint.
H2: quadratic classification handles zero polynomial, nonzero constant, linear, repeated/zero/negative/no-real roots, and candidates are complete by the audited strict quasiconvex theorem.
H3: weighted path (1,2), focus1 at collapsed99/100 and98/101, and interval[0,99/100], plus uniform collapsed four-cycle produce exact certificates preserving no-action and location ties. No balance winner assumed.

Fresh --output required; deterministic UTF8 LF JSON with runtime/module hashes and rational bounds. No executable evidence strings or floating tolerances. General exact utility comparisons may be inconclusive or resource-limited; no universal termination guarantee. At most two full 90-second logged evaluations, both logger/child uv, D cache/env, verified pinned metadata. Distinct implementation audit required before promotion.
