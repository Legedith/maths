import sympy as s,json,hashlib
from pathlib import Path
t,m,T,r,ss=s.symbols('t m T r s',positive=True);f=(m+t)*(T-t*ss/(1+r*t));A=T-m*ss;B=r*T-ss
assert s.factor(s.diff(f,t)-(A+B*(2*t+r*t*t))/(1+r*t)**2)==0
v=s.symbols('v');critical=(v-1)/r
assert s.factor((A+B*(2*critical+r*critical**2))*r-(B*v*v-ss*(m*r-1)))==0
src=Path('D:/CodexWorkspaces/mathematics-atlas/astra-uniform-noop-work/batch1.json');pin=json.loads(Path(__file__).with_name('input-hash.json').read_text(encoding='utf-8-sig'))['Hash'].lower();assert hashlib.sha256(src.read_bytes()).hexdigest()==pin
out=[]
for row in json.loads(src.read_text()):
 a,b,c=row['parts']
 if [a,b,c] not in [[3,3,3],[3,3,4],[3,4,5],[4,4,6]]:continue
 name='uv' if a==b==c else ('B' if b>=c else 'C');p=row['orbits'][name];rr=s.Rational(p['r']);sv=s.Rational(p['s']);mm=s.Rational(row['m']);TT=s.Rational(row['T']);BB=rr*TT-sv;AA=TT-mm*sv
 assert AA<0 and BB>0
 rad=s.factor(sv*(mm*rr-1)/BB);assert rad>1
 opt=s.simplify((s.sqrt(rad)-1)/rr);d1=s.factor((AA+BB*(2+rr))/(1+rr)**2)
 out.append({'parts':row['parts'],'orbit':name,'r':str(rr),'s':str(sv),'T':str(TT),'m':str(mm),'A':str(AA),'B':str(BB),'radicand':str(rad),'t_star':str(opt),'fprime_at1':str(d1),'unit_optimal':d1==0})
print(json.dumps(out,indent=2));Path(__file__).with_name('result.json').write_text(json.dumps({'generic_derivative_identity':True,'critical_identity':True,'input_sha256':pin,'cases':out},indent=2))
