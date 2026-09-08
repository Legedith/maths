# Independent continuous one-edge certificate review

Reviewer /root/astra_damage_symbolic, 2026-09-08. All four scoped gates PASS. No material correction. This verifies the frozen root prototype and mathematical statement, not a future changed public CLI or publication gate.

## Reproduction: PASS

One logged <=60s uv Python3.12.11/SymPy1.14.0 batch reconstructed all71 candidate pseudoinverses independently as (L_candidate+J/n)^(-1)-J/n, with a full centered inverse for each actual missing edge. No root grounded inverse or root solver was executed/copied. Each inverse satisfies L_candidate*M=I-J/n. For every context, independently calculated T,r,s agree with the certificate. Every quadratic was reconstructed by interpolation of its cross-multiplied rational comparison at -1/10,0,1/10, rather than copying the root coefficient formula. All3896 coefficient triples, minimum values/locations, tested arguments and strict flags agree exactly. Coverage is96contexts. Four direct full inversions of perturbed333 matrices (u-B perturbation, one incumbent and outsider, both endpoints) agree with the rational update diagnostics.

The run returned0. stderr contains uv package-index compatibility warnings/download/install messages, not an evaluator failure; it is retained without claiming empty stderr. The root's separate canonical run has rc0, runtime below60s and empty stderr as reported. All8 root manifest entries and the three supplied hashes match. This reviewer needed no second batch and no broader domain.

## Specification compliance: PASS

The frozen root contract.md and this review's plan.md fix333,334,345,446, theta0,1/10,1/2, exactly one unit missing-edge insertion and exactly one existing edge changed by real delta in[-1/10,1/10]. Restoration uh is eligible for insertion but is not an existing edge. All10,13,20,28 missing edges were independently enumerated. At theta0 the optimal sets have2,6,10,15 edges; at each positive theta restoration alone wins. The checker recomputes these sets from nominal matrices, not just assumed theorem labels.

Under the subgroup independently permuting A without u, B and C while fixing u,h, existing edges partition into u-B,u-C,Aother-B,Aother-C,B-C,h-Aother,h-B,h-C. Their sizes are b,c,(a-1)b,(a-1)c,bc,a-1,b,c; they sum to m and each class is nonempty. Every class is transitive under that subgroup. The workload, nominal candidate set and complete original optimal set O are invariant. Transporting a representative perturbation by such a permutation maps every candidate comparison onto the corresponding actual-edge comparison. Equal-sized B,C may admit additional symmetries; using this finer eight-class subgroup partition remains complete. No assertion that these symmetries survive a fixed perturbation is needed, since all actual candidates are checked afterward.

For each of96contexts, the retained comparisons are exactly O times its complement with no duplicates or missing pairs. Total8[(16+42+100+195)+2(9+12+19+27)]=3896. The actual theorem is strict separation of every old optimum from every old nonoptimum throughout the interval, hence the new argmin is a subset of O. It does not preserve ties or guarantee every member of O remains optimal. The domain excludes simultaneous changes, arbitrary sizes, arbitrary workloads and no-action comparisons.

## Mathematical bridge and implementation alignment: PASS

On1-perp, positive conductances give an invertible Laplacian. The changed existing edge still has weight1 in each nominal candidate graph. Thomson's principle permits routing unit flow directly through that edge at energy1, giving0<r<=1. Thus1+delta*r>=9/10 and all changed graphs stay connected. Rank-one inversion yields Q_e(delta)=T_e-delta*s_e/(1+delta*r_e). For fixed iid p, commute symmetry gives2(m+1+delta)tr(CM); the hub-mixture identity gives tr(CM)=(1-theta)[tr(M)/n+theta*M_hh]. All factors canceled in the root comparison are positive and common across candidates. They cannot be canceled against no action or unequal inserted weights.

Bringing Q_j-Q_i to a common denominator yields a polynomial of degree at most2. The denominator is positive throughout the interval, so its sign is the comparison sign. Three exact interpolation values uniquely determine that polynomial because the degree bound is an algebraic proof, not a numerical assumption. This makes the independently reconstructed coefficients a full identity check, not three-point evidence for arbitrary functions.

A quadratic's interval minimum is at an endpoint unless its leading coefficient is positive and its stationary point lies inside. Root and reviewer both implement that complete criterion, including linear/constant cases. All3896 minima are strictly positive; no convex interior vertex occurs in this packet. No hypothetical interior branch is claimed empirically exercised. Root's Fraction arithmetic, workload scaling, insertion update, pair coverage and certificate serialization agree with the prose. The immutable output guard is respected; root result bytes were never changed.

## Source verification: PASS, bounded reuse

This reviewer authored the earlier source investigation and therefore does not use it as a self-certified source gate. The separate independent source review ../astra-link-robust-bound-review-work/source-review.md was read and is pinned in input-hashes.json. It independently checks the actual Zelazo-Burger passages, Sardar publisher preview/access gap, and reused Monnig-Meyer/Ghosh sources, and explicitly accepts the quadratic/Loewner algebra as known-method inference. This supplies the distinct source reviewer required here. It does not establish global novelty or close the unresolved fulltext overlap lead. No source retrieval, new priority claim or physical-benefit claim is introduced.

## Frozen packet

plan.md, check.py, run.py, run.json, stdout.bin and stderr.bin retain the sole independent batch. input-hashes.json pins root contract/proposal/code/results/manifest/run and the distinct source review. verdict.json records the four scoped checks; hashes.json seals this directory. All other stages/project remained read-only. A changed portable CLI or final publication bundle requires its own later alignment review.
