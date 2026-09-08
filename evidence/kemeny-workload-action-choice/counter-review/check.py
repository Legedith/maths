import sympy as S,json,itertools
from pathlib import Path
p=Path(__file__).resolve().parent;n=12;h=11
labels=[0]*3+[1]*4+[2]*4+[3]
old=[e for e in itertools.combinations(range(n),2) if labels[e[0]]!=labels[e[1]] and e!=(0,h)]
missing=sorted(set(itertools.combinations(range(n),2))-set(old));assert len(old)==50 and len(missing)==16
L=S.zeros(n)
def v(e):return S.eye(n)[:,e[0]]-S.eye(n)[:,e[1]]
for e in old:L+=v(e)*v(e).T
J=S.ones(n)/n
M=(L+J).inv()-J
assert L*M==S.eye(n)-J
T=S.trace(M);hh=M[h,h];assert T==S.Rational(985,792) and hh==S.Rational(269,3168)
theta=S.Symbol('theta');base=2*50*(1-theta)*(T/n+theta*hh)
tau=S.Rational(14,405);lo=S.Rational(124,4035);hi=S.Rational(59,1662)
assert 0<lo<tau<hi<1
FC=S.Rational(31,990)-S.Rational(269,264)*theta
FR=-S.Rational(59,396)+S.Rational(277,66)*theta
assert FC.subs(theta,lo)==0 and FR.subs(theta,hi)==0
rows=[];objectives={};margins={}
for e in missing:
 A=L+v(e)*v(e).T;N=(A+J).inv()-J
 assert A*N==S.eye(n)-J
 U=2*51*(1-theta)*(S.trace(N)/n+theta*N[h,h]);objectives[e]=U
 F=S.expand(n*(50*(T/n+theta*hh)-51*(S.trace(N)/n+theta*N[h,h])))
 margins[e]=F
 if e==(0,h):assert S.expand(F-FR)==0
 elif labels[e[0]] in (1,2):assert S.expand(F-FC)==0
 else:
  # Strict inferiority to the relevant envelope on each whole subinterval.
  assert all((FC-F).subs(theta,t)>0 for t in (0,tau))
  assert all((FR-F).subs(theta,t)>0 for t in (tau,1))
 rows.append({'edge':e,'margin':str(F),'objective_at_tau':str(U.subs(theta,tau))})
best=min(U.subs(theta,tau) for U in objectives.values())
winners=[e for e,U in objectives.items() if U.subs(theta,tau)==best]
assert len(winners)==13 and (0,h) in winners
assert base.subs(theta,tau)==S.Rational(53465731,5196312)
assert best==S.Rational(222787499,21651300)
assert best-base.subs(theta,tau)==S.Rational(7429,11809800)>0
assert all(U.subs(theta,1)==0 for U in objectives.values()) and base.subs(theta,1)==0
out={'status':'PASS','baseline_trace':str(T),'baseline_hh':str(hh),'matrices':17,'rows':rows,'winners_at_tau':winners,'interval':[str(lo),str(hi)],'baseline_at_tau':str(base.subs(theta,tau)),'best_at_tau':str(best),'excess':str(best-base.subs(theta,tau)),'sympy':S.__version__}
(p/'result.json').write_text(json.dumps(out,indent=2)+'\n',encoding='utf-8');print(json.dumps(out))
