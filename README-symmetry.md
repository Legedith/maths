# Exact batch reuse under unordered terminal symmetry

`SymmetryBatchAnalyzer` is an opt-in batch front end for the unchanged
version-1 `analyze_graph` engine. It validates each payload, identifies the
isomorphism class of the graph with its terminal pair treated as unordered,
stores one exact result for canonical source `0` and target `1`, and restores
all public fields to the caller's labels and source-to-target orientation.

This is a project-specific optimization assembled from standard relabelling,
electrical-network, random-walk, and spanning-tree facts. The evidence here
does not establish a new graph theorem, new graph counts, novelty over all
algorithms, or an efficient general graph-isomorphism method.

## API and cache behavior

```python
from atlas_engine import SymmetryBatchAnalyzer

batch = SymmetryBatchAnalyzer(capacity=256)
result = batch.analyze(payload)
statistics = batch.diagnostics()
batch.clear()
```

The cache is private to each analyzer instance and uses least-recently-used
eviction. `capacity` must be a positive, non-boolean integer. `diagnostics()`
returns detached `capacity`, `size`, `hits`, `misses`, `core_calls`, and
`evictions` counters. `clear()` removes all entries and resets the counters.
Every input is fully validated before canonicalization or lookup, so an invalid
input cannot hit a warm key and does not change any counter. A miss calls only
the unchanged `analyze_graph`; exceptions are not inserted. Each response
rebuilds its nested edge list, Laplacian, potential list, and check mapping, so
caller mutation cannot reach a cached object.

## Canonical key

For an admitted input `(G,s,t)` with `n` vertices, a candidate relabelling is a
bijection `phi: V(G) -> {0,...,n-1}` satisfying
`{phi(s),phi(t)} = {0,1}`. The implementation enumerates both orders of the
terminals and all permutations of the other vertices, exactly
`2 * (n-2)!` candidates. For each candidate it relabels every edge and encodes
the edge set as a bit mask. Bit positions follow
`combinations(range(n), 2)` in lexicographic order, with the first edge in the
low bit. The key is `(n, minimum mask)`. If several maps attain the same mask,
the lexicographically least caller-to-canonical map is used for transport and
the tie count is retained by the internal canonical descriptor.

The key characterizes precisely the admitted unordered-terminal isomorphism
classes. If `f` is an isomorphism from `(G,{s,t})` to `(H,{a,b})`, composition
with `f` gives a bijection between their candidate relabellings without
changing any encoded edge set, so the minima agree. Conversely, if two inputs
have the same key, their selected relabellings map them to the same labelled
canonical graph and map both terminal sets to `{0,1}`. Composing one selected
map with the inverse of the other gives the required graph isomorphism. Thus a
cache hit never joins different unordered-terminal classes.

## Correctness of output transport

Let `C` be the canonical graph, let `phi` map caller vertices to canonical
vertices, and let the cached result use source `0`, target `1`. Write `R` for
its exact resistance and `p` for its potential vector, so
`L_C p = e_0 - e_1`, `p_1 = 0`, and `p_0 = R`.

**Laplacian.** Relabelling preserves adjacency and degree. Entry by entry,
`L_G[u,v] = L_C[phi(u),phi(v)]`; equivalently, the two matrices are related by
a simultaneous row-and-column permutation. The implementation applies both
indices, so the returned matrix has the caller's labels.

**Potentials and resistance.** If `phi(s)=0`, the caller potential at `u` is
`p[phi(u)]`. If `phi(s)=1`, the requested current direction is reversed and
the caller potential is `R - p[phi(u)]`. Indeed, the Laplacian kills the
constant vector, so `L_C(R*1-p)=e_1-e_0`; the caller target maps to `0` and is
grounded at zero, while the caller source maps to `1` and has value `R`.
Resistance is therefore unchanged. All arithmetic in this step uses
`Fraction`, followed by the engine's exact rational-string convention.

**Hitting and commute times.** A graph isomorphism preserves degrees,
neighbors, transition probabilities, and therefore every finite random-walk
path probability. Hence `H_G(s,t)=H_C(phi(s),phi(t))`. When `phi(s)=0`, cached
forward and backward times are used directly; when `phi(s)=1`, they are
exchanged. Their sum, the commute time, is invariant.

**Spanning-tree fields and nonedges.** Relabelling each edge gives a bijection
between spanning trees. It also gives a bijection between trees containing the
caller terminal edge and trees containing canonical edge `{0,1}`. Total tree
count, selected-edge count, and their ratio are invariant. Edge presence is
also invariant, so a nonedge terminal pair remains inapplicable and both
`tree_edge_count` and `edge_probability` remain `null`.

**Checks.** The analyzer recomputes the complete version-1 check mapping after
transport. Simultaneous Laplacian permutation preserves zero row sums; the
exact identities `commute = 2*m*R`, positive tree count, and, when applicable,
`edge_probability = R` use the transported values. No cached true flag is
trusted as a substitute for these caller-labelled checks.

