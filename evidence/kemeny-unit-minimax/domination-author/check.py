import sympy as S,json
from pathlib import Path
p=Path(__file__).resolve().parent
n,d,e=S.symbols('n d e',positive=True)
k=(n-1)*(d-1)/(n*d);W=(n*(n-1)+d*(d-1))/(n*n*d*d);Z=d*(d+2)*k+1
C=2/(e*(e+2));I=(2*k+2/d+W/k)/Z;lam=1/(n*k*Z)
gap=S.cancel(C-I-lam);num,den=S.fraction(gap)
x,y,z=S.symbols('x y z',nonnegative=True);a=x+3
out={'gap':str(S.factor(gap)),'orthants':[]}
for name,b,c in [('b_equal_a',a,a+1+z),('b_above_a',a+1+y,a+1+y+z)]:
 expr=S.cancel(gap.subs({n:a+b+c+1,d:b+c+1,e:a+b+1},simultaneous=True))
 N,D=S.fraction(expr);record={'name':name,'coefficients':{}}
 for key,poly in [('numerator',N),('denominator',D)]:
  P=S.Poly(poly,x,y,z);terms=[{'powers':list(power),'coefficient':str(coef)} for power,coef in P.terms()]
  record['coefficients'][key]=terms
  record[key+'_constant']=str(P.eval({x:0,y:0,z:0}))
  record[key+'_all_positive']=all(coef>0 for _,coef in P.terms())
 out['orthants'].append(record)
 print(name,{k:v for k,v in record.items() if k!='coefficients'},flush=True)
(p/'result.json').write_text(json.dumps(out,indent=2)+'\n',encoding='utf-8')
assert all(r['numerator_all_positive'] and r['denominator_all_positive'] and S.Rational(r['numerator_constant'])>0 for r in out['orthants'])
print('PASS')
