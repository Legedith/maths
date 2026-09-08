# Exact workload and one-link robustness checks

See the [theorem and scope](../../docs/kemeny-workload-robustness.md) and
[frozen contract](../../docs/kemeny-workload-robustness-contract.md).
Use uv with the committed lock: Python 3.12.11, SymPy 1.14.0. The continuous
checker itself needs only the standard library. Run ordinary Python with
assertions enabled; do not use `-O` or `PYTHONOPTIMIZE`.

From the repository root, create the output parent if it does not exist, and
choose fresh output names. For example in PowerShell:

```powershell
New-Item -ItemType Directory -Force work/kemeny-workload-replay
uv run --project experiments/kemeny-workload-proof --frozen python experiments/kemeny-workload-proof/verify_workload_envelope.py --output work/kemeny-workload-replay/envelope.json
uv run --project experiments/kemeny-workload-proof --frozen python experiments/kemeny-workload-proof/verify_continuous_perturbation.py --output work/kemeny-workload-replay/continuous.json
```

The envelope output contains 33 exact symbolic checks, formulas and full
positive coefficient lists for four equal-family rational expressions. It
explicitly lists the additional graph, covariance, orbit, sign, tie and
endpoint arguments needing independent analytic review. It does not infer a
universal theorem from a finite grid.

The continuous output retains all 96 contexts and 3,896 quadratic comparisons
for graphs333/334/345/446, theta0/0.1/0.5, and any single existing edge changed
throughout [-10%,10%]. The conclusion is that the new optimal set is contained
in the old set. Ties inside that set can break. It is not a simultaneous-box
or arbitrary-graph-size certificate.

Both programs reject an existing output in the documented invocation. The
continuous checker uses an assertion for this guard and performs computation
before that check; the envelope checker rejects before computation.

For raw command records use the established logger and an explicit uv child:

```powershell
uv run --project experiments/kemeny-workload-proof --frozen python experiments/kemeny-three-part-proof/run_logged.py --attempt-id envelope-replay --timeout-seconds 60 --log-dir work/kemeny-workload-replay/logs -- uv run --project experiments/kemeny-workload-proof --frozen python experiments/kemeny-workload-proof/verify_workload_envelope.py --output work/kemeny-workload-replay/envelope-logged.json
```

Use a fresh attempt ID and output on each replay. The logger creates the log
parent and records exact argv, cwd, UTC times, exit status and raw streams.
The [integration packet](../../evidence/kemeny-workload-robustness/integration/summary.json)
retains the initial missing-SymPy child failure and explicit-uv recovery.
Historical stage scripts in the evidence packet are frozen research records;
the two scripts in this directory are the portable entry points.
