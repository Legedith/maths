import sympy as s,json
from pathlib import Path
a,b,c,x,y,z=s.symbols('a b c x y z')
prior=json.loads(Path('D:/CodexWorkspaces/mathematics-atlas/astra-uniform-repair-review-work/result.json').read_text())
scores={k:s.sympify(v,locals=dict(zip('abc',(a,b,c)))) for k,v in prior['scores'].items()}
n=a+b+c+1
# base trace: n-1 nonconstant dimensions, with a-1,b-1,c-1 part contrasts.
T=3/n+sum((q-1)/(n-q) for q in (a,b,c))+scores['restore']
m=a*b+a*c+b*c+n-2
packet=json.loads(Path('D:/CodexWorkspaces/mathematics-atlas/astra-uniform-noop-work/batch2.json').read_text())
out={}
for name,S,sub in [('equal',scores['uv'],{a:3+x,b:3+x,c:3+x}),('one_larger',scores['B'],{a:3+x,b:4+x+y,c:3+x}),('both_larger',scores['B'],{a:3+x,b:4+x+z+y,c:4+x+z})]:
 row=packet['comparisons'][name]
 p=lambda key:sum(s.Integer(v)*x**e[0]*y**e[1]*z**e[2] for e,v in row[key])
 pn,pd=p('numerator_terms'),p('denominator_terms')
 assert s.cancel(((m+1)*S-T).subs(sub)-pn/pd)==0
 for key in ['numerator_terms','denominator_terms']:
  assert all(s.Integer(v)>0 for e,v in row[key])
 assert pn.subs({x:0,y:0,z:0})>0 and pd.subs({x:0,y:0,z:0})>0
 out[name]=True
# Ground h, derive centered full inverse from grounded Green matrix, no projector/deletion update.
labs=[0]*3+[1]*3+[2]*3+[3];N=len(labs)
A=s.Matrix(N,N,lambda i,j:int(labs[i]!=labs[j]));A[0,9]=A[9,0]=0
L=s.diag(*list(A*s.ones(N,1)))-A
F=s.zeros(N);F[:9,:9]=L[:9,:9].inv();P=s.eye(N)-s.ones(N)/N;M=P*F*P
tt=s.trace(M);mm=sum(A)/2
assert tt==s.cancel(T.subs({a:3,b:3,c:3}))==s.Rational(751,630)
assert mm==m.subs({a:3,b:3,c:3})==35
v=s.eye(N)[:,1]-s.eye(N)[:,2];r=(v.T*M*v)[0];ss=(v.T*M*M*v)[0]
crit=s.cancel((mm*ss-tt)/(r*tt-ss))
AA=A.copy();AA[1,2]=AA[2,1]=1;LL=s.diag(*list(AA*s.ones(N,1)))-AA
FF=s.zeros(N);FF[:9,:9]=LL[:9,:9].inv();MM=P*FF*P
delta=s.cancel(2*(mm+1)*s.trace(MM)/N-2*mm*tt/N)
assert delta==s.Rational(31,3150) and crit==s.Rational(1043,1322)
t,R,Q,V,E=s.symbols('t R Q V E')
assert s.cancel(2*((E+t)*(V-t*Q/(1+t*R))-E*V)-2*t*((V-E*Q)+t*(R*V-Q))/(1+t*R))==0
result={'identities':out,'T':str(tt),'m':str(mm),'r':str(r),'s':str(ss),'U':str(2*mm*tt/N),'bad_delta':str(delta),'threshold':str(crit),'weighted_identity':True,'sympy':s.__version__}
import sys
result['python']=sys.version
Path(__file__).with_name('result.json').write_text(json.dumps(result,indent=2));print(json.dumps(result,indent=2))

