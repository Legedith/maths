# A generated summary loses a normalization convention

Live [TheoremSearch](https://www.theoremsearch.com/docs) query on 2026-09-08: `effective resistance random walk commute time`, with `n_results=3`. Result `slogan_id=5481547`, `theorem_id=20543909`, refers to Proposition 2.4 of arXiv:1807.07167v1. Its generated slogan includes the phrase “sum of the stationary probabilities over all vertices”.

The [original paper](https://arxiv.org/html/1807.07167v1), Section 2.2, defines pi(x) as the sum of the incident conductances. This is an unnormalized reversible measure. Proposition 2.4 multiplies effective resistance by its total mass. The retrieved mathematical body keeps this formula; the generated wording loses the normalization convention. This finding concerns the slogan, not an error in the original theorem.

An exact witness uses two vertices joined by one unit-conductance edge. Each one-way trip takes one step, so the commute is two. Resistance is one. The paper's measure is (1,1), giving total mass two and the correct answer. Normalized stationary probabilities are (1/2,1/2), giving total one and the incorrect answer one if substituted into the slogan's reading.

Run `uv run --frozen python scripts/check_normalization_case.py`. The script uses the existing exact engine and checks both readings. A separate Sol Max agent independently retrieved the result, read the definition and proposition, and reproduced the witness. The [independent report](../evidence/reuse/independent/theoremsearch-assumption-audit.md), raw response and separate witness are retained alongside the root check.

This is one verified normalization mismatch under the standard meaning of probability. It does not establish a rate of errors, failure of the service as a whole, a new mathematical theorem, or globally novel detection. The semantic annotation was made by a human-style source comparison; the exact counterexample check is automated. This is a concrete reason to reuse retrieval while retaining source-level definitions and verification.
