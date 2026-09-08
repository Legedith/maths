import sympy as s,json,sys
from pathlib import Path
a,b,c,x,y,z=s.symbols('a b c x y z');n=a+b+c+1;d=b+c+1
# r follows accepted deletion inverse; recover s independently from prior grounded unit-score S=s/(1+r).
rho=(n+d-1)/(n*d);k=1-rho
rr={'restore':rho/k,'uv':2/d+1/(d*d*k),'untouched_A':2/d,'B':2/(n-b),'C':2/(n-c)}
prior=json.loads(Path('D:/CodexWorkspaces/mathematics-atlas/astra-uniform-repair-review-work/result.json').read_text())
ss={key:s.cancel(s.sympify(val,locals={'a':a,'b':b,'c':c})*(1+rr[key])) for key,val in prior['scores'].items()}
cert=json.loads(Path('D:/CodexWorkspaces/mathematics-atlas/astra-uniform-weight-work/batch2.json').read_text())
checks={}
for i,j,sub in [('uv','restore',{a:3+x,b:3+x+y,c:3+x+z}),('uv','untouched_A',{a:3+x,b:3+x+y,c:3+x+z}),('B','uv',{a:3+x,b:4+x+y,c:3+x+z})]:
 for mode,expr in [('intercept',ss[i]-ss[j]),('slope',ss[i]*rr[j]-ss[j]*rr[i])]:
  name=i+'>'+j+':'+mode;row=cert['comparisons'][name]
  poly=lambda key:sum(s.Integer(v)*x**e[0]*y**e[1]*z**e[2] for e,v in row[key])
  pn,pd=poly('num_terms'),poly('den_terms')
  assert s.cancel(s.cancel(expr).subs(sub)-pn/pd)==0
  assert all(s.Integer(v)>0 for key in ['num_terms','den_terms'] for e,v in row[key])
  assert pn.subs({x:0,y:0,z:0})>0 and pd.subs({x:0,y:0,z:0})>0
  checks[name]=True
labs=[0]*4+[1]*4+[2]*6+[3];N=len(labs);A=s.Matrix(N,N,lambda i,j:int(labs[i]!=labs[j]));A[0,N-1]=A[N-1,0]=0
L=s.diag(*list(A*s.ones(N,1)))-A;F=s.zeros(N);F[:N-1,:N-1]=L[:N-1,:N-1].inv();P=s.eye(N)-s.ones(N)/N;M=P*F*P
vals={}
for name,(i,j) in {'restore':(0,N-1),'uv':(0,1),'untouched_A':(1,2),'B':(4,5),'C':(8,9)}.items():
 v=s.eye(N)[:,i]-s.eye(N)[:,j];r=(v.T*M*v)[0];q=(v.T*M*M*v)[0]
 assert r==s.cancel(rr[name].subs({a:4,b:4,c:6})) and q==ss[name].subs({a:4,b:4,c:6})
 vals[name]=(r,q)
r1,q1=vals['restore'];r2,q2=vals['untouched_A']
cross=s.cancel((q2-q1)/(q1*r2-q2*r1));assert cross==12
at={k:s.cancel(q/(1+12*r)) for k,(r,q) in vals.items()}
assert at['restore']==at['untouched_A']==at['B']
assert all(at['C']>v for k,v in at.items() if k!='C')
result={'six_identities':checks,'crossing':str(cross),'at_crossing':{k:str(v) for k,v in at.items()},'grounded_rs':{k:list(map(str,v)) for k,v in vals.items()},'python':sys.version,'sympy':s.__version__}
Path(__file__).with_name('result.json').write_text(json.dumps(result,indent=2));print(json.dumps(result,indent=2))

