import sympy as S,json
from pathlib import Path
n,d,e,t,a=S.symbols('n d e t a',positive=True)
k=(n-1)*(d-1)/(n*d);W=(n*(n-1)+d*(d-1))/(n*n*d*d)
DR=k+t*(1-k);DU=d*d*k+t*(2*d*k+1)
rR=(1-k)/k;sR=W/k**2;rU=2/d+1/(d*d*k);sU=2/d**2+2/(d**3*k)+W/(d*d*k*k)
R=W/(k*DR);U=(2*k+2/d+W/k)/DU;C=2/(e*(e+2*t));lr=1/(n*k*DR);lu=1/(n*k*DU)
assert S.factor(R-sR/(1+t*rR))==0 and S.factor(U-sU/(1+t*rU))==0
assert S.factor(lr-n/(n*n*k*k)/(1+t*rR))==0 and S.factor(lu-n/(n*n*d*d*k*k)/(1+t*rU))==0
E=(DU-DR)*C-DU*U+DR*R
assert S.factor(E-2*(k*((d*d-1+t*(2*d+1))/(e*(e+2*t))-1)-1/d))==0
# Lower-bound algebra: numerator difference >= e+(2e+1)t when d>=e+1.
num=d*d-1-e*e+t*(2*d+1-2*e)
assert S.factor(num.subs(d,e+1)-(2*e+3*t))==0
# actual inequality uses d-1>=e, and num>=2e+3t
lower=(n-1)*(2*e+3*t)/(n*(e+2*t))-1
assert S.factor(lower-((n-2)*e+(n-3)*t)/(n*(e+2*t)))==0
tau=S.factor((C-R)/lr);eq=S.factor((U-R)/(lr-lu))
assert S.factor(tau-(2*n*k*DR/(e*(e+2*t))-n*W))==0
assert S.factor(eq-(2*n*(k+1/d)*DR/(d*d-1+t*(2*d+1))-n*W))==0
assert S.factor(S.diff(tau,t)-2*n*k*(e-k*(e+2))/(e*(e+2*t)**2))==0
assert S.factor(((d*d-1)-k*d*(d+2)).subs(n,d+a)+(d-1)*(a-2)/(d+a))==0
equal=S.factor(eq.subs({n:3*a+1,d:2*a+1}));eq0=S.factor(equal.subs(t,0));eqinf=S.factor(S.limit(equal,t,S.oo));eqone=S.factor(equal.subs(t,1))
assert S.factor(eqone-(a-2)*(10*a*a+a-1)/((2*a+1)**2*(2*a+3)*(3*a+1)))==0
result={'identities':'PASS','equal_tau':str(equal),'equal_t0_limit':str(eq0),'equal_tinf_limit':str(eqinf),'equal_one_minus_t0':str(S.factor(1-eq0)),'unequal_t0_limit':str(S.factor(tau.subs(t,0))),'unequal_tinf_limit':str(S.factor(S.limit(tau,t,S.oo))),'DU_minus_DR':str(S.factor(DU-DR))}
Path(__file__).with_name('result.json').write_text(json.dumps(result,indent=2),encoding='utf-8');print(json.dumps(result,indent=2))
