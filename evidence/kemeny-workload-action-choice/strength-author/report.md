# Candidate exact strength rescue at344

Author result; separate independent audit required. Frozen graph is H=(K_3,4,4 join K1)-uh, fixed iid hub-mixture theta=14/405, unit existing weights. A freely chosen subunit insertion improves no action although every unit insertion worsens it.

## Exact global optimum

Label A={0,1,2},B={3,4,5,6},C={7,8,9,10},h=11,u=0. The complete optimal edge set is ALL twelve internal pairs in B or C. Each has the SAME unique optimal strength
 tstar=4*(sqrt(27945/22432)-1)=(-5608+9*sqrt(483690))/1402,
strictly between0 and1. The exact global objective is
 Ustar=(391/2430)*(9*sqrt(483690)+64492)^2/78357780.
The no-action objective is(391/2430)*(62155/972), strictly larger. A simple rational improvement witness is any internal B/C pair at strength1/2:
 U(1/2)-U(noaction)=-117691/11809800<0.
No edge in A and no restoration edge ties the optimum. At t0 all action labels represent the same no-action graph; those are not global optima.

H1, some subunit insertion improves: ACCEPTED at this frozen instance. H2, largest-part locations optimize after strength selection: ACCEPTED here. H3, optimized restoration wins globally: REJECTED by strict exact minimum comparison. These statements are not promoted to another workload or graph.

## Workload substitution and global boundary proof

The baseline full centered inverse is M=(L+J/n)^(-1)-J/n, n=12,m=50. With fixed p_theta and zero diagonal, accepted covariance/commute algebra gives
 U_e(t)=2(1-theta)/n * (m+t)*(Ttheta-t*s_theta/(1+r*t)),
 Ttheta=tr(M)+n*theta*M_hh=12431/9720,
 r=v^T M v,
 s_theta=||Mv||^2+n*theta*(Mv)_h^2.
The positive common factor is391/2430. This explicitly retains the changing volume m+t. It is a valid substitution because the new hub diagonal and trace each receive the same rank-one denominator; p is fixed independently of t and e.

Write f(t)=(m+t)(T-t*s/(1+rt)), A=T-ms,B=rT-s. Exact differentiation gives
 sign f'(t)=sign[A+B*(2t+rt^2)], t>=0.
All denominators are positive. Here B>0 in each class (table below). More generally with this workload, D=I+n*theta*e_h*e_h^T is positive definite, rM-Mvv^TM is positive semidefinite by Cauchy-Schwarz and is nonzero on1-perp when n>=3. Its trace against D is rTtheta-s_theta>0. Thus the weighted substitution retains the required strict positivity, rather than assuming the uniform spectral argument unchanged.

If A>=0, f increases for t>0 and its unique minimum is t0. If A<0, the derivative numerator is strictly increasing on t>=0 and has one positive zero,
 tstar=(sqrt(s*(mr-1)/B)-1)/r.
A<0 implies s>0,mr>1 and radicand>1. The function decreases then increases, giving a unique global minimum. As t->infinity, f(t)~(B/r)t->infinity; no missing optimum occurs at infinity. The actual objective has the same extrema because its prefactor is positive.

## Complete class data

| Class | Count | r | s_theta | A | B |
|---|---:|---|---|---|---|
|uv|2|47/198|2027/71280|-3821/26730|66191/240570|
|restore|1|5/22|27/880|-6821/26730|2527/9720|
|untouched_A|1|2/9|2/81|431/9720|11351/43740|
|B/C internal|12|1/4|1/32|-5513/19440|701/2430|

These16 actual missing edges are enumerated individually in result.json. Unit-minus-noaction differences after removing the positive391/2430 factor are31802/297675 for uv,19/4860 for restore and B/C, and26581/106920 for untouched_A. All are positive. The optimum strengths for uv and restore are also subunit but give strictly worse minima than B/C; untouched_A is optimized by no action.

## Exact radical ordering

For A<0, set x=1+rt. Completing the one-variable minimum gives
 min f=[B(mr-1)+s+2*sqrt(B*s*(mr-1))]/r^2.
Batch2 bounds every square root by consecutive rational multiples of10^-12 using integer square roots and explicitly asserts lower^2<=radicand<upper^2. The resulting B/C minimum upper bound is strictly below the minimum lower bound of EACH other class, and below baseline. Thus ordering uses exact inequalities, not floating values or displayed decimal estimates. All rational bounds and the full twelve-edge winner set are retained in batch2.json. The analogous isolations prove0<tstar<1 for the three improving classes. Each class's closed radical value is retained in result.json.

## Evidence and limits

plan.md froze only344 andtheta14/405 before evaluation, with three hypotheses and two bounded attempts. Batch1 constructs the full baseline matrix independently and records every candidate's exact r,s,A,B,radicand,optimum and unit comparison. Batch2-plan.md freezes the same-instance derivative/radical-order/half-strength verification. Both evaluators returned rc0, empty stderr,2.16s and1.65s, each timeout60s, uv isolated/SymPy1.14.0/D cache. Exact argv/cwd/status/raw streams are retained. No extra graph, theta, matrix grid, retry or physical performance calculation occurred.

The known iid covariance/update and one-variable calculus methods are explicitly reused; their application is derived here. Numerical claims resolve to result.json and batch2.json; global same-instance optimality resolves to all candidate coverage, derivative boundaries and exact radical isolation. This is unreviewed next-round evidence excluded fromPR11, not a new generic algorithm, general strength theorem, cost-aware recommendation or measured network benefit.
