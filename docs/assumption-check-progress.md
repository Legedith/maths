# Structured checking milestone: integration status

The prospective contract and interface remain unchanged. This page records later progress without rewriting the frozen specification.

On 2026-09-08, the implementation worker froze `atlas-checks/1.0.0` under manifest SHA-256 `3f81fa516b2e9240abdc9141874b2108bc6b02af84de2f62b593a211ce58c8c5`. Root verified all 24 listed file hashes and copied the 14 runtime modules byte for byte into `src/atlas_checks/`. The original worker package metadata and development logs are retained under `evidence/assumption-checks/worker/`.

The root package now includes both `atlas_engine` and `atlas_checks`. Development tests live in `tests/assumption_checks/`, preserving the worker's relative helper imports. The complete integrated project test run passed 132 tests. This establishes packaging and regression evidence; it is not the independent mathematical gate.

The independent verifier committed 80 structured evaluation cases before inspecting implementation output: 54 mathematical cases, 12 definedness/provenance/precedence cases and 14 representation/resource cases. The first run is pending. Its cases and gold labels have not been provided to the implementation author or root before this freeze.

Separately, the prospective retrieval policy produced 24 unique results from 12 fixed queries. Reviewer A has frozen source-only labels under SHA-256 `39123f5a9d8197de23be95969e8d8dca432fbb3390fab63640487dc268b50307`; reviewer B is still independent and unfinished. No retrieval-review outcome is claimed here.

## Candidate interface

```powershell
uv run --frozen python -m atlas_checks input.json
```

`check_transfer(payload)` evaluates explicitly supplied structured claims and assumptions. It returns exact values, traces, provenance and one of five scoped verdicts. It does not translate arbitrary prose, verify source entailment or establish a universal theorem from one successful instance. The browser graph lab keeps its original unweighted interface; this Python checker has not been presented as a browser execution feature.

See the immutable [interface](assumption-check-interface.md), [clarifications](assumption-check-clarifications.md), [additional clarification](assumption-check-clarification-2.md), and [worker implementation documentation](../README-checks.md). The active evidence bundle remains pending until independent evaluation and source review are complete.
