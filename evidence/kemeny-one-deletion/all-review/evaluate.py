import sympy as s,json,time
from sympy.polys.matrices import DomainMatrix
from pathlib import Path
root=Path(__file__).parent; author=root.parent/'astra-all-deletions-recovery-work'
a,b,c,t=s.symbols('a b c t'); x,y,z=s.symbols('x y z')
cases={'uB':('u','j'),'rB':('r','j'),'BC':('j','k'),'uh':('u','h'),'rh':('r','h'),'Bh':('j','h')}
parts={'u':0,'v':0,'r':0,'j':1,'k':2,'h':3,'A':0,'B':1,'C':2}
results=[]; matrices=[]
for case,pair in cases.items():
 names=['u','v','h']+[q for q in ('r','j','k') if q in pair]+['A','B','C']
 sizes={q:s.Integer(1) for q in names}; sizes.update(A=a-2-int('r' in names),B=b-int('j' in names),C=c-int('k' in names)); m=len(names)
 qs=[]
 for e in (0,1):
  R=s.Matrix(m,m,lambda i,j: sizes[names[j]]*int((parts[names[i]]!=parts[names[j]] and set((names[i],names[j]))!=set(pair)) or (e==1 and set((names[i],names[j]))=={'u','v'})))
  deg=list(map(sum,R.tolist())); L=s.diag(*deg)-R
  dm=DomainMatrix.from_Matrix(L+t*s.diag(*deg)).convert_to(s.ZZ.poly_ring(a,b,c,t))
  det=dm.det().as_expr(); poly=s.Poly(det,t); assert poly.coeff_monomial(1)==0
  qs.append([s.expand(poly.coeff_monomial(t**j)) for j in (1,2)])
 print(case,'determinants complete',flush=True)
 packet=json.loads((author/f'{case}.json').read_text())
 for e in (0,1):
  for j in (0,1): assert s.expand(qs[e][j]-s.sympify(packet['q'][e][j]))==0
 N=s.sympify(packet['N']); D=s.sympify(packet['D']); cross=qs[1][1]*qs[0][0]-qs[0][1]*qs[1][0]
 assert s.Poly(s.expand(cross*D-N*qs[1][0]*qs[0][0]),a,b,c).is_zero
 row={'case':case,'cells':m}
 for label,expr,key in [('negative_numerator',-N,'negative_numerator_terms'),('denominator',D,'denominator_terms')]:
  poly=s.Poly(expr.subs({a:3+x,b:3+x+y,c:3+x+z}).expand(),x,y,z); expected={ex:int(v) for ex,v in poly.terms()}; actual={tuple(ex):int(v) for ex,v in packet[key]}
  assert len(actual)==len(packet[key]) and expected==actual and min(expected.values())>0 and expected[(0,0,0)]>0
  row[label]={'terms':len(expected),'minimum':min(expected.values()),'constant':expected[(0,0,0)],'degree':poly.total_degree()}
 for av,bv,cv in [(3,3,3),(3,4,5),(4,4,6)]:
  labels=[0]*av+[1]*bv+[2]*cv+[3]; n=len(labels); ids={'u':0,'v':1,'r':2,'j':av,'k':av+bv,'h':n-1}; values=[]
  for e in (0,1):
   adj=s.Matrix(n,n,lambda i,j:int(labels[i]!=labels[j])); ii,jj=map(ids.get,pair);adj[ii,jj]=adj[jj,ii]=0;adj[0,1]=adj[1,0]=e
   ds=list(map(sum,adj.tolist())); P=s.Matrix(n,n,lambda i,j:adj[i,j]/ds[i]); pi=s.Matrix(1,n,lambda i,j:ds[j]/sum(ds))
   K=s.trace((s.eye(n)-P+s.ones(n,1)*pi).inv())-1; sub={a:av,b:bv,c:cv}; qK=n-m+qs[e][1].subs(sub)/qs[e][0].subs(sub)
   assert K==qK; values.append(K); matrices.append({'case':case,'tuple':[av,bv,cv],'e':e,'K':str(K),'qK':str(qK)})
  assert values[1]-values[0]==(N/D).subs(sub)<0
 results.append(row); print(row,flush=True)
 (root/'partial-results.json').write_text(json.dumps(results,indent=2))
(root/'result.json').write_text(json.dumps({'status':'PASS','case_results':results,'matrix_comparisons':len(matrices),'negative_differences':len(matrices)//2,'matrices':matrices},indent=2)); print('PASS all six cases; 36 matrix comparisons and 18 strict differences',flush=True)
