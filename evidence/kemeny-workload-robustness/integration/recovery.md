# Integration launcher recovery

The first logged envelope attempt, envelope-01, returned 1 with
ModuleNotFoundError: No module named 'sympy'. It did not produce its requested
result. Its stdout, stderr and status record remain unchanged.

A direct `uv run --project experiments/kemeny-workload-proof --frozen python`
probe successfully imported SymPy 1.14.0 and reported the project's
`.venv/Scripts/python.exe`. The failed logger launched a bare child `python`;
the probe does not establish that this child used the same interpreter.

Recovery changes only the invocation: the logger launches `uv run --project
experiments/kemeny-workload-proof --frozen python` explicitly. The proof code,
package lock and frozen mathematical specification remain unchanged. Use fresh
attempt envelope-02 and output envelope-02.json. Apply the same explicit uv
child invocation to the first continuous attempt and new CI steps.
