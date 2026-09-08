# Atlas structured transfer checker

This package implements version 1 of the frozen structured checker interface. It evaluates explicit, typed mathematical claims on finite simple undirected weighted graphs. It performs no natural-language interpretation, URL retrieval, theorem discovery, or source verification.

The implementation is standard exact graph algebra for a project-specific checking interface. It makes no claim of algorithmic or mathematical novelty.

## Public entry points

Python:

```python
from atlas_checks import check_transfer

result = check_transfer(payload)
```

CLI:

```powershell
$env:UV_CACHE_DIR='D:/CodexWorkspaces/mathematics-atlas/uv-cache'
uv run python -m atlas_checks input.json
```

The CLI writes one JSON object. It exits 0 after processing any parsed JSON payload, including a structural `invalid_input` verdict. Usage, file-read, and JSON-decoding errors also produce structured `invalid_input` JSON and exit 2.

## Input boundary

Top-level, graph, edge, provenance, assumption, and AST records accept exactly the fields in the frozen interface. The check ID, annotation ID, assumption IDs, and other provenance strings must be nonempty strings; values are not coerced. `source` and `target` are distinct non-boolean integer vertex IDs.

Graphs have 2–6 vertices. Edges are simple, undirected, and unique after endpoint canonicalization. Conductances are strictly positive rationals supplied as JSON integers or strings. Whitespace around rational strings is trimmed, optional numerator signs are accepted, denominators must be positive, and signs, greatest common divisors, and leading zeros normalize to canonical `p/q` output. The written numerator and denominator of a conductance or AST rational literal may each contain at most 12 digits, excluding a sign. Booleans and floating-point values are never treated as integers.

Structural validation covers the complete payload before interpreting provenance. Unknown AST kinds or operators, missing or extra fields, wrong structural types, invalid indices, more than 300 AST nodes across all assumptions and the claim, or depth greater than 20 with the root at depth 1 produce `invalid_input`.

A structurally valid unknown quantity, undefined quantity, operand/shape mismatch, division by zero, out-of-range index, or non-boolean assumption/final claim produces `abstain`. Boolean `and` and `or` are strict: both operands are evaluated, and either undefined operand propagates even when the other operand determines the classical Boolean result.

## Verdict order

1. Any structural invalidity yields `invalid_input`.
2. An `ambiguous` or `unsupported` provenance interpretation yields `abstain` before mathematical evaluation.
3. Every declared assumption is evaluated, using only quantities its expression references.
4. If any assumption is false, the verdict is `not_applicable`, even when another assumption is undefined and even when the unevaluated conclusion would happen to hold.
5. Otherwise, any unevaluable assumption or claim yields `abstain`.
6. A defined false claim yields `counterexample`; a defined true claim yields `no_counterexample_in_instance` plus an explicit instance-scope warning.

Human semantic support labels are outside this API and must remain separate from these machine verdicts.

## Expression language

The checker supports rational and Boolean literals, named quantities, exact scalar `add`, `sub`, `mul`, `div`, `lt`, and `le`, strict Boolean `and` and `or`, same-type/same-shape `eq` and `ne`, scalar `neg`, Boolean `not`, rational-vector `sum` and `product`, and vector or matrix `entry`. It never evaluates input as Python or any other executable language.

Each evaluation trace contains its normalized AST path, child operands, exact value, type, shape, status, and any runtime error. The output also contains the normalized input and its SHA-256 hash, supplied provenance, all assumption records, the claim record, lazily accessed quantity records, certificates, errors, and `atlas-checks/1.0.2` as the algorithm version. Hash input is JSON with sorted keys, compact separators and ASCII escapes, encoded as ASCII/UTF-8. Escaped unpaired surrogates are retained as supplied strings without crashing the hash operation.

## Exact quantities

All numeric output is a canonical rational string. Computed results may exceed the 12-digit input limit. Output integers are formatted in base-one-billion chunks, so each individual decimal conversion uses at most nine digits and Python's process-wide integer conversion limit remains unchanged. Repeated division gives the exact base expansion; printing the leading chunk followed by nine-digit zero-padded remaining chunks restores the original integer. Fraction normalization supplies a positive denominator and removes common factors before formatting.

