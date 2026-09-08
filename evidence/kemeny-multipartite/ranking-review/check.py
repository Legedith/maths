import sympy as s
import json
n,g,H,x,y=s.symbols('n g H x y')
def B(k):
 a=n-k
 t=g-k*a
 return -g/(2*a)+((k-2)*g/2+(H-k*a*a)/n+t*((k-2)/2+(n-2)*t/(2*n*a)))/g+(g-a)/(a*(a+2))
a,b=s.symbols('a b')
N=g*((n-2)*(a+b+2)-a*b)+a*b*(2*(a+2)*(b+2)-n)
res=s.factor((B(x)-B(y))/(x-y)-N.subs({a:n-x,b:n-y})/(n*(n-x)*(n-y)*(n-x+2)*(n-y+2)))
assert res==0
C=(n-2)*(a+b+2)-a*b
L=a*a+b*b-a*b+a+b+2*(n-2)
assert s.expand(C-L-a*(n-a-3)-b*(n-b-3))==0
assert s.expand(2*(a+2)*(b+2)-n-(2*a*b+3*a+3*b+8)-(a+b-n))==0
def K(A):
 d=A*s.ones(A.rows,1); vol=sum(d)
 T=s.diag(*[1/z for z in d])*A
 pi=d.T/vol
 return s.trace((s.eye(A.rows)-T+s.ones(A.rows,1)*pi).inv())-1
def diagnostic(q):
 labels=[i for i,v in enumerate(q) for _ in range(v)]
 m=len(labels); A=s.Matrix(m,m,lambda i,j:int(labels[i]!=labels[j])); base=K(A)
 gg=sum(v*(m-v) for v in q); hh=sum(v*(m-v)**2 for v in q)
 out=[]
 for i in (0,1):
  u=sum(q[:i]); AA=A.copy(); AA[u,u+1]=AA[u+1,u]=1
  actual=K(AA)-base
  formula=s.cancel(2*B(s.Integer(q[i])).subs({n:m,g:gg,H:hh})/(gg+2))
  assert actual==formula
  out.append(str(actual))
 assert s.sign(s.Rational(out[0])-s.Rational(out[1]))==s.sign(q[0]-q[1])
 return {'parts':q,'deltas':out}
print(json.dumps({'identity_residual':str(res),'positivity_gaps':'a*(n-a-3)+b*(n-b-3); a+b-n','diagnostics':[diagnostic([3,4]),diagnostic([3,5,2,1])],'sympy':s.__version__},indent=2))
