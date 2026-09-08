import sympy as s,json
from pathlib import Path
a,b,c,x,y,z=s.symbols('a b c x y z');n=a+b+c+1;d=n-a;k=(n-1)*(d-1)/(n*d);W=(n*(n-1)+d*(d-1))/(n*n*d*d);m=a*b+a*c+b*c+a+b+c-1
T=3/n+(a-1)/(n-a)+(b-1)/(n-b)+(c-1)/(n-c)+W/k
uv=(2/d**2+2/(d**3*k)+W/(d**2*k**2))/(1+2/d+1/(d**2*k));SB=2/((n-b)*(n-b+2))
for row in json.loads(Path(__file__).with_name('batch1.json').read_text()):
 sub=dict(zip((a,b,c),row['parts']));assert s.cancel(T.subs(sub))==s.Rational(row['T']);assert m.subs(sub)==s.Rational(row['m'])
 for name,S in [('uv',uv),('B',SB)]:
  assert s.cancel((2*(T-(m+1)*S)/n).subs(sub))==s.Rational(row['orbits'][name]['delta_U'])
out={}
for name,expr,sub in [('equal',(m+1)*uv-T,{a:3+x,b:3+x,c:3+x}),('one_larger',(m+1)*SB-T,{a:3+x,b:4+x+y,c:3+x}),('both_larger',(m+1)*SB-T,{a:3+x,b:4+x+z+y,c:4+x+z})]:
 expr=s.factor(expr.subs(sub));num,den=s.fraction(expr);pp=s.Poly(num,x,y,z);qq=s.Poly(den,x,y,z)
 out[name]={'expression':str(expr),'num_count':len(pp.terms()),'num_min':str(min(pp.coeffs())),'num_constant':str(pp.coeff_monomial(1)),'den_min':str(min(qq.coeffs())),'den_constant':str(qq.coeff_monomial(1)),'positive':all(v>0 for v in pp.coeffs()) and all(v>0 for v in qq.coeffs()),'numerator_terms':[[list(e),str(v)] for e,v in pp.terms()],'denominator_terms':[[list(e),str(v)] for e,v in qq.terms()]}
 print(name,json.dumps({k:v for k,v in out[name].items() if k not in ('expression','numerator_terms','denominator_terms')},indent=2))
Path(__file__).with_name('batch2.json').write_text(json.dumps({'T_H':str(T),'m_H':str(m),'comparisons':out},indent=2))
