# Workload and conductance robustness evidence

The [research note](../../docs/kemeny-workload-robustness.md) is governed by the
[frozen contract](../../docs/kemeny-workload-robustness-contract.md). Its typed
claims and artifact hashes are in the [bundle](../../.codex/evidence/runs/kemeny-workload-robustness-v1/bundle.json).
Author and implementation packets are historical records; their statements
that review is pending describe the time they were frozen. Separate review
packets record the subsequent independent audits.

| Packet | Responsibility |
|---|---|
| envelope-author | Full common-strength/workload derivation and two raw symbolic batches |
| envelope-review | Independent mathematical review and symbolic reconstruction |
| envelope-implementation | Portable symbolic implementation, lock and raw run |
| envelope-portable-review | Independent fresh replay and existing-output rejection |
| continuous-author | Full one-old-link interval certificate, every quadratic and raw run |
| continuous-review | Independent inverse and exact minimum reconstruction |
| continuous-implementation | Portable CLI-only adaptation and rejection test |
| bound-author / bound-review | Sufficient simultaneous certificate, eight radii and independent audit |
| adversary-author | Sixteen feasible assignments, all candidates and first-witness direct hitting check |
| adversary-and-cli-review | Independent adversary checks and continuous CLI audit |
| integration | Root canonical outputs, exact comparisons and all logged attempts |
| source | Bounded source notes, queries and retained-return hashes |
| reused | Accepted workload-effect input and independent attestations |

`copy-manifest.json` records byte-preserving copies, source locations, sizes,
hashes and producers. Stage paths in frozen scripts/logs describe their
historical environment; the portable scripts are under
`experiments/kemeny-workload-proof`. The full original source returns stay
local, with notes and hashes public.

The main theorem covers all stated integer sizes and positive common strength;
the continuous and adversary results have their explicit finite graph/workload
domains. Failed attacks are not robustness proofs. The first integrated
envelope attempt failed to import SymPy; the explicit-uv recovery and unchanged
code hashes are documented in `integration/recovery.md`. No failed run was
replaced by a successful record.

The historical envelope author code contains an unused incorrect lower-bound
comment. Its executed assertion, final analytic proposal, independent review
and portable code use the correct bound `N >= 2e+3t`. Frozen author bytes are
preserved and the stale comment is not promoted as a claim.

The new fixed-ray switching and minimax-workload explorations are outside this
release. Publication priority, full publisher-source access, practical benefit
and broader mathematics coverage remain open. Static workflow configuration
does not attest a future CI run.
