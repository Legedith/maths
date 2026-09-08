import sympy as s,json,hashlib,sys
from pathlib import Path
root=Path('D:/CodexWorkspaces/mathematics-atlas');out=Path(__file__).parent
assert hashlib.sha256((root/'astra-weight-workload-family-work/proposal.md').read_bytes()).hexdigest()=='973868b9277394cb1fe6a1e3abfc659481ff19a8c3a7e77b7bb96cb5e0254850'
n,d,e,k,W,t=s.symbols('n d e k W t',positive=True)
DR=k+t*(1-k);DU=d*d*k+t*(2*d*k+1)
rR=(1-k)/k;sR=W/k**2;rU=2/d+1/(d*d*k);sU=2/d**2+2/(d**3*k)+W/(d*d*k*k)
R=W/(k*DR);U=(2*k+2/d+W/k)/DU;C=2/(e*(e+2*t));lr=1/(n*k*DR);lu=1/(n*k*DU)
assert s.cancel(sR/(1+t*rR)-R)==0 and s.cancel(sU/(1+t*rU)-U)==0
assert s.cancel(n/(n*k)**2/(1+t*rR)-lr)==0 and s.cancel(n/(n*d*k)**2/(1+t*rU)-lu)==0
assert s.expand(DU-DR-k*(d*d-1+t*(2*d+1)))==0
E=(DU-DR)*C-DU*U+DR*R
assert s.cancel(E-2*(k*((d*d-1+t*(2*d+1))/(e*(e+2*t))-1)-1/d))==0
tau=2*n*k*DR/(e*(e+2*t))-n*W
assert s.cancel((C-R)/lr-tau)==0
assert s.cancel(s.diff(tau,t)-2*n*k*(e-k*(e+2))/(e*(e+2*t)**2))==0
a=s.symbols('a',positive=True);nn=d+a;kk=(nn-1)*(d-1)/(nn*d);WW=(nn*(nn-1)+d*(d-1))/(nn*nn*d*d)
assert s.cancel((d-1)-kk*(d+1)+(a-1)*(d-1)/(nn*d))==0
assert s.cancel(nn*kk*(1-kk)/(d-1)-nn*WW-(a-1)*(d-1)/(d*d*nn))==0
assert s.cancel((d*d-1)-kk*d*(d+2)+(d-1)*(a-2)/nn)==0
teq=2*n*(k+1/d)*DR/(d*d-1+t*(2*d+1))-n*W
assert s.cancel((U-R)/(lr-lu)-teq)==0
assert s.cancel(s.diff(teq,t)-2*n*(k+1/d)*((d*d-1)-k*d*(d+2))/(d*d-1+t*(2*d+1))**2)==0
# Equal-family specialization after keeping rational identities factored.
dd=2*a+1;nn=3*a+1;kk=(nn-1)*(dd-1)/(nn*dd);WW=(nn*(nn-1)+dd*(dd-1))/(nn*nn*dd*dd)
formula=(a-2)*(20*a**3+8*a*a*t+4*a*a-a*t-t)/((2*a+1)**2*(3*a+1)*(4*a*a+4*a*t+4*a+3*t))
assert s.cancel(teq.subs({n:nn,d:dd,k:kk,W:WW})-formula)==0
lo=(a-2)*(8*a*a-a-1)/((2*a+1)**2*(3*a+1)*(4*a+3))
hi=a*(a-2)*(5*a+1)/((a+1)*(2*a+1)**2*(3*a+1))
assert s.cancel(formula.subs(t,0)-hi)==0
p,q=s.fraction(s.factor(formula));assert s.cancel(s.Poly(p,t).LC()/s.Poly(q,t).LC()-lo)==0
assert s.cancel(1-hi-(12*a**4+23*a**3+32*a*a+10*a+1)/((a+1)*(2*a+1)**2*(3*a+1)))==0
unit=(a-2)*(10*a*a+a-1)/((2*a+1)**2*(2*a+3)*(3*a+1))
assert s.cancel(formula.subs(t,1)-unit)==0
result={'score_slope_identities':True,'E_identity':True,'threshold_derivatives':True,'strict_bound_identities':True,'equal_limits_and_unit':True,'python':sys.version,'sympy':s.__version__}
(out/'result.json').write_text(json.dumps(result,indent=2),encoding='utf-8');print(json.dumps(result,indent=2))

