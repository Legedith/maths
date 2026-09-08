import sympy as s,json,itertools,hashlib
from sympy.polys.rings import ring
from pathlib import Path
root=Path(__file__).parent; author=root.parent/'astra-damage-symbolic-work'
rg,a,b,c,t=ring('a,b,c,t',s.QQ)
coeff=[]
for e in (0,1):
 # Explicit graph neighbor counts, independently transcribed from graph definition.
 R=[[0,e,0,b,c,0],[e,0,0,b,c,1],[0,0,0,b,c,1],[1,1,a-2,0,c,1],[1,1,a-2,b,0,1],[0,1,a-2,b,c,0]]
 ds=[sum(row) for row in R]
 mat=[[(1+t)*ds[i]-R[i][j] if i==j else -R[i][j] for j in range(6)] for i in range(6)]
 det=rg.zero
 for perm in itertools.permutations(range(6)):
  sign=(-1)**sum(perm[i]>perm[j] for i in range(6) for j in range(i+1,6)); prod=rg(sign)
  for i in range(6): prod*=mat[i][perm[i]]
  det+=prod
 assert all(exp[3]>0 for exp in det)
 coeff.append([s.expand(sum(s.Rational(v.numerator,v.denominator)*s.Symbol('a')**exp[0]*s.Symbol('b')**exp[1]*s.Symbol('c')**exp[2] for exp,v in det.items() if exp[3]==j)) for j in (1,2)])
 print('full determinant',e,'done',flush=True)
packet=json.loads((author/'symbolic.json').read_text()); aa,bb,cc=s.symbols('a b c'); x,y,z=s.symbols('x y z')
for e in (0,1):
 for j in (0,1): assert s.expand(coeff[e][j]-s.sympify(packet[f'q{e}'][j]))==0
N=s.expand(coeff[1][1]*coeff[0][0]-coeff[0][1]*coeff[1][0]); assert s.expand(N-s.sympify(packet['N']))==0
negative=s.Poly(-N.subs({aa:3+x,bb:3+x+y,cc:3+x+z}),x,y,z)
actual={tuple(e):int(v) for e,v in negative.terms()}; stored={tuple(e):int(v) for e,v in packet['negative_N_shift_terms']}
assert len(stored)==len(packet['negative_N_shift_terms']) and actual==stored
assert len(actual)==284 and min(actual.values())==6 and actual[(0,0,0)]==1784916000 and negative.total_degree()==10
results=[]
for av,bv,cv in [(3,3,3),(3,4,5),(4,4,6)]:
 labels=[0]*av+[1]*bv+[2]*cv+[3]; n=len(labels); row=[]
 for e in (0,1):
  adj=s.Matrix(n,n,lambda i,j:int(labels[i]!=labels[j])); adj[0,n-1]=adj[n-1,0]=0
  adj[0,1]=adj[1,0]=e
  degrees=list(map(sum,adj.tolist())); vol=sum(degrees)
  P=s.Matrix(n,n,lambda i,j:adj[i,j]/degrees[i]); pi=s.Matrix(1,n,lambda i,j:degrees[j]/vol)
  K=s.trace((s.eye(n)-P+s.ones(n,1)*pi).inv())-1
  subs={aa:av,bb:bv,cc:cv}; reduced=n-6+coeff[e][1].subs(subs)/coeff[e][0].subs(subs)
  assert K==reduced
  row.append(K)
  results.append({'tuple':[av,bv,cv],'e':e,'full_K':str(K),'reduced_K':str(reduced)})
 print([av,bv,cv],str(row[1]-row[0]),flush=True)
checks=json.loads((author/'checks.json').read_text())['full_matrix_checks']
assert all(r['full_K']==c['full_K'] for r,c in zip(results,checks))
res={'status':'PASS','determinant_method':'full permutation expansion, 720 terms each','terms':len(actual),'minimum':min(actual.values()),'constant':actual[(0,0,0)],'degree':negative.total_degree(),'matrix_checks':results}
(root/'result.json').write_text(json.dumps(res,indent=2)); print(json.dumps(res,indent=2))

