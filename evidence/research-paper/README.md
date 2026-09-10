# Proof and evidence index

The computational result is the uniform-source mixed-target solver. Start with
the [main proof](../../docs/kemeny-source-target.md),
[exact implementation](../../experiments/kemeny-source-target-proof/README.md),
[canonical certificate](../kemeny-source-target/integration/check-01.json),
and [independent final mathematical/code audit](../kemeny-source-target/final-review/review.md).
The [original typed bundle](../../.codex/evidence/runs/kemeny-source-target-v1/bundle.json)
certifies that unchanged solver release. The [hosted replay review](pr16-hosted-review/ci-review.md)
certifies the retained two downloaded GitHub outputs at ba90dd8fceb136cc757b06b9511e3aebc9b515fb.

The following are separately proved analytic supplements, not additions to the API:

| Result | Proof | Independent audit |
| --- | --- | --- |
| Target-avoiding connectivity determines linear hitting growth | [Proof](supplement/growth/author/proposal.md) | [Audit](supplement/growth/review/review.md) |
| Sharp fork-path classification and two-source coercivity | [Proof](supplement/classification/author/proposal.md) | [Audit](supplement/classification/review/review.md) |
| General-source infimum and attainment characterization | [Proof](supplement/infimum/author/proposal.md) | [Audit](supplement/infimum/review/review.md) |

The [Palacios source assessment](sources/palacios/author/source-notes.md) and
[distinct source audit](sources/palacios/review/review.md) identify substantial
known voltage/cutpoint ingredients. Full third-party returns remain local;
[retention hashes](sources/raw-retention.json), requests, locators and our notes
are public. No priority certificate or deployment benefit is claimed.

Original stage manifests retain their original local paths. The
[copy manifest](copy-manifest.json) maps retained bytes into this repository;
the final release bundle supplies repository-relative evidence paths.
Draft prose is retained as drafting history, including resolved placeholders.
The published README is authoritative for the finished paper.
