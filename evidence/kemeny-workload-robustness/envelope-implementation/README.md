# Portable common-strength workload symbolic checker

Run from this directory, selecting an output path that does not exist:

```powershell
$env:UV_CACHE_DIR='D:/CodexWorkspaces/mathematics-atlas/astra-workload-portable-work/uv-cache'
$env:UV_PROJECT_ENVIRONMENT='D:/CodexWorkspaces/mathematics-atlas/astra-workload-portable-work/.venv'
uv sync --frozen
uv run --frozen python verify_workload_envelope.py --output fresh-result.json
```

The environment locations above are local isolation settings, not checker inputs. The CLI itself has no D-specific paths or external certificate/proposal dependency. Python is pinned exactly3.12.11, SymPy1.14.0, uv package=false; uv.lock is generated and frozen. The output parent must exist. --output is required; existing outputs are rejected before computation, and exclusive mode x prevents overwrite even if a file appears during computation. JSON is UTF-8 with deterministic key ordering, exact formula strings, full coefficients, runtime versions and code hash. No timestamps or absolute paths enter the certificate.

certificate() explicitly constructs the rational expressions from symbols. Its33 checks cover restore/incident/untouched scores and slopes, denominator difference/unit reductions, E and N identities, bound remainders, unequal crossing/derivative/limits and n=d+a sign bounds, equal crossing/derivative/closed form/limits/complement/unit reduction, and complete positive shifted coefficients. The four rational expressions with complete coefficient lists are equal zero-limit, infinity-limit, zero-limit complement and unit specialization. Each numerator and denominator is canceled after a=x+3 and emitted in descending order including every degree; each coefficient must be strictly positive. No sample-based positivity claim or blind multivariate expansion is used. Assertions raise on nonzero residuals or nonpositive coefficients.

The JSON PASS applies to these symbolic checks. It expressly lists additional analytic bridges: graph inverse action; workload covariance/commute normalization; orbit exhaustion and accepted common-strength uniform ordering; positive-domain interpretation of factored bounds; envelope exclusion; symmetry ties; endpoint/limit conventions; and transition invariance under uniform old-weight scaling. Identities alone do not prove these bridges. No new matrix grid, joint strength optimizer, no-action rule, global priority or physical-impact claim is supplied.

The selected source is the frozen astra-weight-workload-family-work/proposal.md SHA256973868b9277394cb1fe6a1e3abfc659481ff19a8c3a7e77b7bb96cb5e0254850. It was used to define the expressions, not loaded or executed by the CLI. Its independent analytic review is separate.

Implementation execution: one evaluator attempt only, timeout60s, elapsed10.906s, rc0, empty stderr; all33 checks PASS. attempt1.json and attempt1.stdout.bin/attempt1.stderr.bin retain argv/cwd/status/streams. No numerical failure or second attempt occurred. run.py is the local logging harness; it is not required to use the portable CLI. uv lock and uv sync --frozen succeeded; their setup streams/return codes are retained separately. Negative-interface testing was left to independent changed-interface review rather than consuming another symbolic attempt.

Author /root/astra_damage_symbolic owns this implementation and does not certify a final code/evidence gate. Root integration, independent changed-interface verification and final publication review remain pending. No repository, Git, Sites or other stage was changed.
