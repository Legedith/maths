import sympy as s, json, hashlib
from pathlib import Path
base=Path('D:/CodexWorkspaces/mathematics-atlas'); out=base/'astra-general-proof-review-work'
a,n,g,x,S0,S1=s.symbols('a n g x S0 S1')
nums=[-g,x-2,S1,(x-2)*S0,(n-2)*S0**2,g-a]
dens=[2*a,s.Integer(2),g*n,2*g,2*g*n*a,a*(a+2)]
D=2*a*n*(a+2)*g
complements=[s.cancel(D/d) for d in dens]
assert all(s.denom(t)==1 for t in complements)
M=sum(z*c for z,c in zip(nums,complements))
k,p,U,V,W=s.symbols('k p U V W')
nn=(k+1)*x+U+p; aa=nn-x
T2=(k+1)*x*x+2*x*U+V+p; T3=(k+1)*x**3+3*x*x*U+3*x*V+W+p
gg=nn**2-T2
Q=s.Poly(s.expand(-M.subs({a:aa,n:nn,g:gg,S0:gg-x*aa,S1:nn**3-2*nn*T2+T3-x*aa**2}, simultaneous=True)),U,V,W)
assert max(e[0]+2*e[1]+3*e[2] for e,c in Q.terms())<=5
A,R,P=s.symbols('A R P'); us=s.symbols('u1:6'); vs=(A,R,P)+us
qq=s.Poly(Q.as_expr().subs({x:A+3,k:R+2,p:P+1,U:sum(us),V:sum(t*t for t in us),W:sum(t**3 for t in us)}, simultaneous=True).expand(),*vs)
expected={tuple(e):int(c) for e,c in qq.terms()}
certpath=base/'astra-network-generalization-work/certificate.json'
assert hashlib.sha256(certpath.read_bytes()).hexdigest()=='b264e53aa98bb9171fcb327cb82cd01ec31e4c67eecbf30af6752545c078804c'
c=json.loads(certpath.read_text()); assert c['variables']==list(map(str,vs)); actual={tuple(e):v for e,v in c['terms']}
assert len(actual)==len(c['terms']) and expected==actual
assert min(expected.values())>0 and expected[(0,)*8]==60948
for i in range(4):
 for e,c in expected.items():
  f=list(e); f[i+3],f[i+4]=f[i+4],f[i+3]; assert expected[tuple(f)]==c
# Direct graph transition matrices, no closed-form K.
def K(q,p,added=False):
 labels=[i for i,t in enumerate(q+[1]*p) for _ in range(t)]; N=len(labels)
 adj=s.Matrix(N,N,lambda i,j:int(labels[i]!=labels[j]))
 if added: adj[0,1]=adj[1,0]=1
 deg=[sum(adj.row(i)) for i in range(N)]; vol=sum(deg)
 T=s.Matrix(N,N,lambda i,j:adj[i,j]/deg[i]); pi=s.Matrix(1,N,lambda i,j:deg[j]/vol)
 return s.trace((s.eye(N)-T+s.ones(N,1)*pi).inv())-1
results=[]
for q,pp in [([9,9],1),([3,3,4,4,5,6],2)]:
 N=sum(q)+pp; xx=q[0]; al=N-xx; gam=sum(t*(N-t) for t in q)+pp*(N-1)
 z0=sum(t*(N-t) for t in q[1:])+pp*(N-1); z1=sum(t*(N-t)**2 for t in q[1:])+pp*(N-1)**2
 b=sum(z/d for z,d in zip(nums,dens)).subs({a:al,n:N,g:gam,x:xx,S0:z0,S1:z1})
 delta=K(q,pp,True)-K(q,pp); assert delta==2*b/(gam+2)
 results.append({'q':q,'p':pp,'delta':str(delta)})
assert results[0]['delta']=='229/627000'
res={'status':'PASS','complements':list(map(str,complements)),'terms':len(expected),'minimum_coefficient':min(expected.values()),'constant':60948,'weighted_gap_degree':max(e[0]+2*e[1]+3*e[2] for e,c in Q.terms()),'matrix':results}
(out/'result.json').write_text(json.dumps(res,indent=2)); (out/'independent-aggregate.txt').write_text(str(Q.as_expr()))
print(json.dumps(res,indent=2))
