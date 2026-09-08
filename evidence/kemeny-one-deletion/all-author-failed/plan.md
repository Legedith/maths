# Frozen all-single-deletion task
Domain integer a,b,c>=3, a<=b,c; G=K_(a,b,c) join K1; fixed u,v in A. Claim: for every original edge f, K(G-f+uv)-K(G-f)<0. No worst-deletion assumption. Prior uh result is frozen elsewhere and used only as a known comparison.

Approaches:
1. Enumerate endpoint orbits and certify each quotient determinant numerator after a=3+x,b=a+y,c=a+z. Selected.
2. Rank-two edge update formula and universal inequality; rejected for algebraic denominator complexity.
3. Prove worst-deletion dominance, then reuse uh; rejected because dominance is unproved and stronger than needed.

Orbit enumeration under permutations fixing unordered {u,v}: uB,uC,rB,rC,BC,uh,rh,Bh,Ch (r in A except u,v). Exchanging labels B,C reduces these to six representative formulas: uB,rB,BC,uh,rh,Bh. Since b,c both independently range >=a, the exchanged cases are covered by variable renaming.

Batch 1 frozen: uv run --python .venv/Scripts/python.exe --no-project batch1.py. Exact full-matrix and twin-quotient comparisons for six representatives at exactly (3,3,3),(3,4,5),(4,4,6). Stop immediately on nonnegative Delta; save witness. No grid.
Batch 2 frozen conditional on batch1 passing: uv run --python .venv/Scripts/python.exe --no-project batch2.py. Exactly six representative symbolic cases uB,rB,BC,uh,rh,Bh, each with e=0,1. Finite principal minor sums for coefficients t,t^2. Expand rational Delta, cancel factors, then test all coefficients of negative numerator at a=3+x,b=3+x+y,c=3+x+z; test denominator positivity by same coefficient test if necessary. At most 300 seconds per case. Stop case on failure; no retries or further symbolic route. Store complete coefficient lists and raw output. No further batches permitted.
