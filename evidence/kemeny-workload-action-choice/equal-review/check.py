from fractions import Fraction as F
from pathlib import Path
import json, sympy as S, hashlib
p=Path(__file__).resolve().parent;src=p.parent/'astra-workload-noop-explore-work'
rows=json.loads((src/'result.json').read_text(encoding='utf-8'))['rows']
assert [(r['parts'],r['theta']) for r in rows]==[(list(g),str(t)) for g in [(3,3,3),(3,3,4),(3,3,100)] for t in [F(0),F(1,10),F(1,2),F(9,10)]]
checks=[]
for parts in [(3,3,3),(3,3,4),(3,3,100)]:
 a,b,c=parts;n=a+b+c+1;h=n-1;labs=[0]*a+[1]*b+[2]*c+[3];sizes=[a,b,c,1]
 def intact(i,j):return F(int(i==j),n-sizes[labs[i]])-F(int(labs[i]==labs[j]),n*(n-sizes[labs[i]]))-F(1,n*n)
 z=[intact(i,0)-intact(i,h) for i in range(n)];den=1-z[0]+z[h]
 def M(i,j):return intact(i,j)+z[i]*z[j]/den
 T=sum(M(i,i) for i in range(n));hh=M(h,h)
 m=sum(labs[i]!=labs[j] for i in range(n) for j in range(i+1,n))-1
 reps={'restore':(0,h),'uv':(0,1),'untouched_A':(1,2),'B':(a,a+1),'C':(a+b,a+b+1)}
 acts={}
 for name,(i,j) in reps.items():
  v=[M(k,i)-M(k,j) for k in range(n)];r=v[i]-v[j];s=sum(q*q for q in v)
  acts[name]=(T-s/(1+r),hh-v[h]**2/(1+r))
 for row in [r for r in rows if r['parts']==list(parts)]:
  t=F(row['theta']);baseline=2*m*(1-t)*(T/n+t*hh)
  values={name:2*(m+1)*(1-t)*(tr/n+t*diag) for name,(tr,diag) in acts.items()}
  assert baseline==F(row['baseline']) and values=={k:F(v) for k,v in row['candidate_U'].items()}
  best=min(values.values());assert baseline-best==F(row['improvement'])>0
  assert row['best_edges_orbits']==[k for k,v in values.items() if v==best]
  assert row['restore_improves']==(values['restore']<baseline)
  checks.append({'parts':parts,'theta':str(t),'all_values_equal':True})
a=S.symbols('a',positive=True);n=3*a+1;d=2*a+1;m=3*a*a+3*a-1
k=(n-1)*(d-1)/(n*d);w=(n*(n-1)+d*(d-1))/(n*n*d*d)
T=3*(a-1)/d+3/n+w/k;hh=(n-1)/n**2+1/(n*n*k)
rR=(1-k)/k;sR=w/k**2;zR=-1/(n*k)
rU=2/d+1/(d*d*k);sU=2/d**2+2/(d**3*k)+w/(d*d*k*k);zU=-1/(n*d*k)
tau=(a-2)*(10*a*a+a-1)/((2*a+1)**2*(2*a+3)*(3*a+1))
FR0=(m+1)*sR/(1+rR)-T;FRs=(m+1)*n*zR*zR/(1+rR)-n*hh
FU0=(m+1)*sU/(1+rU)-T;FUs=(m+1)*n*zU*zU/(1+rU)-n*hh
num=18*a**6+531*a**5+306*a**4+39*a**3-15*a*a-8*a-1
cross=num/(3*a*a*(2*a+1)**2*(2*a+3)*(3*a+1)**2)
rs=(18*a**4+15*a**3+12*a*a-2*a-1)/(6*a*a*(3*a+1))
us=-(216*a**6+342*a**5+105*a**4+51*a**3+12*a*a+5*a+1)/(6*a*a*(3*a+1)*(12*a**3+18*a*a+3*a+1))
assert all(S.cancel(v)==0 for v in [FR0+tau*FRs-cross,FU0+tau*FUs-cross,FRs-rs,FUs-us])
x=S.symbols('x');coeff=[str(v) for v in S.Poly(num.subs(a,x+3),x).all_coeffs()];assert all(int(v)>0 for v in coeff)
out={'status':'PASS','diagnostic_rows':checks,'symbolic_identities':4,'switch_positive_shift_coefficients':coeff,'sympy':S.__version__}
(p/'result.json').write_text(json.dumps(out,indent=2)+'\n',encoding='utf-8');print(json.dumps(out))
