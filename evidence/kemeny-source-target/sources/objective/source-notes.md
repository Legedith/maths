# One pinned reachability objective: exact alignment

Author investigation; independent source/algebra audit required. No code execution, dataset access, empirical reproduction, or reuse authorization.

## Immutable scope and primary locators

The GitHub commits/main API response (request/raw-01.json) resolves revision `20f35f4c28da3f40049f5b10caa64a3371905cb8`. Two individual files were then read at that revision: [utils.py](https://github.com/alexmartinezmiguel/reachability/blob/20f35f4c28da3f40049f5b10caa64a3371905cb8/utils.py) (request-02.json/raw-02.txt), and [compute_SLSQP_rewirings-reweighting.py](https://github.com/alexmartinezmiguel/reachability/blob/20f35f4c28da3f40049f5b10caa64a3371905cb8/compute_SLSQP_rewirings-reweighting.py) (request-03.json/raw-03.txt). Three successful HTTP GET requests, zero searches, zero clone, zero execution. Raw files remain local, not proposed for public redistribution. Earlier publisher/README access and limitations are retained in astra-source-target-priority-work and its independent review.

## Exact normalization in the selected code

Let P be a finite irreducible row-stochastic transition matrix, Q_j=P with row and column j removed, and F_j=(I-Q_j)^(-1). Directed first-step equations give H_ij=(F_j*1)_i for i!=j and H_jj=0. Hence S_j=sum(F_j)=sum_i H_ij and S=sum_j S_j.

utils.py lines 38-55 solve for F; lines 76-88 remove the target. Its mean helper at lines 166-180 returns S/[n^2(n-1)]. The selected SLSQP `fun` independently implements exactly that same factor at lines 48-56, returning it as `reach` at line 114. Therefore the code score G is

    G=S/[n^2(n-1)] = U_0/(n-1) = C/n,

where U_0=S/n^2 is uniform independent source and target with the zero diagonal included, and C=S/[n(n-1)] is the mean conditioned on distinct source and target. The selected implementation is neither unscaled U_0 nor unscaled C. This is a static formula finding; the incomplete retained publisher equations do not establish whether the paper intentionally uses this extra normalization. Do not label it a paper error based on this inspection.

For our uniform-source, target p_theta=(1-theta)Uniform+theta*delta_q objective on the SAME P,

    U_theta=(1-theta)*S/n^2 + theta*S_q/n
           =(1-theta)*(n-1)*G + theta*S_q/n.

The current selected function has no mixed-target weighting: it sums every target equally. A freshly written weighted mathematical analogue sum_j p_theta(j)*S_j/[n(n-1)] would equal U_theta/(n-1). For fixed n a common positive factor preserves action rankings and relative regret if applied consistently to both action and oracle. It does not justify matching scores computed on different transition matrices or feasible action sets. Source and target conventions must remain explicit.

## Matrix and intervention differences

SLSQP lines 35-46 form X from selected directed entries, then use P=0.985*X+0.015*J/n. The feasible-set code, lines 179-203, imposes positive selected-entry bounds and per-row sum 1; utils.py lines 393-421 select entries by relevance threshold and exclude the source itself. Conditional on feasible nonnegative row-stochastic X, the damped P is row-stochastic and entrywise positive, hence irreducible and all target hitting means finite. No separate strong-connectivity check is necessary for that damped feasible matrix. This is not a claim that every intermediate floating SLSQP evaluation exactly satisfies the constraints: `fun` itself does not validate them. The solve can only be interpreted as hitting times when its input is a valid transition matrix.

The damping introduces positive diagonal entries and all-to-all transitions. This is a different chain from the original X and is not automatically in our loopless undirected-conductance theorem's domain. Lines 61-74 also report a separate damped top-k score `reach_k`; it is not the full-support `reach` returned to the optimizer. No optimizer/gradient correctness or convergence audit was performed.

Selected directed probabilities can change across many rows simultaneously subject to relevance and row constraints. No undirected reciprocity/conductance constraint or single-edge-strength parameter is imposed in this code. Our insertion changes one symmetric conductance pair, its two endpoint degrees, and corresponding transition rows through degree normalization. The prior publisher passages describe discrete outgoing-link replacement preserving its probability, but no discrete implementation was inspected in this bounded task. Neither intervention is directly interchangeable with the other.

## Feasible comparison protocol and remaining gaps

First compare independently written first-step solves on one synthetic valid P: compute every S_j, U_0 and C, then verify the exact factors above. A rational positive P permits exact arithmetic. This would validate the formula mapping, not reproduce the authors' empirical results. For the undirected theorem choose P=D^(-1)W from a connected positive undirected graph and compare our objective against a newly implemented absorbing-matrix calculation on precisely that P; do not silently apply the repository's teleportation or top-k transformation. Add mixed-target weighting explicitly and preserve the actual conductance-induced row updates. Comparing optimization algorithms would require a separately agreed common feasible set; this inspection does not supply one.

The prior inspected README/root did not expose a code license, and its dataset link failed. This task did not resolve those terms; an article license does not settle code/data terms, and absence in inspected pages is not a global prohibition finding. An actual third-party implementation run/reuse or dataset comparison remains separate work. No improvement, model validation, global literature absence, or novelty is claimed.
