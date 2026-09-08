from fractions import Fraction as F
from math import isqrt
from pathlib import Path
import sympy as S,json
p=Path(__file__).parent;data=json.loads((p/'result.json').read_text());m=F(data['m']);T=F(data['Ttheta']);factor=F(data['objective_factor']);D=10**12
x,rr,ss,tt,mm=S.symbols('x r s T m');f=(mm+x)*(tt-x*ss/(1+rr*x));assert S.factor(S.diff(f,x)*(1+rr*x)**2-(tt-mm*ss+(rr*tt-ss)*(2*x+rr*x*x)))==0
classes={}
for row in data['rows']:
 key=(row['r'],row['s']);classes.setdefault(key,[]).append(row['edge'])
results=[]
for (rs,ss),edges in classes.items():
 r,s=F(rs),F(ss);A=T-m*s;B=r*T-s
 if A>=0:lo=hi=m*T;tl=th=F(0)
 else:
  rad=s*(m*r-1)/B;z=isqrt(rad.numerator*D*D//rad.denominator);rl=F(z,D);rh=F(z+1,D);assert rl*rl<=rad<rh*rh
  tl=(rl-1)/r;th=(rh-1)/r;assert 0<tl<th<1
  rad2=B*s*(m*r-1);z=isqrt(rad2.numerator*D*D//rad2.denominator);ql=F(z,D);qh=F(z+1,D);assert ql*ql<=rad2<qh*qh
  lo=(B*(m*r-1)+s+2*ql)/r**2;hi=(B*(m*r-1)+s+2*qh)/r**2
 results.append({'edges':edges,'minimum_scaled_interval':[str(lo),str(hi)],'tstar_interval':[str(tl),str(th)]})
winner=next(v for v in results if [3,4] in v['edges']);assert all(F(winner['minimum_scaled_interval'][1])<F(v['minimum_scaled_interval'][0]) for v in results if v is not winner)
r,s=F(1,4),F(1,32);half=(m+F(1,2))*(T-F(1,2)*s/(1+r/2));delta=factor*(half-m*T);assert delta<0
result={'derivative_identity':'PASS','sqrt_isolation_denominator':D,'class_bounds':results,'global_optimal_edges':winner['edges'],'half_strength_U_minus_noaction':str(delta),'global_minimum_below_noaction':F(winner['minimum_scaled_interval'][1])<m*T}
(p/'batch2.json').write_text(json.dumps(result,indent=2),encoding='utf-8');print(json.dumps(result,indent=2))
