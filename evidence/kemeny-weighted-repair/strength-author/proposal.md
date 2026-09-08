# Candidate corollary: joint edge-location and conductance optimum

Separate NEXT packet, author-derived and requiring independent review. H=K_(a,b,c) join K1-uh,3<=a<=b,c, fixed independent uniform source/target, zero diagonal hitting time. Choose one missing edge and its conductance t>=0 with no monetary penalty. t=0 means no change. Current release and prior stages are read-only and unchanged.

## Complete joint optimum, conditional on audited family inputs
Choose the same optimal edge set as in the common-positive-weight theorem: uv edges if a=b=c; otherwise internal pairs in a largest original part (both B,C if tied). For any edge in that set, with r=v^TL_H+v, s=v^T(L_H+)^2v, T=tr(L_H+) and m=m_H, choose the unique conductance

  t* = [sqrt(s(mr-1)/(rT-s))-1]/r.

Every such edge with this same t* attains the joint global minimum. No other edge/weight pair does, and t=0 is strictly inferior. This is a clean consequence of the independently audited pointwise edge ordering and best-unit-versus-noop result, plus the scalar calculus below. It is not a new generic derivative method.

## Verify every premise and endpoint
H is connected, n>=10, and L_H+ is positive definite on 1-perp. Therefore r,s,T>0. Let its n-1 positive eigenvalues be lambda_i and write v=sum c_i e_i on that space. Then
  B=rT-s=sum_i c_i^2 lambda_i sum_(j!=i)lambda_j>0,
since n-1>=2 and v is nonzero. This strict positivity holds for every candidate edge, not just the optimal ones.

The established weighted bridge gives U(t)=(2/n)f(t),
  f(t)=(m+t)[T-ts/(1+rt)].
Set A=T-ms. Exact differentiation yields
  f'(t)=[A+B(2t+rt^2)]/(1+rt)^2.
For an edge in the pointwise-optimal set, the best-unit improvement theorem gives f(1)-f(0)<0. Since
  f(1)-f(0)=(A+B)/(1+r),
we obtain A+B<0, hence A<0. Thus f'(0)<0 and no-op cannot minimize. This implication uses the family no-op theorem; it is not inferred from resistance decrease alone.

The derivative numerator has derivative 2B(1+rt)>0 for t>=0, starts at A<0, and tends to positive infinity. Hence it crosses zero exactly once: f strictly decreases before that crossing and strictly increases afterward. Solving A+B(2t+rt^2)=0 gives the displayed t*. Its radicand exceeds one, since
  s(mr-1)/(rT-s)-1 = r(ms-T)/(rT-s)>0.
Consequently mr>1 and t*>0; the radical is real and there is no extraneous root. As t tends to infinity,
  f(t)/t -> T-s/r = B/r>0,
so arbitrarily large conductance is not an alternative boundary optimum.

For every t>0, audited pointwise ordering strictly places every excluded edge below the selected orbit(s) in trace-benefit score, hence above them in U. Therefore an excluded edge at any t cannot reach the minimum achieved by a selected edge: compare it with a selected edge at that same t, then with the latter's optimum t*. At t=0 all locations coincide with no-op, already strictly worse. This proves global joint optimization, not merely a local stationary point.

All uv representatives have identical r,s by graph symmetry. Equal largest B,C have the same d=n-part_size and r=2/d,s=2/d^2, so they share t*. The optimum is a set of equivalent edge choices with one common unique strength; no uniqueness of an individual edge is asserted.

## Counterexample to universal unit strength
At (3,3,3), the selected edge is uv and
  m=35, T=751/630, r=59/189, s=587/11907,
  t*=(189/59)[sqrt(1573160/1037853)-1].
The exact derivative f'(1)=66587/538160>0, while f'(0)<0, so 0<t*<1 and f(t*)<f(1). Thus unit strength is not universally optimal even though the best unit insertion improves U over no-op.

Other declared exact cases (3,3,4),(3,4,5),(4,4,6) also have f'(1)>0 and t*<1; all radicals and derivatives are retained in result.json. These four examples do not establish that t*=1 never occurs, nor that t*<1 universally. The exact equality criterion is A+B(2+r)=0; classifying graph parameters satisfying it remains uninvestigated beyond the declared cases.

## Ledger and execution
H1 unit t=1 always jointly optimal: REJECTED by (3,3,3).
H2 unique finite positive strength and pointwise-optimal location solve the joint problem: analytic corollary candidate above.
H3 no-op or infinity might beat the selected finite strength despite best-unit improvement: REJECTED by the full-domain derivative/end-point argument.
H4 tied optimal orbits share strength: follows from equal r,s as above.

One frozen batch only; no second batch, failure, retry or expanded search. plan.md preceded execution. batch1.py symbolically verifies the derivative identity and the radical critical-point equation, pins ../astra-uniform-noop-work/batch1.json via input-hash.json, and computes the four exact declared cases. uv isolated SymPy1.14.0 with D-drive cache; argv/stdout/stderr/rc retained, rc0. No decimal approximation, numerical optimization, benchmark or deployed-impact claim. hashes.json pins this stage.

Typed numerical claims -> result.json and stdout; methodological identities -> script and analytic argument; universal conclusion -> audited pointwise ordering and no-op family inputs plus derivative monotonicity, positivity and endpoints. Independent reviewer must confirm inherited proof hashes/status and this corollary before promotion; author does not self-certify. The conductance model is mathematical, without a price/engineering cost for weight and without physical latency guarantees.
