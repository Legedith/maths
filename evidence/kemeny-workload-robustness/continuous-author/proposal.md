# Continuous robustness on the frozen network/workload set

Root-authored candidate; independent verification required before promotion. The sole evaluator passed rc0 with empty stderr. It produced96 continuous contexts and3896 strict candidate comparisons, all positive. This strengthens the earlier endpoint screen but does not extend to arbitrary part sizes or simultaneous edge changes.

## Claim and exact domain

Take H=(K_(a,b,c) join K1)-uh with part sizes333,334,345,446, u in A and h the hub. For each theta in{0,1/10,1/2}, endpoints are independent draws from p=(1-theta)Uniform+theta*delta_h. Choose exactly one missing edge to insert with conductance1. Existing conductances are1, except that any ONE existing edge may have conductance1+delta for any real delta in[-1/10,1/10]. Let O be the complete optimal insertion set before the existing-edge change.

The certificate establishes the stronger statement that every candidate in O has strictly smaller expected hitting time than every candidate outside O throughout the interval. Therefore every perturbed optimizer lies in O. Equalities within O can break: this does not claim that all original optimal candidates remain tied or optimal. Exactly one insertion is required; doing nothing is outside this comparison. Physical timing, traffic realism and engineering cost remain unassessed.

## Continuous comparison identity

Let M_e be the pseudoinverse after the unit insertion e but before the existing-edge perturbation. Put C=diag(p)-pp^T. The accepted weighted commute identity makes the objective proportional to tr(C M_e(delta)). For fixed delta the total conductance m+1+delta is common to every candidate, so it cancels in comparisons.

Writing f for the existing edge's signed incidence vector, rank-one inversion on the subspace perpendicular to constants gives

    M_e(delta)=M_e-delta*(M_e f)(M_e f)^T/(1+delta*r_e),
    r_e=f^T M_e f.

This edge has unit conductance in the unperturbed candidate graph, hence0<r_e<=1 by the effective-resistance variational bound. Therefore1+delta*r_e>=9/10 on the whole interval. All matrices remain connected, since every original conductance is at least9/10.

For the hub mixture and centered matrices/vectors, tr(C M)=(1-theta)[tr(M)/n+theta*M_hh]. Drop the positive common factor(1-theta)/n and define

    T_e=tr(M_e)+n*theta*(M_e)_hh,
    s_e=||M_e f||^2+n*theta*((M_e f)_h)^2.

The scaled comparison objective is Q_e(delta)=T_e-delta*s_e/(1+delta*r_e). For nominal optimal i and nominal nonoptimal j, let D=T_j-T_i. Directly bringing Q_j-Q_i over its positive common denominator gives the polynomial

    P_ji(delta)=D
      +[D(r_j+r_i)-s_j+s_i]*delta
      +[D*r_j*r_i-s_j*r_i+s_i*r_j]*delta^2.

Thus positivity of this exact quadratic on the interval proves strict separation. This is an elementary consequence of known inverse updates, not a claimed new generic optimization algorithm.

## Why the certificate covers every interval point and edge

A real quadratic A+B*x+C*x^2 has its minimum on a closed interval at an endpoint, except that a convex quadratic can also minimize at its vertex -B/(2C) when that vertex lies inside. The checker evaluates both endpoints and any such interior vertex using Fraction arithmetic. Every retained minimum is strictly positive. None of the3896 quadratics happened to have an interior vertex requiring that extra evaluation, but the criterion does not assume this in advance. Three exact residual evaluations are only diagnostics; the displayed algebra proves the polynomial identity at every delta.

Permutations inside A excluding u, inside B, and inside C preserve H and each fixed workload. They have exactly eight existing-edge classes: u-B,u-C,Aother-B,Aother-C,B-C,h-Aother,h-B,h-C. All are nonempty here. The missing edge uh is excluded from existing-edge perturbations. Changing a representative transports to every edge in its class by the same permutation, which also maps the full candidate set and O. Accordingly eight representatives suffice before perturbation, while every actual missing-edge insertion is enumerated afterward.

The four nominal graphs have10,13,20,28 missing edges. At theta0, O has2,6,10,15 members respectively; at theta1/10 and1/2 it consists of restoration alone. These sets are recomputed from full exact candidate matrices instead of inserted as assumed winners. There are4*3*8=96 contexts and8*((2*8+6*7+10*10+15*13)+2*(9+12+19+27))=3896 comparisons. Every possible pair in O times its complement is present once per context. Positivity therefore supports the stated finite-domain, continuous-interval claim.

## Implementation and evidence

check.py builds each adjacency, removes only uh, obtains a centered inverse from a Fraction grounded inverse and checks L*M=I-J/n. Each missing-edge insertion uses the rank-one formula. It retains all T,r,s values, polynomial coefficients, minimum arguments and values, sets, graph labels, and implementation hash in result.json. The generic graph, update, workload and symmetry bridges are explicit above; finite values do not replace these bridges.

run.py captures the evaluator's exact argv/cwd, D environment/cache, timeout, runtime, returncode and binary stdout/stderr. One permitted initial batch ran in about0.97seconds, Python3.12.11, rc0; no second batch or failure. The fresh output guard prevents overwriting result.json. Reproduction in a separate stage may copy the same source bytes before executing; a future public CLI is not implied by this prototype.

The separate simultaneous-perturbation gap bound and this one-edge interval certificate have different uncertainty sets. Neither should be used to claim the other. The bounded prior-work note identifies established rank-one/quadratic and Loewner methods and an unresolved close sensitivity source; family-specific publication priority remains unverified. Independent source review is in astra-link-robust-bound-review-work/source-review.md.
