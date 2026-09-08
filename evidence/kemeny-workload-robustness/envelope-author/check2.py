import sympy as S,json
from pathlib import Path
n,d,e,t,a=S.symbols('n d e t a',positive=True);k=(n-1)*(d-1)/(n*d);W=(n*(n-1)+d*(d-1))/(n*n*d*d)
limit=n*k*(1-k)/e-n*W;lower=S.factor((n*k*(1-k)/(d-1)-n*W).subs(n,d+a))
DR=k+t*(1-k);eq=2*n*(k+1/d)*DR/(d*d-1+t*(2*d+1))-n*W
assert S.factor(S.diff(eq,t)-2*n*(k+1/d)*((d*d-1)-k*d*(d+2))/(d*d-1+t*(2*d+1))**2)==0
# derivative e-k(e+2) increases with e because k<1, so use e<=d-1
upper=S.factor(((d-1)-k*(d+1)).subs(n,d+a))
result={'unequal_limit_lower':str(lower),'unequal_derivative_sign_upper':str(upper),'equal_derivative_identity':'PASS'}
Path(__file__).with_name('batch2.json').write_text(json.dumps(result,indent=2),encoding='utf-8');print(json.dumps(result,indent=2))
