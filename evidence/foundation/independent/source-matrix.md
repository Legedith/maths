# Source entailment matrix

## Curated Atlas sources

| Source | Type | Corpus use | Precise passages reviewed | Verdict |
|---|---|---:|---|---|
| [Spielman, *The Laplacian*](https://cs.yale.edu/homes/spielman/561/lect02-15.pdf) | First-party lecture note | 5 nodes / 5 edges | §2.2, equations (2.1)–(2.3): weighted quadratic form, weighted adjacency/degree, `L=D-A`, and Laplacian action | **PASS** |
| [Spielman, *Effective Resistance*](https://cs.yale.edu/homes/spielman/561/lect13-18.pdf) | First-party lecture note | 10 nodes / 14 edges | §13.1 pp.1–2; §13.2 pp.2–3; §13.3; §§13.4–13.5; §13.6 Lemma 13.6.1 | **PASS** |
| [Spielman, *More Effective Resistance*](https://www.cs.yale.edu/homes/spielman/561/lect14-18.pdf) | First-party lecture note | 6 nodes / 6 edges | §14.2 energy dissipation; §14.5 Theorem 14.5.1; §14.6 Theorem 14.6.1 | **PASS** |
| [Chandra et al., *Electrical resistance captures commute and cover times*](https://homes.cs.washington.edu/~ruzzo/papers/resist.pdf) | Research paper | 4 nodes / 4 edges | §1 definitions and §2 Theorem 2.1, PDF p.6 | **PASS** |
| [Spielman & Srivastava, *Graph Sparsification by Effective Resistances*](https://arxiv.org/abs/0803.0929) | Research paper | 3 nodes / 4 edges | §1.1 `Sparsify(G,q)`, Laplacian quadratic form, and Theorem 1 including all stated restrictions | **PASS** |
| [Grady, *Random Walks for Image Segmentation*](https://leogrady.net/wp-content/uploads/2017/01/grady2006random.pdf) | Research paper | 3 nodes / 5 edges | Abstract and §§II–III: weighted pixel graph, seed first-hit probabilities, label assignment, and discrete Dirichlet equivalence | **PASS** |
| [Klein & Ivanciuc, *Resistance-Distance Sum Rules*](https://hrcak.srce.hr/127542) | Research paper | 2 nodes / 2 edges | Abstract and Introduction, journal p.633: resistance-distance sums, graph invariants, and chemical-graph context | **PASS** |

The first five PDFs were locally retained and their retrieval hashes matched the fetch log. The Grady and Klein downloads failed local TLS; their author-hosted/journal primary web passages were used instead. The current corpus accurately calls the collection seven authoritative sources: four research papers and three first-party lecture notes.

## Reuse and external-search claims

| Claim family | Authoritative source | What it supports | Verdict |
|---|---|---|---|
| Loogle behavior and license | [official README](https://github.com/nomeata/loogle/blob/master/README.md), [official usage page](https://github.com/nomeata/loogle/blob/master/blurb.html), [Apache-2.0 license](https://github.com/nomeata/loogle/blob/master/LICENSE) | `/json?q=...`, quoted name-substring search, Mathlib declarations, unstable JSON warning, and Apache-2.0 code | **PASS** |
| TheoremGraph / TheoremSearch | [official graph page](https://www.theoremsearch.com/theorem-graph), [API docs](https://www.theoremsearch.com/docs), [official dataset card](https://huggingface.co/datasets/uw-math-ai/math-graph) | Statement retrieval, dependency navigation, formal/informal graph, and CC-BY-4.0 dataset-card license with per-record source-license caveat | **PASS** |
| zbMATH Open KG | [paper](https://arxiv.org/abs/2609.00969), [official repository](https://github.com/zbMATHOpen/zbmath-open-kg) | Bibliographic metadata, classifications, software links, scholarly relations, RDF access, and the stated CC-BY-SA-4.0 dataset terms | **PASS** |
| MathGloss | [paper](https://arxiv.org/abs/2311.12649), [official repository](https://github.com/MathGloss/MathGloss) | Linked undergraduate concepts and learning-resource alignment; current Atlas docs correctly defer resource-specific reuse review before copying | **PASS** |
| Normalization witness | [Kious, Schapira & Singh, arXiv:1807.07167v1](https://arxiv.org/html/1807.07167v1) §2.2, Proposition 2.4 | `pi(x)` is the unnormalized incident-conductance measure and commute equals resistance times its total mass | **PASS** |

No external search hit is promoted to the curated graph or treated as proof, equivalence, novelty, or an “unsolved” result.
