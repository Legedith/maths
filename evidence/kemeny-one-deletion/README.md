# Single-failure proof evidence

The current release is described in
[the research note](../../docs/kemeny-fault-tolerant-design.md) and
[the frozen contract](../../docs/kemeny-single-failure-contract.md).
It contains the specified hub-deletion proof, the extension to every
original-edge deletion, and the optimal-repair comparisons. These are
distinct from the earlier intact-network result.

## Portable reproduction

From the repository root, with uv available:

```powershell
$env:UV_CACHE_DIR = 'D:/CodexWorkspaces/mathematics-atlas/uv-cache'
uv run --project experiments/kemeny-one-deletion-proof --frozen python experiments/kemeny-one-deletion-proof/verify_certificate.py --certificate experiments/kemeny-one-deletion-proof/symbolic.json --output work/kemeny-one-deletion-proof/check-01.json
uv run --project experiments/kemeny-one-deletion-proof --frozen python experiments/kemeny-one-deletion-proof/verify_all_deletions.py --certificates experiments/kemeny-one-deletion-proof/all-deletions --output work/kemeny-one-deletion-proof/all-deletions-01.json
uv run --project experiments/kemeny-one-deletion-proof --frozen python experiments/kemeny-one-deletion-proof/verify_optimal_repair.py --certificate experiments/kemeny-one-deletion-proof/optimal-repair.json --output work/kemeny-one-deletion-proof/optimal-repair-01.json
```

Choose fresh output names on repeat runs and an appropriate local cache
on other hosts. Python 3.12.11 is pinned and no package dependencies are
required. The proof CI is configured to execute all three commands and retain raw logs.
The [release bundle](../../.codex/evidence/runs/kemeny-single-failure-v1/bundle.json)
records the typed claims and independent integrity checks.

## Packet map

| Directory | Role |
| --- | --- |
| `hub-author` | Frozen first proof, both declared batches and exact certificate |
| `hub-review` | Independent full-determinant and portable implementation audits |
| `all-author-failed` | Original all-deletion attempts, including both failures |
| `all-author-recovery` | Explicit extra-run amendment, exact source diff, six complete certificates and raw recovery execution |
| `all-review` | Independent orbit/boundary proof, six full determinants, full matrices, portable replay and input rejection |
| `optimal-author` | Hypotheses, eliminated candidate, exact comparisons, original serialization failure and corrected execution |
| `optimal-review` | Independent split-endpoint determinants, full matrices, two review rounds and portable replay |
| `integration` | Root canonical outputs and original raw command records |
| `source` | Bounded prior-art assessment and scoped primary-source notes |

[copy-manifest.json](copy-manifest.json) pins every public copy against its
original stage path and bytes. The complete third-party papers, environments,
caches and web-return snapshots remain outside public Git. Historical
scripts and logs retain their actual local paths; the portable package above
is the fresh-checkout reproduction route. Historical author status statements
remain unchanged; final adoption is determined by the independent reviews
and the current bundle.

The preliminary one-deletion-only release bundle was superseded before
promotion when the broader candidates survived; its frozen task contract
remains in the repository. The current release requires all three canonical
checks. No old PASS is used to certify a changed proof input.

No Lean formalization, global publication priority, general multi-failure
guarantee, or measured practical benefit is claimed.
