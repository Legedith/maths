# Exact Laplacian bridge engine

This bounded version accepts connected, simple, undirected, unweighted graphs with 2–6 integer-indexed vertices. It reports exact electrical resistance, random-walk hitting and commute times, and exhaustive spanning-tree counts. All rational values use Python `Fraction` strings (`2/3`, `1`, `0`); no floating-point comparison is used.

## Setup and use

From this directory, with the cache kept on D:

```powershell
$env:UV_CACHE_DIR = "D:\CodexWorkspaces\mathematics-atlas\uv-cache"
uv sync
uv run python -m atlas_engine analyze path/to/input.json
uv run python -m atlas_engine evaluate --output-dir logs/canonical
```

The input object has exactly four fields: `n`, `edges`, `source`, and `target`. `edges` is an array of two-element arrays. The runtime validator also enforces distinct terminals, vertex bounds, absence of self-loops and duplicate undirected edges, and connectivity. `src/atlas_engine/schema.json` is the basic machine-readable input schema; semantic constraints are enforced in Python. `src/atlas_engine/output-schema.json` describes the returned object and exact rational-string fields.

For a source/target pair that is not an edge, `resistance` and `commute` remain valid while `tree_edge_count` and `edge_probability` are `null`. The edge-specific check is omitted because that statement is not applicable.

## Independent computation paths

- Resistance grounds the target and solves the reduced integer Laplacian with exact fractions.
- Hitting times are constructed separately from adjacency lists and random-walk first-step transition equations. They do not consume resistance or potentials.
- The spanning-tree oracle enumerates every `(n-1)`-edge subset and checks connectivity. It does not use a Laplacian, determinant, resistance, or Markov result.

The resistance and Markov formulations share only the generic exact Gauss-Jordan solver in `linear.py`, as allowed by the frozen contract. The baseline evaluator selects the lexicographically first existing edge for each connected labeled simple graph on 2–5 vertices, plus one named 6-vertex cycle: 772 records. The later supplemental check, `uv run --frozen python scripts/check_supplemental.py`, separately covers the complete graph, endpoint path and center-to-leaf star on six vertices in `fixtures/supplemental-six.json`. These three cases are not part of the frozen baseline count. This engine deliberately contains no corpus-dependent search.
