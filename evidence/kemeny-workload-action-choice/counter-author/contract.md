# Frozen unequal no-action proof search

Domain integers3<=a<=b<=c,c>a, theta in[0,1), unit insertion. No numerical grid. At most2 symbolic evaluators60s each with uv Python3.12.11/SymPy1.14.0,D cache/environment; retain failures.

Approaches: (1) show positive crossing margin F_C(tau) for all sorted sizes, even tau>=1, plus positive restoration slope. Selected: simplifies the two envelope cases at once. (2) constrain tau<1 and tau>=1 separately with polynomial inequalities; reserve if unconditional crossing positivity fails. (3) search exact counterexample by symbolic asymptotics; reserve, no numeric grid allowed.

Batch1 derive cancellation F_C(tau)=C[m-(n-1)k]-T0+(n-1)W, and restoration slope. Factor denominators; expand only these two univariate-in-c/rational numerators under a=x+3,b=a+y,c=b+z, record all coefficients and signs. This substitution parametrizes entire sorted nonnegative orthant; strict unequal is subset. Positive coefficient certificate is valid if all coefficients nonnegative with positive constant and denominator factors positive. If any coefficient negative, report failure of certificate, not false theorem, and freeze a second targeted bound route before execution. Accepted uniform/envelope/inverse arguments remain separate analytic inputs; proposal not self-certified.