**Canonical ties.** Suppose two minimizing maps `phi` and `psi` yield the same
canonical edge mask. Then `psi` composed with `phi^{-1}` is an automorphism of
the canonical graph that preserves `{0,1}`. If it fixes the terminals, it
preserves the unique grounded potential solution and the ordered hitting
times. If it swaps the terminals, it sends `p` to `R-p` and exchanges the two
hitting times; the orientation branch applies exactly those compensations.
Laplacian and spanning-tree transports are already invariant under the same
automorphism. Therefore every minimizing map gives the same caller result,
including graphs with terminal-swapping automorphisms.

Eviction and clearing affect reuse only. Any later miss recomputes the same
canonical result through `analyze_graph`, so neither operation changes the
argument above. This establishes the transformation for every graph in the
entire admitted domain (`2 <= n <= 6`), rather than deriving correctness only
from finite testing.

## Canonical correctness run

The worker staging focused unit command
`uv run python -m pytest -p no:cacheprovider` passed 31 tests in 0.08 seconds.
Those tests cover public-field equality, all frozen fixtures, asymmetric
orientation transport, nonedges, relabelled cache hits, nested mutation,
normalization aliases, automorphism ties, LRU/clear/instance behavior, strict
capacity validation, and a synthetic core exception that must not be cached.
Raw command and console records are `evidence/symmetry/worker/logs/pytest-attempt-03.*`.

The canonical command was:

```powershell
$env:UV_CACHE_DIR = "D:\CodexWorkspaces\mathematics-atlas\uv-cache"
uv run python scripts/run_symmetry_correctness.py --output-dir logs/correctness-attempt-01
```

It ran under CPython 3.13.7 on Windows 10 and finished in
13.059059899998829 seconds. Every comparison used exact Python dictionary
equality over all public fields; no sampling or float tolerance was used.

| Scope | Graphs/families | Ordered pairs | Existing-edge pairs | Nonedge pairs | Reversal pairs | Canonical classes |
|---|---:|---:|---:|---:|---:|---:|
| `n=2` | 1 | 2 | 2 | 0 | 1 | 1 |
| `n=3` | 4 | 24 | 18 | 6 | 12 | 3 |
| `n=4` | 38 | 456 | 288 | 168 | 228 | 16 |
| `n=5` | 728 | 14,560 | 8,280 | 6,280 | 7,280 | 98 |
| Exhaustive subtotal | 771 | 15,042 | 8,588 | 6,454 | 7,521 | 118 |
| Five named `n=6` families | 5 | 150 | 76 | 74 | 75 | 20 |
| Entire ordered-pair file | 776 | 15,192 | 8,664 | 6,528 | 7,596 | 138 |

The five six-vertex families were path `P6`, cycle `C6`, star `K1,5`, complete
`K6`, and two triangles joined by one bridge; each contributed all 30 ordered
terminal pairs. The run made 138 unchanged core calls, recorded 138 misses,
15,054 hits, and zero evictions. It also reproduced all seven valid and ten
invalid frozen fixtures, checked all 7 cache/mutation behavior cases, and found
zero failures. The 15,192 compact JSONL records retain the input, canonical
key, orientation, tie count, both full outputs, their SHA-256 hashes, and the
equality result.

Finite agreement supports the implementation and detects errors in label and
orientation transport. The algebraic and combinatorial argument above is the
reason the method applies beyond the enumerated cases within the admitted
domain.

## Frozen paired benchmark

The benchmark command was:

```powershell
$env:UV_CACHE_DIR = "D:\CodexWorkspaces\mathematics-atlas\uv-cache"
uv run python scripts/run_symmetry_benchmark.py --output-dir logs/benchmark-attempt-01
```

The workload was generated before timing and contained all 771 labelled
connected graphs for `n=2..5`, with the lexicographically first existing edge
as terminals. One separate direct batch and one separate symmetry batch warmed
the Python/code paths; their outputs were checked and discarded. Each measured
symmetry batch constructed a fresh capacity-771 analyzer inside its timer. Its
timer included validation, all canonicalization, cache construction, all
misses and hits, unchanged core calls, output transport, and checks. Output
dictionary equality and hashing occurred after both timers. Odd rounds ran the
direct method first and even rounds ran symmetry first.

