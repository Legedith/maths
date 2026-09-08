# Exact source-target conductance minimax

The graph is undirected. A request starts uniformly and independently selects
its target from (1-theta)Uniform+theta delta_focus, with0<=l<=h<1. This is a
separate API from the earlier iid-mixture solver. See the [result and model
boundaries](../../docs/kemeny-source-target.md).

From the repository root, with a fresh output in an existing directory:

```powershell
uv run --project experiments/kemeny-source-target-proof --frozen python experiments/kemeny-source-target-proof/verify_source_target.py --output source-target-replay.json
```

For an importable call, place a script beside the three modules:

```python
from source_target_minimax import solve, encode_certificate, InconclusiveError
result = solve(3, [(0, 1, 1), (1, 2, 2)], 1, ("0", "99/100"), [(0, 2)])
certificate = encode_certificate(result)
```

Run that script with uv run --project experiments/kemeny-source-target-proof
--frozen python PATH from the root. Inputs require integer labels0..n-1,
connected loopless graphn>=3, positive rational weights, a valid focus and a
nonempty set of distinct absent pairs. Parallel present weights merge. Floating
and boolean rational inputs reject. All candidate objectives retain m+t.

The return includes exact quadratic coefficients, root classifications,
endpoint oracles with the same allowed edges and strength continuum, all
candidates and unique strength per physical edge, tied global locations and
one no-action label. Negative curvature is allowed. Boundary, stationary and
quadratic balance cases include identical/constant/linear/repeated/nonreal/zero/
negative/duplicate roots. No evidence expressions are executed.

Package source_target_minimax.py, verify_source_target.py, exact_support.py,
pyproject.toml, uv.lock and .python-version. exact_support.py is a pinned copy
of the prior module; only rational/comparison/minimum/encoding/error utilities
are imported, never its iid solve function. Runtime paths do not depend on D
staging directories. Python3.12.11, SymPy1.14.0 and mpmath1.3.0 are pinned.

The checker has30direct first-step hitting comparisons,3symbolic identities,
7abstract root cases and7malformed inputs. It pins all three module hashes,
requires assertions, checks for existing output before work and uses exclusive
UTF-8 LF creation. Existing-output rejection was independently verified.
Partial exact comparison can raise InconclusiveError; the CLI then exits3
without a result. Symbolic simplification may be expensive. These finite cases
do not formalize the analytic proof or guarantee all-input termination.

Canonical bounded replay (choose a fresh attempt/output for another run):

```powershell
uv run --project experiments/kemeny-source-target-proof --frozen python experiments/kemeny-three-part-proof/run_logged.py --attempt-id source-target-01 --timeout-seconds 90 --log-dir work/kemeny-source-target/logs -- uv run --project experiments/kemeny-source-target-proof --frozen python experiments/kemeny-source-target-proof/verify_source_target.py --output work/kemeny-source-target/check-01.json
```

Both outer logger and child use uv. On the author's Windows host, environment
and cache stay on D. The logger terminates the process tree on timeout. Raw
worker, distinct replay and root results are in the [evidence guide](../../evidence/kemeny-source-target/README.md).
Hosted CI requires separate post-push inspection for the final commit.