| Name | Definition and domain |
|---|---|
| `n`, `edge_count` | input counts |
| `degrees` | weighted degree vector |
| `total_conductance` | `sum(degrees)=2*sum(edge conductances)`, the graph volume |
| `laplacian` | combinatorial `L=D-A` |
| `transition_matrix` | row-stochastic `P=D^-1 A`; undefined if any vertex is isolated |
| `laplacian_rw` | exactly `I-P=D^-1 L`; the symmetric normalized Laplacian is not exposed |
| `laplacian_rank`, `laplacian_determinant` | exact Gaussian elimination on `L` |
| `target_cofactor` | determinant after deleting the target row and column of `L` |
| `nonzero_spectrum_product` | sum of principal `(n-1)`-minors of `L`, exposed only when connected |
| `rw_nonzero_spectrum_product` | same coefficient for `L_rw`, exposed only when connected |
| `tree_mass` | exhaustive sum of conductance products over spanning trees; zero when disconnected |
| `tree_edge_mass`, `edge_probability` | only for an existing terminal edge in a connected graph |
| `stationary_measure` | unnormalized degree vector |
| `stationary_distribution` | canonical degree-normalized stationary vector when there are no isolates; on a disconnected graph this is not asserted unique or limiting |
| `resistance` | unit-current voltage difference when terminals share a component |
| `hit_forward` | `E_source[tau_target]` from independent first-step equations |
| `hit_backward` | `E_target[tau_source]` from an independent reversed system |
| `commute` | the sum of the two directed hitting times |
| `potentials` | global solution of `Lv=e_source-e_target`, with `v_target=0`; connected graphs only |
| `ones` | exact all-ones vector |
| `connected`, `terminals_connected`, `terminal_is_edge` | structural Boolean predicates |
| `period` | 2 from a bipartition/parity certificate or 1 from an explicit odd cycle; connected graphs only |

Resistance and hitting times are solved on the terminal component when the whole graph is disconnected but the terminals remain connected. They are undefined between components. Global potentials remain undefined on every disconnected graph.

## Construction independence and certificates

Electrical systems are assembled directly from conductance edges and solved after grounding the target. Markov transitions and first-step hitting equations are assembled independently in `markov.py`; hitting time is never derived from resistance or commute identities. Weighted trees are enumerated independently of determinants and resistance. These paths share only the exact rational Gaussian-elimination utilities in `linear.py`.

When a period quantity is referenced, the result includes every bipartition edge check or a closed explicit odd cycle. Finite transition samples are not used as convergence evidence. When a gauge-related quantity is referenced, the result includes `L*ones=0`, exact rank/nullity, and, when global potentials were requested, both a grounded solution and its shift by the all-ones vector with equal current vectors.

## Development evidence and limits

The authored development tests exercise every quantity name, every verdict, exact matrices and rational normalization, same- and different-component terminals, isolated vertices, nonedges, period and gauge certificates, malformed inputs, runtime abstentions, precedence, AST limits, and the module CLI. A separate development script checks every labeled unweighted simple graph through five vertices by comparing independently computed invariants.

These tests are implementation evidence only. They do not use or replace the independently frozen evaluation set, do not measure natural-language accuracy or real-retrieval performance, and do not certify the final evidence gate.

## Post-freeze repair

The original version 1.0.0 is retained at commit `97b5aaf` with its worker freeze manifest and first independent evaluation. All 80 precommitted structured cases matched their semantic gold records, but later public probes found five representation defects outside that suite. Version 1.0.1 adds CLI decoder-error handling, rejects oversized integers before decimal conversion, enforces the frozen AST literal digit cap, and makes normalized-input hashing safe for JSON-escaped strings. Its exact frozen files are retained under `evidence/assumption-checks/worker/version-1.0.1-source/`; the retention manifest describes when and how that archive was reconstructed against the earlier hashes.

A subsequent valid 281-node expression produced an 8,400-digit exact integer and exposed a separate decimal-output failure. Version 1.0.2 changes only output integer formatting and the version marker relative to 1.0.1 runtime code. The regression uses a six-vertex weighted star, whose one spanning tree has weight `999999999999^5`, and multiplies that quantity 140 times. An independent Decimal calculation checks the resulting `999999999999^700` string. The integrated development/regression suite passes 155 tests; independent review of this final formatter delta is pending. Historical failure logs and earlier freezes remain intact. These counts are separate evaluations and do not establish universal correctness.

## Mathematical locators

- Masuda, Porter, and Lambiotte, [Random walks and diffusion on networks](https://www.math.ucla.edu/~mason/papers/rw-review-final3.pdf), PDF p. 17, equations 75–77, defines the row-oriented random-walk normalized Laplacian as `D^-1 L=I-T`.
- Spielman, [Random Walks on Graphs, Lecture 10](https://cs.yale.edu/homes/spielman/561/lect10-18.pdf), PDF pp. 1–4, gives weighted transitions, their matrix orientation, the symmetric normalized operator's similarity relation, stationary degree weights, and the bipartite parity obstruction.
- Spielman, [More Effective Resistance, Lecture 14](https://www.cs.yale.edu/homes/spielman/561/lect14-18.pdf), PDF pp. 3–6, states the weighted Matrix-Tree and weighted edge-inclusion identities.
- Levin, Peres, and Wilmer, [Markov Chains and Mixing Times](https://pages.uoregon.edu/dlevin/MARKOV/markovmixing.pdf), PDF pp. 132 and 147–148, states the connected network domain and conductance-volume commute identity.

The runtime does not access these URLs. Provenance strings in a payload are recorded without treating them as proof.
