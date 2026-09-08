from pathlib import Path
from fractions import Fraction as F
from math import isqrt
import sympy as S,json,hashlib
p=Path(__file__).parent;src=p.parent/'astra-strength-minimax-explore-work'
for name,h in {'proposal.md':'6e673f48ed1070017ab5cecd2ca17a245dbd844b658765508fc9f1cd5acd2ef7','result.json':'9c1bb733c9312f6a8860be8130f1c74384a85fca2a715f135c6ad6a7cc0b0a43'}.items():assert hashlib.sha256((src/name).read_bytes()).hexdigest()==h
old=json.loads((src/'result.json').read_text())
def rat(q):return F(int(q.p),int(q.q))
class I:
 def __init__(self,a,b=None):self.a=F(a);self.b=F(a if b is None else b)
 def __add__(self,o):
  o=asI(o);return I(self.a+o.a,self.b+o.b)
 __radd__=__add__
 def __neg__(self):return I(-self.b,-self.a)
 def __sub__(self,o):return self+-asI(o)
 def __rsub__(self,o):return asI(o)+-self
 def __mul__(self,o):
  o=asI(o);v=[a*b for a in (self.a,self.b) for b in (o.a,o.b)];return I(min(v),max(v))
 __rmul__=__mul__
 def inv(self):
  assert not self.a<=0<=self.b
  return I(1/self.b,1/self.a)
 def __truediv__(self,o):return self*asI(o).inv()
 def __rtruediv__(self,o):return asI(o)*self.inv()
 def rec(self):return [str(self.a),str(self.b)]
def asI(v):return v if isinstance(v,I) else I(v)
def root(q):
 q=F(q);assert q>=0;scale=1<<200
 k=isqrt(q.numerator*scale*scale//q.denominator)
 assert F(k*k,scale*scale)<=q<F((k+1)**2,scale*scale)
 return I(F(k,scale),F(k+1,scale))
n=12;lab=[0]*3+[1]*4+[2]*4+[3];L=S.zeros(n);missing=[];m=0
for i in range(n):
 for j in range(i+1,n):
  if lab[i]!=lab[j] and (i,j)!=(0,11):
   L[i,i]+=1;L[j,j]+=1;L[i,j]-=1;L[j,i]-=1;m+=1
  else:missing.append((i,j))
assert m==50 and len(missing)==16
G=S.zeros(n);G[:11,:11]=L[:11,:11].inv();P=S.eye(n)-S.ones(n)/n;M=P*G*P;assert L*M==P
Ts=[rat(S.trace(M)+n*th*M[11,11]) for th in (S.Integer(0),S.Rational(1,10))]
assert [str(q) for q in Ts]==old['T_endpoints']
groups={}
for i,j in missing:
 z=M[:,i]-M[:,j];r=rat(z[i]-z[j]);ss=[rat((z.T*z)[0]+n*th*z[11]**2) for th in (S.Integer(0),S.Rational(1,10))]
 groups.setdefault((r,*ss),[]).append([i,j])
rows=[]
for (r,*ss),edges in groups.items():
 Bs=[r*T-s for T,s in zip(Ts,ss)];As=[T-m*s for T,s in zip(Ts,ss)]
 assert all(q>0 for q in Bs)
 stars=[];mins=[];rad=[]
 for T,s,B,A in zip(Ts,ss,Bs,As):
  if A>=0:stars.append(I(0));mins.append(I(m*T));rad.append(None)
  else:
   q=s*(m*r-1)/B;assert q>1
   stars.append((root(q)-1)/r);rad.append(str(q))
   mins.append((B*(m*r-1)+s+2*root(B*s*(m*r-1)))/(r*r))
 rows.append({'edges':edges,'r':r,'ss':ss,'B':Bs,'A':As,'stars':stars,'mins':mins,'rad':rad})
oracles=[];ow=[]
for k in (0,1):
 idx=min(range(len(rows)),key=lambda j:rows[j]['mins'][k].b);v=rows[idx]['mins'][k]
 assert all(j==idx or row['mins'][k].a>v.b for j,row in enumerate(rows))
 oracles.append(v);ow.append(rows[idx]['edges'])
 assert F(old['oracle_endpoint_values'][k]['bounds'][0])<=v.a<=v.b<=F(old['oracle_endpoint_values'][k]['bounds'][1])
allc=[];records=[]
for row in rows:
 r=row['r'];ss=row['ss'];Bs=row['B'];cross=(Ts[1]*oracles[0]-Ts[0]*oracles[1])/(Bs[0]*oracles[1]-Bs[1]*oracles[0])
 candidates=[('zero',I(0))]
 for k,name in enumerate(('left_stationary','right_stationary')):
  if row['A'][k]<0:candidates.append((name,row['stars'][k]))
 assert cross.a>0 or cross.b<0
 if cross.a>0:candidates.append(('balance',cross))
 author=next(q for q in old['classes'] if q['edges']==row['edges'])
 assert author['r']==str(r) and author['s_endpoints']==[str(q) for q in ss]
 assert set(q['kind'] for q in author['candidates'])==set(q[0] for q in candidates)
 cr=[]
 for name,t in candidates:
  losses=[(m+t)*(T-t*s/(1+r*t))/O-1 for T,s,O in zip(Ts,ss,oracles)]
  worst=I(max(q.a for q in losses),max(q.b for q in losses))
  ar=next(q for q in author['candidates'] if q['kind']==name)
  assert F(ar['worst_bounds'][0])<=worst.a<=worst.b<=F(ar['worst_bounds'][1])
  cr.append({'kind':name,'strength_bounds':t.rec(),'regret_bounds':worst.rec()})
  allc.append((worst,row['edges'],name))
 records.append({'edges':row['edges'],'r':str(r),'s':[str(q) for q in ss],'B':[str(q) for q in Bs],'A':[str(q) for q in row['A']],'stationary_radicands':row['rad'],'candidates':cr})
best=min(allc,key=lambda q:q[0].b)
assert all(q is best or q[0].a>best[0].b for q in allc)
assert best[1]==[[0,11]] and best[2]=='balance'
out={'status':'PASS','old_volume':m,'T':[str(q) for q in Ts],'endpoint_oracle_edges':ow,'endpoint_oracle_bounds':[q.rec() for q in oracles],'classes':records,'candidate_count':len(allc),'winner_edges':best[1],'winner_kind':best[2],'winner_regret_bounds':best[0].rec(),'all_author_candidate_bounds_contain_independent_bounds':True}
(p/'result.json').write_text(json.dumps(out,indent=2)+'\n',encoding='utf-8');print(json.dumps({'status':'PASS','candidate_count':len(allc),'winner':best[1],'kind':best[2]}))

