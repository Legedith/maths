import json, sympy as s, importlib.util
from pathlib import Path
from fractions import Fraction as F
out=Path(__file__).parent
spec=importlib.util.spec_from_file_location('diag','D:/CodexWorkspaces/mathematics-atlas/project/evidence/kemeny-three-part/independent/scripts/exact_matrix_diagnostic.py'); diag=importlib.util.module_from_spec(spec);spec.loader.exec_module(diag)
n,g,h,x,y=s.symbols('n g h x y'); u,v,w=s.symbols('u v w'); a=n-x;t=g-x*a
B=-g/(2*a)+(x-2)/2+(h-x*a*a)/(g*n)+(x-2)*t/(2*g)+(n-2)*t*t/(2*g*n*a)+(g-a)/(a*(a+2))
diff=s.factor((B-B.subs(x,y))/(x-y)); num,den=s.fraction(diff)
poly=s.Poly(s.expand(num.subs(n,x+y+w).subs({x:u+3,y:v+3})),g,u,v,w)
alpha,beta=s.symbols('alpha beta')
compact=s.factor(num.subs({x:n-alpha,y:n-beta}))
checks=[]
for q in [(3,4,5,1),(3,5,1,1),(3,4),(3,4,5,6,1)]:
 adj,parts=diag.complete_multipartite_adjacency(q); base=diag.kemeny(adj)
 for i,k in enumerate(q):
  if k<3:continue
  changed=[r[:] for r in adj]; l,r=parts[i][:2];changed[l][r]=changed[r][l]=1
  observed=diag.kemeny(changed)-base
  nn=sum(q); gg=sum(k*(nn-k) for k in q); hh=sum(k*(nn-k)**2 for k in q)
  expected=B.subs({n:nn,g:gg,h:hh,x:k})*2/(gg+2)
  assert s.Rational(observed.numerator,observed.denominator)==expected
  checks.append({'q':q,'selected':k,'delta':str(observed)})
report={'symbolic_difference':str(diff),'numerator_alpha_beta':str(compact),'substitution':'n=x+y+w,x=3+u,y=3+v; gamma=g>0,u,v,w>=0','coefficient_count':len(poly.terms()),'minimum_coefficient':str(min(poly.coeffs())),'all_positive':all(c>0 for c in poly.coeffs()),'constant_in_u_v_w':str(poly.as_expr().subs({u:0,v:0,w:0})),'matrix_checks':checks}
(out/'batch2-result.json').write_text(json.dumps(report,indent=2));(out/'ranking-polynomial.json').write_text(json.dumps([[list(m),str(c)] for m,c in poly.terms()],indent=2));print(json.dumps(report,indent=2))
