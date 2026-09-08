from fractions import Fraction as F
from itertools import combinations_with_replacement
import json
import sympy as s
from pathlib import Path

def delta(q,p):
 x=q[0]; n=sum(q)+p; a=n-x; g=n*n-sum(t*t for t in q)-p
 S0=g-x*a; S1=sum(t*(n-t)**2 for t in q[1:])+p*(n-1)**2
 B=-F(g,2*a)+F(x-2,2)+F(S1,g*n)+F((x-2)*S0,2*g)+F((n-2)*S0*S0,2*g*n*a)+F(g-a,a*(a+2))
 return 2*B/(g+2)
out={}
for r in range(2,8):
 count=0; nonnegative=[]; maximum=None
 for q in combinations_with_replacement(range(3,10),r):
  for p in range(1,9):
   d=delta(q,p); count+=1
   if maximum is None or d>maximum[0]: maximum=(d,q,p)
   if d>=0 and len(nonnegative)<10: nonnegative.append([q,p,str(d)])
 out[r]={'count':count,'first_nonnegative':nonnegative,'maximum':[str(maximum[0]),maximum[1],maximum[2]]}
 print(r,out[r],flush=True)
Path('batch1.json').write_text(json.dumps(out,indent=2))
x,k,p,U,V,W=s.symbols('x k p U V W')
n=(k+1)*x+U+p; a=n-x
g=n*n-((k+1)*x*x+2*x*U+V+p)
S0=g-x*a
S1=n**3-2*n*((k+1)*x*x+2*x*U+V+p)+(k+1)*x**3+3*x*x*U+3*x*V+W-x*a*a
M=-g*n*(a+2)*g+(x-2)*a*n*(a+2)*g+2*S1*a*(a+2)+(x-2)*S0*a*n*(a+2)+(n-2)*S0*S0*(a+2)+2*(g-a)*n*g
poly=s.Poly(s.expand(-M),V,W)
Path('aggregate.txt').write_text('\n'.join(str(mon)+': '+str(s.factor(c)) for mon,c in poly.terms()))
print(Path('aggregate.txt').read_text())
