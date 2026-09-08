# Final outcome: incomplete certificate, exact obstruction retained

The two-batch budget is exhausted. No universal all-deletion theorem is claimed from this packet.

## Candidate and orbit ledger
- Approach 1 (endpoint orbit quotient certificates): retained as mathematically plausible; execution certificate incomplete due to serialization failure.
- Approach 2 (rank-two direct inequality): not executed; rejected before selection due to denominator complexity.
- Approach 3 (worst-deletion dominance): not executed; rejected because it assumes a stronger unproved ordering.
- Nine original edge orbits reduce to six representative formulas: uB/uC, rB/rC, BC, uh, rh, Bh/Ch. Completeness and the zero-size boundary correction are justified in method.md.
- uB, rB, BC, rh, Bh: all three declared exact examples negative and quotient-identical; full-domain sign remains uncertified by this packet.
- uh: same checks passed; separately already proved in the frozen astra-damage-symbolic-work packet. No files in that packet were changed.

## Raw attempts
Batch 1 exited 1 before mathematical evaluation because Python bool subtraction is unsupported by SymPy Add. batch1-original.py retains the source; batch1.log retains the traceback. The sole arithmetic construction repair converted those booleans to int.

Batch 2 performed all 36 full exact matrix/quotient comparisons and found all 18 differences negative. checks.json retains exact rational values. Each of six symbolic subprocesses then computed both coefficient pairs and reached JSON serialization, but failed with TypeError: Object of type BooleanTrue is not JSON serializable. All six case exit codes are 1, retained in ledger.json and individual .rc files with tracebacks in .log files. The wrapper exit code is 0 because it records failures and continues; it does NOT certify success. Complete symbolic polynomials were held in process memory and lost before being saved. No additional run was performed.

## Precise remaining work
A separately authorized new bounded batch could convert the two positivity flags to native bool before json.dumps and rerun the same six formulas, then independently verify all resulting coefficient identities. This is a serialization repair, but a rerun is still needed to recover actual certificate artifacts; the present logs are insufficient to claim the coefficient lists or full-domain theorem. This packet is frozen. Independent review, novelty, and practical impact remain pending.
