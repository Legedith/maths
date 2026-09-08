# When an added link improves a three-part network

We have an exact, independently audited proof for one family of networks. Its
publication novelty is **unestablished** and its practical impact has **not
been demonstrated**. It is algorithmically checked, with an independent source
and mathematical audit; it is not a Lean 4 formalization.

Imagine three groups of vertices. Every vertex connects to everyone in the
other groups, and none connects to anyone in its own group. Add a fourth group
of connector vertices, each connected to every other vertex, including the
other connectors. Our result says: adding a link between any two vertices in
any smallest one of the original three groups makes a particular average
random-walk journey shorter. All three original groups must have at least
three vertices, and there must be at least one connector.

The average here is Kemeny's constant: choose a destination with the random
walk's stationary probabilities and average the time to reach it. This is a
statement about that mathematical model, not an observed improvement to a
real transport or communication network.

## Precise theorem

For all integers `a,b,c >= 3` and `p >= 1`, let `G = K_{a,b,c} join K_p` and
`m = min(a,b,c)`. For every non-singleton part `S` with `|S| = m` and every
pair of distinct vertices `u,v` in `S`,

```text
K(G + uv) - K(G) < 0.
```

Here `K` uses the simple random walk `T = D^{-1} A` and zero hitting time
when starting at the target. All ties for the smallest part are included.
The result does not cover a larger part, four or more non-singleton parts,
`p = 0`, weighted graphs, or a different walk normalization.

## Proof and what the computer checks

[The full argument](experiments/kemeny-three-part-proof/proposal.md) starts
from Hu and Kirkland's edge-update formula, Theorem 3.2.3 on PDF page 12 of
[their 2019 manuscript](https://mspace.lib.umanitoba.ca/server/api/core/bitstreams/04a4246d-2b67-4e4c-9c4b-60f0c5417031/content).
Relabel a smallest part as `x`, the others as `y,z`, and substitute
`A=x-3`, `u=y-x`, `v=z-x`, `P=p-1`. These four quantities are nonnegative.
Clearing strictly positive denominators expresses the sign of the difference
as the negative of a polynomial in those quantities.

The [certificate](experiments/kemeny-three-part-proof/coefficient-certificate.json)
has 124 positive integer coefficients and a positive constant term. An exact
integer-polynomial checker reconstructs the identity and checks every
coefficient. This proves the sign for the entire stated parameter range;
the finite graph examples are only diagnostic checks.

The [independent review](evidence/kemeny-three-part/independent/independent-review-report.md)
checked the actual source, reconstructed the polynomial with separate code,
checked denominator positivity and the full domain, and addressed every
minimum-part tie and every pair of vertices.

## Reproduce the frozen polynomial check

From the repository root, using [uv](https://docs.astral.sh/uv/) and a fresh
output path:

```text
uv run --project experiments/kemeny-three-part-proof --frozen python experiments/kemeny-three-part-proof/verify_coefficient_certificate.py --certificate experiments/kemeny-three-part-proof/coefficient-certificate.json --output work/kemeny-three-part-proof/certificate-check.json
```

The package pins Python 3.12.11 and has no third-party runtime dependencies.
On this host, keep the checkout, virtual environment, and `UV_CACHE_DIR` on D:.

The checker validates the core polynomial identity, not all descriptive
metadata in an arbitrary certificate. The accepted proof is restricted to the
exact [frozen package](experiments/kemeny-three-part-proof/package-freeze.json).
In particular, the independent audit found that some incorrect source and
domain descriptions are accepted by the core checker. The independent
source/domain audit is an essential part of the proof's evidence.

To rerun the separate source-aware evaluator, obtain the source PDF yourself
at the recorded URL and hash, and supply it with the exact certificate to
`evidence/kemeny-three-part/independent/scripts/independent_polynomial_audit.py`.
Its `--help` lists the required paths and hashes. Source PDFs are not bundled.

## Existing work and remaining questions

Hu and Kirkland already supply the general update formula, the equal-size
case, and a sufficiently-large-`p` result. The contribution checked here is
the all-`p` sign argument for three possibly unequal parts and every pair in
every smallest part. It is distinct from the closest primary results inspected
in the [bounded source review](evidence/kemeny-three-part/independent/source-notes/priority-review-v2.json).
That does not establish that nobody else has proved it. A later general
[twin-clique formula](https://arxiv.org/abs/2608.04150) was also inspected.

Human contributions include finding a prior proof, simplifying this one,
formalizing its source bridge in Lean, or studying a justified broader family.
None of those follow automatically from the certificate.

## Evidence history

The portable package and independent review are preserved byte-for-byte.
Their historical manifests and README describe the state when each was
written, including review that was then pending. The accepted mathematical
status is recorded in the later independent report and
[adoption record](evidence/kemeny-three-part/root-proof-adoption.json).

The copied historical independent evidence bundle depends on omitted local
artifacts and is not a portable release gate. The current
[release bundle](.codex/evidence/runs/kemeny-network-design-v1/bundle.json)
and [release contract](docs/kemeny-three-part-release-contract.md) cover this
repository integration. Retained original paths in old logs describe past
runs; they are not instructions for a fresh checkout.
