# Source grounding and transfer limits

The independent [source review](../source-review/review.md) checked the retained
primary passages and exact request arrays: four searches and three opens.
`requests.json` retains the requests and hashes of full local responses.
The public packet omits bulk third-party text. Known methods and unresolved
overlap in the [previous assessment](../../kemeny-workload-robustness/source/README.md)
remain applicable.

- Aldous and Fill, [Reversible Markov Chains and Random Walks on Graphs,
  chapter4 section4.1](https://www.stat.berkeley.edu/~aldous/RWG/Book_Ralph/Ch4.S1.html),
  Corollary4.3, retained HTML lines55-66: under increased edge weights, the
  commute-time ratio is bounded by the total-weight ratio. This supports
  retaining the volume factor; the bound itself does not prove worsening or
  supply our exact decision interval. The section's stationary-weighted
  averages must not be substituted for the fixed iid hub-mixture law.
- Ji Zeng, [On average hitting time and Kemeny's constant for weighted
  trees](https://arxiv.org/html/2109.09249), Theorem1.2 and Lemma2.1,
  retained lines53-55 and81-85: arithmetic-average hitting time is a distinct
  objective, with identity alpha=volume*tr(L+)/n. Its fixed positive weight
  multiset and tree feasible set differ from adding a weighted missing edge
  to our cyclic graph. The inspected unversioned HTML is recorded as such;
  no equivalence to a final journal revision is asserted.
- Adriaens, Wang and Gionis, [Minimizing Hitting Time between Disparate Groups
  with Shortcut Edges](https://helda.helsinki.fi/server/api/core/bitstreams/3f51d1b1-ed3f-43f8-9a24-a12f71a7f7cd/content),
  KDD2023, Definition1 and Observations2-3: the objective is time from a uniform
  red start to first entry into a blue set. Monotonicity and supermodularity
  use restricted red-to-blue additions. This is an absorbing-set objective,
  not iid selection of a target vertex from the same law as the start.
  Correct locator: zero-based PDF index3, the fourth PDF page including the
  institutional cover, printed article page3; retained lines233-294.

These statements establish nearby objectives and methods. Their inspected
hypotheses do not directly yield the equal-family theorem,344 no-action
interval or exact strength rescue. This is an entailment comparison of those
statements, not proof that no other result contains or implies our findings.
Generic commute identities, inverse updates, conductance optimization and
Braess-type degradation are known. Sardar fulltext and graph-join overlap
remain unresolved; no originality or physical-impact clearance follows.
