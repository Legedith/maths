# Three-part Kemeny proof certificate

This directory packages the frozen branch-3 proof candidate for the graph
`K_{a,b,c} join K_p`, where `p >= 1` and `a,b,c >= 3`. The candidate says that
adding an edge within any minimum-size non-singleton part strictly decreases
Kemeny's constant. `proposal.md` gives the argument and readable eleven-group
positive polynomial; `coefficient-certificate.json` carries all 124 integer
coefficients.

The dependency-free checker reconstructs the six terms obtained directly from
Hu and Kirkland's Theorem 3.2.3, Case 1, clears the stated positive denominator,
and compares the result exactly with both the expanded certificate and grouped
display. The selected checker and certificate are copied byte-for-byte from the
frozen branch-3 proposal.

From this directory, choose a new output path and run:

```text
uv run --project . --frozen python verify_coefficient_certificate.py --certificate coefficient-certificate.json --output work/certificate-check.json
```

From a repository root after this directory is integrated at
`experiments/kemeny-three-part-proof`, the equivalent command is:

```text
uv run --project experiments/kemeny-three-part-proof --frozen python experiments/kemeny-three-part-proof/verify_coefficient_certificate.py --certificate experiments/kemeny-three-part-proof/coefficient-certificate.json --output work/kemeny-three-part-proof/certificate-check.json
```

The requested output file must not already exist in the evidence-producing
workflow. Python 3.12.11 is pinned in `.python-version` and `pyproject.toml`;
`uv.lock` contains no third-party runtime dependency.

An exit code of zero records that this author-supplied exact consistency checker
passed. It is not independent mathematical certification. The frozen selection
requires a fresh reviewer to check the source formula, reconstruct the identity
separately, test altered and malformed certificates, and assess prior art.
That final proof and novelty gate remains pending.

Full source papers and rendered pages are intentionally omitted. See
`ATTRIBUTION.md` for the primary-source locator and proof provenance.
