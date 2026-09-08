# Fixed source destroys finite-strength attainment

Exploratory author result requiring distinct audit. A counterexample to extending uniform-source finite attainment to arbitrary fixed sources; no change to the accepted theorem or implementation API.

Take the three-vertex path with c01=1 and c12=2, fixed source 1, and add the absent edge 02 with conductance t>=0. The target is independent with law (1-theta)Uniform+theta*delta1, where 0<=theta<=h<1. H11=0. All times are actual discrete-time random-walk steps, not conductance-normalized resistance scores.

For target 0, the directed first-step equations are H10=1+(2/3)H20 and H20=1+2H10/(2+t). Thus H10=5(t+2)/(3t+2). For target 2, H12=1+(1/3)H02 and H02=1+H12/(1+t), giving H12=4(t+1)/(3t+2). The source vertex has total conductance 3 independently of t; the other transition denominators change to 1+t and 2+t. This accounts for the actual walk and does not assume symmetric directed hitting times.

Consequently the target-averaged objective is

    U_theta(t)=(1-theta)*(9*t+14)/(3*(3*t+2))
              =(1-theta)*(1+8/(3*(3*t+2))).

For every theta<1 and finite t>=0,

    U'_theta(t)=-8*(1-theta)/(3*t+2)^2 < 0,
    U_theta(0)=7*(1-theta)/3,
    lim_{t->infinity} U_theta(t)=1-theta,
    U_theta(t)-(1-theta)=8*(1-theta)/(3*(3*t+2)) > 0.

Thus the infimum is positive and is not attained at any finite conductance. Infinity is a limit, not a legal finite-strength action. Uniform-source coercivity cannot be transferred to this fixed-source model. Strict convexity alone does not repair attainment: U''=48*(1-theta)/(3*t+2)^3>0 here despite the missing finite minimizer. Theta=1 is excluded; there the objective is identically zero.

For any closed [l,h] with h<1, the same failure holds uniformly. If one defines an endpoint oracle by its infimum rather than an attained minimum, the relative regret is 8/(3*(3*t+2)), independent of theta, with unattained infimum zero. A formulation requiring an attained oracle minimum must be revised before such a regret is even introduced. This is a mathematical distinction, not a claim about the current solver's accepted domain.

A minimal mathematical remedy is a prescribed finite strength cap 0<=t<=Tmax. Continuity gives attainment on that compact interval; this example's unique optimizer is Tmax (including the singleton cap Tmax=0). A general bounded-strength candidate scheme must include the upper boundary as well as zero and interior candidates. No physical justification or calibration for a cap or cost law is asserted.

Evidence: plan.md froze this one graph and selected first-step equations over inverse updates and numerical sampling. check.py independently solves both two-equation systems and verifies exact residuals, objective, derivative, finite gap, and limits. result.json and logs/attempt-explore01.* retain the sole evaluator. Python 3.12.11/SymPy 1.14.0, D isolated environment/cache, uv outer and child, process-tree-aware logger; rc0, no timeout, empty stderr, 2.750009 seconds under a 60-second cap. Setup via frozen uv sync succeeded before evaluation. No other graph, symmetric variant, second run, external-source assertion, or shared write occurred.

This is a proposed source-law extension and a refuted assumption, not a validated application, novelty claim, or author-certified release gate.
