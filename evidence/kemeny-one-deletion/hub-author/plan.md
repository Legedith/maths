# Frozen approaches and batch 1
1. Generalized quotient Laplacian determinant coefficient ratio, followed by nonnegative-variable coefficient certificate. Selected: bounded 6x6 principal minors, exact polynomials.
2. Rank-two perturbation of full normalized fundamental matrix, derive rational Delta and inequalities. Not selected due to more denominators.
3. Electrical-resistance/spanning-forest update identities, split affected vertex pairs. Not selected due to case proliferation.

Batch 1 command: uv run --python .venv/Scripts/python.exe --no-project batch1.py
Range: symbolic a,b,c; two graphs e=0,1; 6 principal minors of order5 and 15 of order4 each. Substitute a=3+x,b=3+x+y,c=3+x+z and test all coefficients. No numeric sweep. Maximum symbolic script wall time 240 seconds.
Batch 2 reserved for full exact matrix checks at (3,3,3),(3,4,5),(4,4,6).
