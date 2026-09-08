import sympy as s,json,sys
from pathlib import Path
t,m,T,r,q=s.symbols('t m T r q',positive=True)
f=(m+t)*(T-t*q/(1+r*t));A=T-m*q;B=r*T-q
assert s.cancel(s.diff(f,t)-(A+B*(2*t+r*t*t))/(1+r*t)**2)==0
assert s.cancel((f.subs(t,1)-f.subs(t,0))-(A+B)/(1+r))==0
assert s.cancel(q*(m*r-1)/B-1-r*(m*q-T)/B)==0
# critical equation without radicals: let h=1+rt, h^2=q(mr-1)/B
h=s.symbols('h')
assert s.cancel((A+B*(2*t+r*t*t)).subs(t,(h-1)/r)-(B*h*h-q*(m*r-1))/r)==0
labs=[0]*3+[1]*3+[2]*3+[3];n=len(labs);adj=s.Matrix(n,n,lambda i,j:int(labs[i]!=labs[j]));adj[0,n-1]=adj[n-1,0]=0
L=s.diag(*list(adj*s.ones(n,1)))-adj;F=s.zeros(n);F[:n-1,:n-1]=L[:n-1,:n-1].inv();P=s.eye(n)-s.ones(n)/n;M=P*F*P
v=s.eye(n)[:,0]-s.eye(n)[:,1];rr=(v.T*M*v)[0];qq=(v.T*M*M*v)[0];tt=s.trace(M);mm=sum(adj)/2
assert (rr,qq,tt,mm)==(s.Rational(59,189),s.Rational(587,11907),s.Rational(751,630),35)
bb=rr*tt-qq;aa=tt-mm*qq;rad=s.cancel(qq*(mm*rr-1)/bb)
assert rad==s.Rational(1573160,1037853)
der1=s.cancel((aa+bb*(2+rr))/(1+rr)**2)
assert der1==s.Rational(66587,538160)
assert aa<0 and bb>0 and der1>0
# sqrt(rad)>1 and sqrt(rad)<1+r prove strict 0<t*<1 without approximation
assert rad>1 and rad<(1+rr)**2
out={'derivative_identity':True,'critical_equation':True,'radicand':str(rad),'inverse_r':str(1/rr),'derivative_at_0':str(aa),'derivative_at_1':str(der1),'B':str(bb),'strict_between_0_and_1':True,'python':sys.version,'sympy':s.__version__}
Path(__file__).with_name('result.json').write_text(json.dumps(out,indent=2));print(json.dumps(out,indent=2))

