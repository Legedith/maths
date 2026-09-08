# Independent one-deletion theorem review

Verdict: PASS for the frozen author's one-deletion theorem; all four integrity gates pass. This is a separate theorem from the all-r undamaged result. Auditor /root/astra_general_proof_verifier authored neither candidate nor certificate. New portable implementation and publication prose are outside this verdict.

## Reproduction: PASS

Evaluator contract was frozen in evaluator-contract.md before execution. evaluate.py reconstructs each entire determinant det(L+tD) by all 720 signed permutation products in an exact polynomial ring; it does not use the author's principal-minor sums. Extracted t and t^2 coefficients match symbolic.json:/q0 and /q1 exactly, and their cross-product numerator matches /N. The shifted coefficient dictionary agrees entry-for-entry with /negative_N_shift_terms: 284 terms, smallest coefficient 6, constant 1784916000, degree 10 (result.json:/terms,/minimum,/constant,/degree).

All six independently built full adjacency/fundamental matrices agree with quotient ratios plus n-6 and with checks.json:/full_matrix_checks. Differences: (3,3,3) -787/41664; (3,4,5) -89013391/6289074792; (4,4,6) -3360439/385735350. Exact values are in result.json:/matrix_checks and round2-run.json:/stdout. These are implementation diagnostics; the symbolic identity proves the full-domain sign.

A first evaluator run failed at dictionary comparison because author coefficients were decimal strings and reviewer coefficients integers. All determinant and numerator assertions had already passed. evaluate-round1.py and run-2.json retain that failure. Round 2 changed only conversion of stored coefficients to int; round2-plan.md records this before execution. round2-run.json records rc=0. No mathematical defect, expanded parameter range, or additional search was hidden by this correction.

## Specification compliance: PASS

The six cells {u},{v},A-rest,B,C,{h} have sizes 1,1,a-2,b,c,1. Direct neighbor inspection yields the displayed R_e: u lacks h and gains v precisely when e=1; v has h and gains u; A-rest sees B,C,h; B and C see every other original part; h sees all except u. Each row sum is the common positive degree within its cell. Thus the full transition operator sends cell-constant vectors to cell-constant vectors with quotient D^-1 R.

For a vector supported on A-rest, B or C with coordinate sum zero, every output coordinate is zero: inside the cell there are no edges, while each outside row has identical transition weight to every vertex of the cell. The three zero-sum subspaces have dimensions a-3,b-1,c-1 and are disjoint from the six-dimensional cell-constant subspace. Their dimensions sum to n-6, and direct decomposition of each cell's coordinates proves the subspaces span the entire space. This also works when a=3. Therefore the full spectrum is the quotient spectrum together with exactly n-6 extra zero eigenvalues, including multiplicity; any additional zeros already in the quotient cause no problem.

Both full graphs are connected (u connects through B or C to all other cells) and undirected with strictly positive degrees. D_full^(1/2) P D_full^(-1/2) is real symmetric. Its eigenvalues are <=1; connectedness makes 1 simple. The invariant quotient therefore has 1 simple and five remaining eigenvalues strictly less than 1. With mu_i=1-lambda_i, det(L+tD)=det(D)*t*product_(i=2..6)(t+mu_i). Hence q_e1=det(D)*product mu_i>0 and q_e2/q_e1=sum 1/mu_i. The omitted full modes each contribute 1, establishing K=n-6+q_e2/q_e1 and the stated signed numerator N over the strictly positive product q_11*q_01. No unproved quotient stationary-distribution assumption is needed.

The substitution x=a-3,y=b-a,z=c-a is a bijection between the allowed integer tuples and nonnegative integer triples. Every scalar coefficient of -N is positive with positive constant, so N<0 throughout this domain. Combined with denominator positivity this proves Delta<0.

The endpoint scope must remain precise: any choice of u in any selected minimum part and any distinct v in that same part is covered when the deleted edge is that u's edge to h. For a fixed damaged H, permutations fixing u act transitively on choices of v in its part. Relabelling also permits tied minima as the original selected part. This theorem does not assert that every missing edge elsewhere in H, or even every same-part edge not incident to u, improves K. It does not cover arbitrary deletions, p>1, or more than three non-singleton parts.

## Source verification: PASS for the self-contained claim

The target is frozen in ../kemeny-discovery-round-1-work/one-deletion-proof-contract.md. The graph-to-spectrum and determinant-ratio bridges above are proved directly from the graph definition and elementary linear algebra; no external paper or unverified update identity is an input. The author's proof.md exact-reduction and sign-certificate sections match these arguments. Therefore the source gate certifies entailment from the frozen graph/convention, not literature novelty. Publication priority, worst-deletion dominance, general robustness, and practical impact remain unestablished. The author explicitly preserves these limits.

## Implementation alignment: PASS for frozen author packet

Compared the independently reconstructed polynomials and diagnostics to the actual symbolic.json and checks.json, not merely the proof's summary. Author batch1.py uses determinant multilinearity via principal minors; the reviewed full determinant is mathematically independent of that algorithm. Author plan.md lists three approaches and freezes symbolic domain/two states; batch2-plan.md freezes exactly the three diagnostic tuples used here. The proof correctly states the zero-diagonal stationary-target convention, sign, constant, degree and diagnostic values. No selected portable checker has been reviewed in this packet.

## Evidence retention

run.py records actual argv, cwd, stdout, stderr and returncodes in run-0.json through run-2.json; round2-run.py retains the corrected evaluator execution separately. Environment: isolated D-drive .venv, uv-created CPython 3.12.11 with SymPy 1.14.0; UV_CACHE_DIR=D:/CodexWorkspaces/mathematics-atlas/uv-cache. hashes.json pins the specification, author proof/certificate/diagnostics, final and original evaluators, raw runs, result, runtime executable and this report. The executable hash identifies the venv launcher, not the entire Python distribution. Shared files were read only. The review took two bounded rounds and is complete for this scope.
