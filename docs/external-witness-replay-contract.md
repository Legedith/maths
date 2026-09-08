# Existing-tool replay of two reviewed transfer errors

Frozen before study encoding, 2026-09-08. This is a small, known-case integration
demonstration following the completed structured-checker study. It does not
replace or rescore that study. Use the ready isolated Z3 Python API and SymPy;
defer the unselected 24-by-10 formal-retrieval proposal and unavailable large
proof environments. Do not extend the Atlas grammar, write a new solver or
retrieve replacement study rows.

Both selected source labels and witness graphs were disclosed before this
contract. They cannot become held-out tests, new error detections or novelty
evidence. Measure whether existing tools produce source-faithful, independently
replayable records. Do not infer superiority to the custom checker: a new manual
annotation using constants could also make some individual cases expressible.

## Inputs and semantic boundary

Use the immutable source-only adjudication and its additive corrections in
`evidence/assumption-checks/independent/`. Retain their hashes in the run manifest.
Generated summaries are the targets of refutation; neither original paper is
alleged to contain these errors. An encoding author must state every object,
domain, quantity and negation. An independent reviewer must approve the two
encodings before their scored execution. An erroneous encoding is a failed
attempt and cannot be silently repaired or replaced in the scored run.

1. **TheoremSearch row 23150070**, source `0802.2576v2`, PDF page 2,
   Theorem 1.2(1)-(2). The source is an any-graph weighted matrix-tree identity.
   It omits one designated zero from the eigenvalue product and retains every
   remaining eigenvalue with multiplicity, including additional zeros. The
   generated summary instead multiplies all nonzero eigenvalues. This is an
   indexing/quantity error; do not invent a missing connectedness premise for
   the original theorem. Freeze four vertices and precisely the two unit-weight
   undirected edges `{0,1}` and `{2,3}`. All present edge weights are positive
   rational conductances. SymPy must construct the exact Laplacian, report its
   characteristic polynomial and eigenvalue multiplicities, and evaluate all
   principal cofactors. Retain the source spectral expression, the summary's
   nonzero-only expression, and the spanning-tree conclusion. The known expected
   values are 0, 1 and 0 respectively. Preserve a simple explicit eigenbasis or
   equivalent exact certificate that an independent reviewer can check without
   accepting a floating-point spectrum.

2. **TheoremSearch row 23832572**, source `2109.01324v2`. Preserve the
   source-only review's exact locator. Freeze a connected, loop-free undirected
   triangle with conductances `w01=2`, `w02=1`, `w12=1`, and queried edge `{0,1}`.
   Define `tau` as the sum of products of edge conductances over spanning trees
   and `tau_e` as that sum restricted to trees containing the queried edge.
   The source identity is `R_eff = tau_e / (tau * w01)`; the generated summary
   substitutes ordinary tree counts for the weighted sums. List the three
   spanning trees and their weights explicitly. Their weighted totals are 5
   and 4; ordinary counts are 3 and 2. Ground vertex 1, inject unit current at
   vertex 0 and extract at vertex 1. Z3 must encode the exact node equations,
   positive rational conductances, domain and nonzero denominator guards, and
   the negated summary identity. Retain its exact `sat` model; the known
   resistance is `2/5`, while the substituted formula is `1/3`. In a separate
   control query, negate the source identity under the same equations and
   expect `unsat`. SymPy must independently replay the returned voltages,
   electrical equations and weighted cofactor/inclusion calculations.

For both cases retain the correct source identity as a within-instance control.
A match on these controls is not a universal proof of the source theorem. Z3
proves only a claim about its supplied encoding; source reading and independent
semantic review connect that encoding to the original mathematical statement.

## Execution, review and decision

Pin package versions and Python version. Use uv and isolated environments on D:.
Save input hashes, code, exact argv, stdout/stderr, exit codes, package versions,
SMT-LIB assertions and models where applicable, exact rational/matrix results,
and chronological start/end timestamps. Use no floating-point arithmetic.
Each solver invocation has a 5-second timeout; each script process has a
60-second timeout. Retain `unknown`, timeout and setup failures as outcomes.

Limit author implementation and initial execution to 20 minutes wall time from
assignment, and independent semantic/replay verification to 20 minutes wall
time from assignment. Record any overrun rather than claiming cap compliance.
These are machine/agent workflow timestamps, not person-hours, researcher time
saved, performance benchmarks or human-effort estimates.

The author owns only a separate staging directory. Root alone integrates project
files. The independent verifier must not author the accepted implementation;
it must compare the source premises, check exact certificates and rerun the
retained commands. Shared mathematics packages do not establish complete
implementation independence; identify direct certificate checks separately.

The outcome is two approved replay records only if both summary discrepancies
and both within-instance source controls survive independent review with no
missing premises, approximate quantities or incorrect encodings. Otherwise
retain the partial or failed result and stop expanding this experiment. Success
justifies attaching these reviewed witnesses to source packets case by case;
it does not justify a general accuracy, practical impact, theorem novelty or
map-completeness claim. A larger evaluation requires a new untouched corpus and
a separate prospective contract.
