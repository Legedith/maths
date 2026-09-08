import sympy as s,json
from pathlib import Path
a,b,c,t=s.symbols('a b c t');x,y,z=s.symbols('x y z')
author=Path('D:/CodexWorkspaces/mathematics-atlas/astra-postfailure-design-work')
names=['restore','uv','untouched_A','B','C']
data=json.loads((author/'batch2.json').read_text());vals={n:s.sympify(json.loads(Path(n+'.json').read_text())['K']) for n in names}
for n in names:assert s.cancel(vals[n]-s.sympify(data['values'][n]))==0
for key,cert in data['comparisons'].items():
 left,right=key.split(' minus ');diff=s.factor(s.cancel(vals[left]-vals[right]));assert s.cancel(diff-s.sympify(cert['difference']))==0
 pp=[]
 for field in ['numerator_certificate','denominator_certificate']:
  terms=cert[field];assert all(s.Integer(v)>0 for e,v in terms)
  poly=sum(s.Integer(v)*x**e[0]*y**e[1]*z**e[2] for e,v in terms);assert poly.subs({x:0,y:0,z:0})>0;pp.append(poly)
 assert s.cancel(diff.subs({a:x+3,b:x+y+3,c:x+z+3})-pp[0]/pp[1])==0
 print('identity and positivity',key,flush=True)
full={};parts=[0]*3+[1]*3+[2]*3+[3]
for name in names:
 A=s.Matrix(10,10,lambda i,j:int(parts[i]!=parts[j]));A[0,9]=A[9,0]=0
 i,j={'restore':(0,9),'uv':(0,1),'untouched_A':(1,2),'B':(3,4),'C':(6,7)}[name];A[i,j]=A[j,i]=1
 deg=A*s.ones(10,1);P=s.diag(*[1/d for d in deg])*A;pi=deg.T/sum(deg)
 K=s.trace((s.eye(10)-P+s.ones(10,1)*pi).inv())-1;assert K==vals[name].subs({a:3,b:3,c:3});full[name]=str(K)
assert s.Rational(full['uv'])-s.Rational(full['untouched_A'])==s.Rational(17,17856)
Path('result.json').write_text(json.dumps({'five_symbolic_values_equal':True,'five_differences_equal':True,'all_certificate_identities_positive':True,'full_matrix_K_333':full,'gap':'17/17856'},indent=2));print('PASS all checks',flush=True)

