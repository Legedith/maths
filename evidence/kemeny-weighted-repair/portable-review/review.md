# Independent changed weighted portable review

All four scoped gates PASS. One frozen review round, successful replay and one expected changed-input rejection; no source/mathematical/implementation correction needed. Final publication prose and evidence bundle remain excluded. Reviewer did not author this checker. No shared/project/worker file was changed.

## Reproduction and inputs
review-run.py checked every worker-record hash and all nine copied code/certificate/environment files. Script SHA71e0efbf26f28b4c8b73662fc26e5f123dd285a0f81f266fd50463125b9ccd0d matches the assigned input. A fresh stage-local uv --frozen Python3.12.11 environment with no dependencies replayed successfully. replay.json is byte-for-byte identical to canonical worker check-02.json (SHA dcd6953f9ad73c78873e117b0a91a9c2c108623e203a91c15d8d26b330f0900b). Nine exact identities pass. One whitespace byte appended only to a stage-local weighted certificate is rejected rc1 by the correct weighted-certificate flag, with no output file. Raw argv/stdout/stderr/rc for both are retained; first environment setup output is not mistaken for evaluator failure.

The worker's attempt1-rc file is EMPTY, so its exit status is unknown and is not certified as0. Attempt2 is the recorded canonical rc0 run with empty stderr. check01 and check02 bytes are equal; implementation-notes.md and attempt2-plan.md disclose the capture failure accurately. This review does not reinterpret output production as proof of attempt1 success. Worker plans and both attempts were inspected, and their frozen hashes checked.

## Changed-code alignment
With d=n-a,k0=(n-1)(d-1),w0=n(n-1)+d(d-1), accepted rho=(n+d-1)/(nd),k=k0/(nd),W=w0/(n^2d^2) yield restore r=rho/k=(n+d-1)/k0 and s=W/k^2=w0/k0^2. For uv, accepted formulas clear to r=(2k0+n)/(d k0) and s=(2k0^2+2n k0+w0)/(d^2 k0^2). Untouched pairs have r=2/(n-q),s=2/(n-q)^2. These are exactly electrical_pairs. All numerator/denominator polynomials are positive on admitted shifted domains.

For score s/(1+tr), comparison numerator is s_i-s_j+t(s_i*r_j-s_j*r_i). multiply and imported difference implement these rational pairs with exact cross-products. Six expected keys pin both components for uv>restore,uv>untouched_A,B>uv; the third integer shift covers b>=a+1 and B/C symmetry belongs to the accompanying audited proof. The three imported no-op cases are unchanged (m+1)S-T certificates. graph_expressions supplies the already audited trace/m; no factor of2 or m+t is silently introduced into those sign certificates.

Only x,y,z are constructed. electrical_pairs and finite evaluation explicitly reject any fourth exponent. The unchanged coefficient parser places all certificate terms in the first three variables, and imported graph expressions are polynomials in the passed sizes only. Therefore helper truncation in its fourth dimension cannot discard a term here. Exact dependency SHA checks run before certificate computation; both certificates and expected comparison sets are pinned. Positive certificate/reconstruction denominators and constants plus full equality checks establish the stated identities. No stored symbolic expression string is executed.

## Mathematical boundary and finite diagnostics
Reuse independent common-conductance, joint-strength and no-op reviews recorded in prior-review-hashes.json. They supply connected weighted graph/commute bridge, five orbits, tied maxima/a=3, integer exhaustiveness, monotonic untouched scores, generic derivative/endpoints and the joint-global comparison. The checker appropriately lists those as proof obligations; the nine certificate outputs alone do not claim to machine-prove all analysis.

finite_diagnostics uses exact Fraction arithmetic. At(4,4,6) it computes a nonzero crossing slope and the unique crossing12 for restore versus untouched_A, checks restore=A=B there and C strictly above every other score. This shows suboptimal order may change without affecting the maximizing orbit. At(3,3,3), it reproduces189/59,1573160/1037853, derivative at1=66587/538160 and1<radicand<(1+r)^2, hence0<t*<1 for that example only. No universal t*<1, no impossibility of t*=1, and no generic strength proof are inferred from these finite tests.

## Four gates
Reproduction PASS: fresh canonical-byte replay and correctly invoked changed-input rejection, all worker/copy hashes and attempt accounting retained.
Specification compliance PASS: frozen weighted release contract is respected; nine identities support prescribed common t and prior unit improvement, finite diagnostics explicitly limited, analytic/joint bridges reused; no monetary/physical/novelty claim.
Source verification PASS within reused mathematical input entailment: r/s/trace/m and derivative/endpoint assumptions match prior independently audited packets, not new source or priority assertions. The separate strength-priority source packet requires its assigned independent source review before publication.
Implementation alignment PASS: new rational pairs, affine components, pinned sets/inputs/dependencies, safe variable scope and finite calculations agree with accepted formulas and actual output. Final release prose/bundle not covered.

Packet frozen. Integrate exact reviewed bytes only, then request final publication review; no future deterministic gate or CI outcome is attested.
