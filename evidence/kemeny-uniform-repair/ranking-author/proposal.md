# Candidate: exact optimal repair for a fixed uniform workload

Author-derived NEXT result; separate independent source/mathematical verification required. No current PR/public files changed. Let G=K_(a,b,c) join K1, 3<=a<=b,c, u in A, h hub, H=G-uh. The objective for J=H+e is U(J)=n^-2 sum_(i,j) E_i T_j with diagonal hitting time zero and unchanged uniform start/target distributions. All interventions are one unweighted missing edge.

## Candidate theorem
If a=b=c, exactly the pairs {u,v}, v in A minus {u}, minimize U(H+e). If max(b,c)>a, exactly the internal pairs of the largest original part(s) minimize U(H+e). Equal largest B,C give both optimal orbits. These statements hold whether restoring uh is allowed or forbidden, because restoration is strictly worse than uv everywhere. Optimality is for an orbit/set of edges, not a unique individual edge. No Kemeny stationarity assumption is substituted into U.

## Electrical reduction and provenance
The standard commute identity M_ij+M_ji=2m R_ij, together with zero self-hit and sum_(i<j)R_ij=n tr(L+), yields
U(J)=(2m_J/n) tr(L_J+).
The second identity follows directly from R_ij=L+_ii+L+_jj-2L+_ij and L+1=0. The first is classical electrical/random-walk theory, not a claimed discovery; source grounding is assigned separately by root. All candidate graphs J have the same m_J=m_H+1. Hence minimizing U is equivalent to maximizing the trace decrease from L_H+.

For an insertion vector v=e_i-e_j, inversion on 1-perp (ordinary rank-one inverse identity) gives
L_(H+ij)+ = L_H+ - (L_H+ v)(L_H+ v)^T/[1+v^T L_H+ v].
The trace benefit is S(v)=v^T(L_H+)^2v/[1+v^TL_H+v]. Thus larger S is better. This is established update machinery, not method novelty.

## Derive the base inverse and deletion
Put n=a+b+c+1 and P=I-J/n. For each original part of size q, let E_q=I_part-J_part/q, embedded in the full vertex space. These are mutually orthogonal projectors onto zero-sum within-part vectors, all orthogonal to 1. Directly L_G=nP-sum_q q E_q; on E_q its eigenvalue is n-q, and on the remaining part-constant subspace in 1-perp it is n. Therefore
L_G+ = P/n + sum_q q/[n(n-q)] E_q.
The singleton projector is zero. This derives the proposed formula rather than assuming it.

Let d=n-a=b+c+1, y=e_u-e_h, w=L_G+y, rho=y^TL_G+y, and k=1-rho. The coordinates are
w_u=(n-1)/(nd), w_v=-1/(nd) for v in A minus {u}, w_h=-1/n, other coordinates zero.
Consequently rho=(n+d-1)/(nd), k=(n-1)(d-1)/(nd)>0, and
W=||w||^2=[n(n-1)+d(d-1)]/(n^2 d^2).
H stays connected, also established by the positive rank-one deletion denominator. Inversion on 1-perp gives L_H+=L_G+ + ww^T/k.

## Five missing-edge orbit scores
All missing edges are restore uh, uv, untouched_A pair, B pair, C pair. The original part-preserving permutations fixing u,h preserve the uniform objective, so these representatives exhaust the possibilities.

For restoration, L_H+y=w/k and 1+y^TL_H+y=1/k, so
S_restore=W/k.
For v=e_u-e_v with v in A minus {u}, L_G+v=v/d and w^Tv=1/d. Therefore
S_uv=[2/d^2+2/(d^3 k)+W/(d^2 k^2)]/[1+2/d+1/(d^2 k)].
For a pair not incident to u within a part of size t, its vector is orthogonal to w and L_G+v=v/(n-t). Thus
S_t=2/[(n-t)(n-t+2)], t=a,b,c.
All denominators are positive. S_t strictly increases with t on eligible sizes t<n, so among untouched pairs the largest parts win, with exact ties for equal sizes.

## Exact full-domain comparisons
batch2.py constructs the preceding rational scores and exactly subtracts three comparisons. Full original expressions and all shifted numerator/denominator coefficient lists are in batch2.json.

1. S_uv-S_restore: substitute a=3+x,b=3+x+y,c=3+x+z. Numerator 16 nonzero terms, minimum coefficient 2, constant 92; denominator minimum coefficient 1, constant 34720.
2. S_uv-S_a: same substitution. Numerator 20 nonzero terms, minimum coefficient 2, constant 1404; denominator minimum coefficient 1, constant 241056.
3. S_b-S_uv: substitute a=3+x,b=4+x+y,c=3+x+z. Numerator 77 nonzero terms, minimum coefficient 2, constant 71442; denominator minimum coefficient 1, constant 25084080.

Every nonzero coefficient in each numerator and denominator is strictly positive. Each constant is positive. Hence all three rational differences are strictly positive throughout their respective nonnegative orthants. The first two substitutions exhaust 3<=a<=b,c; the third exhausts b>=a+1,c>=a. Integer sizes make b>a equivalent to b>=a+1. Swapping b,c gives the corresponding strict comparison for c>a. The last step uses integrality essentially; no continuous-size threshold claim is made.

If all parts equal a, the second comparison puts uv above all untouched scores, and the first above restoration. Otherwise a largest part has size at least a+1; its score beats uv by comparison 3, and beats smaller untouched parts by monotonicity of S_t. Restoration is already below uv. This proves the exact optimum-set statement if the algebra/source bridge passes separate audit.

## Frozen tests and elimination ledger
H1 uv beats restoration: survived all diagnostics and obtained full-domain certificate candidate.
H2 equal a=b=c gives incident-u optimal orbit: survived; follows from comparisons 1/2.
H3 otherwise largest-part internal pairs optimal: survived; follows from comparison 3 and monotonic untouched scores.
H4 inverse/trace scores match independent hitting matrices: all 35 intervention cases agree exactly (seven tuples, five orbits), with no tolerance.
No hypotheses were rejected and no failed run occurred. Surviving universal claims rely on explicit proof above, not these samples.

Batch1 fixed tuples: (3,3,3),(3,3,4),(3,4,4),(3,4,5),(3,3,7),(4,4,5),(4,5,5). The code computes independent full adjacency matrices and fundamental-matrix hitting times, then compares U against direct Laplacian pseudoinverse update values. Batch2 also checks every closed score formula against all recorded batch1 benefits before constructing certificates. This is cross-formulation validation by the author, not an independent-agent audit.

Raw argv/stdout/stderr/rc, frozen plans, scripts and results retained; both runs rc=0, uv isolated SymPy 1.14.0 with D-drive cache. No retries, added tuple ranges, third batch, benchmark or other-stage write. hashes.json pins the packet.

Typed claims: finite exact agreements -> batch1.json, batch1.py, batch2 assertions/logs; methodological inverse and objective derivations -> this note and scripts, with root's separate source review required for classical commute grounding; coefficient facts -> batch2.json complete dictionaries; universal conclusion -> source bridge plus orbit coverage, three positive rational comparisons and untouched-score monotonicity. Author cannot self-certify final evidence gate.

This is an ideal fixed uniform workload decision rule. It makes no claim about observed latency, weighted networks, nonuniform traffic, multiple failures, greedy batches, or generic-update novelty. It is separate from earlier stationary-target Kemeny optimality, whose edge ordering differs.
