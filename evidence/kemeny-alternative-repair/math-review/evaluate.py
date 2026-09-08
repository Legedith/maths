import sympy as s,json,hashlib
from pathlib import Path
a,b,c=s.symbols('a b c');x,y,z=s.symbols('x y z')
old=Path('D:/CodexWorkspaces/mathematics-atlas/astra-postfailure-review-work');new=Path('D:/CodexWorkspaces/mathematics-atlas/astra-alternative-repair-work')
def read(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def hashfile(p):return hashlib.sha256(p.read_bytes()).hexdigest()
checked=[]
for stage,needed in [(old,{'B.json','C.json','untouched_A.json','result.json','verdict.json','input-hashes.json'}),(new,None)]:
 for row in read(stage/'hashes.json'):
  p=Path(row['Path'])
  if needed is None or p.name in needed:
   assert hashfile(p)==row['Hash'].lower();checked.append(str(p))
pin=read(new/'input-hash.json')['Hash'].lower();original=Path('D:/CodexWorkspaces/mathematics-atlas/astra-postfailure-design-work/batch2.json')
assert hashfile(original)==pin==read(old/'input-hashes.json')[str(original)]
data=read(new/'result.json');assert data['input_sha256']==pin
vals={k:s.sympify(read(old/(k+'.json'))['K']) for k in ['B','C','untouched_A']}
result={}
for k in ['B','C']:
 row=data['comparisons'][k];diff=s.factor(s.cancel(vals[k]-vals['untouched_A']));assert s.cancel(diff-s.sympify(row['difference']))==0
 polys=[]
 for field in ['numerator_terms','denominator_terms']:
  terms=row[field];exps=[tuple(e) for e,v in terms];assert len(set(exps))==len(exps)
  assert all(len(e)==3 and all(isinstance(i,int) and i>=0 for i in e) and s.Integer(v)>0 for e,v in terms)
  p=s.Poly(sum(s.Integer(v)*x**e[0]*y**e[1]*z**e[2] for e,v in terms),x,y,z);assert p.TC()>0;polys.append(p)
 N,D=s.fraction(s.sympify(row['difference']))
 for p,v in zip(polys,[N,D]):assert s.expand(v.subs({a:x+3,b:x+y+3,c:x+z+3})-p.as_expr())==0
 assert s.cancel(diff.subs({a:x+3,b:x+y+3,c:x+z+3})-polys[0].as_expr()/polys[1].as_expr())==0
 assert len(polys[0].terms())==row['num_count']==104
 assert str(min(polys[0].coeffs()))==row['num_min']=='2';assert str(polys[0].TC())==row['num_constant']=='39690'
 assert str(min(polys[1].coeffs()))==row['den_min']=='1';assert str(polys[1].TC())==row['den_constant']=='77157360'
 prior=read(old/'result.json')['full_matrix_K_333'];gap=s.Rational(prior[k])-s.Rational(prior['untouched_A']);assert gap==s.Rational(1,1944)
 result[k]={'exact_difference_identity':True,'complete_coefficient_identities':True,'positive_every_coefficient_and_constant':True,'numerator_terms':104,'full_matrix_gap_333':str(gap)};print(k,result[k],flush=True)
Path('result.json').write_text(json.dumps({'pass':True,'checked_hash_paths':checked,'same_previously_reviewed_input':True,'comparisons':result},indent=2));print('PASS',flush=True)
