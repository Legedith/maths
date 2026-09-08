# Endpoint comparison evidence

The active contract and typed bundle are under docs/kemeny-strength-comparison-contract.md
and .codex/evidence/runs/kemeny-strength-comparison-v1/bundle.json.

- implementation/: both worker attempts, final result-02.json, inert baseline,
  code, manifests and original failed-input records.
- implementation-review/: distinct code audit, fresh-replay.json, successful
  replay and existing-output rejection with raw streams.
- profile/ and profile-review/: separate unsuccessful diagnostic, stack samples,
  and independent qualification of the sampled path and historical uv deviation.
- integration/: root canonical output, raw process-tree-aware log and comparison.
- final-review/: distinct release audit, added after the frozen input is reviewed.

copy-manifest.json records byte-preserving copies. Historical manifests contain
original local paths as provenance; the solver and checker use no D-stage paths.
Earlier timeout and graph-general analytic premises remain pinned by references
to evidence/kemeny-strength-minimax. No third-party full text is added here.
Local final audit does not imply hosted CI success; actual commit-level CI is
checked separately after push.
