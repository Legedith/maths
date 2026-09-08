import sympy as s,json,hashlib,itertools
from pathlib import Path
src=Path('D:/CodexWorkspaces/mathematics-atlas/astra-uniform-noop-work/batch1.json');pin=json.loads(Path(__file__).with_name('input-hash.json').read_text(encoding='utf-8-sig'))['Hash'].lower();assert hashlib.sha256(src.read_bytes()).hexdigest()==pin
out=[]
for row in json.loads(src.read_text()):
 vals={k:(s.Rational(v['r']),s.Rational(v['s'])) for k,v in row['orbits'].items()};weights=[];crossings=[]
 for t in map(s.Rational,['1/100','1/10','1','10','100']):
  sc={k:ss/(1+t*r) for k,(r,ss) in vals.items()};weights.append({'t':str(t),'best':[k for k,v in sc.items() if v==max(sc.values())],'scores':{k:str(v) for k,v in sc.items()}})
 for i,j in itertools.combinations(vals,2):
  ri,si=vals[i];rj,sj=vals[j];coef=si*rj-sj*ri
  if coef!=0:
   t=(sj-si)/coef
   if t>0:crossings.append({'pair':[i,j],'t':str(t)})
 out.append({'parts':row['parts'],'weights':weights,'positive_crossings':crossings})
print(json.dumps(out,indent=2));Path(__file__).with_name('batch1.json').write_text(json.dumps({'input_sha256':pin,'cases':out},indent=2))
