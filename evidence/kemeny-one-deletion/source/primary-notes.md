# Scoped primary-source notes

Retrieved/inspected 2026-09-08 by root, independently of the source investigator.

S1: Altafini, Bini, Cutini, Meini and Poloni, An Edge Centrality Measure
Based on the Kemeny Constant, SIAM J. Matrix Anal. Appl. 44(2), 2023,
DOI 10.1137/22M1486728.
URL: https://arpi.unipi.it/bitstream/11568/1170026/2/Poloni_1170026.pdf
Locators: PDF index 3, printed page 651, Corollaries 2.2-2.3; PDF index 4,
printed page 652, Theorem 3.1; PDF indices 1 and 5, printed pages 649 and
653, description of the loop replacement and start of Section 4.
The source supplies K=trace((I-P+1*pi)^(-1))-1 and its reciprocal-eigenvalue
form. It also supplies an exact update for ordinary non-cut-edge deletion.
Its modified nonnegative centrality replaces the removed edge with loops,
so that positivity is not a theorem about ordinary deletion.

S2: Breen, deBlieck and Vander Meulen, Kemeny's constant and Braess cliques
in graphs, arXiv:2608.04150v1, 2026-08-04.
URL: https://arxiv.org/html/2608.04150v1
Locator: Section 3, Lemmas 3.1-3.2 and Theorem 3.5.
Equitable/twin quotient spectra and clique-insertion formulas are published
tools. The twin-set insertion condition fails for u,v after removing uh:
their neighborhoods differ. Unaffected residual cells remain twins.
The theorem proofs here independently derive their graph and spectral
reductions; neither generic quotient compression nor edge updates are
claimed as new methods.

Source investigation: the unchanged investigator report is retained beside
this file. Its eight targeted queries and scoped source comparisons do not
certify originality. Root additionally queried the exact strings:

1. "Kemeny" "edge relocation" multipartite
2. "Kemeny" "edge switching" "multipartite"
3. "Kemeny" "rewiring" "optimal"

Those combined search returns mainly concerned stochastic resetting,
unrelated network models, voting, or unrelated uses of the name. They did
not identify a directly applicable theorem and are weak retrieval, not
evidence that the present sign or repair problem was open. No numerical
application result from those returns is adopted. Global novelty and real
network benefit remain unresolved.
