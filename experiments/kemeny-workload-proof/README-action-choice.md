# Exact action-choice certificate

This checker covers the [equal-family improvement theorem,344no-action
interval and exact strength rescue](../../docs/kemeny-workload-action-choice.md).
Use the existing pinned uv environment: Python3.12.11 and SymPy1.14.0.
Run ordinary Python with assertions enabled, without `-O` or `PYTHONOPTIMIZE`.

From the repository root, create the parent directory and choose a fresh path:

```powershell
New-Item -ItemType Directory -Force work/kemeny-action-replay
uv run --project experiments/kemeny-workload-proof --frozen python experiments/kemeny-workload-proof/verify_action_choice.py --output work/kemeny-action-replay/result.json
```

The output contains full shifted positive coefficients for five equal-family
expressions; the complete344unit/no-action policy; all16candidate margins and
strength quantities; rational strength/minimum bounds; the unit excess and
half-strength improvement. It records the implementation hash and runtime.
The program builds expressions directly and does not execute expressions from
evidence files. Existing output is refused before computation and by exclusive
file creation. JSON uses explicit UTF8 LF.

Graph/covariance reduction, the accepted equal-family envelope, positivity
from coefficients, affine interval reasoning and calculus proving global
strength minima remain explicit independently audited analytic bridges. This
is not a proof-assistant formalization or a theorem about every unequal graph.

For a retained raw command record, use a fresh attempt ID and output:

```powershell
uv run --project experiments/kemeny-workload-proof --frozen python experiments/kemeny-three-part-proof/run_logged.py --attempt-id action-replay --timeout-seconds 60 --log-dir work/kemeny-action-replay/logs -- uv run --project experiments/kemeny-workload-proof --frozen python experiments/kemeny-workload-proof/verify_action_choice.py --output work/kemeny-action-replay/logged.json
```

The explicit uv child selects the same pinned environment. The root canonical
run and independent replay are in the [evidence packet](../../evidence/kemeny-workload-action-choice/README.md).
Historical stage scripts and paths are frozen records; this file's command is
the portable entry point. Earlier workload/one-old-link checks retain their
[separate instructions](README.md).
