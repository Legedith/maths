# Network-design proof release contract

This integration extends the earlier three-part release with two selected,
independently audited mathematical results. It supersedes the earlier release
assembly while preserving that proof package and its historical records.

The research scope is simple random walks, Kemeny's constant, and edge design.
The user requested hypothesis generation, early elimination, focus on this
subset, and GPT-6 Astra at low reasoning for new subagents. The initial round
contract and root selection record are retained in this release's evidence.

Publish the exact arbitrary-part-count certificate and a dependency-free
checker, the independently audited part-size ranking with an exact checker,
a readable research note, and the source/review/attempt evidence. No source
PDFs, rendered pages, environments, cache contents, or solver-restricted
outputs belong in this release.

The improvement theorem quantifies r>=3, p>=1, q_i>=3, every minimum part,
and every pair. The ranking theorem compares distinct eligible parts x,y>=3
with arbitrary other positive part sizes. Combined optimality concerns one
edge in the improvement theorem's graph family. Preserve all normalization,
eligibility, source, metadata, finite-support, novelty, and impact boundaries.

Canonical commands from the repository root, with fresh outputs:

```text
uv run --project experiments/kemeny-multipartite-proof --frozen python experiments/kemeny-multipartite-proof/verify_certificate.py --certificate experiments/kemeny-multipartite-proof/certificate.json --output work/kemeny-multipartite-proof/check-01.json
uv run --project experiments/kemeny-multipartite-proof --frozen python experiments/kemeny-multipartite-proof/verify_ranking.py --output work/kemeny-multipartite-proof/ranking-01.json
```

Acceptance requires successful exact reconstruction of the frozen certificate
and ranking identities, retained raw command outputs/exit statuses, and a
separate reviewer's approval of the actual copied evidence, implementation,
and publication text. The root implementation author cannot self-certify
the final semantic gate. Prior mathematical reviews remain valid only for
their fixed inputs; later packaging changes need scoped review, not a repeat
of unchanged mathematical experiments.

The published proof is algorithmically checked and independently audited.
Global novelty, current open-problem status, measured practical impact,
Lean formalization, deletion robustness, weighted extensions, and arbitrary
batch or greedy insertion guarantees remain unestablished.
