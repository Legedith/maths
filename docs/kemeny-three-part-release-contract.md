# Three-part Kemeny proof release contract

Date: 2026-09-08. This release packages an already independently audited proof;
it does not change its theorem, checker, certificate, or mathematical argument.

## Accepted mathematical scope

For integers `a,b,c >= 3` and `p >= 1`, every missing edge inside every
minimum-size non-singleton part of `K_{a,b,c} join K_p` strictly decreases
Kemeny's constant for the simple random walk `T=D^{-1}A`, using stationary-target
hitting time and zero hitting time at the starting vertex. The proof covers
all minimum-part ties and every pair in each such part.

The selected exact polynomial certificate and source/domain argument have an
independent mathematical review. Lean 4 formalization, publication priority,
global novelty, current open-problem status, and real-world benefit are not
established. No assertion is made for nonminimum parts, four or more
non-singleton parts, `p=0`, or other walk normalizations.

## Published files and identity

- Copy the portable package to `experiments/kemeny-three-part-proof`, preserving
  all 29 files from its publication manifest plus that manifest byte-for-byte.
- Copy the independent review's selected 39 files plus its public subset
  manifest to `evidence/kemeny-three-part/independent`, preserving bytes.
- Preserve the root mathematical adoption record. Add current landing text
  that supersedes the historical package's pending-review status without
  editing those historical records.
- Publish third-party source URLs, source hashes, and concise review notes.
  Full papers, rendered pages, environments, and caches remain local.
- Record actual copied paths and hashes. The historical review bundle retains
  local dependencies and is explicitly not a portable release certificate.

## Canonical release check

From the repository root, with a new output path:

```text
uv run --project experiments/kemeny-three-part-proof --frozen python experiments/kemeny-three-part-proof/verify_coefficient_certificate.py --certificate experiments/kemeny-three-part-proof/coefficient-certificate.json --output work/kemeny-three-part-proof/certificate-check.json
```

Retain the exact command, stdout, stderr, exit status, and result. Acceptance
requires exit zero, all reported polynomial checks passing, the exact frozen
checker/certificate hashes, and byte-preserved public copies. A separate
reviewer must check the release's claims and integration against the accepted
mathematical report and original manifests. The author cannot certify this
final semantic gate.

The core checker does not validate every descriptive provenance field. The
accepted proof applies to the exact pinned input; its source formula, domain,
and target are independently verified in the published review. Do not present
the checker as a general certificate-schema validator or a Lean proof.

## Integration boundary

This is a repository proof package with a readable landing page and reproducible
command. It does not modify the deployed atlas corpus or its search interface.
Only checks needed for the added package and documentation are required. Any
later graph/API integration is a separate change with its own validation.
