import sympy as s,json,hashlib
from pathlib import Path
source=Path('D:/CodexWorkspaces/mathematics-atlas/astra-postfailure-design-work/batch2.json')
pin=json.loads(Path(__file__).with_name('input-hash.json').read_text(encoding='utf-8-sig'))['Hash'].lower()
assert hashlib.sha256(source.read_bytes()).hexdigest()==pin
data=json.loads(source.read_text());a,b,c=s.symbols('a b c');x,y,z=s.symbols('x y z');local={str(v):v for v in (a,b,c)}
vals={k:s.sympify(v,locals=local) for k,v in data['values'].items()}
rows={}
for target in ('B','C'):
 diff=s.factor(vals[target]-vals['untouched_A']);num,den=s.fraction(diff)
 pp=s.Poly(s.expand(num.subs({a:3+x,b:3+x+y,c:3+x+z})),x,y,z);qq=s.Poly(s.expand(den.subs({a:3+x,b:3+x+y,c:3+x+z})),x,y,z)
 rows[target]={'difference':str(diff),'numerator_terms':[[list(e),str(v)] for e,v in pp.terms()],'denominator_terms':[[list(e),str(v)] for e,v in qq.terms()],'num_count':len(pp.terms()),'num_min':str(min(pp.coeffs())),'num_constant':str(pp.coeff_monomial(1)),'den_min':str(min(qq.coeffs())),'den_constant':str(qq.coeff_monomial(1)),'positive':all(v>0 for v in pp.coeffs()) and all(v>0 for v in qq.coeffs()),'diagnostics':[{'parts':q,'difference':str(diff.subs(dict(zip((a,b,c),q))))} for q in [(3,3,3),(3,4,5),(3,3,7),(4,4,6),(4,5,5)]]}
 print(target,json.dumps({k:v for k,v in rows[target].items() if k not in ('numerator_terms','denominator_terms')},indent=2))
Path(__file__).with_name('result.json').write_text(json.dumps({'input_sha256':pin,'comparisons':rows},indent=2))
