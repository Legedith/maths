# Final ranking implementation and prose review

Fresh replay PASS; mathematical four-gate release acknowledgment applies to the hashes in release-hashes.json, with the README correction below now verified. Release bundle itself was not yet supplied at review time.

Reproduction PASS: release-freeze.md and release-pre-run-hashes.json preceded one uv isolated CPython 3.12.11 replay of the promoted verify_ranking.py. release-argv.json, release-stdout.txt, release-stderr.txt, release-rc.txt and release-replay.json retain the run. rc=0; all five checks pass. Output is the same structured result as project/work/kemeny-multipartite-proof/ranking-01.json. No matrix/grid rerun.

Specification compliance PASS: research note states connected simple undirected unweighted simple random walks; improvement requires r>=3,p>=1,all q>=3, minimum non-singleton part, every tie/pair; ranking only compares distinct eligible parts >=3, with arbitrary other positive sizes. Combined global optimum is restricted to the improvement family, where eligible missing edges exist. No size-2 ranking, nonminimum-part improvement, weighted extension, or iterative greedy guarantee is asserted. Workload fit and real-world benefit remain unestablished. README was corrected to 'a smallest non-singleton part'; this removes the singleton eligibility ambiguity.

Source verification PASS by reuse of sealed prior independent mathematical audits: initial review.md independently grounds Hu--Kirkland formula and Remark 2. General report.md and portable-review.md in astra-general-proof-review-work establish the full-domain sign theorem and exact portable implementation; no reproof was attempted. New docs reproduce the corrected singleton moments and valid finite-support argument and distinguish historical conjecture from current verification and unknown priority. PROOF.md openly distinguishes rejected missing-singleton-cube candidate from corrected accepted proof, and historical three-part package from current all-r package.

Implementation alignment PASS: cleared_brace is M=D*B with D=2*a*n*(a+2)*g. Since x=n-a,y=n-b, x-y=b-a. The first code identity gives Dx*Dy=4*n*g^2*[n*a*b*(a+2)*(b+2)]; second gives Mx*Dy-My*Dx=4*n*g^2*(b-a)*N. Dividing the identities yields exactly the independently audited rational difference. All three positivity decompositions match that proof. Imported Poly file matches the separately approved frozen hash. Exact integer polynomial checks do not purport to certify source interpretation or graph domain. CLI rejects preexisting output. Workflow runs historical, general, ranking checks via a logger that propagates child failures and preserves raw outputs; artifact uploads use always(). Static workflow review only, no hosted execution claimed. AGENTS focus and Astra low update match the supplied instruction.

Checker SHA256 ca9aa8d9b29aca9840a525d0ad289965e58a47b700caf7bda4cefd9d739de895.
Poly module SHA256 7b656d33739a7a77834d1ae47f8115cd830f04bb05638a68a8de73189f747749.

No bespoke documentation-checker framework was introduced. Original historical numerical sweeps are not newly certified by this release follow-up.

