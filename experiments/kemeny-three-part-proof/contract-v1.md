# Three non-singleton parts: frozen proof exploration contract

Frozen by root on 2026-09-08 before any mathematical experiment under this contract. This is a research task toward verified discovery, not a claim that the historically stated conjecture remains open today. Existing infrastructure and formulas must be reused with attribution.

## Primary objective

Resolve the three-non-singleton-part branch of Hu and Kirkland (2019), Conjecture 3.4.7: for every integer p >= 1 and every three integers a,b,c >= 3, let G be the complete multipartite graph with parts of sizes a,b,c and p additional singleton parts. Equivalently, G = K_{a,b,c} join K_p. Prove that at least one missing edge e satisfies K(G+e) - K(G) <= 0, or give an exact counterexample for which every missing edge produces a strictly positive difference.

G is finite, simple, undirected and unweighted. The walk chooses a neighbor uniformly; K is Kemeny's constant with zero hitting time at the starting vertex and a stationary, degree-weighted target. A Braess edge strictly increases K. Equality supplies a non-Braess edge. All missing edges lie within a non-singleton part; vertex permutations make all such choices within one part equivalent. Thus there are exactly three edge-addition types to consider.

Ordering a <= b <= c is permitted only with an explicit permutation argument. Do not assume that an extremal part always supplies the desired edge unless proved. The p=0 case is outside the primary conjecture branch and has existing source results; it may be checked as a diagnostic but cannot substitute for p>=1. A stronger all-number-of-parts theorem is welcome if fully proved, but is not assumed.

## Frozen source and notation

Primary manuscript: https://mspace.lib.umanitoba.ca/server/api/core/bitstreams/04a4246d-2b67-4e4c-9c4b-60f0c5417031/content

Local read-only PDF: D:/CodexWorkspaces/mathematics-atlas/kemeny-postresult-review-work/sources/hu-kirkland-2019.pdf
SHA256 c896d263c6bec602274f84a29c30492f99e85e3bde654f3e61dcf5aa10718c77.

Locators: PDF page 10, Section 3.2 notation and Case 1; page 12, Theorem 3.2.3; pages 16-17, large-p partial result; page 19, Conjecture 3.4.7. Root visually inspected the complete rendered pages 12 and 19 on 2026-09-08. Source-investigator packet: D:/CodexWorkspaces/mathematics-atlas/kemeny-open-questions-source-work/source-notes.json, SHA256 0c40a2e2748b08414a85fb76261f36a3110bb9567742d3c41cb90208707f0d10. This packet records prior results and source limitations, not a candidate proof.

Use R=3+p for the TOTAL number of parts in Section 3.2, q=(a,b,c,1,...,1), n=sum(q), alpha_j=n-q_j and gamma=sum(q_j alpha_j). Every singleton remains in every sum, with combined gamma contribution p(n-1). Conjecture 3.4.7 uses r for the NON-SINGLETON part count; these two meanings must not be conflated.

For a selected non-singleton part, permute it to position 1. The applicable Theorem 3.2.3 is:

Delta = 2/(gamma+2) * {
  -gamma/(2 alpha_1)
  + (1/gamma) * [ (q_1-2) gamma/2
    + sum_{j=2}^R q_j alpha_j * (
        alpha_j/n + (q_1-2)/2
        + (n-2)(gamma-q_1 alpha_1)/(2 n alpha_1)
      ) ]
  + (gamma-alpha_1)/(alpha_1(alpha_1+2))
}.

The prefactor is positive. Establish signs of ALL denominators before clearing them. Theorem 3.2.5 concerns q_1=2 and is inapplicable here. The expanded equation (13) on page 19 has a visibly missing operator in the pinned manuscript; this task does not use that expansion or silently repair it.

## Independent exploration

Three Sol Max branches receive this identical contract and the same source packet. Each reads the project and sources without changing them, writes only a separately assigned D-drive staging directory, and does not inspect other branches' proposals. Root must not relay their proposed identities, observations or attack choices to each other until all three proposals are frozen. Scratch exact computations are allowed as hypothesis exploration, with source, command, dependency and raw-output logs retained. Use uv and an isolated D-drive environment/cache for Python. No large unbounded scans or paid external compute.

Each branch returns one best proposal or an explicit failure/obstacle report. Include: exact proposed theorem/counterexample; dependency on published statements; derivation; reusable algebraic certificate or a precise description of missing steps; finite sanity checks clearly labelled as such; all failed probes and source/transcription concerns; proposed independent verification. A plain argument that can be checked is preferred to a huge opaque expansion. Do not self-certify a final evidence gate.

Root selects only after comparing all three frozen proposals against this same objective. If a proposal is merely a published corollary, a restated known update formula, or a bounded search with no counterexample/proof, it does not meet the contribution threshold. A prior-art resolution found during exploration must be reported immediately and will trigger a reuse/pivot decision.

## Evaluation contract for a selected proposal

Successful proof path: a derivation valid for all admitted integer parameters, with every positivity assertion and case split justified, plus a portable exact certificate checker or Lean 4 proof. A certificate checker must reconstruct the sourced target expression independently and check identities with exact integer/rational arithmetic; it may not trust a worker-provided numeric pass flag. If positivity is certified by nonnegative coefficients after variable substitutions, the checker must verify the substitution covers the entire ordered domain, exact polynomial identity, coefficient signs, and any strictness claim. If another certificate form is selected, freeze its soundness argument and canonical command before the implementation run. Finite probes alone never certify a universal assertion.

Successful counterexample path: explicit integers and graph construction within scope, with exact base K and all three post-addition K values; an independent matrix-based method must reproduce every strictly positive difference. Orbit symmetry must justify that three types exhaust all missing edges.

Before publication, independently compare the source formula with its actual manuscript, verify all four CoE integrity gates, and review later primary literature for prior resolution or an already equivalent theorem. A negative literature search is not proof of novelty. Reproduction and mathematical validity may pass while publication novelty stays unresolved; report these statuses separately and keep the larger goal active.

## Scope and stop rules

Retain raw unsuccessful work. Do not change quantifiers, strictness, walk normalization, graph class or the definition of Braess graph to obtain a passing result. Stop a candidate route if its crucial inequality fails, and return the counterexample to that intermediate claim. Do not call the research goal complete for this contract's preparation, a finite scan, infrastructure delivery or a known identity. No demonstrated real-world impact follows from a graph-family theorem alone.
