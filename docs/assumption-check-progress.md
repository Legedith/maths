# Structured checking milestone: integration status

The prospective contract and interface remain unchanged. This page records later progress without rewriting the frozen specification.

On 2026-09-08, the implementation worker froze `atlas-checks/1.0.0` under manifest SHA-256 `3f81fa516b2e9240abdc9141874b2108bc6b02af84de2f62b593a211ce58c8c5`. Root verified all 24 listed file hashes and copied the 14 runtime modules byte for byte into `src/atlas_checks/`. The original worker package metadata and development logs are retained under `evidence/assumption-checks/worker/`.

The root package now includes both `atlas_engine` and `atlas_checks`. Development tests live in `tests/assumption_checks/`, preserving the worker's relative helper imports. The complete integrated project test run passed 132 tests. This establishes packaging and regression evidence; it is not the independent mathematical gate.

The independent verifier committed 80 structured evaluation cases before inspecting implementation output: 54 mathematical cases, 12 definedness/provenance/precedence cases and 14 representation/resource cases. The first frozen run matched all 80 semantic gold records. The cases and gold labels were not provided to the implementation author or root before the implementation freeze. A first comparison script treated equivalent rational spellings and noncontractual type/error labels as mismatches; the retained second comparison corrected that evaluator issue against the same original outputs. This was not a replacement implementation run.

Later public probes found five representation defects outside the 80-case suite. The 1.0.1 patch and its first independent rerun are retained separately; that rerun also matched all 80 cases. A further admitted expression exposed a decimal-output failure for an 8,400-digit exact result. Version 1.0.2 fixes output formatting without changing the mathematical quantities or the frozen input contract. Its 19-file manifest is `evidence/assumption-checks/worker/root-patch-freeze-v1.0.2.json`, SHA-256 `50fd6ed3f43f8bdd30e325b249e605cd2bbde33db2336cf0142eba9a1ec5505d`. The latest integrated development/regression suite passed 155 tests. The independent final report passes all four scoped checks for 1.0.2; its 80-case rerun and the integrated portable rerun have identical output bytes. These finite evaluations do not establish universal correctness.

Separately, the prospective retrieval policy produced 24 unique results from 12 fixed queries. Both AI reviewers froze source-only labels before seeing each other's labels: A under SHA-256 `39123f5a9d8197de23be95969e8d8dca432fbb3390fab63640487dc268b50307` and B under `cc99747b80e03dfc24a5518bd53eb67e98f5b164c761c1a33dba03be33d6d2f7`. They agreed on 21 records and disagreed on three. Subsequent source-resolving adjudication retained 12 supported, nine refuted and three insufficient labels. These are descriptive counts for a purposive sample of generated summaries, not an error-rate estimate or a finding that the original papers are wrong.

The separate machine-checking round is complete. Six retrieved statements have evaluable instance annotations; two more map syntactically but require disconnected spectrum quantities that the API deliberately leaves undefined; the remaining 16 have individually recorded exclusions. The six evaluable statements produce seven fixtures because the cycle-period statement has both even- and odd-cycle instances. All nine fixtures matched their declared instance verdicts: seven no-counterexample results and two abstentions. The checker added zero source-refutation detections. This separation prevents source-review findings from being misreported as automated detections. No researcher-time saving or new mathematical discovery is established by this milestone.

The [independent final report](../evidence/assumption-checks/independent/final-audit.md), immutable original reviews, additive corrections, raw runs and public 80-case release are retained under `evidence/assumption-checks/independent/`. This progress page supersedes the pending-review wording in the immutable frozen implementation README. The final project evidence bundle is being assembled and independently reviewed separately.

## Candidate interface

```powershell
uv run --frozen python -m atlas_checks input.json
```

`check_transfer(payload)` evaluates explicitly supplied structured claims and assumptions. It returns exact values, traces, provenance and one of five scoped verdicts. It does not translate arbitrary prose, verify source entailment or establish a universal theorem from one successful instance. The browser graph lab keeps its original unweighted interface; this Python checker has not been presented as a browser execution feature.

See the immutable [interface](assumption-check-interface.md), [clarifications](assumption-check-clarifications.md), [additional clarification](assumption-check-clarification-2.md), and [worker implementation documentation](../README-checks.md). The active evidence bundle remains pending until independent evaluation and source review are complete.
