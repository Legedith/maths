from pathlib import Path
import sympy as S,json,hashlib
p=Path(__file__).parent;src=p.parent/'astra-forbidden-workload-work'
for name,h in {'proposal.md':'161f3b82f41ba7ada806fa1d2779bbee18066b31aaa29ce6ef1cb586e96094bf','result.json':'12373b7f62ccb631da09b31840ab3b337eb1a7f424c4dfb8d78a0a66feafe681'}.items():assert hashlib.sha256((src/name).read_bytes()).hexdigest()==h
n,d,e=S.symbols('n d e',positive=True);k=(n-1)*(d-1)/(n*d);W=(n*(n-1)+d*(d-1))/(n*n*d*d)
r=2/d+1/(d*d*k);norm=2/d**2+2/(d**3*k)+W/(d*d*k*k);hub=-1/(n*d*k)
I=norm/(1+r);lam=n*hub**2/(1+r);C=(2/e**2)/(1+2/e);gap=S.cancel(C-I-lam)
# Reconstruct every retained polynomial, not selected sign coefficients.
x,y,z=S.symbols('x y z',nonnegative=True);a=x+3;author=json.loads((src/'result.json').read_text());results=[]
for record,(b,c) in zip(author['orthants'],[(a,a+1+z),(a+1+y,a+1+y+z)]):
 expr=S.cancel(gap.subs({n:a+b+c+1,d:b+c+1,e:a+b+1},simultaneous=True));N,D=S.fraction(expr);res={'name':record['name']}
 for name,poly in [('numerator',N),('denominator',D)]:
  terms=record['coefficients'][name];powers=[tuple(t['powers']) for t in terms];assert len(set(powers))==len(powers)
  reconstructed=sum(S.Rational(t['coefficient'])*x**t['powers'][0]*y**t['powers'][1]*z**t['powers'][2] for t in terms)
  P=S.Poly(poly,x,y,z);assert S.Poly(reconstructed,x,y,z)==P
  assert set(P.monoms())==set(powers) and all(c>0 for c in P.coeffs())
  const=P.coeff_monomial(1);assert const==S.Rational(record[name+'_constant'])>0
  res[name]={'full_polynomial_equal':True,'nonzero_terms':len(terms),'constant':str(const),'degree':P.total_degree(),'all_nonzero_positive':True}
 assert S.cancel(N/D-expr)==0
 results.append(res)
result={'status':'PASS','independent_gap':str(S.factor(gap)),'orthants':results,'sympy':S.__version__}
(p/'result.json').write_text(json.dumps(result,indent=2),encoding='utf-8');print(json.dumps(result,indent=2))
