import sympy as s,json
from pathlib import Path
a,b,c,x,y,z=s.symbols('a b c x y z');n=a+b+c+1;d=n-a;k=(n-1)*(d-1)/(n*d);W=(n*(n-1)+d*(d-1))/(n*n*d*d)
restore=s.factor(W/k);uv=s.factor((2/d**2+2/(d**3*k)+W/(d**2*k**2))/(1+2/d+1/(d**2*k)))
S=lambda t:2/((n-t)*(n-t+2))
vals={'restore':restore,'uv':uv,'untouched_A':S(a),'B':S(b),'C':S(c)}
for row in json.loads(Path(__file__).with_name('batch1.json').read_text()):
 sub=dict(zip((a,b,c),row['parts']))
 for name,v in vals.items():assert v.subs(sub)==s.Rational(row['benefits'][name])
results={}
for label,expr,sub in [('uv_minus_restore',uv-restore,{a:3+x,b:3+x+y,c:3+x+z}),('uv_minus_untouchedA',uv-S(a),{a:3+x,b:3+x+y,c:3+x+z}),('larger_B_minus_uv',S(b)-uv,{a:3+x,b:4+x+y,c:3+x+z})]:
 expr=s.factor(expr);num,den=s.fraction(expr);pp=s.Poly(s.expand(num.subs(sub)),x,y,z);qq=s.Poly(s.expand(den.subs(sub)),x,y,z)
 results[label]={'expression':str(expr),'numerator_terms':[[list(e),str(v)] for e,v in pp.terms()],'denominator_terms':[[list(e),str(v)] for e,v in qq.terms()],'num_count':len(pp.terms()),'num_min':str(min(pp.coeffs())),'num_constant':str(pp.coeff_monomial(1)),'den_min':str(min(qq.coeffs())),'den_constant':str(qq.coeff_monomial(1)),'positive':all(v>0 for v in pp.coeffs()) and all(v>0 for v in qq.coeffs())}
 print(label,json.dumps({j:v for j,v in results[label].items() if j not in ('numerator_terms','denominator_terms')},indent=2))
Path(__file__).with_name('batch2.json').write_text(json.dumps({'scores':{j:str(v) for j,v in vals.items()},'comparisons':results},indent=2))
