# Exact conductance minimax solver

The [result note](../../docs/kemeny-strength-minimax.md) gives the mathematical
characterization and its limits. This implementation accepts rational graph
conductances and rational interval endpoints, with the pinned Python3.12.11,
SymPy1.14.0 and mpmath1.3.0 uv environment.

From the repository root, run the checker with a fresh output in an existing
directory:

```powershell
uv run --project experiments/kemeny-workload-proof --frozen python experiments/kemeny-workload-proof/verify_strength_minimax.py --output strength-minimax-replay.json
```

The checker requires the packaged inert `baseline/result.json` to compare the
four original API certificates. The importable solver needs no baseline file.
See the [endpoint comparison update](../../docs/kemeny-strength-comparison.md).

For an importable solver, put a script beside strength_minimax.py in this
directory and run it with `uv run --frozen python your_script.py`:

```python
from strength_minimax import solve, encode_certificate, InconclusiveError

result = solve(
    n=3,
    edges=[(0, 1, 1), (1, 2, 2)],
    focus=1,
    interval=("0", "1/10"),
    allowed=[(0, 2)],
)
certificate = encode_certificate(result)
```

solve returns exact SymPy expressions. encode_certificate turns them into
exact strings with enclosing rational bounds. The graph is connected,
loopless and undirected with positive present weights and integer labels
0..n-1, n>=3. Parallel weights are summed. Allowed pairs must be distinct,
absent and nonempty. The focus is valid, 0<=l<=h<1, and floats/booleans are
rejected in rational inputs. Malformed domain inputs raise ValueError.

The result includes both endpoint oracles, all oracle actions, every allowed
physical label, exact classes, all candidate strengths, actual volumes and
endpoint objectives, the unique optimum for each class, and every global
location tie. No action is represented once as edge=None,strength=0. The
oracle has the same allowed edges and strength continuum as the chosen action.

## Exact comparison boundary

Nonzero signs require rational intervals lying strictly on one side of zero.
Square-root bounds use integer square roots on dyadic lattices at80,160 and320
bits. Overlapping intervals establish equality only if exact symbolic
simplification proves zero. Otherwise the solver raises InconclusiveError.
Unsupported expressions and unresolved zero-containing divisions also fail
explicitly. No floating tolerance becomes a tie or a recommendation.

The checker catches InconclusiveError, exits3 and writes no result. Symbolic
simplification has no internal wall-clock interrupt, so use a bounded subprocess
for resource control. This is a partial exact comparison implementation: there
is no promise of polynomial time or termination on arbitrarily large rational
inputs. A failed comparison is an implementation limit, not a disproof of the
mathematical finite characterization.

An earlier exploratory invocation using the PR14 solver on344,[0,9/10]
exceeded its60-second subprocess limit and produced no diagnostic result.
The record reports exit124 and132.485 seconds total elapsed, including setup
and subsequent waiting. Retained logs do not identify which calculation
consumed the time. This is a concrete resource limitation on an admitted
input for that version. The current affine endpoint comparison completes this
input in the declared local regression, while general runtime reliability
remains unestablished. The invocation and raw streams are retained under
evidence/kemeny-strength-minimax/resource-limit. The canonical logger below
terminates the process tree on timeout; the exploratory launcher did not.

Ordinary Python assertions must remain enabled. The checker rejects an existing
output before computation and uses exclusive creation. Deterministic sorted
JSON is explicit UTF-8 LF, including runtime versions and hashes of both
modules. No executable evidence expression is loaded. Runtime inputs do not
depend on historical D-stage paths.

## Validation and logged replay

The checker includes the complete344,[0,1/10] witness with16allowed pairs,
four exact classes and11candidate entries. It also checks a weighted path,
a collapsed uniform cycle with tied locations, and the344 untouched-A-only
set whose optimum is no action. Grounded graph inverses at strengths0 and1/2
independently check actual covariance objectives for every physical edge and
both endpoints:80 original comparisons plus64 for the wide interval [0,9/10],
144 in total. Three original and two cross-product symbolic identities, five
abstract balance degeneracies and seven malformed-domain cases supplement
these graph checks. The abstract cases are not asserted graph realizations.

The canonical logged invocation is:

```powershell
uv run --project experiments/kemeny-workload-proof --frozen python experiments/kemeny-three-part-proof/run_logged.py --attempt-id strength-comparison-01 --timeout-seconds 90 --log-dir work/kemeny-strength-comparison/logs -- uv run --project experiments/kemeny-workload-proof --frozen python experiments/kemeny-workload-proof/verify_strength_minimax.py --output work/kemeny-strength-comparison/check-01.json
```

Choose a new attempt ID and output path for another run. On the author's
Windows host, caches and the isolated uv environment remain on D. Original
worker logs, the distinct replay and root canonical artifacts are retained in
the [evidence directory](../../evidence/kemeny-strength-comparison/README.md).
Actual hosted CI requires a separate record for the final pushed commit.

The universal proof additionally uses the separately audited Dirichlet equality,
covariance/inverse identity, positive rank trace, coercivity, continuum endpoint
interchange, strict convexity and candidate completeness. Finite checks do not
enumerate every graph or formalize those arguments in Lean. Randomized/adaptive
actions, multiple insertions, arbitrary demand and costs are outside this API's
theorem. Priority and measured physical benefit remain unresolved.
