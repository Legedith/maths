# Independent portable implementation audit

Four scoped integrity checks: PASS. No correction required. This reviewer did not author the portable implementation. This is not final release approval, hosted CI verification, or a new audit of the original endpoint theorem authored by this reviewer.

## Frozen targets and distinct mathematical evidence

Script SHA25639100ca08b809d629341326eab55f27278b29ef73243b0a6061003f5a6872a6a; author result SHA256e7d260218dd6ed48700fff61417311d2b10f48f30ec15ef3e8287644a07bcc60; contract SHA25619d4aac28a4df98d217a8a2c57cc8b4a345facaff0e408ef074f30830de0075e. All were checked before execution, together with every input-hashes.json entry. Copied script, pyproject.toml and uv.lock are byte-identical to author inputs.

Source gate relies on distinct accepted reviews: astra-minimax-endpoint-review-work/review.md SHA256c0b0112767bb251a87c45eefccc12dd803f69ca7a0ca1e61f7774a7899a274d8 and astra-full-unit-minimax-review-work/review.md SHA2569c1579ed18ba979c5a6141f16778a97d50689b31356cb8e39a5cad9bc1325e22. They were read and their precise positive-affine, strict-domination, physical-tie and boundary statements checked against this code. Inherited inverse/unequal-unit/counterexample audits remain pinned and unchanged. This avoids self-certification of the original endpoint lemma; no fresh priority search or novelty clearance is asserted.

## Reproduction: PASS

Exactly two logged subprocess attempts with 60-second caps: fresh copied-code uv --frozen replay rc0, then the same command against existing output rc2. Both completed within the cap. run1.json and run2.json retain argv, cwd, environment and elapsed time; each has raw stdout/stderr. The fresh output matches the author's result byte for byte, including runtime Python3.12.11/SymPy1.14.0 and implementation hash. Rejection occurs before certificate computation; the existing output remains byte-identical. audit_run.py/result.json retain these checks. UTF8 decoding succeeds, no CR bytes occur, and JSON ends with LF. No numerical grid, third evaluation or additional witness was used.

## Specification compliance: PASS

unit_policy checks integer sorted sizes3<=a<=b<=c and exact rational0<=lo<=hi<1. Bool inputs cannot satisfy the minimum size. Callers are instructed to supply exact rational endpoints. X labels include all a-1 incident edges in the equal case, every pair in the unique largest part, or every pair in both tied largest parts. Restoration is included separately. Collapsed intervals, endpoint crossing, one-sided intervals, interior product equality and tau>=1 use the accepted signs and complete ties. Policy values are computed from endpoint oracle ratios and asserted equal to the branch rule. Positive affine endpoint values ensure positivity throughout the interval. The finite policy illustrations are not asserted as a universal proof.

The actual witness objectives use common fixed iid hub-mixture law, zero self-hitting and candidate conductance volume before cancellation. Exactly one unit insertion is required for the universal rule. No action, variable-strength optimization, randomized/adaptive choice and theta1 are excluded. The strength16 example is separately marked a restoration-forbidden scope counterexample, not part of the unit policy domain.

## Implementation alignment: PASS

The symbolic code independently constructs r_I,s_I and the hub inverse-action component, verifies compact I and lambda identities, forms C-I-lambda, and substitutes the two exhaustive unequal shifts. It emits every nonzero monomial of each complete SymPy polynomial, rebuilds that polynomial exactly, checks all listed coefficients positive and checks a strictly positive constant. Counts are27 numerator/42 denominator in b=a<c and83/161 in a<b<=c. No omitted-zero term can affect a polynomial; the explicit reconstruction checks coverage of every nonzero term. Nonnegative shifts and positive constants prove positivity including a3,b=a,b=c boundaries, conditional on the accepted score/inverse bridge. This is not an unchecked list of sampled coefficients.

All22 finite candidates are constructed directly: ten on333 with old volume35/final36, twelve allowed on334 at strength16 with old42/final58. graph_lines enumerates the complete complement of the multipartite join with the single deleted hub edge, removes restoration only in the latter case, forms each weighted Laplacian, computes(L+J/n)^(-1)-J/n and asserts LM=I-J/n. Its reduced actual line is2volume*trace(M)/n+2volume*M_hh*theta, so multiplying by1-theta is the actual hitting objective under the accepted covariance identity. It retains each physical label and exact line/objective.

The333 witness returns only(0,1),(0,2) as minimax and(0,9) at the midpoint, with exact regrets23305/10372104 and23/10021. The334 witness returns only(0,1),(0,2); C-minus-winner actual gap145/6815897088 converts through the explicit positive common factor to score gap1/4333056. The previous independent mathematical reviews ground these exact witnesses; this audit checks code/replay alignment without inferring universal claims from them.

The abstract weak-domination and oracle-inactive compromise examples correctly retain worst regrets(1,1,1) and(1,1,1/2). They are explicitly marked non-graph realizations. The symbolic quotient derivative is correct; commuting finite maxima, full-family action domination, graph inverse formulas, equal-family ordering and complete classification are explicitly listed as analytic bridges. The checker does not pretend to prove these by finite enumeration.

The CLI reads no historical evidence or certificate expression. Integer conversion of self-generated coefficients is not executable expression evaluation. No eval/exec, D-drive runtime dependency, network access or subprocess occurs inside the portable script. Its only output is the requested fresh file, written exclusively as sorted UTF8 LF JSON. Ordinary Python with assertions enabled is the documented invocation; the audit explicitly removes PYTHONOPTIMIZE and uses no -O. Assertion-disabled execution is not certified. The environment/lock remain portable and the copied compatible package name is harmless.

## Source verification: PASS by scoped reuse

The two distinct reviews above support the endpoint/product and full-family elimination arguments used by this implementation. The covariance reduction allows differing fixed volumes inside separate affine lines; this code retains them correctly. Historical failed arbitrary-strength positivity and successful counterexample attempts remain in the original author stage; the portable checker neither overwrites nor reclassifies them. No executable evidence strings or historical author self-verdict substitute for those distinct audits.

All shared/author files remained read-only. No Git or release artifact was changed. Four gates cover this implementation candidate and its exact local reproduction only; root integration, public evidence gates and actual CI remain separate.
