import sympy as s
from pathlib import Path
import json
A,R,P=s.symbols('A R P'); u=s.symbols('u1:6'); x=3+A;k=2+R;p=1+P
U=sum(u);V=sum(t*t for t in u);W=sum(t**3 for t in u)
n=(k+1)*x+U+p;a=n-x;g=n*n-((k+1)*x*x+2*x*U+V+p);S0=g-x*a
S1=n**3-2*n*((k+1)*x*x+2*x*U+V+p)+(k+1)*x**3+3*x*x*U+3*x*V+W+p-x*a*a
M=-g*n*(a+2)*g+(x-2)*a*n*(a+2)*g+2*S1*a*(a+2)+(x-2)*S0*a*n*(a+2)+(n-2)*S0*S0*(a+2)+2*(g-a)*n*g
q=s.Poly(-M,A,R,P,*u)
terms=q.terms(); bad=[(m,int(c)) for m,c in terms if c<=0]
print('terms',len(terms),'bad',len(bad),'gap degree',max(sum(m[3:]) for m,c in terms),flush=True)
print('bad first',bad[:10],flush=True)
Path('certificate.json').write_text(json.dumps({'variables':['A','R','P']+[str(t) for t in u],'terms':[[list(m),int(c)] for m,c in terms]},indent=2))
groups={}
for m,c in terms:
 gaps=m[3:]
 if tuple(sorted(gaps,reverse=True))==gaps:
  groups.setdefault(gaps,[]).append((m[:3],c))
rows=[]
for gaps,cs in groups.items():
 coeff=sum(c*A**m[0]*R**m[1]*P**m[2] for m,c in cs)
 rows.append({'partition':[i for i in gaps if i],'coefficient':str(coeff),'term_count':len(cs),'min_coefficient':min(int(c) for m,c in cs)})
Path('symmetric-coefficients.json').write_text(json.dumps(rows,indent=2))
result={'terms':len(terms),'bad_count':len(bad),'gap_degree':max(sum(m[3:]) for m,c in terms),'constant':int(q.coeff_monomial((0,)*8)),'partition_count':len(rows)}
Path('batch2.json').write_text(json.dumps(result,indent=2));print(result)

