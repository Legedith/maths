# Independent final audit: unordered-terminal symmetry reuse

Date: 2026-09-08  
Auditor: `/root/sol_symmetry_audit`, independent verifier with no candidate authorship  
Governed implementation: `src/atlas_engine/symmetry.py` SHA-256
`5d4c502a7d3b8116664aef00c3ff6627672d90221d6b4e08e0f031f1a468333e`

## Decision

All four scoped chain-of-evidence checks pass for the frozen, opt-in
`SymmetryBatchAnalyzer`. I found no semantic defect in the final engine. Two
promotion-only path defects were found during independent reproduction: the
first runner version referred to a missing staging `task-spec.md`, and the
first promoted test used a checkout directory named `project`. Root corrected
those paths to `docs/symmetry-contract.md`, repository `fixtures/frozen.json`,
and `tests/../fixtures/frozen.json`. The engine hash did not change. The failed
attempts are retained, and the corrected final commands pass.

This decision supports an exact project-specific optimization for the admitted
`2 <= n <= 6` connected, simple, undirected, unweighted graph API. It does not
support a globally novel algorithm, a new theorem, a general performance
guarantee, or demonstrated scientific or real-world impact.

## Proof and implementation alignment

The canonical key enumerates both terminal orders and every permutation of the
other vertices, uses the documented injective upper-triangle edge bit order,
and includes `n`. Equality of keys is therefore equivalent to graph
isomorphism preserving the unordered terminal set. The implementation's
lexicographically least tied map is deterministic.

The full output transport matches the algebraic obligations:

- Both Laplacian indices are permuted back to caller labels.
- When endpoint orientation reverses, grounded potential becomes `R-p` after
  permutation. Plain negation fails even on the one-edge graph.
- Directional hitting times swap under reversal; they are not assumed equal.
- Scalar resistance, commute, and tree quantities remain invariant.
- An existing terminal edge maps to canonical edge `{0,1}`; a nonedge remains
  a nonedge, preserving null `tree_edge_count`, null `edge_probability`, and
  absence of its conditional check.
- Caller edges, Laplacian rows, potentials, and checks are reconstructed, so
  mutation cannot reach the cached canonical result.
- Full validation occurs before canonicalization or lookup; invalid aliases
  cannot hit a warm valid key and do not change diagnostics.

The grounded electrical solution is unique because the grounded reduced
Laplacian is positive definite: extending a grounded vector gives
`z^T L z = sum_{uv in E}(z_u-z_v)^2`, and connectedness forces a zero-energy
grounded vector to vanish. The absorbing Markov first-step system is unique by
the discrete maximum principle. These uniqueness results justify voltage and
hitting-time transport for the entire admitted domain.

If two minimizers tie, their composition is a canonical-graph automorphism
preserving `{0,1}`. A terminal-fixing automorphism preserves the unique ordered
solutions. A terminal-swapping automorphism changes voltage to `R-p` and swaps
directional hitting times; the implementation changes orientation in the same
branch. Hence tied minimizers give one caller result. Relabelling also gives a
bijection on spanning trees and on trees containing the selected terminal edge.

The cache is instance-local, bounded LRU state with explicit, detached
diagnostics. `clear()` resets cache and counters. A core exception is counted as
a miss/core call but is never inserted, matching the documented test behavior.

## Independent semantic and raw-record verification

The final full-project pytest command was
`uv run python -m pytest -p no:cacheprovider`; it passed **75 tests** in the
corrected promoted checkout. Exact argv, environment overrides, timestamps,
exit status, and console text are retained in
`verifier-pytest-attempt-03.command.json` and
`verifier-pytest-attempt-03.console.log`.

The corrected canonical correctness run compared **15,192 complete result
dictionaries** with exact equality and found zero failures. It covered every
ordered distinct terminal pair on every labelled connected simple graph for
`n=2..5` (15,042 records) and all 30 ordered pairs in five named six-vertex
families (150 records). All seven valid and ten invalid fixtures and all seven
cache/mutation behavior cases passed. It made 138 unchanged core calls, with
138 misses, 15,054 hits, and zero evictions.

I then parsed every raw JSONL record with verifier-only code that does not
import the candidate symmetry module or either runner. It independently:

