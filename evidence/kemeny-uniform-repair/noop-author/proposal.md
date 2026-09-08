# Candidate: optimal uniform insertion strictly beats doing nothing

NEXT author-derived result, independent review required. Prior stages and current public release remain unchanged. H=K_(a,b,c) join K1-uh with 3<=a<=b,c. U is mean first hitting time with fixed independent uniform source/target and zero diagonal. The earlier candidate identifies the best unit insertion: uv if a=b=c, otherwise an internal pair in any largest original part. This packet supplies the missing comparison with no intervention.

## Full-domain candidate
That best unit insertion strictly decreases U relative to H throughout the stated integer domain, whether restoring uh is allowed or forbidden. Thus no-op is strictly suboptimal for this family under this objective and equal unit insertion cost. This does not say every insertion improves U.

Put n=a+b+c+1, d=n-a, m=ab+ac+bc+a+b+c-1,
k=(n-1)(d-1)/(nd), W=[n(n-1)+d(d-1)]/(n^2 d^2).
The previously derived spectrum and rank-one deletion give
T=tr(L_H+)=3/n+(a-1)/(n-a)+(b-1)/(n-b)+(c-1)/(n-c)+W/k.
The three part-zero-sum eigenspaces contribute their displayed terms; the three remaining nonconstant part-constant eigenvalues equal n. Deleting uh adds trace W/k.

For a unit candidate let S be the trace reduction. Then the known bridge gives
U(H+e)-U(H)=(2/n)[T-(m+1)S].
The previous derivation supplies
Suv=[2/d^2+2/(d^3 k)+W/(d^2 k^2)]/[1+2/d+1/(d^2 k)],
SB=2/[(n-b)(n-b+2)].
No generic-update novelty is claimed. Source grounding: ../astra-fixed-workload-source-work/report.md, section 2 (Chandra et al. commute identity; Monnig--Meyer exact edge/Kirchhoff update), section 3 (uniform-workload factors and no-op boundary).

Batch2 certifies positive (m+1)S-T in three exhaustive cases, with full shifted numerator and denominator lists retained:
- Equal: a=b=c=3+x, S=Suv. Numerator 6 terms, min216, constant100288; denominator min432, constant624960.
- Exactly one larger: a=c=3+x,b=4+x+y, S=SB. Numerator26 terms,min2,constant53102; denominator min4,constant388080.
- Both larger: a=3+x,c=4+x+z,b=4+x+z+y, S=SB. Numerator117 terms,min1,constant190464; denominator min1,constant6082560.
All variables nonnegative; all listed nonzero coefficients positive. The last two cases assume b>=c, which loses no graph by exchanging B,C. They cover every unequal integer tuple with a minimum; case three includes b=c ties. Positive constants make strictness explicit, including parameter boundaries. Together with prior best-orbit classification, these establish the candidate claim subject to independent audit.

## Exact falsification: resistance improvement is insufficient
At (3,3,3), U(H)=751/90. Adding an untouched_A pair, or a B/C pair, strictly lowers tr(L+) but increases U by 31/3150. Best uv instead changes U by -1567/48825. Restoring uh changes U by -41/3150. Thus neither a resistance reduction nor being a legal alternate insertion alone guarantees fixed-workload improvement.

## Weighted intervention threshold, a generic identity rather than novelty
For inserting conductance t>0 at v=e_i-e_j, write r=v^TL_H+v>0 and s=v^T(L_H+)^2v>0. Total edge conductance becomes m+t. Weighted random walks give
Delta U(t)=(2t/n)*[(T-ms)+t(rT-s)]/(1+tr).
This follows by substituting tr(L_new+)=T-ts/(1+tr) into U=2(m+t)tr(L_new+)/n and subtracting 2mT/n.
For these graphs rT-s>0: diagonalize L_H+ on 1-perp with positive eigenvalues lambda_i. Then rT-s=sum_i c_i^2 lambda_i sum_(j!=i)lambda_j>0 because dimension n-1>=2 and v is nonzero. Therefore:
- If ms<=T, every t>0 worsens U (strictly even at equality).
- If ms>T, improvement occurs exactly for 0<t<tcrit=(ms-T)/(rT-s), equality at tcrit, worsening for t>tcrit.
There is no smallest positive improving weight: the infimum is zero when improvement is possible. A positive maximum improving weight is the relevant threshold. This weighted conclusion changes the design model explicitly; it is not silently substituted into the unit-edge theorem.

At (3,3,3) for an untouched pair, r=2/7,s=2/49,T=751/630,m=35. Hence tcrit=1043/1322<1. Small conductance improves this fixed workload, but a unit edge exceeds its improving range. These exact quantities are independently obtained from full L_H+ in batch1. No weighted benchmark or real-network claim.

## Ledger and execution
H1 best unit insertion always improves: no diagnostic counterexample; full-domain positive-polynomial candidate above.
H2 some legal insertions worsen despite resistance decrease: confirmed by exact (3,3,3) witness.
H3 threshold identity decides no-op/weighted improvement: derived exactly above; recognized known-method algebra, not new theorem priority.
Batch1 frozen tuples (3,3,3),(3,3,4),(3,4,5),(3,3,7),(4,4,6), five missing-edge orbits; full Laplacian pseudoinverse yields all r,s,T and exact deltas. Batch2 verifies symbolic T,m and uv/B score-derived deltas against all recorded cases, then constructs exactly the three frozen symbolic certificates. Two batches rc0, no failed runs, retries, extra ranges or third batch. uv isolated SymPy1.14.0 with D-drive cache. Plans, argv, stdout, stderr, rc and full results retained; hashes.json pins them.

Typed numerical claims -> batch1.json and batch2.json complete coefficients; methodological claims -> plans/scripts and source report; universal conclusion -> prior best-orbit candidate, derived T, exhaustive parameter cases and coefficient signs. Independent reviewer must check formula provenance and exact polynomials; this author does not self-certify.

Conditional meaning: doing nothing is inferior to the best unit insertion in this ideal mathematical model. It does not establish a monetary budget optimum, physical latency improvement, multiple-failure guarantee, or publication novelty.
