# Targeted exact endpoint comparison candidate

This candidate changes only the endpoint maximum inside solve. The general compare function, candidate generation, global comparison, ties, no-action deduplication, and explicit inconclusive behavior are unchanged. It is not approved for release; an independent implementation audit is required.

For each candidate strength, positive factors reduce endpoint ordering to the sign of N=(T0+B0*t)*O1-(T1+B1*t)*O0. A positive balancing strength was constructed from precisely N=0 after checking the denominator. Coincident branches have both affine coefficients zero. These cases select the first equal endpoint directly, matching the previous tie convention. Other candidates use the unchanged exact comparator on N. Symbolic identities and existing abstract zero/negative/parallel/coincident/positive balance checks accompany all original validations.

Canonical command from this directory:

    uv run --frozen python verify_strength_minimax.py --output fresh-result.json

Package strength_minimax.py, verify_strength_minimax.py, pyproject.toml, uv.lock, and baseline/result.json together. The baseline JSON is inert reference data; no evidence expression is executed. The importable solver needs no baseline file. The checker rejects an existing requested output, uses exclusive creation, and writes explicit UTF-8 LF JSON. There are no D-specific runtime dependencies in either module.

Two full evaluations total, both successful under the 90-second process-tree-aware logger. Attempt 1 retained its checker snapshot and separate wide-result.json; attempt 2 consolidates that result into result-02.json and records two symbolic identities and four exact original certificate comparisons. Original API certificate subtrees (including expression strings and rational bounds) equal the frozen original JSON data exactly. The original 80 direct-grounded checks remain, plus 64 for the named (3,4,4), [0,9/10], all-16-edge regression. Seven invalid-input checks remain. No additional graph grid was introduced.

Logged child elapsed times were 4.562356 and 2.248650 seconds respectively, each rc0 with empty stderr. These are execution observations, not a controlled speed comparison or proof of a crash fix. The prior profile sampled general simplify at endpoint comparison but did not identify the candidate or crash cause. The original timeout/profile are retained as inputs, not replaced. No assertion of all-input termination is made; general exact simplification elsewhere remains potentially expensive.

Both invocations used outer `uv run --project STAGE --frozen python LOGGER` and explicit child `uv run --project STAGE --frozen python CHECKER --output OUTPUT`; LOGGER was the existing project/experiments/kemeny-three-part-proof/run_logged.py, with --timeout-seconds 90. UV_CACHE_DIR=STAGE/uv-cache, UV_PROJECT_ENVIRONMENT=STAGE/.venv, UV_PYTHON_INSTALL_DIR=D:/uv-python. Raw child argv, environment selection, timestamps, streams and statuses are in logs/. Outer startup on attempt 1 created Python 3.12.11 environment and installed two pinned packages; this is outside the child elapsed time.

Analytic bridges remain the accepted graph inverse/covariance formula, positive endpoint oracles and common factors, complete finite candidate characterization and strict convexity. Finite diagnostics do not prove the universal graph theorem. No physical-impact or generic-method novelty claim is made.
