# Conjecture proof and evidence

The main result resolves the r>=3, p>=1 assertion of Hu--Kirkland (2019),
Conjecture 3.4.7, by proving that every missing edge in a smallest part strictly
decreases Kemeny's constant. Actual changes are strictly ordered by eligible
part sizes. Start with the [paper](../../README.md).

| Claim | Proof / canonical artifact | Distinct review |
| --- | --- | --- |
| Universal strict improvement | [Proof](../../docs/kemeny-network-design.md), [1,777-term exact certificate](../../experiments/kemeny-multipartite-proof/certificate.json) | [Independent reconstruction and all-parameter proof](../kemeny-multipartite/general-review/report.md) |
| Strict actual-change ranking | [Portable identity checker](../../experiments/kemeny-multipartite-proof/verify_ranking.py) | [Separate ranking audit](../kemeny-multipartite/ranking-review/review.md) |
| Implication for named conjecture | [Bridge](bridge/author/bridge.md) | [Bridge audit](bridge/review/review.md) |
| Closest prior work and scoped contribution | [Primary-source notes](sources/root/comparison-notes.md), [follow-up search](sources/followups/source-notes.md) | [Independent source review](sources/review/review.md) |
| Correction of 2026 v1 Example 4.8 | [Derivation and all 89 values](clique/author/proposal.md), [portable checker](../../experiments/kemeny-multipartite-proof/verify_clique_example.py) | [Characteristic-polynomial and full 100-vertex matrix check](clique/review/review.md) |

The [typed bundle](../../.codex/evidence/runs/novelty-investigation-v1/bundle.json)
records hashes, typed claims and independent gate decisions. Its local release
gate precedes publication; final deployed revision and CI are separately checked.
Integration outputs and raw command logs are in [integration](integration/).

For the subsidiary correction, use a fresh output path:

```text
uv run --project experiments/kemeny-multipartite-proof --frozen python experiments/kemeny-multipartite-proof/verify_clique_example.py --output work/kemeny-multipartite-proof/clique.json
```

The immutable author and independent reviewer scripts retain original local
paths for provenance. The portable checkers above are the fresh-checkout route.
Python is managed by uv; versions and dependencies are pinned in each experiment.
No full third-party paper is republished: public notes, request records and
hashes identify the complete raw source returns retained locally. The
[copy manifest](copy-manifest.json) records promoted source/destination identity.

The [initial screening packets](screen/) retain rejected or unqualified novelty
directions. Their preliminary judgments are history, not additional novelty
claims. Neither negative searches nor the example correction alone constitute
the central contribution. Journal peer review, Lean formalization and measured
benefits on real networks are outside this release.

The previous paper remains in [the archive](../../docs/robust-link-design-paper.md);
its exact original README bytes are retained under [historical](historical/).
Older bundles are historical-revision records and must be interpreted at their
original commits when a former top-level document has since changed.
