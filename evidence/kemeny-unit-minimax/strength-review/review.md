# Independent counterexample audit

Four scoped integrity checks: PASS.

Scope: H=(K_(3,3,4) join K1)-uh; all original edges have weight 1; exactly one allowed missing edge has common weight t=16; restoration uh is forbidden. The same iid law p=(1-theta)1/11+theta e_h, theta=9147/9152, is used for every action. No action and optimization over strength are excluded. This is a finite counterexample, not a universal ordering or public-code approval. Excluded from PR12.

## Typed numerical evidence and reproduction: PASS

One independent evaluator run, rc=0, timeout 60 seconds, elapsed 1.0504705905914307 seconds, empty stderr. Exact argv and cwd are in run.json; raw streams are stdout.bin and stderr.bin. No second reviewer evaluator was needed. check.py constructs the entire adjacency matrix independently and inverts every grounded post-insertion Laplacian using exact SymPy arithmetic. It verifies L M=I-J/n for each centered inverse and enumerates all 12 allowed missing edges.

The complete optimal set is {(0,1),(0,2)}. Labels: A={0,1,2}, B={3,4,5}, C={6,7,8,9}, h=10, u=0. The four orbit counts are 2 incident-A, 1 untouched-A, 3 B, 6 C. Normalized benefit scores are 4535/619008, 1/160, 1/160, and 2/273, respectively. The incident-A minus C score gap is exactly 1/4333056. C also strictly beats the untouched-A/B score because 2/273>1/160. Thus both and only the incident-A edges minimize the objective.

Actual objective values are 389957345/31720136448 for each incident-A edge, 109900111/8867995136 for untouched-A/B, and 327061565/26603985408 for each C edge. The actual C minus incident-A objective gap is 145/6815897088. All edge identities and fractions are retained in result.json, /rows and /winners.

## Specification compliance: PASS

The graph has total old conductance m=42 and post-insertion conductance 58. theta is strictly between zero and one. All graphs are connected, all inserted conductances are positive, and the target and source are independent with the same fixed law. Diagonal hitting time is zero. Restoration (0,10) is explicitly excluded; there are no other omitted missing-edge candidates. The two tied incident-A edges are retained individually. This counterexample refutes transfer of the unit-strength forbidden-restoration ordering to all common positive strengths; it does not contradict the accepted unit-strength theorem.

## Source and analytic bridge verification: PASS (scoped)

For a connected undirected weighted graph, commute time is 2m R_ij. Symmetry of iid p_i p_j therefore gives sum p_i p_j H_ij=m sum p_i p_j R_ij=2m tr(M Cov(p)). This is the known weighted-resistance bridge, not a new method. Since M1=0, Cov(p) yields tr(M Cov(p))=(1-theta)/n [tr(M)+n theta M_hh]. check.py independently forms p and Cov(p) directly, rather than relying on the author's compact hub score formula. For fixed common insertion strength, all candidate volumes agree; the common positive score-to-objective factor is 2(42+16)16(1-theta)/11=145/1573. This independently justifies cancellation and the displayed actual objective gap. No new literature or priority assertion is made.

## Implementation alignment and retained failures: PASS

The frozen author proposal SHA256 is 60459628123dedb3f4300c083ed6dcd4a79ca6f1cd1a9506a02fa409d375f68c; batch2.json is 2dcbe58de0ac5e384c4140a6f1379270ff9d1adfb1b69753b6c3340147e73a17. The independent evaluator checks both hashes before execution and compares every orbit score against batch2.json.

The author history contains two distinct attempts, not two successful proofs. The first check.py/run.json exits rc=1 after saving coefficient data to result.json and failing the attempted universal positivity assertion; its stdout.bin and stderr.bin are retained. The separately declared batch2-plan.md and check2.py produce the counterexample with batch2-run.json rc=0. That second result does not repair or erase the failed universal claim. The proposal's sigma=4571/4576 and theta=(sigma+1)/2=9147/9152 are consistent with its exact score definitions. The independently reconstructed matrices suffice for the counterexample without relying on positivity of any failed coefficient certificate.

No correction required for the scoped counterexample. All shared and author artifacts remained read-only. This independent audit does not certify other graph sizes, theta intervals, strength ranges, forbidden-action policies, novelty, or practical impact.
