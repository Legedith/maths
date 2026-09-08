import sympy as s,json
from pathlib import Path
def K(A):
 d=A*s.ones(A.rows,1); T=s.diag(*[1/z for z in d])*A
 return s.trace((s.eye(A.rows)-T+s.ones(A.rows,1)*d.T/sum(d)).inv())-1
rows=[]
for a,b,c in [(3,3,3),(3,4,5),(4,4,6),(3,3,7),(4,5,5)]:
 labs=[0]*a+[1]*b+[2]*c+[3]; n=len(labs)
 A=s.Matrix(n,n,lambda i,j:int(labs[i]!=labs[j])); A[0,n-1]=A[n-1,0]=0
 base=K(A); out={}
 for name,(u,v) in {'restore':(0,n-1),'uv':(0,1),'untouched_A':(1,2),'B':(a,a+1),'C':(a+b,a+b+1)}.items():
  X=A.copy();X[u,v]=X[v,u]=1;out[name]=K(X)-base
 rows.append({'parts':[a,b,c],'deltas':{k:str(v) for k,v in out.items()},'order':sorted(out,key=out.get),'H1':out['restore']==min(out.values()),'H2':bool(out['untouched_A']<out['uv']),'H3':out['uv']==min(v for k,v in out.items() if k!='restore')})
print(json.dumps(rows,indent=2))
Path(__file__).with_name('batch1.json').write_text(json.dumps(rows,indent=2))

