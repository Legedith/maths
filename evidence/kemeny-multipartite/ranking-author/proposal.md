# Candidate: exact ranking of within-part edge insertions

Status: author-derived candidate proof, independent semantic audit REQUIRED. Not a novelty certificate.

For a connected complete multipartite graph, compare two distinct parts of sizes x,y>=3. All other parts may have any positive integer sizes, including singleton and size-2 parts. Write Delta_x for insertion within the x-part. Candidate theorem: sign(Delta_x-Delta_y)=sign(x-y). Thus the smallest eligible part minimizes the resulting Kemeny constant. If every nonsingleton part has size>=3, this is globally optimal among all single missing-edge insertions. If a size-2 part exists, no claim compares against its insertion.

## Derivation
Use Hu--Kirkland Theorem 3.2.3 (actual source page 12, lines 699-714 of pinned page-marked text), and independent source-domain audit. Define n=sum q, g=sum q(n-q)>0, H=sum q(n-q)^2. For selected x>=3, a=n-x, t=g-x*a:
B(x)=-g/(2a)+(x-2)/2+(H-x*a*a)/(g*n)+(x-2)*t/(2g)+(n-2)*t*t/(2g*n*a)+(g-a)/(a*(a+2)); Delta_x=2B(x)/(g+2).
This aggregate formula is directly published-update algebra, not an original inversion-free method.

Let alpha=n-x, beta=n-y. Exact symbolic subtraction in batch2 gives
(B(x)-B(y))/(x-y)=N/[n*alpha*beta*(alpha+2)*(beta+2)], where
N=g*((n-2)*(alpha+beta+2)-alpha*beta)+alpha*beta*(2*(alpha+2)*(beta+2)-n).
This identity is for x!=y; equality for tied sizes follows directly from B.

For distinct parts x,y>=3, n>=alpha+3, n>=beta+3, and n<=alpha+beta (the last follows since n-x-y is the sum of all remaining sizes). Therefore
(n-2)*(alpha+beta+2)-alpha*beta >= alpha^2+beta^2-alpha*beta+alpha+beta+2*(n-2)>0;
2*(alpha+2)*(beta+2)-n >=2*alpha*beta+3*alpha+3*beta+8>0.
Hence N>0 and the denominator is positive. This is a short full-domain sign proof, subject to independent checking of the identity and inequalities. Batch2 also expands N at x=3+u,y=3+v,n=x+y+w into 37 positive coefficients (minimum 1), constant in u,v,w equal 23g+396; this is redundant evidence, not needed by the short proof.

## Screening and eliminations
Batch1 exhaustively evaluated 3640 sorted triples from 3..14 with p=1..10, all part deltas exact rational. No ranking counterexamples. Raw records retained. H2, that more dominating vertices makes the minimum-part improvement stronger, is rejected: (3,3,3), p=1 gives -1693/93240 while p=2 gives -3457/237820, which is less negative. All 3640 p increments violated H2. No reverse-monotonicity theorem is asserted.
Batch2 validated 11 representative insertions using the independently authored exact fundamental-matrix code on four graphs: (3,4,5,1), (3,5,1,1), (3,4), (3,4,5,6,1). All match the formula. Two experiment batches only. The uv invocation emitted a harmless no-project warning; scripts produced results and no traceback.

## Prior-work boundary and application
Hu--Kirkland already gives the exact update via Sherman Morrison. Its page 19 compares cleared sign numerators for two non-singleton parts. That comparison alone is not a comparison of actual Kemeny changes because denominators vary. The prior accepted proposal already notes an uncertified pairwise monotonic-brace probe. Therefore this candidate is a general ranking proof developed from that known observation, not claimed as first discovery. Root must check literature for the exact ranking statement before priority claims.
Prospective application: in an exact multipartite architecture, choose the smallest part in O(r) time and evaluate one sourced rational update to determine its benefit; ranking eliminates testing all part orbits and certifies optimal one-edge location. In the accepted three-part plus clique setting, it adds optimality to strict improvement. Requires exact model fit, uniform simple random walk, one-edge objective; no guarantee for approximate multipartite networks, arbitrary costs, weighted walks or repeated greedy insertions, since insertion leaves the multipartite class.

## Typed claims awaiting independent gate
citation: source update formula; support pinned source lines 699-714 and independent source-domain audit.
numerical: 3640 grid cases, no H1 counterexample; support batch1-result.json and batch1-raw.json.
numerical: 11 matrix matches and 37 positive coefficients; support batch2-result.json, batch2.py and ranking-polynomial.json.
methodological: O(r) selection and aggregate update use one pass over part sizes; support formula and algorithm above. Arithmetic-operation count only, not bit complexity or runtime benchmark.
conclusion: universal ranking candidate follows source identity plus displayed positivity proof; independent review pending.
