# Independent review: optimum when hub repair is forbidden

Verdict: PASS on all four scoped mathematical gates. This is a next-candidate audit; no current release/project file was changed or promoted. Independent reviewer is not the alternative-repair author.

## Verified conclusion and scope
Let H=(K_(a,b,c) join K1)-uh, with integer 3<=a<=b,c and u in A. Exactly one missing edge may be inserted, with unit weight, and restoring uh is forbidden. Then the optimal edge set is exactly the unordered pairs wholly in A excluding u. There is one optimal orbit and binomial(a-1,2) optimal edges. A unique edge exists exactly when a=3. The strict comparison includes tied sizes a=b or a=c. This is not a claim that all minimizers are a single edge for arbitrary a, and does not rank B against C.

After excluding uh, the only missing-edge categories are u-incident A pairs, untouched A pairs, B pairs, and C pairs. These exhaust the original within-part nonedges. Part-preserving automorphisms fixing u and h map any untouched A pair to any other, so every such pair has the same final K. The already independently audited strict uv-minus-untouched_A comparison excludes the first category. The TWO new strict differences exclude B and C. Therefore both necessity and sufficiency for the exact set of optimal edges follow. All categories exist since every part has at least three vertices.

## Independent computation
The review reused the previously independently reconstructed SINGLETON-endpoint full determinant K formulas in astra-postfailure-review-work, not the current author's solver. Their recorded hashes, prior full-matrix result, prior verdict and original input hashes were verified. The author's frozen input hash exactly matches the same previously reviewed postfailure batch2.json. Every supplied new-packet hash was also verified. result.json lists all verified paths.

For B and C separately, evaluate.py independently subtracts the reused K formulas and checks exact equality with the author's rational difference. It reconstructs both complete exponent/coefficient lists, rejects duplicate exponents or invalid exponent shapes, checks every coefficient is a positive integer and every constant is positive, and checks EACH numerator and denominator polynomial identity against the stored rational expression after a=3+x,b=3+x+y,c=3+x+z. It also checks the resulting rational ratio against the independently reconstructed difference. Thus coefficient identities do not rest on a finite sample.

Both numerators have 104 nonzero terms, minimum coefficient 2 and constant 39690; each denominator has minimum coefficient 1 and constant 77157360. For x,y,z>=0 these imply numerator>=39690>0 and denominator>=77157360>0. This parameter substitution covers all admitted integer sizes, including a=3 and either/both tied minima. There is no division by size differences and no omitted tie boundary.

The prior independently computed full 10-vertex matrices give K(untouched_A)=497/60 and K(B)=K(C)=80519/9720 at (3,3,3). Subtraction independently reproduces 1/1944 for both new gaps. The old quotient normalization, merged-pair/zero-mode accounting, empty A-rest correction and stationary-target convention were already audited against these full matrices and remain unchanged; their hashes were verified rather than recomputing unchanged determinants.

## Four gates
1. Reproduction PASS: both independently reconstructed differences match, both complete numerator/denominator identities pass, every coefficient and constant is positive, and the independent full-matrix gap is 1/1944. Evidence: evaluate.py, result.json, stdout.txt, execution.json.
2. Specification compliance PASS: exact admitted non-restoration orbit coverage, fixed unit-weight single insertion, complete a=3 and tied-size domain, and optimum-set cardinality are justified above. No current release expansion occurred.
3. Source verification PASS within mathematical entailment: same previously audited graph formulas and input bytes were verified, and two new differences were independently reconstructed. Prior uv domination and graph-to-quotient arguments are reused only within their already reviewed scope. External priority attribution, novelty and impact are excluded.
4. Implementation alignment PASS for this candidate packet: inspected batch1.py performs precisely the declared two subtractions and stores their actual complete coefficient lists; those lists and advertised numerical constants match the independently evaluated artifacts. No portable next-release implementation or final publication prose is reviewed here.

## Execution accounting
One frozen review round ran, no failure or retry. evaluate.py executed via run.py with an explicit 180-second cap; execution.json retains actual argv, elapsed seconds and rc=0, stdout.txt and stderr.txt retain raw streams (evaluator stderr empty). wrapper.log and wrapper.rc retain the uv invocation and wrapper status. The plan records the evaluator command; actual invocation used the capture wrapper: uv run --python .venv/Scripts/python.exe --no-project run.py. uv's --no-project warning is retained separately and is not an evaluator failure. Environment/cache are isolated in this D-drive stage (Python 3.13.7, SymPy 1.14.0).

No novelty, practical benefit, cost variation, other failure type, weighted graph, or multi-edge intervention claim is certified. Packet frozen for the following continuation.
