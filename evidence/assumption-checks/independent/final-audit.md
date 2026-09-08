# Independent final audit: structured assumption checker 1.0.2

Auditor: `/root/sol_atlas_audit`  
Role: independent read-only chain-of-evidence verifier  
Implementation freeze: `atlas-checks/1.0.2`, manifest SHA-256 `50fd6ed3f43f8bdd30e325b249e605cd2bbde33db2336cf0142eba9a1ec5505d`

All four gates pass for the frozen structured checker within the stated evidence boundary.

| Gate | Verdict | Evidence |
|---|---|---|
| `reproduction` | **PASS** | The exact frozen 1.0.2 bytes matched the prospective oracle on all 80 cases (54 mathematical, 12 definedness/provenance/precedence, 14 malformed/type/resource), with zero escaped exceptions. The public path-free runner reproduced the identical output JSONL hash. A separate 8,400-digit result matched an independent Decimal oracle through both API and CLI. |
| `specification_compliance` | **PASS** | The final checker implements the frozen interface plus both preimplementation clarifications on the tested domain. Five public representation-boundary defects found after the first 80-case run are structured at 1.0.2, and the later valid-large-output serializer defect is repaired without changing Python's global integer digit limit. This is finite evidence, not exhaustive verification of all valid ASTs. |
| `source_verification` | **PASS** | Ten authoritative source anchors support the exposed graph, random-walk, electrical, and tree conventions with exact locators and limitations. For the fixed 24-result source-only retrieval review, two frozen reviewers agreed on 21 and three disagreements were source-resolved; descriptive final counts are 12 supported, 9 refuted, and 3 insufficient. An additive correction withdraws an unverified model string and fixes theorem 18276974 to 2302.07170v2 PDF p.3, Theorem 4 without changing labels. |
| `implementation_alignment` | **PASS** | The 1.0.2 freeze manifest SHA-256 and every one of its 19 declared files match. Only model.py and api.py differ among runtime files from 1.0.1, consistent with the exact-output formatter and version delta. The nine retrieval-derived structured fixtures match their declared hashes and expected instance verdicts: seven no-counterexample results and two connected-only spectrum abstentions. |

## Reproduction results

The final frozen run matched all **80/80** prospective oracle records: 54 mathematical, 12 definedness/provenance/precedence, and 14 malformed/type/resource cases. There were no escaped exceptions. The portable public runner produced the identical output JSONL SHA-256 `c2e4f4fe94e08318324ea779a152f4252ccc07c82c7bf82d44c2021fd98ebb78` and again compared 80/80.

The valid large-output probe contains 281 AST nodes at depth 10 and 140 `tree_mass` references. Both API and CLI returned the same 8,400-digit value as `Decimal(999999999999) ** 700` under precision 9,000; the decimal text SHA-256 is `3297d742456991a0e4d0964bc05ad156b0f0ce2258416a5549fa0dcd32c29be1`. Python's integer-string digit limit stayed 4,300 before and after the call, and no runtime file sets it globally.

## Source verification

The source matrix records ten convention anchors with URLs, exact PDF/book locators, local snapshot hashes, entailment, and limitations. In particular, Masuda, Porter and Lambiotte p.17 equations (75)-(77) support `L_rw=D^-1L=I-P`; Spielman Lecture 4 pp.1-2 and Chung book pp.2 and 15 support the row-walk convention and similarity to the distinct symmetric normalized matrix; Levin-Peres-Wilmer pp.7-10 and Theorem 4.9 separate stationarity from convergence; their network chapters and Spielman's tree notes support the electrical, commute, weighted-tree, and edge-inclusion quantities.

For the fixed 24-result retrieval corpus, two frozen source-only reviews agreed on 21 results. Three disagreements were adjudicated from exact-version sources. Final descriptive counts are 12 supported, 9 refuted, and 3 insufficient. The additive correction withdraws the self-inferred runtime-model string and corrects theorem 18276974 to arXiv 2302.07170v2, PDF p.3, Theorem 4; neither correction changes a label.

## Structured retrieval round two

All 24 retrieval rows remain accounted for. Sixteen are fully outside the grammar. Eight theorem IDs are syntax-mappable; six yield evaluable instances, while two disconnected spectrum witnesses use quantities deliberately undefined off connected graphs. Nine fixtures cover those eight IDs because the period result has separate even- and odd-cycle instances. The frozen checker returned seven `no_counterexample_in_instance` verdicts and two `abstain` verdicts, exactly as declared, with zero counterexamples and zero escaped exceptions.

This adds **zero incremental source-refutation detections**. A successful instance is not a theorem proof, and an abstention is not a source judgment.

## Historical evidence retained

- The first comparator's 20/80 report is an evaluator calibration failure. A corrected comparator scored the exact same immutable run 80/80; both are retained.
- The original 1.0.0 checker had five supplemental representation-boundary defects outside the 80 cases. Version 1.0.1 repaired them, and 1.0.2 preserves those repairs.
- Hash-matched retained 1.0.1 source reproduces the valid 8,400-digit serialization crash. Version 1.0.2 fixes it.
- The preliminary serializer reproduction that raced with a code edit is explicitly invalid and excluded.
- Exact-output verification attempt 01 failed one auditor-authored fraction-format assertion because it ignored canonical gcd reduction; attempt 02 changes the expectation only and passes all 16 checks.

## Limits

- The 80-case suite is prospective and independently generated but finite; 80/80 is not a proof over the full input space.
- The checker consumes structured ASTs and supplied provenance. It does not verify URLs or infer whether a natural-language slogan was translated correctly.
- The 24 retrieval results are a fixed purposive corpus. Their label counts are not prevalence, service accuracy, timing, productivity, novelty, or practical-impact estimates.
- Sixteen retrieval rows are outside the grammar. Of eight syntax-mappable theorem IDs, six have evaluable instances and two produce designed abstentions on disconnected spectrum quantities.
- The round-two outputs add zero source-refutation detections: seven instances found no counterexample and two abstained. This does not revise any source-only judgment.
- The historical reviewer/adjudicator model string is self-inferred and withdrawn; actual runtime model identity was not independently verified.
- No browser, DOM, WebMCP, or natural-language runtime validation is claimed here.

Machine-readable gate record: `final-audit.json`. Publication inventory: `publication/publication-manifest.json`.
