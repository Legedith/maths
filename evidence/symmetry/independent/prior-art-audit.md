# Primary-source prior-art audit

Date: 2026-09-08.  Search target: whether unordered-terminal graph
canonicalization, caching one evaluation per isomorphism class, and transporting
an equivariant multi-field result can be described as globally novel.

## Sources checked and what they establish

1. Brendan D. McKay, *Practical Graph Isomorphism*, Congressus Numerantium 30
   (1981), 45-87.  Author-hosted scan:
   https://users.cecs.anu.edu.au/~bdm/papers/pgi.pdf

   McKay defines canonical labels for vertex-coloured graphs, requires
   invariance under relabelling, relates equal canonical labels to an
   automorphism, and formulates coloured-graph isomorphism via a vertex
   partition.  An unordered distinguished pair is directly represented as one
   two-vertex colour cell with the remaining vertices in another cell.  The
   selected exhaustive minimum-bit-mask construction is a small-domain brute
   force canonical label, not a new canonization principle.

2. Johannes Koebler and Oleg Verbitsky, *From Invariants to Canonization in
   Parallel*, arXiv:cs/0608074 (2006; revised 2007):
   https://arxiv.org/abs/cs/0608074

   The paper defines a complete graph invariant, canonical form, and canonical
   labelling, including extensions to coloured graphs.  It reinforces that
   mapping isomorphic graphs to the same representative is established theory.

3. Jens Niehaus, Christian Igel, and Wolfgang Banzhaf, *Reducing the Number of
   Fitness Evaluations in Graph Genetic Programming Using a Canonical Graph
   Indexed Database*, Evolutionary Computation 15(2) (2007), 199-221,
   DOI 10.1162/evco.2007.15.2.199.  Author-hosted paper:
   https://www.cs.mun.ca/~banzhaf/papers/ecj2007.pdf

   This is particularly close prior art for the optimization pattern.  Section
   5 describes storing and looking up canonically labelled graphs so an
   isomorphic graph evaluated earlier avoids a new evaluation; the paper
   empirically measures saved evaluations.  Its workload and cached output are
   different, but it rules out claiming that canonical-form-indexed reuse of
   expensive graph evaluation is a new general algorithmic idea.

4. Ashok K. Chandra, Prabhakar Raghavan, Walter L. Ruzzo, Roman Smolensky, and
   Prasoon Tiwari, *The Electrical Resistance of a Graph Captures Its Commute and
   Cover Times*, Computational Complexity 6 (1996), 312-340.  Author-hosted
   paper: https://homes.cs.washington.edu/~ruzzo/papers/resist.pdf

   The paper defines one-sided hitting times and commute as their sum, and proves
   `C_uv = H_uv + H_vu = 2m R_uv`.  This supports the established status of the
   electrical/Markov identities while also keeping the two directional hitting
   quantities distinct.

5. Peter G. Doyle and J. Laurie Snell, *Random Walks and Electric Networks*
   (1984 monograph; freely redistributed 2006 version):
   https://math.dartmouth.edu/~doyle/docs/walks/walks.pdf

   The monograph develops voltage/current and random-walk correspondence,
   defines effective resistance through terminal voltage and current, and uses
   uniqueness principles for harmonic/Dirichlet solutions.  Endpoint voltage
   reversal and its gauge correction are applications of these classical facts.

6. Robert Burton and Robin Pemantle, *Local Characteristics, Entropy and Limit
   Theorems for Spanning Trees and Domino Tilings via Transfer-Impedances*,
   Annals of Probability 21 (1993), 1329-1371; arXiv version:
   https://arxiv.org/abs/math/0404048

   The paper develops finite-dimensional marginals of uniform spanning trees
   from transfer impedance.  Together with Kirchhoff's classical effective
   resistance formula, it places edge-in-tree probabilities firmly in prior
   art.  The project's subset enumeration remains valuable as an independent
   oracle, not a new identity.

7. Sékou-Oumar Kaba et al., *Equivariance with Learned Canonicalization
   Functions*, ICML/PMLR 202 (2023):
   https://proceedings.mlr.press/v202/kaba23a.html

   This is a different machine-learning setting, so it is not direct prior art
   for the exact graph engine.  It does formalize the broad pattern of
   canonicalizing an input, applying another function in canonical coordinates,
   and transforming the output, including the complication from stabilizers and
   tied canonical poses.  It supports treating full-output transport as an
   equivariance application rather than a globally new concept.

## Calibrated conclusion

The search found direct primary prior art for canonical graph labels and for a
canonical-graph-indexed database that avoids repeated graph evaluations.  It
also found established primary sources for every mathematical transport
ingredient.  I did not locate a source with this exact combination of an
unordered terminal pair and this exact result dictionary; absence from a
bounded search is not evidence of global novelty.

Defensible wording is: a newly implemented, project-specific optimization of
the Mathematics Atlas exact-analysis batch workload, assembled from established
canonicalization, symmetry, electrical-network, Markov, and spanning-tree
facts.  Any speed or reuse claim must be limited to the frozen benchmark and its
audited environment.  No larger scientific or real-world impact has been
demonstrated.
