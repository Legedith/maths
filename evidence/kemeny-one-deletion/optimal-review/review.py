import sympy as s, json,sys,subprocess,time,hashlib
from pathlib import Path
a,b,c,t=s.symbols('a b c t');x,y,z=s.symbols('x y z')
author=Path('D:/CodexWorkspaces/mathematics-atlas/astra-postfailure-design-work')
names=['restore','uv','untouched_A','B','C']
def independent(name):
 # Vertex labels 0=u, 1=h; insertion endpoints receive their own cells.
 types=[0,3];sizes=[s.Integer(1),s.Integer(1)]
 if name=='uv':types += [0];sizes += [s.Integer(1)];edge=(0,2)
 elif name=='untouched_A':types += [0,0];sizes += [s.Integer(1)]*2;edge=(2,3)
 elif name in ['B','C']:types += [1 if name=='B' else 2]*2;sizes += [s.Integer(1)]*2;edge=(2,3)
 else:edge=(0,1)
 for p,total in enumerate([a,b,c]):sizes.append(total-types.count(p));types.append(p)
 m=len(types);W=s.zeros(m)
 for i in range(m):
  for j in range(m):
   if types[i]!=types[j]:W[i,j]=sizes[j]
 W[0,1]=W[1,0]=0
 i,j=edge;W[i,j]=W[j,i]=1
 D=s.diag(*[sum(W.row(i)) for i in range(m)])
 poly=s.Poly((t*D+D-W).det(method='domain-ge'),t)
 value=s.cancel(poly.nth(2)/poly.nth(1)+a+b+c+1-m)
 Path(name+'.json').write_text(json.dumps({'K':str(value),'q1':str(poly.nth(1)),'q2':str(poly.nth(2)),'cells':m}))
 print(name,'constructed full determinant',flush=True)
if len(sys.argv)>1:independent(sys.argv[1]);sys.exit()
Path('input-hashes.json').write_text(json.dumps({str(author/p):hashlib.sha256((author/p).read_bytes()).hexdigest() for p in ['proposal.md','batch2.json','batch2.py']},indent=2))
ledger=[]
for name in names:
 argv=[sys.executable,'review.py',name];start=time.time()
 try:
  r=subprocess.run(argv,capture_output=True,text=True,timeout=300);rc=r.returncode;out=r.stdout;err=r.stderr
 except subprocess.TimeoutExpired as ex:rc=124;out=ex.stdout or b'';err=ex.stderr or b''
 for suffix,v in [('stdout',out),('stderr',err)]:Path(name+'.'+suffix).write_bytes(v if isinstance(v,bytes) else v.encode())
 ledger.append({'name':name,'argv':argv,'seconds':time.time()-start,'rc':rc});Path('execution.json').write_text(json.dumps(ledger,indent=2));print(ledger[-1],flush=True)
 if rc:sys.exit(rc)
data=json.loads((author/'batch2.json').read_text());vals={n:s.sympify(json.loads(Path(n+'.json').read_text())['K']) for n in names}
for n in names:assert s.cancel(vals[n]-s.sympify(data['values'][n]))==0
for key,cert in data['comparisons'].items():
 left,right=key.split(' minus ');diff=vals[left]-vals[right];assert s.cancel(diff-s.sympify(cert['difference']))==0
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