- reconstructed the exact graph and terminal sequence;
- enumerated each canonical minimum, all ties, and the selected map;
- checked each returned Laplacian and exact unit-current equation;
- separately solved both absorbing Markov systems over `Fraction`;
- recomputed total tree counts with a fraction-free matrix-tree determinant;
- recomputed selected-edge tree counts after contraction while retaining
  parallel-edge multiplicity; and
- checked nonedge applicability, dictionary hashes, summaries, source hashes,
  fixture records, behavior records, and worker/raw byte identity.

It found zero canonicalization, equation/oracle, applicability, hash, sequence,
or dictionary mismatches. The raw verifier observed 3,242 records whose tied
minimizers span both endpoint orientations. This total combines 3,142 in the
exhaustive `n<=5` corpus and 100 in the named `n=6` families.

## Frozen benchmark

The independently executed benchmark used all 771 labelled connected graphs
for `n=2..5`, selecting the lexicographically first existing edge. Workload
generation, equality, hashing, and artifact writes were outside the timed
regions. Each measured direct region made 771 unchanged calls. Each symmetry
region constructed a fresh capacity-771 analyzer inside the timer and included
validation, canonicalization, cache construction, 69 misses/core calls, 702
hits, transport, and checks. Execution order alternated over 21 rounds after
separate discarded warm-up batches.

All 21 result lists were exactly equal and had the same result hash. The
independent raw parser reconstructed the complete workload and independently
found its 69 canonical classes. On the recorded Windows 10 / CPython 3.13.7
environment, median direct time was **0.2803868 s** and median symmetry time was
**0.1129344 s**, a direct/symmetry ratio of **2.482740422758699** and median
time-saved fraction of **0.5972192699513672**.

These wall-clock values describe only this finite repeated workload and this
recorded environment. Canonicalization costs `2*(n-2)!` candidates per call, so
the cache can be slower for cold, isolated, or larger inputs.

## Primary-source and novelty check

Primary sources were retrieved and hashed. Niehaus, Igel, and Banzhaf (2007,
DOI `10.1162/evco.2007.15.2.199`) directly describe storing and looking up
canonically labelled graphs so isomorphic prior evaluations can be reused.
Koebler and Verbitsky formalize canonical labels and their colored-graph
extension. Chandra et al. establish the commute/resistance identity; Burton and
Pemantle establish uniform-spanning-tree transfer-impedance marginals; Kaba et
al. supply broader conceptual prior art for canonicalize-compute-transport and
stabilizer ties. The retained McKay scan is the foundational canonical-labeling
reference used by the direct graph-cache paper.

These sources support the implementation's mathematical assumptions and block
a claim that graph canonicalization plus cached evaluation is globally novel.
The exact Mathematics Atlas result dictionary was not found in this bounded
search; that absence is not evidence of novelty.

## Gate evidence

- **Reproduction — pass.** `verifier-pytest-attempt-03.*`,
  `verifier-correctness-attempt-02/`, `verifier-benchmark-attempt-01/`, and
  `verifier-raw-artifact-audit.json` contain the final raw commands, every case,
  every timed round, and the independent semantic parse.
- **Specification compliance — pass.** `preintegration-proof-audit.md`,
  `preintegration_audit.json`, `boundary6_preintegration_audit.json`, the final
  code hashes in `audited-project-files.json`, and the corrected raw runs cover
  each frozen contract obligation.
- **Source verification — pass.** `prior-art-audit.md`,
  `primary-source-verification.json`, and `primary-sources/` retain the primary
  references, extracted passages, URLs, and hashes used for the calibrated
  prior-art conclusion.
- **Implementation alignment — pass.** The report, contract, public export,
  engine, tests, runners, README, source hashes, and final runtime records were
  compared after the last path-only delta. The candidate engine hash is the
  same one exercised by correctness and benchmark records.

## Limitations

- Exhaustive enumeration stops at all labelled connected graphs on five
  vertices; only five named six-vertex families were enumerated. The general
  admitted-domain conclusion rests on the proof above, not extrapolation from
  enumeration.
- The tree determinant/contraction verifier is independent of the baseline's
  subset-connectivity tree oracle, but both execute on the same finite corpus.
- No thread-safety or multi-process cache behavior is specified or certified.
- The source check is targeted prior-art verification, not an exhaustive patent
  or global literature search.
- No claim is made for mathematical novelty, scientific discovery, external
  adoption, or measured real-world impact.

