import sympy as S,json
from pathlib import Path
p=Path(__file__).resolve().parent
n,d,e,t=S.symbols('n d e t',positive=True)
k=(n-1)*(d-1)/(n*d);W=(n*(n-1)+d*(d-1))/(n*n*d*d)
D=d*d*k+t*(2*d*k+1)
gap=S.cancel(2/(e*(e+2*t))-(2*k+2/d+W/k)/D-1/(n*k*D))
num,den=S.fraction(gap);assert S.Poly(num,t).degree()<=1
x,y,z=S.symbols('x y z',nonnegative=True);a=x+3
out={'gap':str(S.factor(gap)),'numerator_degree_in_t':S.Poly(num,t).degree(),'cases':[]}
for name,b,c in [('b_equal_a',a,a+1+z),('b_above_a',a+1+y,a+1+y+z)]:
 N,D0=[S.expand(poly.subs({n:a+b+c+1,d:b+c+1,e:a+b+1},simultaneous=True)) for poly in (num,den)]
 rec={'case':name,'coefficients':{}}
 for key,poly in [('numerator_t0',N.coeff(t,0)),('numerator_t1',N.coeff(t,1)),('denominator',D0)]:
  P=S.Poly(poly,x,y,z,t);terms=[{'powers':list(q),'coefficient':str(v)} for q,v in P.terms()]
  rec['coefficients'][key]=terms
  rec[key+'_positive']=all(v>0 for _,v in P.terms())
  rec[key+'_constant']=str(P.eval({x:0,y:0,z:0,t:0}))
 out['cases'].append(rec)
 print(name,{k:v for k,v in rec.items() if k!='coefficients'},flush=True)
(p/'result.json').write_text(json.dumps(out,indent=2)+'\n',encoding='utf-8')
assert all(r[k+'_positive'] and S.Rational(r[k+'_constant'])>0 for r in out['cases'] for k in ('numerator_t0','numerator_t1','denominator'))
print('PASS')
