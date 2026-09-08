# Independent all-original-edge-deletions review

Verdict: PASS on all four mathematical integrity gates for the frozen six-case author packet. This proves the stated all-single-original-edge-deletion theorem for 3<=a<=b,c and any fixed pair u,v in the selected minimum part. No novelty, practical impact, optimality, or multi-deletion conclusion is certified. Portable implementation has a separate follow-up review.

## Reproduction: PASS

The independent evaluator was frozen in evaluator-contract.md. evaluate.py constructs a different cell order and obtains each FULL det(L+tD) with SymPy's polynomial DomainMatrix determinant, rather than the author's sums of principal minors. All 24 extracted q coefficients agree exactly with the saved expressions in the six author files (/q). For every case, exact polynomial cross multiplication proves that the saved canceled N/D equals the independently obtained coefficient-ratio difference. All shifted -N and D coefficient dictionaries agree entry-for-entry with /negative_numerator_terms and /denominator_terms; each has strictly positive coefficients and a strictly positive constant.

result.json:/case_results records, respectively, negative-numerator/denominator term counts: uB 275/431, rB 160/272, BC 157/266, uh 163/278, rh 118/212, Bh 115/206. Every negative-numerator minimum coefficient is 3 and every denominator minimum coefficient is 2. The complete values and constants are retained in result.json, not inferred from author's summary.

I independently reran all 36 full adjacency/fundamental matrix comparisons and all 18 strict differences at exactly (3,3,3),(3,4,5),(4,4,6), for six cases and two states (result.json:/matrices,/matrix_comparisons,/negative_differences). Each full K equals n-m+q2/q1, including empty-cell boundary cases. These checks diagnose the implementation; the polynomial identities and semantic proof supply universality.

## Specification compliance: PASS

manual-proof-notes.md provides the complete independent graph/orbit/spectrum/domain analysis. All original edges partition into nine endpoint categories; within-part permutations and swapping u,v preserve the prospective pair. B/C exchange reduces three categories to representative cases without requiring b<=c because b and c are independently >=a. This covers every fixed pair and every original deleted edge.

Only rB and rh can have an empty residual A cell at a=3. Its zero R column and positive row degree imply one exact artificial normalized-Laplacian eigenvalue 1. Removing the cell gives the genuine quotient, and the correction n-m cancels that extra contribution. No empty-cell degree or size is divided by zero. The code retains this formal cell consistently in both states. Strict connectedness and reversibility imply all nontrivial normalized-Laplacian eigenvalues are positive. Thus q1>0, q2/q1 gives the quotient spectral sum, and the same omitted-mode correction cancels between states. Exact rational identity plus positive saved D prevents any cancellation-domain loophole. Substitution x=a-3,y=b-a,z=c-a covers precisely the admitted integer domain, including ties and a=3.

## Source verification: PASS for the self-contained theorem

Sources are the frozen graph/domain contract in ../astra-all-deletions-work/plan.md, its method.md, and the author's six explicit determinant certificates. The source-to-claim bridge is derived directly in manual-proof-notes.md from the graph definition and elementary linear algebra. No borrowed edge-update theorem, literature novelty assumption, or unverified damage-dominance rule is used. The recovery amendment ../kemeny-discovery-round-1-work/all-deletions-recovery-amendment.md explicitly permits one serialization-only extra execution beyond the old cap. source.diff shows the native-bool positivity serialization correction and incidental blank line. Historical failures remain limitations of those runs; they are not mathematical evidence. This audit independently supplies the completed certificate verification.

## Implementation alignment: PASS for author packet

Read the actual author quotient construction and compare it to independently generated matrices and full determinants, saved rational expressions, coefficient dictionaries and full matrix K values. The proof's nine/six coverage, positive signs, and explicit empty-cell treatment agree with the implementation. The theorem is broader than the earlier uh-only result; it is certified here by six cases, not inferred from that special case. The separate portable checker and final publication prose require their own alignment checks.

## Raw execution and bounded correction

Environment setup and first attempt are recorded in run-0.json through run-2.json. Round 1 failed BEFORE any mathematics because the reviewer's helper inspect.py shadowed stdlib inspect at SymPy import. Renaming that helper to packet-inspection.py fixed only the environment naming collision; evaluate.py was unchanged. round2-plan.md freezes this correction, and round2-run.json retains actual argv, cwd, stdout, stderr and returncode 0. All failed output is retained. Two review rounds were used, with no added symbolic cases or finite search. Isolated D-drive uv environment: CPython 3.12.11, SymPy 1.14.0, D-drive uv cache. hashes.json pins source packets, specification, evaluator, result, logs, semantic notes and report. No shared source file was modified.
