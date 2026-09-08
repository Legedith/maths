# Network-discovery round 1

Frozen on 2026-09-08 after the user requested focus, many ideas, aggressive
testing/elimination, and GPT-6 Astra light subagents. Interpret light as the
available low reasoning setting. Root retains shared project write ownership.

## Subset and purpose

Stay within simple random walks, Kemeny's constant, and network edge design.
The accepted starting point is: for a,b,c>=3 and p>=1, every missing edge in
every minimum-size non-singleton part of K_{a,b,c} join K_p strictly decreases
Kemeny's constant. Its exact polynomial proof is independently audited;
global publication priority and real-world impact remain unresolved.

The next objective is a stronger theorem, a justified edge-selection rule,
or a useful computational method whose contribution is distinct from the
closest checked literature. Generate multiple concrete hypotheses; eliminate
false ones promptly. Do not replace discovery with repeated packaging or audits.

## Frozen mathematical conventions and evaluator boundary

- Graphs are finite, connected, simple, undirected, and unweighted unless a
  new hypothesis explicitly announces a separate model before testing.
- The transition matrix is T=D^{-1}A. K is stationary-target expected hitting
  time with zero hitting time at the starting vertex, equivalently
  trace((I-T+1*pi)^-1)-1. Improvement means strictly negative Delta K.
- A single missing-edge addition is the primary action. Batch additions or
  different models are new declared hypotheses, never silently substituted.
- For complete multipartite graphs with selected part x>=3, Hu--Kirkland
  Theorem 3.2.3 gives the source formula in the accepted package. Retain all
  singleton parts. x=2 is a different formula and must not use this one.
- Test exact rational arithmetic where feasible. Finite sweeps can refute
  universal claims but cannot establish them. An exact symbolic identity with
  a full-domain sign proof, or an exhaustive finite claim with a complete
  specified domain, may be promoted only after independent review.
- Preserve all executed hypotheses, input ranges, commands, raw results,
  counterexamples, failures, and eliminations in each owner's D-drive staging.
  Separate sampled, exhaustive-finite, and universal conclusions.

## Source and implementation anchors

Project: D:/CodexWorkspaces/mathematics-atlas/project (read-only to subagents).
Accepted proof: experiments/kemeny-three-part-proof/proposal.md and
coefficient-certificate.json; separate independent audit:
evidence/kemeny-three-part/independent/independent-review-report.md.
Canonical exact matrix code is retained at
evidence/kemeny-three-part/independent/scripts/exact_matrix_diagnostic.py.
Source/domain transcription is retained at
evidence/kemeny-three-part/independent/source-domain-proof-notes.md.
Use primary literature for technical and novelty claims; retrieve only what
is needed for the candidate. Do not publish full third-party papers.

## Output and decision rules

Every branch proposes at least three falsifiable ideas before choosing a
bounded first probe. Use at most two short experiment batches in this round;
declare ranges before each execution. Give exact counterexamples for rejected
ideas and the smallest clear surviving claim. A surviving claim is a candidate,
not a discovery certificate. Include one concrete prospective application and
the additional assumptions/evidence required before claiming real impact.

Keep branch proposals independent until root selection. Own only the assigned
staging directory; do not modify the project, another branch, Git, or Sites.
Python uses uv, an isolated environment on D:, and
UV_CACHE_DIR=D:/CodexWorkspaces/mathematics-atlas/uv-cache.
No paid compute, new solver licenses, external messages, or infrastructure
expansion. Old role-mining and graph-search work is paused for this round.
