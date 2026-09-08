# Candidate theorem: safety after any one original edge deletion

Independent verification pending; this author does not certify the final semantic gate.

For every integer 3<=a<=b,c, every two distinct vertices u,v of the a-part, and every original edge f of G=K_(a,b,c) join K1, the stationary-target simple-random-walk Kemeny constant satisfies

    K(G-f+uv) - K(G-f) < 0.

The proof is the complete endpoint-orbit reduction and quotient argument in method.md, combined with the six exact coefficient certificates in uB.json, rB.json, BC.json, uh.json, rh.json, Bh.json. Each file defines q_e1,q_e2 as determinant coefficients, the canceled rational numerator N and denominator D of Delta, and all monomials of -N and D after a=3+x,b=3+x+y,c=3+x+z. Positive coefficients with positive constants establish -N>0 and D>0 on the full parameter domain. There is no assumption that uh is a worst deletion. The uh orbit was previously proved separately; five representative cases, covering eight additional labeled categories together with the old category, complete the new all-deletion statement.

Important boundary detail: some quotient constructions contain an empty A-rest cell at a=3. method.md proves that this formal cell contributes exactly one artificial transition eigenvalue zero, canceled by the n-m term. This case is not silently excluded.

## Recovery history
This packet comes from ONE explicitly authorized additional execution beyond the original two-batch cap, as recorded in amendment.md. The original first batch failed before evaluation on bool subtraction; the original second batch passed 36 exact matrix/quotient comparisons and 18 negative differences but all six symbolic subprocesses failed on JSON serialization. Those frozen failures remain in astra-all-deletions-work. They are not reclassified as successes or excluded from the original budget.

The recovery copies the original source and changes only the two positivity flags to native bool for JSON serialization (plus an incidental final blank line); source.diff records the exact difference. recover.py runs precisely the six previously declared symbolic cases, each capped at 300 seconds, and aggregates nonzero child exit codes or sign failures into a nonzero aggregate status. No finite grid was rerun and no mathematical method, domain, or symbolic case was changed.

The raw recovery.log contains the wrapper transcript; individual .stdout and .stderr files retain child streams; recovery-ledger.json retains argv, runtime, rc and certificate statuses. input-hashes.json binds all execution inputs. The environment is an isolated stage-local uv virtual environment with Python 3.13.7, SymPy 1.14.0 and mpmath 1.3.0; UV_CACHE_DIR is stage-local. The exact execution command was:

    uv run --python .venv/Scripts/python.exe --no-project recover.py

The mathematical certificate still needs an independent identity check and review of the orbit completeness, graph construction, spectral reduction, empty-cell boundary, and full-domain sign logic. Publication novelty and practical impact remain unresolved. The result concerns a single deletion of an original edge; it makes no multi-deletion claim.

## Observed recovery outcome
All six child return codes and the aggregate return code are 0. Both positivity flags are true for every case. certificate-summary.json records term counts and strictly positive constants from the saved complete certificates. The full-domain certificate construction therefore succeeded; independent review remains pending.
