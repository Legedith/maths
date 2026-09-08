# Next milestone: check structured mathematical transfers

Status: prospective contract, 2026-09-08. The atlas foundation and its audits remain separate. This milestone is not implemented or evaluated yet. The enduring mapping and discovery objective remains active.

## Objective and boundary

Reuse existing theorem retrieval, then test whether an explicitly annotated mathematical statement applies to a concrete graph problem. Build a general small expression checker over exact graph quantities, with assumption checks, separating witnesses and source provenance. A recognizer hard-coded to the previously found two-vertex normalization slogan is not an acceptable implementation.

Natural-language interpretation is outside this implementation until independently evaluated. The system must preserve who translated a retrieved statement into a structured claim, the exact retrieved text and identifier, the original source definition and locator, and the structured expression. Ambiguous or unsupported translations must abstain. Generated summaries, extracted bodies, original source statements, semantic annotations and machine results are separate records.

## Mathematical scope

Use finite simple undirected graphs with 2–6 vertices and strictly positive rational edge conductances. Keep the original unweighted lab API unchanged. Disconnected graphs may be represented for checking connectedness and rank; undefined electrical or hitting quantities must be reported as undefined, never replaced by zero or an arbitrary finite value. Invalid weights or directed/multigraph inputs are rejected explicitly.

Compute rational quantities exactly: combinatorial and random-walk normalized Laplacians, degree/conductance totals, electrical potentials and resistance where defined, independently constructed hitting times, weighted spanning-tree mass and pair-inclusion mass by exhaustive enumeration, cofactors, rank, and stationary measure versus normalized stationary distribution. An expression language may use rational constants, named quantities, arithmetic and equality/comparison; it may not execute input code. Type and undefined-value errors must remain visible.

A graph-period claim needs an explicit mathematical justification for the admitted undirected domain. A finite number of transition steps alone cannot prove failure of convergence. Likewise, finite successful identity checks cannot establish a universal theorem.

## Verdicts and evidence

- `counterexample`: admitted, defined quantities yield a separating exact witness for the annotated claim.
- `no_counterexample_in_instance`: equality or predicate holds for this specific instance; this is not universal proof or a novelty decision.
- `not_applicable`: a recorded theorem assumption is false for the instance.
- `abstain`: translation, quantity, or inference is unsupported or insufficiently specified.
- `invalid_input`: the input violates the representation contract.

Every machine verdict includes the normalized input, evaluated assumptions, expression operands, exact values, algorithm version and source/annotation links. Applying a theorem despite a failed hypothesis must never be labelled valid merely because its conclusion accidentally holds on that instance.

## Two separate evaluations

1. **Synthetic diagnostic suite.** Cover normalization conventions, the Matrix-Tree scaling factor, weighted edge inclusion, total conductance in commute time, hitting-time direction, periodicity, voltage gauge, nonedge inclusion and disconnectedness. Use source-faithful statements and explicitly synthetic single-clause alterations. Separate development fixtures from an independently produced evaluation set. Report only performance on this declared structured suite, with abstentions and false alarms; do not call it real-retrieval or natural-language accuracy.
2. **Prospective real-retrieval study.** Before retrieving evaluation examples, freeze the query list, results-per-query, de-duplication and sampling rules. Retain all selected result IDs and outcomes, including unsupported/ambiguous cases. An independent annotator checks inherited definitions against original sources and records support, contradiction or insufficient information. Report manual annotation separately from automated checking, and compare the added checker against retrieval alone. Do not cherry-pick only obvious mistakes or infer an error rate from the earlier development example.

Baseline: the same structured claims and sources without computed assumption/counterexample checks. Any claimed benefit needs exact counts of new correctly flagged transfers and false flags; a researcher-time benefit requires a separately designed timing study and is not assumed here. Any asserted algorithmic originality requires fresh prior-art comparison beyond implementing standard exact algebra.

## Work and audit boundaries

Root owns this contract, corpus integration and the Site. The implementation worker owns an isolated D: staging checkout and uses uv. An independent verifier owns evaluation fixtures and semantic certification in another staging directory; the implementation author cannot certify final results. Retain raw commands, failures, annotations, all verdicts and independent comparison records. Promote only supported scoped claims after the chain-of-evidence gate passes.