| Round | Order | Direct seconds | Symmetry seconds | Core calls | Hits |
|---:|---|---:|---:|---:|---:|
| 1 | direct first | 0.3094530 | 0.1093508 | 69 | 702 |
| 2 | symmetry first | 0.3345553 | 0.1167148 | 69 | 702 |
| 3 | direct first | 0.3426445 | 0.1281034 | 69 | 702 |
| 4 | symmetry first | 0.3100215 | 0.1046217 | 69 | 702 |
| 5 | direct first | 0.3451168 | 0.1058758 | 69 | 702 |
| 6 | symmetry first | 0.3365707 | 0.1072112 | 69 | 702 |
| 7 | direct first | 0.3596891 | 0.1139159 | 69 | 702 |
| 8 | symmetry first | 0.3322172 | 0.1253277 | 69 | 702 |
| 9 | direct first | 0.3376394 | 0.1066658 | 69 | 702 |
| 10 | symmetry first | 0.3126790 | 0.1293106 | 69 | 702 |
| 11 | direct first | 0.3130447 | 0.1012865 | 69 | 702 |
| 12 | symmetry first | 0.3327639 | 0.1124631 | 69 | 702 |
| 13 | direct first | 0.3084516 | 0.1065070 | 69 | 702 |
| 14 | symmetry first | 0.3062289 | 0.1097333 | 69 | 702 |
| 15 | direct first | 0.2930907 | 0.0989145 | 69 | 702 |
| 16 | symmetry first | 0.3643238 | 0.1090531 | 69 | 702 |
| 17 | direct first | 0.2984380 | 0.1035236 | 69 | 702 |
| 18 | symmetry first | 0.3211197 | 0.1005880 | 69 | 702 |
| 19 | direct first | 0.3216659 | 0.1188300 | 69 | 702 |
| 20 | symmetry first | 0.3189194 | 0.1096827 | 69 | 702 |
| 21 | direct first | 0.3152714 | 0.1164408 | 69 | 702 |

All 21 output pairs were exactly equal. The direct median was 0.3211197
seconds and the symmetry median was 0.1093508 seconds, a measured
direct/symmetry ratio of 2.9366012868675857 and a median time-saved fraction of
0.6594702847567433. Across measured rounds the direct path made 16,191 direct
calls. The symmetry path made 1,449 core calls and misses, served 14,742 hits,
and made zero evictions. The result hash in every round was
`98d8462e4fe3475af8f65ede32b2ad4130d06d1939058d63011f3e99a21f202b`.

Wall-clock results depend on the machine and concurrent load. These numbers
support a benefit only for this finite frozen workload on the recorded CPython
3.13.7 / Windows 10 environment. Canonicalization has factorial cost
`2*(n-2)!` plus edge encoding on every call, and a cold cache adds that work
before an unchanged core miss. The analyzer is intended for the admitted
`n<=6` repeated-batch domain and should not be recommended for large graphs or
isolated queries.

## Raw artifacts and reproduction

- `evidence/symmetry/worker/logs/correctness-attempt-01/ordered-pair-records.jsonl`: all 15,192 exact
  ordered-pair records.
- `evidence/symmetry/worker/logs/correctness-attempt-01/summary.json`: actual exhaustive, class, cache,
  fixture, environment, runtime, command, and source-hash totals.
- `evidence/symmetry/worker/logs/correctness-attempt-01/fixture-records.json` and
  `behavior-cases.json`: frozen fixture and cache/mutation evidence.
- `evidence/symmetry/worker/logs/benchmark-attempt-01/workload.jsonl`: all 771 benchmark inputs.
- `evidence/symmetry/worker/logs/benchmark-attempt-01/rounds.jsonl`: all 21 paired raw records.
- `evidence/symmetry/worker/logs/benchmark-attempt-01/summary.json`: medians, all raw time arrays,
  aggregate call counts, environment, command, and source hashes.
- `evidence/symmetry/worker/logs/*.console.log` and `evidence/symmetry/worker/logs/*.command.json`: unabridged console output,
  exact argv, timestamps, wall runtimes, working directory, and exit status for
  every retained attempt.

The correctness summary records SHA-256
`5d4c502a7d3b8116664aef00c3ff6627672d90221d6b4e08e0f031f1a468333e`
for `src/atlas_engine/symmetry.py`; the benchmark summary records the same
implementation hash. Baseline byte-identity and final artifact hashes are in
`evidence/symmetry/worker/logs/final-manifest.json`. Independent semantic audit is required before any
root-owned evidence gate is certified; this implementation report does not
self-certify that final gate.

## Independent integrated reproduction

The promoted checkout uses `docs/symmetry-contract.md` and its own `fixtures/frozen.json`; the first auditor attempt exposed staging-specific paths in the evaluator scripts. The corrected scripts retain this failure and pass in the project checkout. Run:

```powershell
uv run --frozen python scripts/run_symmetry_correctness.py --output-dir evidence/symmetry/local-correctness
uv run --frozen python scripts/run_symmetry_benchmark.py --output-dir evidence/symmetry/local-benchmark
```

The independent rerun reproduced all 15,192 exact dictionaries with zero failures and all 21 benchmark rounds with equal outputs. Its medians were 0.2803868 seconds direct and 0.1129344 seconds with symmetry reuse, a direct/symmetry ratio of 2.482740422758699. The historical table above is the worker staging run; these independent times are a separate run on the recorded environment. Both show workload-specific reuse, not a general performance guarantee. Raw artifacts are under `evidence/symmetry/independent/`. See its final audit and `prior-art-audit.md`: canonical graph caching has direct prior art.
