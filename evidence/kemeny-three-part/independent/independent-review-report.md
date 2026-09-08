# Independent final review: three-part Kemeny sign theorem

Review date: 2026-09-08  
Reviewer role: fresh mathematical verifier; author of none of the three proposals  
Decision: **mathematical proof accepted for the exact frozen files; publication novelty and practical impact unresolved**

## Exact accepted theorem

Let `a,b,c,p` be integers with `a,b,c>=3` and `p>=1`, and let `G=K_{a,b,c} join K_p`. Put `m=min{a,b,c}`. For every non-singleton part `S` of `G` with `|S|=m` and every pair of distinct vertices `u,v in S`,

```
K(G+uv)-K(G) < 0,
```

where `K` is Kemeny's constant for the simple random walk `T=D^{-1}A`, equivalently the stationary-target hitting-time convention with zero hitting time at the starting vertex.

No statement is accepted here for a nonminimum part, four or more non-singleton parts, `p=0`, a different walk normalization, global novelty, current openness, or practical impact.

## Why the proof is valid

The actual Hu--Kirkland manuscript was inspected visually. PDF page 12, Theorem 3.2.3, agrees exactly with the frozen formula, and pages 2, 3, and 10 supply the needed Kemeny, random-walk, complete-multipartite, and notation conventions. With a chosen minimum part relabelled to size `x`, the other sizes `y,z` satisfy `y,z>=x`; the `p` clique vertices are `p` singleton multipartite parts.

The independent evaluator aggregates every singleton explicitly and derives

```
D*B = M = -Q(A,u,v,P),
D = 2*alpha*n*(alpha+2)*gamma,
A=x-3, u=y-x, v=z-x, P=p-1.
```

It verifies each of the six denominator-clearing complements before summing. On the full domain, `n>=10`, `alpha>=7`, `alpha+2>=9`, and

```
gamma=2xy+2xz+2yz+2p(x+y+z)+p(p-1)>0.
```

Thus `D>0` and the theorem's prefactor `2/(gamma+2)>0`. The substitution is a bijection between the relabelled integer domain and `A,u,v,P>=0`. The independently reconstructed `Q` equals both the 124-term certificate and the eleven-group display. All 124 coefficients are positive, with minimum `2`, maximum `73722`, and constant `60948`; hence `Q>=60948>0`, so `M<0`, `B<0`, and the Kemeny difference is strictly negative.

For every tied minimum part, relabel that part as `x` separately; the remaining parts are still at least `x`. Every within-part pair is a nonedge, and the symmetric group on that part is transitive on unordered pairs. The source's representative edge therefore covers every pair. This handles one-, two-, and three-way minimum ties.

The exact rational matrix diagnostic reproduced the source formula for all 30 within-minimum-part pairs in four finite graphs, including two-way and three-way ties. This is diagnostic support only; the universal conclusion comes from the polynomial identity and sign proof.

## Four evidence gates

| Gate | Status | Independent finding |
|---|---|---|
| Reproduction | **PASS** | The frozen independent stdlib evaluator exited 0 and produced `PASS`; a fresh isolated Python 3.12.11 replay of the byte-preserved portable checker also exited 0. Exact matrix diagnostics exited 0. |
| Specification compliance | **PASS** | The proof retains all quantifiers `a,b,c>=3`, `p>=1`, strict `<0`, the simple random walk, all minimum-part ties, and every pair in the selected part. It does not use the out-of-scope `p=0` theorem or the `k_1=2` formula. |
| Source verification | **PASS** | Theorem 3.2.3 and its conventions were checked against the actual pinned PDF. Pages 13--19 show that `p=0`, size-2, sufficiently-large-`p`, and equal-size subfamilies were known, while the relevant `r=3` existential consequence remained within Conjecture 3.4.7. The later 2026 twin-clique formula was inspected and does not supply this sign theorem. |
| Implementation alignment | **PASS, scoped to the frozen hashes** | Portable checker, certificate, proposal, contract, and selection are byte-identical to the selected frozen inputs. All 14 package-freeze files and 29 publication-manifest entries rehash correctly. The core checker rejects coefficient and term-structure corruption. Its provenance-schema limitation below remains material. |

## Checker-adversarial result

In a fresh D-drive environment using CPython 3.12.11, the preserved checker:

- accepted the exact certificate;
- rejected a coefficient increment, a three-entry exponent vector, a duplicate exponent, a missing schema tag, and a wrong variable order;
- **accepted** a missing `source_formula`, a reversed written target identity, a written domain mutation from `x=3+A` to `x=2+A`, and an unknown top-level field.

This does not invalidate the frozen mathematical proof: the checker hard-codes the correct reconstruction, and the independent evaluator separately enforces the exact certificate hash, source hash, target metadata, domain metadata, polynomial identity, and grouped display. It does mean the preserved checker must be described as a core exact polynomial checker, not a complete certificate/provenance-schema validator.

## Source and priority assessment

The exact general edge-update identity is Hu and Kirkland's published Theorem 3.2.3. Their Corollary 3.4.5 already covers the equal-size subfamily. Their Theorem 3.4.3 gives only sufficiently large `p` for general part sizes, and Conjecture 3.4.7 leaves the relevant three-non-singleton-part existential conclusion conjectural. Breen--deBlieck--Vander Meulen (2026) gives a later general twin-set clique formula but does not prove this three-part all-`p` sign result.

