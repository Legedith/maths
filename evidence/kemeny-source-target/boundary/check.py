import sympy as S
import json,sys,hashlib
from pathlib import Path
t=S.symbols('t',nonnegative=True); theta=S.symbols('theta',real=True)
h10,h20,h12,h02=S.symbols('h10 h20 h12 h02')
eq0=[h10-1-S.Rational(2,3)*h20,h20-1-2*h10/(2+t)]
eq2=[h12-1-S.Rational(1,3)*h02,h02-1-h12/(1+t)]
s0=S.solve(eq0,[h10,h20]);s2=S.solve(eq2,[h12,h02])
assert all(S.cancel(e.subs(s0))==0 for e in eq0)
assert all(S.cancel(e.subs(s2))==0 for e in eq2)
U=S.factor((1-theta)*(s0[h10]+s2[h12])/3)
expected=(1-theta)*(1+S.Rational(8,3)/(3*t+2))
assert S.cancel(U-expected)==0
d=S.factor(S.diff(U,t));assert S.cancel(d+8*(1-theta)/(3*t+2)**2)==0
lim=S.limit(U,t,S.oo);assert lim==1-theta
gap=S.factor(U-lim);assert S.cancel(gap-8*(1-theta)/(3*(3*t+2)))==0
assert S.cancel(U.subs(t,0)-S.Rational(7,3)*(1-theta))==0
out={'status':'pass','python':sys.version,'sympy':S.__version__,'graph':{'old_edges':[[0,1,1],[1,2,2]],'added_edge':[0,2],'fixed_source':1},'first_step_equations':[str(x) for x in eq0+eq2],'solutions':{str(k):str(S.factor(v)) for k,v in (s0|s2).items()},'objective':str(U),'derivative':str(d),'finite_gap':str(gap),'infimum':str(lim),'at_zero':str(S.factor(U.subs(t,0))),'code_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest()}
assert S.__version__=='1.14.0' and sys.version_info[:3]==(3,12,11)
with Path('result.json').open('x',encoding='utf-8',newline='\n') as f:json.dump(out,f,indent=2,sort_keys=True);f.write('\n')
print(json.dumps(out,sort_keys=True))
