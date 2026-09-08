# Portable Kemeny pair-minimum reproduction

This package reruns the two frozen exact finite censuses and compares every deterministic output byte-for-byte with the sealed baselines. It contains the original graph6 inputs, frozen contract, both mathematical implementations, their exact uv environments, and 11 baseline output files.

The author mathematical source at `author/census.py` is byte-identical to the sealed source. Its only portability issue was a machine-specific `CONTRACT_PATH`. `author/portable_entry.py` imports that unchanged file, verifies its hash, replaces only the imported module's `CONTRACT_PATH` with the byte-identical packaged contract, and calls `run_census`. The independent source is invoked unchanged through its existing CLI.

Both census processes pass through `independent/run_logged.py`, copied byte-for-byte from independent auditor B's sealed wrapper (SHA-256 `b6f4c329387705b2adf67f7dd3f806bbcd0a5906d476f5214fe8278d5ea5bfa6`). This describes the portable integration replay only; it does not repair or restate the chronology of an earlier run.

From the repository root, run:

```text
uv run --project experiments/kemeny-pair-minimum/independent --frozen python experiments/kemeny-pair-minimum/reproduce.py --output-dir work/kemeny-pair-run
```

The command works unchanged on Windows PowerShell and Ubuntu shells. Set `UV_CACHE_DIR` to a writable cache path before running when the environment requires an explicit cache location. The retained Windows evaluation used:

```text
UV_CACHE_DIR=D:/CodexWorkspaces/mathematics-atlas/uv-cache
```

The requested output directory must not already exist and must be outside this immutable package. The runner verifies `source-pins.json` and every pinned source, environment, input, contract, and baseline file before creating the output directory. It then gives each census 1,800 seconds, retains child commands and raw stdout/stderr, and reports whether all 11 files are byte-identical.

To run only one implementation, add `--implementation author` or `--implementation independent`. A failed or timed-out census is retained and is never retried automatically.

This is a portable reproduction of a bounded finite computation. It does not certify novelty or replace independent review.
