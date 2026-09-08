# Exact graph strength minimax solver

Implementation candidate by /root/astra_general_proof_verifier. Independent code/replay review is required. The worker authored mathematical premises and cannot self-certify an implementation or release gate. Shared repository and all earlier packets remain unchanged.

The copied compatible uv project pins Python3.12.11, SymPy1.14.0 and locked mpmath1.3.0. Run from this directory with an existing output parent and a fresh filename:

    uv run --frozen python verify_strength_minimax.py --output fresh-result.json

Use ordinary Python with assertions enabled. The checker rejects existing outputs before calculation and opens exclusively for writing. Sorted deterministic JSON uses explicit UTF8 LF and includes hashes of BOTH Python modules plus runtime versions. It has no historical-stage or D-specific runtime inputs and never evaluates executable evidence strings. D paths in run.py are local isolation/logging only.

## Importable interface

    from strength_minimax import solve, encode_certificate, InconclusiveError
    result = solve(
        n=3,
        edges=[(0, 1, 1), (1, 2, 2)],
        focus=1,
        interval=("0", "1/10"),
        allowed=[(0, 2)],
    )

solve returns exact SymPy rational/algebraic expressions, never decimal recommendations. encode_certificate converts them into exact strings plus closed rational enclosures for deterministic JSON. Inputs are exact rational conductances and endpoints; Python/SymPy floating values and booleans are rejected. Present edges must be positive, loopless and connected on integer labels0..n-1, n>=3. Parallel edges are merged by summing weights. Allowed edges must form a nonempty distinct absent-pair list; focus must be valid and0<=l<=h<1. Invalid domain inputs raise ValueError. Caller-supplied iteration/container resource limits remain the caller's responsibility.

Returned records include merged graph, total old volume, all allowed labels, endpoint T values and oracle f/actual U values, every endpoint oracle action, and every exact(r,s_l,s_h) class. A class retains all its physical edges, all distinct candidate strengths and their generating labels, volumes m+t, actual endpoint objectives, endpoint relative regrets, and its unique minimizing strength. Global actions retain every tied location. All t0 labels are represented once as edge=None,strength=0. Grouping exact equal data does not drop physical ties. The oracle always has the SAME allowed edges and continuum of strengths, including no action.

## Exact comparisons and limits

The solver constructs a centered pseudoinverse and verifies LM=I-J/n. Every allowed edge checks r>0,s>0,B=rT-s>0 and mr>=4. Endpoint critical strengths/minima use explicit rational radical formulas. Candidate lists contain0, positive endpoint stationary strengths and the positive normalized-endpoint balance, with exact duplicate merging. Zero/negative balance, zero denominator, coincident functions and collapsed intervals are handled. Strict convexity is the mathematical reason each class has only one distinct minimizing strength; the implementation asserts that uniqueness after exact comparison.

Ordering uses rational interval arithmetic for sums, products, integral powers and square roots. Integer square roots construct outward dyadic enclosures at80,160 and320 bits. Only intervals strictly on one side of zero establish a nonzero sign. Overlapping intervals may be declared equal ONLY when exact symbolic simplification proves zero. Otherwise InconclusiveError is raised. The checker catches that exception, exits3 with INCONCLUSIVE, and writes no result. Unsupported radical expressions or an unresolved zero-containing division also fail explicitly. This is a documented partial comparison implementation, not a floating tolerance and not a claim that the mathematical finite characterization fails. Symbolic simplification itself has no internal wall-clock interrupt; run in a resource-limited subprocess as in run.py. The solver does not claim polynomial complexity or guaranteed termination on arbitrary huge rational inputs.

## Frozen meaningful validations

One full checker evaluation returned0 in the recorded run.json time, within90seconds. Raw argv/cwd/environment/status and stdout.bin/stderr.bin are retained. Stderr contains successful uv setup messages. There were no proof failures or second attempts. result.json is frozen.

-344 interval[0,1/10]: all16missing pairs, four exact classes, all11distinct declared candidate entries. Endpoint oracle expressions match the accepted radicals. Restoration at a unique positive balance strictly beats every other candidate, including every edge's endpoint-stationary strengths and no action. Every strength/objective/regret carries a rational enclosure.
-Weighted path3 with weights1 and2, focus at the middle vertex, interval[0,1/10]: a single absent pair, independently checked effective resistance3/2 and volume3.
-Unit cycle4, focus0, collapsed uniform interval: both opposite absent pairs retained as globally tied physical locations; coincident normalized branches and zero regret verified.
-344 with only untouched A pair(1,2), collapsed theta14/405: global optimum is no action, represented exactly once.

Independent grounded inverses at strengths0 and1/2 check the actual iid covariance objective at both declared endpoints for EVERY physical edge in those API cases:64+4+8+4=80 exact comparisons. This differs from the solver's centered inverse/rank-one prediction. Three generic symbolic identities verify first derivative, second derivative and infinite linear growth. Five abstract coefficient examples check balance degeneracies and their equality equations, explicitly without graph-realizability claims. Seven malformed-domain cases are rejected. These are bounded implementation checks, not proof by universal graph enumeration.

## Analytic bridges and scope

Output explicitly names the independent arguments not mechanized here: Dirichlet resistance/equality theorem; covariance and inverse reduction; PSD rank trace and uniform coercivity; continuum endpoint supremum interchange; strict convexity and global finite candidate completeness; action-label/no-action conventions. The accepted general-graph audit and prior344 audit are pinned in input-hashes.json. The loopless, absent-edge, fixed iid uniform-plus-focus workload and theta<1 restrictions are essential. Adaptive/randomized choices, multiple insertions, arbitrary demand, intervention costs and disconnected graphs are outside the API theorem.

No generic-method novelty, primary attribution clearance, physical-network value, Lean proof or current-release approval is claimed. Root must copy unchanged modules, perform a fresh canonical replay, and obtain distinct independent implementation and final evidence review before promotion. Existing source gaps and earlier failed conjecture records remain in their immutable prior packets.
