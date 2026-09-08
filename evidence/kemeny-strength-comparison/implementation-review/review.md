# Independent targeted endpoint comparison audit

Four scoped integrity checks: PASS. No correction required. This is local candidate implementation review, excluded from completed PR14 and not a new shared release/CI gate.

## Reproduction: PASS

Target solver0057aae1dc61cfcb69c43bd2fcb5b43674e66a252c409a857b71a069eef82980, checker0e44b6866f10db98dec5219333d0527890e768abc112d3953426077e93b5848b, resultdcfc9629fcd975a6dc6a22d1ed87bc6f60c3e92c779a4f2c37c029b77f6069c9 and manifest594e58742bd3e617a1c30754a6842bc1944c4e90ba236b9b1ff71a8450ad38c4 match. Every author manifest artifact matches in input-checks.json. Copied inert baseline/result.json matches frozen original734c9f73753f2ab07232ab8dbf2a1583b42565e88623f9b50d7779aba904665b.

Fresh copied-package replay is fresh-replay.json, byte-identical to result-02.json with the above hash. Strict UTF8 decoding, no CR bytes and final LF verified. Both module hashes/runtime fields consequently match. One90second process-tree-aware run returned child0 in4.456983seconds with empty stderr. Expected existing-output rejection returned child2 in0.585226seconds; its outer uv shell returned1, and the requested output stayed unchanged. Both attempts have separate raw logs under logs/attempt-review01 and attempt-review02. No third evaluator was needed.

Each outer invocation was uv run --project STAGE --frozen python STAGE/run_logged.py --attempt-id review01 (then review02) --timeout-seconds90 --log-dir STAGE/logs -- followed by explicit uv run --project STAGE --frozen python STAGE/verify_strength_minimax.py --output STAGE/fresh-replay.json. UV_CACHE_DIR=STAGE/uv-cache, UV_PROJECT_ENVIRONMENT=STAGE/.venv, UV_PYTHON_INSTALL_DIR=D:/uv-python; PYTHONOPTIMIZE removed. The copied process-tree-aware logger is unchanged. No direct-Python outer-launch exception was used. Outer first-run environment installation is separate from child elapsed time.

## Algebra and specification compliance: PASS

The solver diff changes only construction of the endpoint maximum for one candidate. General compare/enclosure, graph validation, candidate generation/deduplication, per-edge/global comparisons, uniqueness, physical ties and no-action deduplication remain unchanged. For a fixed edge/strength, difference of endpoint regrets is

    (m+t)*N(t)/[(1+r*t)*O0*O1],
    N(t)=(T0+B0*t)*O1-(T1+B1*t)*O0.

All factors removed from the sign are positive under the accepted domain. Positive N selects endpoint0, negative selects1; equality selects0, matching previous maximum's first-entry tie convention. No volume is canceled across different interventions.

A candidate named balance exists only after its nonzero defining denominator and positive strength were certified by unchanged balance_candidate. Substitution yields N=0 exactly. Coincident kind certifies both affine coefficients zero, likewise permitting direct equality. All remaining candidates invoke the unchanged exact compare on N. Zero, negative and parallel crossings retain existing handling; unresolved signs still raise InconclusiveError. A balance identical to a previously entered stationary candidate is merged before this branch; that earlier candidate used a legitimate exact comparison, so correctness is unchanged even if this particular duplicate case receives no shortcut.

## Implementation and regression alignment: PASS

The checker adds two exact symbolic identities for cross-product factorization and balance substitution. It reads baseline/result.json only using json.loads and compares four encode_certificate API subtrees with Python data equality. All exact expression strings, bounds, actions and values must match the original; this is equality of complete parsed subtrees, not a claim that arbitrary textual JSON whitespace is compared. The packaged baseline bytes themselves are pinned to the original hash. No baseline expression is parsed or executed. The solver independently runs without this reference file; checker deployment must include it. Neither runtime module has D-specific input paths.

The original four API certificates,80direct grounded objectives,7invalid inputs and5abstract degeneracy cases are retained. The new344,[0,9/10] all16edge regression adds64direct covariance-objective comparisons at t0and1/2 and both endpoints, totaling144. It certifies uniquely active right baseline regret and B/C per-edge no-action despite negative left derivative; it does not claim global no action. Original344,[0,1/10] still has4classes/11candidate entries and unique balancing restoration. Output serialization and all explicit inconclusive limits are unchanged; no comparison epsilon or untrusted evidence eval is introduced.

Author attempt1 is separately preserved as attempt01-checker.py, result.json and wide-result.json with its own rc0record. Final attempt2 consolidates the wide certificate, two new identities and four old-certificate equality checks into result-02.json with separate rc0record. Neither replaces the earlier timeout or access-violation profile. This audit reproduces the final consolidation only, not two author runs masquerading as one.

## Source and inference boundaries: PASS by scoped reuse

The distinct accepted general-graph review supplies positivity, strict convexity, oracle attainment and candidate completeness; accepted strength and baseline implementation audits remain unchanged. The profile/algebra review validates this exact positive-factor transformation but does not establish a crash cause. Those premises support the optimization as code mathematics; this audit independently checked its actual call-site integration and full replay.

This input now completes under the declared local cap. No controlled before/after performance experiment was conducted, and no runtime percentage, generic speedup, all-input completion, or crash-prevention conclusion follows. Other exact comparisons/simplification and serialization may remain inconclusive or expensive. Raw failures remain historical evidence. No source-priority, physical benefit, publication or hosted-CI approval is included. All other stages and shared repository remained read-only.
