# One-run solver profile

Scope: unchanged solver SHA256 11152f62717a691450361c4227a70eb7674e65b1c3bb3d5889464956898ad1a9, graph (3,4,4), interval [0,9/10], all missing edges. This is a diagnostic author packet, not an independent implementation certification. Other stages and the original timeout record remain unchanged.

## Observations and typed evidence

- RUN-1 (raw execution): logs/attempt-profile01.json records exactly one explicit uv child invocation, 30-second limit, Python 3.12.11 environment creation, frozen dependency resolution, start 2026-09-08T19:42:21.161315+00:00 and end 19:42:36.371845+00:00 (15.210530 seconds). Child return code 3221225477, timed_out=false, termination=null; outer launcher shell exit code was 1. There was no timeout cleanup invocation for this run.
- PHASE-1 (flushed stdout): wrapper_started at monotonic 310434.953, before_sympy_import 310434.968, after_sympy_import and before_solve 310437.250. Import took approximately 2.282 seconds. Environment installation preceded wrapper startup and cannot be attributed to solve. No after_solve or serialization marker appeared.
- STACK-1 (raw stderr): first five-second traceback reaches profile_wrapper.py:20 -> strength_minimax.py:171 -> maximum:75 -> minimum:72 -> compare:61 -> SymPy simplify.py:611. The inner stack performs assumptions/sign inference and minimal-polynomial construction/factorization. Thus the sampled delay was in comparing endpoint regrets during candidate evaluation, not graph construction or output serialization.
- EXIT-1 (raw stderr): the second periodic dump is incomplete and is followed by Windows fatal exception: access violation. The child code is 0xC0000005. The record does not establish whether the fault came from instrumentation, runtime, or another cause. It does not reproduce the earlier 60-second timeout as such.
- LIMIT-1 (inference boundary): one sampled full stack localizes an observed expensive path, not its total runtime share, exact edge/candidate, or the original timeout's complete cause. No result.json was produced. No retry or solver modification was performed.

The exact argv, working directory, UV_CACHE_DIR and UV_PROJECT_ENVIRONMENT are in the raw attempt JSON. The invoking shell additionally set UV_PYTHON_INSTALL_DIR=D:/uv-python and used D:/uv-python/cpython-3.12.11-windows-x86_64-none/python.exe for the logger. The logger is the existing process-tree-aware run_logged.py, SHA256 b6f4c329387705b2adf67f7dd3f806bbcd0a5906d476f5214fe8278d5ea5bfa6. The pinned copied pyproject.toml and uv.lock are retained. All observed streams are raw, including dependency startup and the incomplete crash traceback.

## Proposed bounded optimization, not implemented

For a fixed edge, write B_j=r*T_j-s_j and endpoint oracle O_j>0. The two normalized candidate objectives differ by

    (m+t)/(1+r*t) * ((T_0+B_0*t)/O_0 - (T_1+B_1*t)/O_1).

The common factor and both oracle denominators are positive. Therefore select the larger endpoint using the sign of the affine cross-product

    N(t)=(T_0+B_0*t)*O_1-(T_1+B_1*t)*O_0.

At a certified balancing candidate, N(t)=0 follows directly from its defining numerator/denominator and the already checked nonzero denominator. This allows exact endpoint equality without asking general simplify to discover it from nested full regret expressions. Coincident branches likewise have both coefficients zero. This is a plausible targeted way to avoid the observed path while preserving the exact maximum certificate; the trace does not identify whether the sampled candidate was balancing, so it is not a proven fix.

A future implementation should retain exact sign certification for nonbalancing cases, verify the cross-product identity and positive factors, cover zero/parallel/coincident branches, and return inconclusive when its bounded comparator cannot certify a sign. It must undergo a fresh independent review and regression against existing outputs plus this input. No speed, completion, or crash-prevention claim is made here.

One attempt total. Current frozen release and solver bytes are unchanged.
