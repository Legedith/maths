# Replaying two source-summary mistakes with existing tools

These examples show why a mathematical search result needs its definitions and
assumptions attached. Both mistakes were already identified during source review.
We use SymPy and Z3 to retain exact, reproducible witnesses; neither original
paper is alleged to be wrong.

| Reviewed generated summary | Frozen example | Source expression | Summary expression |
| --- | --- | --- | --- |
| Row 23150070 replaces an indexed eigenvalue product with a product of only nonzero eigenvalues. | Two disconnected unit edges on four vertices; spectrum 0, 0, 2, 2. | 0 spanning trees | 1 |
| Row 23832572 replaces weighted spanning-tree masses with ordinary counts. | Triangle with conductances 2, 1, 1; resistance across the edge of conductance 2. | 2/5 | 1/3 |

For the first case, [Theorem 1.2, page 2](https://arxiv.org/pdf/0802.2576v2)
omits one designated zero; additional zero eigenvalues remain in the product.
For the second, [Corollary 4.7, page 15](https://arxiv.org/pdf/2109.01324v2)
uses weighted tree masses defined on pages 5 and 12. Its three tree weights are
2, 2 and 1. Treating those trees equally changes the answer.

## Reproduce

From a checkout with [uv](https://docs.astral.sh/uv/) installed:

```powershell
uv run --project experiments/external-witness-replay --frozen python scripts/reproduce_external_witness.py --output-dir work/external-witness-reproduction
```

Choose a new output directory on each run. uv creates an isolated environment
with Python 3.12.11, SymPy 1.14.0, z3-solver 5.1.0.0 and mpmath 1.3.0. The wrapper
checks the frozen inputs, runs the original calculation, and runs an independent
standard-library arithmetic certificate. It retains exact commands, outputs,
exit codes, solver assertions and results. The certificate verifies rational
equations, determinants and exhaustive tree enumeration without SymPy or Z3.

## What the review establishes

An independent source reviewer checked both encodings before execution. A
separate verifier reproduced the calculation in another isolated environment
and checked the arithmetic certificates. All 11 frozen expected fields passed;
all nine outputs other than the command record matched the author run byte for
byte in that copied reproduction. The correct source expressions also match
within these two instances.

The [independent audit](evidence/external-witness/independent/final-external-witness-audit.json)
records its exact scope. The [evidence bundle](.codex/evidence/runs/external-witness-v1/bundle.json)
connects claims to code, source review and raw results. Historical files that say
"pending" remain unchanged; the later independent audit supplies the decision.
The [transfer record](evidence/external-witness/integration-transfer.json) maps
historical staging paths to the files in this checkout.

These are disclosed examples, not new detections, new mathematics, a general
accuracy estimate, or evidence of researcher time saved. They do not change the
earlier 24-result study's zero incremental source-refutation detections. They
also do not prove either theorem for all graphs. The rejected first preexecution
attempt remains recorded. The separate readiness task exceeded its time cap;
the combined implementation workflow's timing compliance was not certified.

The next use is to attach exact witnesses to reviewed source packets where they
help explain a mismatch. This small experiment is complete; it does not justify
building another general solver.
