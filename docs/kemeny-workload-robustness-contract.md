# Workload and conductance robustness release contract

Frozen 2026-09-08. Base20fa6f15a4ed569f1285e1546d1cd872fd4e289b, the independently audited weighted-repair release. The previous goal turns made progress by proving and auditing a full workload envelope, eliminating hypotheses, quantifying finite model differences, and constructing robustness certificates. The broader mathematics-map goal remains active. This release consolidates connected findings within random walks and network repair; it does not expand the Site or broader atlas.

## Main theorem

Let H=(K_(a,b,c) join K1)-uh with integer3<=a<=b<=c, unit old conductances, u in A and h the hub. Choose exactly one missing edge of a prescribed common conductance t>0. The endpoint law is iid p=(1-theta)Uniform+theta*delta_h,0<=theta<1, with zero self-hitting time and conductance-proportional transitions. The law remains fixed across candidate graphs.

Prove the complete optimal insertion sets. For equal parts, the only possible winners are all u-incident A pairs and restoration; an explicit rational threshold in(0,1) separates them, with their union tied at the threshold. For unequal parts, the only possible winners are all internal pairs in every largest part and restoration; the explicit positive threshold may be at least1, in which case restoration never wins in the admitted interval. Include all ties, a=3, the positive denominators, and the common t factor in the covariance improvement. Prove both thresholds strictly decrease with t and approach positive limits. This is a prescribed-strength location theorem, not optimization over different candidate strengths.

The accepted unit-strength workload theorem and its finite exact switches may be reused as verified inputs/diagnostics. The all-t proof must use the full score identities, positive factored exclusion inequality, and endpoint bounds, not infer a universal result from a graph or strength grid. Explain that t=0 and theta=1 make actual comparisons degenerate; scaled limiting scores do not classify actual ties there. No-action optimization is outside the main theorem. Uniform scaling q of all old weights with a unit insertion is equivalent to t=1/q; preserve the same endpoint law when applying that interpretation.

## Perturbation findings

Publish the separate continuously certified finite-domain result: graphs333,334,345,446, theta0,1/10,1/2, any one existing edge changed to1+delta for every real delta in[-1/10,1/10], and a unit insertion. All3896 exact quadratic comparisons across96 contexts prove every nominal optimal candidate beats every nominal nonoptimal candidate. This implies containment of the new optimizer set in the old set; it does not preserve ties inside that set. Eight existing-edge representatives are justified by the original graph/workload symmetries, while every actual missing insertion is evaluated after perturbation. Explain denominator positivity, the quadratic identity and closed-interval minima.

Keep simultaneous uncertainty separate. The elementary Loewner gap certificate is sufficient, generally conservative, and uses a single common-volume cancellation. In the declared eight workload instances only three certificates reach a strict1% tolerance; this does not establish actual failure thresholds. Retain the deterministic sixteen-pattern simultaneous screen: three explicit10% assignments switch the winning repair, while eight unsuccessful1% patterns do not prove robustness. Independent direct hitting/matrix checks must support the counterexample and complete recorded candidate coverage. These are mathematical model results, not physical performance or optimal adversaries.

## Implementation and verification

Provide a pinned uv project at experiments/kemeny-workload-proof with Python3.12.11 and SymPy1.14.0. The standalone envelope checker reconstructs33 exact symbolic identities and complete positive coefficient lists; it must explicitly name the additional independently audited analytic bridges. The separate continuous checker uses only the standard library and reproduces all3896 comparisons. Both require a fresh --output path. Use ordinary Python with assertions enabled for these proof programs. No D-specific source paths in the portable implementations; D is the host environment/cache preference.

Canonical commands, with fresh output names from the repository root:

    uv run --project experiments/kemeny-workload-proof --frozen python experiments/kemeny-workload-proof/verify_workload_envelope.py --output work/kemeny-workload/envelope-01.json
    uv run --project experiments/kemeny-workload-proof --frozen python experiments/kemeny-workload-proof/verify_continuous_perturbation.py --output work/kemeny-workload/continuous-01.json

Root alone integrates shared repository files. Independent reviewers must inspect changed code and fresh replays; implementation workers cannot self-certify final gates. Reuse unchanged source/mathematical audits and keep author, reviewer, implementation, integration and historical failure records distinct. Preserve frozen bytes and failed attempts; use strict UTF-8 or ASCII for new locator text. Add CI reproduction with raw stdout/stderr/status artifacts. After push, inspect actual workflows and download/compare the new outputs, rather than treating a static workflow as executed evidence.

Create typed source/method/result/conclusion provenance before final prose. Final Critic/Resolve has at most two rounds, followed by a deterministic PASS gate. This release does not retroactively certify old commits or unrelated work. Earlier unpublished strength-growth corollaries and the two-edge greedy conjecture are not part of its universal claims.

## Source and contribution boundary

Credit the established commute/resistance connection, inverse edge updates, complete-multipartite inverse formulas, normalized conductance optimization, workload-weighted resistance objectives, and uncertainty methods. Keep consensus stability distinct from invariance of the best insertion. Preserve the close Kirchhoff-sensitivity source access gap and existing join-formula overlap. Bounded searches cannot establish originality. The possible contribution is the complete family-specific workload/strength rule and precisely scoped perturbation findings; no novel generic inverse algorithm, deployed benefit, Lean formalization, global integer-threshold classification or completed mathematics map is claimed.
