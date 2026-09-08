from pathlib import Path
from itertools import combinations
from fractions import Fraction as F
import json,hashlib
import sympy as S
p=Path(__file__).parent;src=p.parent/'astra-workload-strength-rescue-work'
def read(q):return json.loads(q.read_text(encoding='utf-8-sig'))
assert hashlib.sha256((src/'report.md').read_bytes()).hexdigest()=='83165e5bf7a62b84814a6b28ae69fad0adabdd73f4db3ffce9be30395d9e144e'
manifest=read(src/'hashes.json')
for z in manifest:assert hashlib.sha256((src/z['path']).read_bytes()).hexdigest()==z['sha256']
old=read(src/'result.json');boundold=read(src/'batch2.json')
n=12;h=11;theta=S.Rational(14,405);groups=[set(range(3)),set(range(3,7)),set(range(7,11)),{11}]
edges={ij for ij in combinations(range(n),2) if not any(ij[0] in g and ij[1] in g for g in groups)}-{(0,h)}
missing=sorted(set(combinations(range(n),2))-edges);assert len(missing)==16;L=S.zeros(n)
for i,j in edges:L[i,i]+=1;L[j,j]+=1;L[i,j]-=1;L[j,i]-=1
G=S.zeros(n);G[:h,:h]=L[:h,:h].inv();H=S.eye(n)-S.ones(n)/n;M=H*G*H
assert L*M==H;m=S.Integer(len(edges));T=S.trace(M)+n*theta*M[h,h];factor=2*(1-theta)/n
assert m==50 and T==S.Rational(12431,9720) and factor==S.Rational(391,2430)
assert S.Rational(old['m'])==m and S.Rational(old['Ttheta'])==T and S.Rational(old['objective_factor'])==factor and S.Rational(old['baseline_scaled'])==m*T
t,r,s,Tt,mm=S.symbols('t r s T m');f=(mm+t)*(Tt-t*s/(1+r*t));A=Tt-mm*s;B=r*Tt-s
assert S.cancel(S.diff(f,t)*(1+r*t)**2-(A+B*(2*t+r*t*t)))==0
assert S.cancel(S.limit(f/t,t,S.oo)-B/r)==0
rows={tuple(z['edge']):z for z in old['rows']};assert len(rows)==len(old['rows'])==16 and set(rows)==set(missing)
classes={}
def square_bounds(q):
 q=F(q);lo=F(0);hi=max(F(1),q)
 for _ in range(60):
  mid=(lo+hi)/2
  if mid*mid<=q:lo=mid
  else:hi=mid
 assert lo*lo<=q<hi*hi
 return lo,hi
for edge in missing:
 z=M[:,edge[0]]-M[:,edge[1]];rr=z[edge[0]]-z[edge[1]];ss=(z.T*z)[0]+n*theta*z[h]**2;aa=T-m*ss;bb=rr*T-ss;assert rr>0 and bb>0
 row=rows[edge]
 for key,v in [('r',rr),('s',ss),('A',aa),('B',bb)]:assert S.Rational(row[key])==v
 rad=S.cancel(ss*(m*rr-1)/bb);assert S.Rational(row['radicand'])==rad
 if aa<0:
  assert m*rr>1 and rad>1
  star=(S.sqrt(rad)-1)/rr
  minimum=(bb*(m*rr-1)+ss+2*S.sqrt(bb*ss*(m*rr-1)))/rr**2
  assert S.simplify(f.subs({mm:m,Tt:T,r:rr,s:ss,t:star})-minimum)==0
  qlo,qhi=square_bounds(bb*ss*(m*rr-1));lo=(F(bb*(m*rr-1)+ss)+2*qlo)/F(rr**2);hi=(F(bb*(m*rr-1)+ss)+2*qhi)/F(rr**2)
  sl,sh=square_bounds(rad);tl,th=(sl-1)/F(rr),(sh-1)/F(rr);assert 0<tl<th<1
 else:star=S.Integer(0);minimum=m*T;lo=hi=F(minimum);tl=th=F(0)
 assert S.simplify(star-S.sympify(row['tstar']))==0 and S.simplify(minimum-S.sympify(row['minimum_scaled']))==0
 unit=S.cancel((m+1)*(T-ss/(1+rr))-m*T);assert unit==S.Rational(row['unit_minus_baseline_scaled']) and unit>0
 key=(rr,ss);classes.setdefault(key,{'edges':[],'interval':[str(lo),str(hi)],'t_interval':[str(tl),str(th)]})['edges'].append(list(edge))
winner=classes[(S.Rational(1,4),S.Rational(1,32))]
assert len(winner['edges'])==12 and set(map(tuple,winner['edges']))==set(combinations(range(3,7),2))|set(combinations(range(7,11),2))
assert all(F(winner['interval'][1])<F(v['interval'][0]) for v in classes.values() if v is not winner)
assert F(winner['interval'][1])<F(m*T)
assert set(map(tuple,boundold['global_optimal_edges']))==set(map(tuple,winner['edges']))
half=S.cancel(factor*((m+S.Rational(1,2))*(T-S.Rational(1,2)*S.Rational(1,32)/(1+S.Rational(1,8)))-m*T))
assert half==-S.Rational(117691,11809800)==S.Rational(boundold['half_strength_U_minus_noaction'])
star=4*(S.sqrt(S.Rational(27945,22432))-1)
assert S.simplify(star-(-5608+9*S.sqrt(483690))/1402)==0
rr=S.Rational(1,4);ss=S.Rational(1,32);value=S.factor((m+star)*(T-star*ss/(1+rr*star)))
assert S.simplify(factor*value-S.Rational(391,2430)*(9*S.sqrt(483690)+64492)**2/78357780)==0
result={'status':'pass','candidate_count':16,'m':str(m),'Ttheta':str(T),'factor':str(factor),'class_bounds':list(classes.values()),'half_difference':str(half),'optimal_edges':winner['edges'],'optimal_t':str(star),'hash_count':len(manifest),'sympy':S.__version__}
(p/'result.json').write_text(json.dumps(result,indent=2),encoding='utf-8');print(json.dumps(result,indent=2))
