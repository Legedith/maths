import sympy as s,json
from pathlib import Path
rows=[]
for a,b,c in [(3,3,3),(3,3,4),(3,4,4),(3,4,5),(3,3,7),(4,4,5),(4,5,5)]:
 labs=[0]*a+[1]*b+[2]*c+[3];n=len(labs);A=s.Matrix(n,n,lambda i,j:int(labs[i]!=labs[j]));A[0,n-1]=A[n-1,0]=0
 L=s.diag(*list(A*s.ones(n,1)))-A;J=s.ones(n)/n;Lp=(L+J).inv()-J;trace0=s.trace(Lp);scores={};benefits={}
 for name,(u,v) in {'restore':(0,n-1),'uv':(0,1),'untouched_A':(1,2),'B':(a,a+1),'C':(a+b,a+b+1)}.items():
  X=A.copy();X[u,v]=X[v,u]=1;deg=X*s.ones(n,1);p=deg/sum(deg);P=s.diag(*[1/d for d in deg])*X;Z=(s.eye(n)-P+s.ones(n,1)*p.T).inv();M=s.Matrix(n,n,lambda i,j:(Z[j,j]-Z[i,j])/p[j]);U=sum(M)/n**2
  e=s.zeros(n,1);e[u]=1;e[v]=-1;benefit=((e.T*Lp*Lp*e)[0])/(1+(e.T*Lp*e)[0]);assert U==sum(deg)/n*(trace0-benefit)
  scores[name]=U;benefits[name]=benefit
 best=[k for k,v in scores.items() if v==min(scores.values())];expected=['uv'] if a==b==c else [k for k,v in [('B',b),('C',c)] if v==max(b,c)]
 rows.append({'parts':[a,b,c],'U':{k:str(v) for k,v in scores.items()},'benefits':{k:str(v) for k,v in benefits.items()},'best':best,'H1':bool(scores['uv']<scores['restore']),'H2_or_H3':set(best)==set(expected)})
print(json.dumps(rows,indent=2));Path(__file__).with_name('batch1.json').write_text(json.dumps(rows,indent=2))
