# Exact deterministic unit-repair minimax checker

This entry point verifies the portable algebra and finite witnesses for the
[complete rule](../../docs/kemeny-unit-minimax.md), under its
[frozen contract](../../docs/kemeny-unit-minimax-contract.md). Use the existing
locked Python 3.12.11, SymPy 1.14.0 and mpmath 1.3.0 uv environment.

From the repository root, choose a fresh output in an existing directory:

```powershell
uv run --project experiments/kemeny-workload-proof --frozen python experiments/kemeny-workload-proof/verify_unit_minimax.py --output minimax-replay.json
```

Ordinary Python assertions must remain enabled. Existing output is rejected
before computation, and exclusive creation protects the write. JSON uses
explicit UTF-8 LF, stable ordering, exact rational values, runtime versions and
the actual implementation hash. No historical expression string is evaluated;
the portable entry point has no D-specific runtime dependency.

The canonical logged invocation uses a fresh attempt and output:

```powershell
uv run --project experiments/kemeny-workload-proof --frozen python experiments/kemeny-three-part-proof/run_logged.py --attempt-id minimax-01 --timeout-seconds 60 --log-dir work/kemeny-unit-minimax/logs -- uv run --project experiments/kemeny-workload-proof --frozen python experiments/kemeny-workload-proof/verify_unit_minimax.py --output work/kemeny-unit-minimax/check-01.json
```

For a new logged replay, change both the attempt ID and output path. The logger
creates its log directory and parents. On the author's Windows host, caches
and environments stay on D; uv's existing proof environment is isolated.

The checker reconstructs the exact unequal-family rational identity and every
coefficient in both shifted numerator/denominator pairs. It checks positive
nonzero coefficients and constants, the quotient derivative identity, ten
policy illustrations, and two abstract affine examples. The importable
unit_policy(a,b,c,lo,hi) returns every physical minimax edge for sorted integer
part sizes and exact rational interval endpoints. Use rational strings for
noninteger endpoints. Illustrations include collapsed intervals, both boundary
crossings, interior product ties, tau>=1 and equal largest-part ties; they are
interface cases, not a graph search or universal enumeration.

The two graph witnesses directly reconstruct all candidate Laplacian inverses:
ten for 333 unit insertion with restoration, and twelve for 334 at strength16
without restoration. Exact actual volumes, endpoint/midpoint objectives,
regrets, labels and gaps are retained. The 33100 policy illustration also
returns all 4950 largest-part pairs to preserve the complete-label contract;
no 107-vertex matrix inversion is performed for it.

The output explicitly names analytic bridges requiring the distinct
mathematical audits: the commute/covariance and universal graph-inverse
formulas, integer-shift coverage, full-domain positivity, equal-family envelope,
strict domination, endpoint reduction and complete tie classification. The
checker does not mechanically formalize these bridges in Lean.

The [evidence directory](../../evidence/kemeny-unit-minimax/README.md) keeps the
worker's original packet, distinct implementation replay, root canonical logs,
source review and final integration review. Historical failed strength
conjecture attempts remain unchanged. Actual hosted CI requires a separate record
for the final pushed commit; a local PASS alone does not assert hosted completion.
