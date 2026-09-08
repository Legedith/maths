# Portable deterministic unit minimax certificate

Implementation candidate by /root/astra_general_proof_verifier. Independent code/replay review is required; this worker authored some mathematical premises and cannot certify a final gate. No shared repository or prior release was changed.

Use the byte-copied compatible uv environment (Python3.12.11, SymPy1.14.0 and locked mpmath1.3.0). From this directory, choose a fresh output whose parent exists:

    uv run --frozen python verify_unit_minimax.py --output fresh-result.json

Run ordinary Python with assertions enabled. Existing output is rejected before computation; exclusive open protects the write. JSON is deterministic, sorted, UTF8 LF, with actual implementation SHA256 and runtime versions. The CLI does not read historical certificates, evaluate expression strings or require D-specific paths. D paths occur only in local raw logging/provenance. The copied pyproject retains its compatible environment package name.

## Certificate and policy

The checker starts from inverse-action r_I,s_I,z_h and reconstructs C-I-lambda_I, verifies equality with the compact score and slope, and emits complete numerator/denominator exponent dictionaries for both unequal integer shifts. It rebuilds each polynomial from its emitted terms and verifies exact equality. All nonzero coefficients and constants are positive. The output names the required graph inverse, domain coverage and positivity arguments explicitly.

The importable unit_policy(a,b,c,lo,hi) takes integer sorted part sizes and exact rational endpoints (rational strings accepted; use exact inputs). It returns both surviving physical action sets, positive reduced lines, crossing, endpoint products, both regrets and every minimax edge. It rejects inadmissible graph sizes or workload intervals. Exactly one UNIT insertion is required, restoration allowed; no action is excluded.

Let X denote incident-u A pairs for equal parts, otherwise every internal pair in every largest part; R denotes restoration. The reduced lines are A=T-J+theta(nHh-lambda_X), B=T-Rscore+theta(nHh-lambda_R), with formulas constructed directly in unit_policy. Actual objectives are2(m+1)(1-theta)A/n and2(m+1)(1-theta)B/n. The positive common factor cancels in relative regret. Strict fixed-action domination excludes every other insertion from all minimax ties, using the accepted equal-family ordering and newly certified unequal endpoint gap.

For a collapsed interval choose the pointwise oracle, including the X/R union if at the crossing. For nondegenerate intervals ending at or below tau choose X; those starting at or above tau choose R. For strict interior crossing compare A(lo)A(hi) and B(lo)B(hi): smaller X product selects X, smaller R product selects R, equality retains both. Worst regrets there are A(hi)/B(hi)-1 and B(lo)/A(lo)-1. If tau>=1, every admitted interval selects X. At theta1 actual objectives vanish and relative regret is undefined. The finite-positive-affine endpoint lemma, monotone quotient reasoning, strict exclusion and full physical ties remain analytic bridges; illustrative policy checks do not replace these proofs.

Illustrations use333 for collapsed/boundary/interior/product equality cases, the previously accepted33100 formula for tau>=1, and344 at theta0 for tied largest parts. These are interface cases, not a numerical graph grid. The33100 result retains every4950 largest-part pair so the policy's complete-label guarantee is visible.

## Independent graph construction in the implementation

Every candidate is reconstructed directly as(L+J/n)^(-1)-J/n and checked by LM=I-J/n. For333 unit insertion all10missing candidates are included, old volume35 and final36. Actual endpoint and midpoint objectives, full reduced lines/products and exact worst regrets are emitted. On[0,21/500], midpoint selects restoration while minimax selects precisely{0,1},{0,2}; regrets are23305/10372104 and23/10021.

For334 strength16 and theta9147/9152, restoration is forbidden and all12allowed candidates are included, old volume42 and final58. The same two incident edges win; exact actual advantage over C pairs is145/6815897088, corresponding to score advantage1/4333056 after the explicit common factor. This is a counterexample to arbitrary-strength extension, not variable-strength optimization or a no-action comparison. Historical failed positivity and successful counterexample attempts stay in their original frozen input stage; this implementation neither reruns nor replaces them.

The abstract positive-affine examples are kept separate: weakly dominated C=3/2+theta still ties minimax value1 for A=1+2theta,B=2-2theta on[0,1/2]; oracle-inactive C=3/2 has smaller minimax value1/2. They are explicitly not asserted graph realizations. The quotient derivative identity is checked symbolically; the finite-maxima and endpoint proof is documented as an analytic bridge.

## Execution and scope

One60second-capped proof evaluation returned0; run.json, stdout.bin and stderr.bin retain exact argv, cwd, D isolation, elapsed and raw streams. Stderr contains successful uv setup, not mathematical failure. No second attempt, retry or failed proof execution. result.json is frozen; input-hashes.json pins the contract, compatible environment and distinct accepted audits. hashes.json seals the packet.

The result is conditional on the explicit analytic bridges, not a Lean proof or universal enumeration. No no-action policy, adaptive/randomized action, arbitrary demand law, generic-method novelty, publication priority or measured benefit is certified. Root integration and an independent reviewer must inspect the unchanged code and a fresh replay before promotion.
