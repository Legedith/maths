import sympy as S,json
from fractions import Fraction as F
from pathlib import Path
p=Path(__file__).resolve().parent
def bounds(expr):
 expr=S.sympify(expr)
 if expr.is_Rational:q=F(int(expr.p),int(expr.q));return q,q
 if expr.is_Add:
  bs=[bounds(z) for z in expr.args];return sum(b[0] for b in bs),sum(b[1] for b in bs)
 if expr.is_Mul:
  lo=hi=F(1)
  for z in expr.args:
   a,b=bounds(z);vs=[lo*a,lo*b,hi*a,hi*b];lo,hi=min(vs),max(vs)
  return lo,hi
 if expr.is_Pow:
  a,b=bounds(expr.base);power=expr.exp
  if power==S.Rational(1,2):
   assert a>=0
   def root(q):
    l,h=F(0),max(F(1),q)
    for _ in range(100):
     m=(l+h)/2
     if m*m<=q:l=m
     else:h=m
    return l,h
   return root(a)[0],root(b)[1]
  if power.is_Integer:
   k=int(power)
   if k<0:
    assert not a<=0<=b
    a,b=1/b,1/a;k=-k
   if k==0:return F(1),F(1)
   vs=[a**k,b**k];return (F(0) if a<=0<=b and k%2==0 else min(vs)),max(vs)
 raise ValueError(str(expr))
def sign(expr):
 if expr==0:return 0
 lo,hi=bounds(expr)
 assert lo>0 or hi<0,str(expr)
 return 1 if lo>0 else -1
def record(expr):return {'exact':str(expr),'bounds':[str(x) for x in bounds(expr)]}
n=12;m=50;lab=[0]*3+[1]*4+[2]*4+[3];L=S.zeros(n);eye=S.eye(n);J=S.ones(n)/n
old=[];missing=[]
for i in range(n):
 for j in range(i+1,n):
  (old if lab[i]!=lab[j] and (i,j)!=(0,11) else missing).append((i,j))
for i,j in old:
 v=eye[:,i]-eye[:,j];L+=v*v.T
M=(L+J).inv()-J;assert L*M==eye-J
groups={}
for i,j in missing:
 z=M*(eye[:,i]-eye[:,j]);r=z[i]-z[j]
 ss=[(z.T*z)[0]+n*th*z[11]**2 for th in (S.Integer(0),S.Rational(1,10))]
 key=(r,*ss);groups.setdefault(key,[]).append([i,j])
Ts=[S.trace(M)+n*th*M[11,11] for th in (S.Integer(0),S.Rational(1,10))]
data=[]
for (r,s0,s1),edges in groups.items():
 ss=[s0,s1];Bs=[r*T-s for T,s in zip(Ts,ss)];As=[T-m*s for T,s in zip(Ts,ss)]
 assert all(b>0 for b in Bs)
 stars=[];mins=[]
 for T,s,B,A in zip(Ts,ss,Bs,As):
  if A>=0:star=S.Integer(0);value=m*T
  else:star=(S.sqrt(s*(m*r-1)/B)-1)/r;value=(B*(m*r-1)+s+2*S.sqrt(B*s*(m*r-1)))/r**2
  stars.append(star);mins.append(value)
 data.append({'edges':edges,'r':r,'ss':ss,'Bs':Bs,'stars':stars,'mins':mins})
oracles=[]
for endpoint in range(2):
 candidates=[g['mins'][endpoint] for g in data]
 winner=min(range(len(data)),key=lambda i:bounds(candidates[i])[1])
 assert all(i==winner or sign(candidates[i]-candidates[winner])>0 for i in range(len(data)))
 oracles.append(candidates[winner])
out=[];allc=[]
for g in data:
 r=g['r'];s0,s1=g['ss'];B0,B1=g['Bs'];O0,O1=oracles
 cross=(Ts[1]*O0-Ts[0]*O1)/(B0*O1-B1*O0)
 candidates=[('zero',S.Integer(0)),('left_stationary',g['stars'][0]),('right_stationary',g['stars'][1])]
 if sign(cross)>0:candidates.append(('balance',cross))
 seen=[];rows=[]
 for name,t in candidates:
  if any(t==v for v in seen):continue
  seen.append(t)
  losses=[(m+t)*(T-t*s/(1+r*t))/O-1 for T,s,O in zip(Ts,g['ss'],oracles)]
  # Bound max directly, avoiding a floating-point branch choice.
  bb=[bounds(z) for z in losses];interval=(max(q[0] for q in bb),max(q[1] for q in bb))
  row={'kind':name,'strength':record(t),'endpoint_regrets':[record(z) for z in losses],'worst_bounds':[str(v) for v in interval]}
  rows.append(row);allc.append((interval,g['edges'],name,t))
 out.append({'edges':g['edges'],'r':str(r),'s_endpoints':[str(z) for z in g['ss']],'endpoint_stationary':[record(z) for z in g['stars']],'candidates':rows})
winner=min(allc,key=lambda row:row[0][1]);assert all(row is winner or row[0][0]>winner[0][1] for row in allc)
assert winner[2]=='balance'
res={'status':'PASS','parts':[3,4,4],'interval':['0','1/10'],'T_endpoints':[str(z) for z in Ts],'oracle_endpoint_values':[record(z) for z in oracles],'classes':out,'winning_edges':winner[1],'winning_kind':winner[2],'winning_strength':record(winner[3]),'minimax_regret_bounds':[str(z) for z in winner[0]],'strictly_beats_all_per_edge_endpoint_stationary_candidates':True}
(p/'result.json').write_text(json.dumps(res,indent=2)+'\n',encoding='utf-8');print(json.dumps({'status':'PASS','winning_edges':winner[1],'kind':winner[2],'approx_for_display':float(sum(winner[0])/2)}))
