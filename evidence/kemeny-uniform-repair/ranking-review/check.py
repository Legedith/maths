import sympy as s,json
from pathlib import Path
a,b,c,x,y,z=s.symbols('a b c x y z')
out={}
# cells u, remaining A, B, C, h; split target pair into singleton cells.
def score(kind):
 cells=[('u',0,s.Integer(1)),('A',0,a-1),('B',1,b),('C',2,c),('h',3,s.Integer(1))]
 if kind=='restore': src,tgt='u','h'
 elif kind=='uv':
  cells[1:2]=[('v',0,s.Integer(1)),('A',0,a-2)];src,tgt='u','v'
 else:
  name={'untouched_A':'A','B':'B','C':'C'}[kind];idx=next(i for i,t in enumerate(cells) if t[0]==name);nm,p,q=cells[idx]
  cells[idx:idx+1]=[('i',p,s.Integer(1)),('j',p,s.Integer(1)),(nm,p,q-2)];src,tgt='i','j'
 N=len(cells);h=N-1;sz=s.Matrix([q for _,_,q in cells])
 adj=lambda i,j: int(cells[i][1]!=cells[j][1] and {cells[i][0],cells[j][0]}!={'u','h'})
 Q=s.Matrix(N,N,lambda i,j: sum(sz[k]*adj(i,k) for k in range(N)) if i==j else -sz[j]*adj(i,j))
 rhs=s.Matrix([int(nm==src)-int(nm==tgt) for nm,_,_ in cells])
 # Ground h. Cramer's rule via fraction-free determinants, independently of rank-one/projectors.
 R=Q[:h,:h];det=s.factor(R.det(method='domain-ge'))
 v=[]
 for j in range(h):
  T=R.copy();T[:,j]=rhs[:h,0];v.append(s.cancel(T.det(method='domain-ge')/det))
 v.append(s.Integer(0));mean=s.cancel(sum(sz[i]*v[i] for i in range(N))/sum(sz))
 vv=[s.cancel(t-mean) for t in v]
 resistance=s.cancel(sum(rhs[i]*vv[i] for i in range(N)))
 norm=s.cancel(sum(sz[i]*vv[i]**2 for i in range(N)))
 return s.factor(norm/(1+resistance))
for k in ['restore','uv','untouched_A','B','C']:
 out[k]=score(k);print(k,str(out[k]),flush=True)
packet=json.loads(Path('D:/CodexWorkspaces/mathematics-atlas/astra-uniform-repair-design-work/batch2.json').read_text())
checks={}
for label,diff,sub in [('uv_minus_restore',out['uv']-out['restore'],{a:3+x,b:3+x+y,c:3+x+z}),('uv_minus_untouchedA',out['uv']-out['untouched_A'],{a:3+x,b:3+x+y,c:3+x+z}),('larger_B_minus_uv',out['B']-out['uv'],{a:3+x,b:4+x+y,c:3+x+z})]:
 row=packet['comparisons'][label]
 poly=lambda key:sum(s.Integer(co)*x**e[0]*y**e[1]*z**e[2] for e,co in row[key])
 pn,pd=poly('numerator_terms'),poly('denominator_terms')
 assert s.cancel(diff.subs(sub)-pn/pd)==0
 assert all(s.Integer(co)>0 for key in ['numerator_terms','denominator_terms'] for e,co in row[key])
 assert pn.subs({x:0,y:0,z:0})>0 and pd.subs({x:0,y:0,z:0})>0
 checks[label]=True
finite=[]
for aa,bb,cc in [(3,5,4),(4,4,4),(3,6,6)]:
 labs=[0]*aa+[1]*bb+[2]*cc+[3];n=len(labs);A=s.Matrix(n,n,lambda i,j:int(labs[i]!=labs[j]));A[0,n-1]=A[n-1,0]=0
 L=s.diag(*list(A*s.ones(n,1)))-A;J=s.ones(n)/n;M=(L+J).inv()-J
 scores={}
 for name,(i,j) in {'restore':(0,n-1),'uv':(0,1),'untouched_A':(1,2),'B':(aa,aa+1),'C':(aa+bb,aa+bb+1)}.items():
  v=s.eye(n)[:,i]-s.eye(n)[:,j];value=(v.T*M*M*v)[0]/(1+(v.T*M*v)[0])
  assert value==out[name].subs({a:aa,b:bb,c:cc});scores[name]=value
 finite.append({'parts':[aa,bb,cc],'best':[k for k,v in scores.items() if v==max(scores.values())]})
result={'scores':{k:str(v) for k,v in out.items()},'identities':checks,'finite':finite,'sympy':s.__version__}
Path(__file__).with_name('result.json').write_text(json.dumps(result,indent=2));print(json.dumps(result,indent=2))

