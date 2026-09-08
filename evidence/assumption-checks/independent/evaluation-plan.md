# Independent held-out evaluation plan

This plan is owned by `/root/sol_atlas_audit`. It is separate from development fixtures, including every existing `synthetic_heldout` example. The implementation author may see this public plan and the contract concerns, but not held-out case bodies, expected values, verdict labels, label counts, graph list, or random seed before code freeze.

## Public commitment

- Suite ID: `structured-transfer-heldout-v1`
- Planned total: **80 checks**
- Public partitions: 54 mathematically well-formed checks, 12 definedness/provenance/verdict-precedence checks, and 14 malformed/type/resource-boundary checks.
- Secret-seed commitment: `sha256("assumption-eval-seed-v1\\0" || seed) = 70bf5e5b10c54cf0505229e3e9721d6c2c65bb150c841215da7e15acbe82ccd6`
- The 32-byte seed is retained outside the shared filesystem.
- Canonical plaintext bundle SHA-256: `ddf50219b87547a9cae547d936a7afba76380f11c4cda7c5fbb473635a01d9ee`.
- Sealed AES-256-GCM ciphertext SHA-256: `3c96287617319c73631c4586296f541204f7d16ed35088e6888ba4595cbc57c4` (156,867 bytes).
- Sealed generator source SHA-256: `deaada903b476b8513142c46a2fbe9cf9957ad9d2d25be4be5eddb8949c7fdce`.

The seed commitment fixed the independent randomness before implementation. The canonical plaintext hash now commits the exact case bodies and gold records after encoding the accepted clarifications and before inspecting implementation output.

## Case construction

The suite will use fresh labeled graphs on 2-6 vertices. No graph is copied from project fixtures. Valid weighted edges use strictly positive reduced rational conductances within the frozen digit bound, and the valid set contains both integral and non-integral weights.

Generation is stratified before implementation results are visible. Coverage obligations include:

- connected and disconnected graphs; disconnected graphs both with and without isolates;
- connected bipartite and connected non-bipartite support, including irregular graphs whose row/column convention is observable;
- trees, unicyclic graphs, graphs with multiple spanning trees, bridges, dense and sparse six-vertex cases;
- existing terminal edges, terminal nonedges, same-component and different-component terminal pairs;
- five- and six-vertex cases with unequal rational degrees;
- source-faithful identities and a single-clause synthetic alteration paired without copying any development example;
- all five verdicts, with the exact label allocation withheld;
- false assumptions whose conclusions happen to be true, multiple assumptions containing both false and undefined results, ambiguous/unsupported provenance, and unused undefined quantities;
- malformed rationals, booleans in integer positions, floats, range errors, loops, duplicate reversed edges, extra/missing fields, unknown syntax versus unknown quantity, type/shape errors, division by zero, bad entry indices, and AST depth/aggregate-node limits.

## Independent exact oracle

The reference evaluator will use Python `fractions.Fraction` under `uv`; it will not import the implementation. It will normalize graphs and expressions independently.

- Determinants and ranks: fraction-preserving elimination.
- Weighted tree mass and selected-edge mass: exhaustive enumeration of `(n-1)`-edge subsets followed by an independent connectivity test and product of conductances.
- Cofactor and characteristic coefficient: independent matrix construction and principal-minor sums. Tree enumeration is not used to manufacture determinant answers.
- Electrical quantities: solve the grounded combinatorial-Laplacian system on the terminal component with the target at zero.
- Hitting quantities: build a separate first-step linear system from `P` for each target. It shares only generic rational elimination with the electrical solver.
- Period: validate an explicit two-coloring or reconstruct and validate an odd cycle; do not sample powers of `P`.
- Stationarity: verify the returned row vector by exact multiplication with `P`; separately record whether uniqueness/convergence hypotheses hold.
- Expression evaluation: typed scalar/vector/matrix/boolean values, strict undefined propagation, aggregate AST limits, and the frozen verdict precedence.

Cross-identities are audit checks rather than circular gold generators: cofactor versus enumerated tree mass; `commute` versus the sum of independently solved directed hitting times; connected-network `graph_volume*resistance`; `c_e R_e` versus enumerated edge mass/tree mass; and the two spectral-product scaling formulas.

## Metamorphic checks

Several secret base cases will have committed transforms:

- vertex relabeling preserves scalar invariants and permutes vectors/matrices;
- uniform conductance scaling by positive rational `alpha` scales `L`, degrees, graph volume and tree mass as expected, sends resistance to `R/alpha`, and leaves `P`, normalized stationary distribution, hitting times, commute time and `c_e R_e` invariant;
- swapping terminals swaps directed hitting times, preserves resistance/commute, and changes the grounded potential representation predictably;
- adding an unrelated positive-weight component leaves same-component hitting/resistance unchanged but changes global graph volume, catching an illicit global commute factor when the connectedness hypothesis is absent;
- adding a constant to an ungrounded voltage witness changes no currents, while the exposed target-zero potential remains canonical.

## Scoring and release

The canonical input and gold records will be serialized with sorted keys and compact JSON separators. Before code execution, record counts, plaintext bundle SHA-256, and an encrypted sealed copy; disclose only count and hash. After root records the implementation commit/tree hash and declares code freeze, run the implementation over cases without giving the author labels. Preserve raw stdout/stderr, normalized machine output, independent oracle output, and a per-case comparison JSONL.

Report exact-match counts for verdicts and referenced exact values, a five-verdict confusion table, invalid/abstain handling, missing/extra records, crashes/timeouts, and metamorphic failures. Do not report this as natural-language accuracy, theorem-retrieval accuracy, proof, novelty, researcher-time savings, browser validation, or a population error rate.
