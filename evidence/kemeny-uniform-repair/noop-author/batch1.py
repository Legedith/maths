import sympy as s,json
from pathlib import Path
rows=[]
for a,b,c in [(3,3,3),(3,3,4),(3,4,5),(3,3,7),(4,4,6)]:
 labs=[0]*a+[1]*b+[2]*c+[3];n=len(labs);A=s.Matrix(n,n,lambda i,j:int(labs[i]!=labs[j]));A[0,n-1]=A[n-1,0]=0;degrees=A*s.ones(n,1);m=sum(degrees)/2;L=s.diag(*list(degrees))-A;J=s.ones(n)/n;P=(L+J).inv()-J;T=s.trace(P);out={}
 for name,(i,j) in {'restore':(0,n-1),'uv':(0,1),'untouched_A':(1,2),'B':(a,a+1),'C':(a+b,a+b+1)}.items():
  v=s.zeros(n,1);v[i]=1;v[j]=-1;r=(v.T*P*v)[0];ss=(v.T*P*P*v)[0];diff=s.cancel(2*((m+1)*(T-ss/(1+r))-m*T)/n)
  out[name]={'delta_U':str(diff),'r':str(r),'s':str(ss),'T_minus_ms':str(T-m*ss),'rT_minus_s':str(r*T-ss),'t_upper':str((m*ss-T)/(r*T-ss))}
 rows.append({'parts':[a,b,c],'m':str(m),'T':str(T),'baseline_U':str(2*m*T/n),'orbits':out})
print(json.dumps(rows,indent=2));Path(__file__).with_name('batch1.json').write_text(json.dumps(rows,indent=2))