The verified mathematical contribution is therefore the all-`p` positive-polynomial sign analysis for three non-singleton parts, together with the stronger statement that every edge in every minimum part strictly decreases `K`. This is materially distinct from the closest inspected primary-source results. The literature review was bounded, and its original investigator also authored proposal branch 2; the corrected v2 packet properly withdraws any claim of independent priority certification. Publication priority, global novelty, and current openness remain **UNRESOLVED / UNESTABLISHED**. A negative search cannot change that status.

## Exact frozen input hashes

| Artifact | SHA256 |
|---|---|
| `contract-v1.md` | `563d11151e21d31a21804e7871db6979996bc2cbe4dc0ed3673563975b1d2aba` |
| `selection-v1.json` | `c750ff018cc7e04db9d9b964486d71a0e5f9b5a42ea93e9de25b68c73632b996` |
| selected `proposal.md` | `53c78f650397b3a791dd6b2a715f2294c564bcb9440feabce7327ceb4dcfa3e4` |
| selected `publication-manifest.json` | `30f667f7a0a7657444984f578bd9f51b9a217d93f2eca10dea5b34f49710f04c` |
| selected `coefficient-certificate.json` | `540ea590fb2e3d671e95102ab8ac5b80a22752f85354c7ded4aa84a4848fb8a9` |
| selected `verify_coefficient_certificate.py` | `08aee29b87793cb288eaa7dfe54dd748b169972c32e46ed6e1b5bb2e1f3327f5` |
| Hu--Kirkland 2019 PDF | `c896d263c6bec602274f84a29c30492f99e85e3bde654f3e61dcf5aa10718c77` |
| corrected priority review v2 | `25545977eafd4f042d90ecc69dfcaf3f82bb86578a3653cb033388d5d2c1a75b` |
| priority correction record | `3f48c1281a59b803af536e0b0cd567c11eedec1d8b26f29a49925b7d8a1960cb` |
| Breen et al. 2026 PDF | `69037b759b6c7948fba80c77c4e50823c4d051658ff93eedf1113d7c21a3d660` |

## Exact independent and portable evidence hashes

| Artifact | SHA256 |
|---|---|
| independent evaluator | `024fb7ba0967c165cae75d6b5b794484ddc93107cea533ff6040d1cf4b322633` |
| evaluator freeze | `8fdb337a6a079aabcb64c3e2886a1891c20469141186697cb9ae229866935e37` |
| canonical independent result | `8eba6d8d05139e3c43a11b382c38387cee83a8794fcafd2832395fa47a96ee87` |
| canonical attempt record | `c153c669a90191aa9cba14db91184c5dda4191226aee2d16e5d6d1630e695e49` |
| canonical stdout | `8eba6d8d05139e3c43a11b382c38387cee83a8794fcafd2832395fa47a96ee87` |
| canonical stderr (empty) | `e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855` |
| fresh adversarial report | `7234f6a336fc9c2645d9add796ea970969bfc2be39806e293a13528aa5894e0b` |
| exact matrix diagnostic | `6fe9690e7538b18174440555720489bb6fc94806b44643e5e654edbb28b5f6dd` |
| portable alignment report | `df80e6c8651fb0f6353b5ec85baedb367249b4da9aceacb35f94ca3cc1935c86` |
| fresh portable replay result | `b54f31bc39b16806b8ca5968b246927dac8c7d722ae67fc35746e82e63df188c` |
| portable package freeze | `bdcb4a2eeae2eac2a7e4c6899c94a9a66ea7867278b87ba62f2d764d812a3024` |
| portable publication manifest | `04471269259bc372bf7296526ebf267625a5323b50970a80305cb9cf4a40e900` |

## Reproduction

The exact canonical argv is frozen in `evaluator-freeze.json`. From PowerShell, with all paths on D except the installed evidence-gate script:

```powershell
$env:UV_CACHE_DIR='D:\CodexWorkspaces\mathematics-atlas\uv-cache'
$env:UV_PROJECT_ENVIRONMENT='D:\CodexWorkspaces\mathematics-atlas\kemeny-three-part-independent-work\.venv'
uv run --project 'D:\CodexWorkspaces\mathematics-atlas\kemeny-three-part-independent-work' --frozen python 'D:\CodexWorkspaces\mathematics-atlas\kemeny-three-part-independent-work\scripts\run_capture.py' --workdir 'D:\CodexWorkspaces\mathematics-atlas\kemeny-three-part-independent-work' --log-dir 'D:\CodexWorkspaces\mathematics-atlas\kemeny-three-part-independent-work\logs' --attempt 'attempt-independent-polynomial-canonical-01' -- python 'D:\CodexWorkspaces\mathematics-atlas\kemeny-three-part-independent-work\scripts\independent_polynomial_audit.py' --certificate 'D:\CodexWorkspaces\mathematics-atlas\kemeny-three-part-explorer-3-work\proof\coefficient-certificate.json' --source-pdf 'D:\CodexWorkspaces\mathematics-atlas\kemeny-postresult-review-work\sources\hu-kirkland-2019.pdf' --output 'D:\CodexWorkspaces\mathematics-atlas\kemeny-three-part-independent-work\outputs\independent-polynomial-audit-canonical.json' --expected-certificate-sha256 '540ea590fb2e3d671e95102ab8ac5b80a22752f85354c7ded4aa84a4848fb8a9' --expected-source-pdf-sha256 'c896d263c6bec602274f84a29c30492f99e85e3bde654f3e61dcf5aa10718c77'
```

The first run must use a fresh output path if the retained canonical output already exists. Raw stdout, stderr, return codes, commands, environments, mutations, and the superseded isolation attempt are retained under `logs/` and `artifacts/`. The complete file-level inventory is `raw-artifact-manifest.json`.
