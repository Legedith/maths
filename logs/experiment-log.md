# Chronological experiment log

## 2026-09-08 — contract inspection

- Command: `Get-Content chain-of-evidence/SKILL.md; Get-Content task-spec.md; Get-Content fixtures/frozen.json`
- Exit code: 0
- Result: selected Laplacian bridge contract and immutable fixture set read before implementation.
- Artifacts: `task-spec.md`, `fixtures/frozen.json`.

## 2026-09-08 — evidence contract inspection

- Command: `Get-Content chain-of-evidence/references/evidence-contract.md; Get-ChildItem engine-work; rg --files src; rg --files tests`
- Exit code: 0
- Result: evidence requirements read; workspace contained only frozen specification and fixtures, with no prior implementation files.
- Artifacts: `task-spec.md`, `fixtures/frozen.json`.

## 2026-09-08 — initial implementation

- Action: added the package, strict validator, exact linear solver, Laplacian resistance path, independently constructed Markov first-step path, connectivity-only exhaustive tree oracle, CLI, deterministic evaluator, tests, runner, and engine documentation with `apply_patch`.
- Result: implementation files created only under the worker-owned paths.
- Artifacts: `src/atlas_engine/`, `tests/`, `scripts/run-canonical.ps1`, `pyproject.toml`, `README-engine.md`.

## 2026-09-08 — environment creation

- Tooling failure before command execution: the first command wrapper was malformed and returned `SyntaxError: Unexpected end of input`; no shell command ran and no workspace state changed.
- Command: `$env:UV_CACHE_DIR = 'D:\CodexWorkspaces\mathematics-atlas\uv-cache'; uv sync`
- Exit code: 0.
- Result: CPython 3.13.7 environment created at `.venv`; 7 packages resolved; local `atlas-engine==0.1.0` and pytest dependencies installed; `uv.lock` generated.
- Limitation: uv emitted warnings while skipping obsolete Pygments distributions; installation completed successfully.
- Artifacts: `.venv/`, `uv.lock`.

## 2026-09-08 — first unit and integration test run

- Command: `$env:UV_CACHE_DIR = 'D:\CodexWorkspaces\mathematics-atlas\uv-cache'; uv run --frozen pytest`
- Exit code: 0.
- Result: 31 tests passed in 0.82 seconds.
- Coverage exercised: frozen valid and invalid fixtures, non-edge applicability, canonical output, additional strict boundaries, exact solver pivot/singularity handling, CLI analysis, and canonical evaluator counts.

## 2026-09-08 — first standalone canonical evaluation

- Command: `$env:UV_CACHE_DIR = 'D:\CodexWorkspaces\mathematics-atlas\uv-cache'; uv run --frozen python -m atlas_engine evaluate --output-dir logs/canonical`
- Exit code: 0.
- Metrics: 771 exhaustive labeled connected graphs (`n=2: 1`, `n=3: 4`, `n=4: 38`, `n=5: 728`), 1 named 6-vertex fixture record, 772 total records, 1 selected existing edge per graph, 7 valid fixtures checked, 10 invalid fixtures rejected, 0 failures, exact comparisons, no sampling.
- Artifacts: `logs/canonical/records.jsonl`, `logs/canonical/summary.json`.

## 2026-09-08 — contract-gap correction

- Finding: initial implementation included a machine-readable input schema but the frozen specification also requires a basic output schema.
- Action: added `src/atlas_engine/output-schema.json`, documented it, and strengthened fixed exact assertions for both hitting directions, commute time, and selected-edge tree count.
- Result: identified gap corrected before final canonical artifacts.

## 2026-09-08 — post-correction test run

- Command: `$env:UV_CACHE_DIR = 'D:\CodexWorkspaces\mathematics-atlas\uv-cache'; uv run --frozen pytest`
- Exit code: 0.
- Result: 31 tests passed in 1.08 seconds.

## 2026-09-08 — deterministic canonical rerun

- Command: `$env:UV_CACHE_DIR = 'D:\CodexWorkspaces\mathematics-atlas\uv-cache'; uv run --frozen python -m atlas_engine evaluate --output-dir logs/canonical`
- Exit code: 0.
- Result: `passed=true`; counts and metrics matched the first standalone canonical run exactly; 0 failures.
- Command: `Get-FileHash -Algorithm SHA256 -LiteralPath logs/canonical/records.jsonl,logs/canonical/summary.json`
- Exit code: 0 on both pre-rerun and post-rerun hash inspections.
- Determinism evidence: `records.jsonl` SHA-256 remained `B05D83051BA0F92713C87CED4742D1A902297B998D6F221250BEF0F80890DD8C`; `summary.json` SHA-256 remained `2A76C8D91764B07983B8012BAA5FE338241F2D0AC28691AF9FB2783623015C0C`.
- Artifacts: `logs/canonical/records.jsonl`, `logs/canonical/summary.json`.

## Current limitations and handoff boundary

- The exhaustive evaluator selects one existing edge per graph rather than all edges; this is declared in every summary via `selection_policy` and `edges_analyzed_per_graph`.
- Exhaustive coverage is bounded to labeled connected simple graphs on 2–5 vertices plus the named 6-vertex fixture, exactly as frozen; the engine accepts arbitrary admitted 6-vertex inputs but does not exhaust all of them.
- The worker tests and evaluator runs are raw implementation evidence only. An independent verifier must assess specification compliance and method/code alignment; this log does not certify either gate.

## 2026-09-08 — final environment and artifact inventory

- Commands: `uv --version`; `uv run --frozen python --version`; inspect `uv.lock` byte length; count `logs/canonical/records.jsonl` lines.
- Exit code: 0.
- Environment: uv 0.8.19; Python 3.13.7; isolated environment at `.venv`; cache at `D:\CodexWorkspaces\mathematics-atlas\uv-cache`.
- Metrics: `uv.lock` is 4,652 bytes; canonical JSONL contains exactly 772 lines.
- Artifacts: `uv.lock`, `.venv/`, `logs/canonical/records.jsonl`.
