import sympy as S,json
from pathlib import Path
a,b,c=3,4,4;n=12;h=11;theta=S.Rational(14,405);labs=[0]*a+[1]*b+[2]*c+[3];adj=S.Matrix(n,n,lambda i,j:int(labs[i]!=labs[j]));adj[0,h]=adj[h,0]=0;deg=adj*S.ones(n,1);m=sum(deg)/2;L=S.diag(*deg)-adj;M=(L+S.ones(n)/n).inv()-S.ones(n)/n;T=S.trace(M)+n*theta*M[h,h];rows=[]
for i in range(n):
 for j in range(i+1,n):
  if adj[i,j]:continue
  z=M[:,i]-M[:,j];r=z[i]-z[j];s=(z.T*z)[0]+n*theta*z[h]**2;A=T-m*s;B=r*T-s;assert B>0
  rad=S.factor(s*(m*r-1)/B);opt=S.factor((S.sqrt(rad)-1)/r) if A<0 else S.Integer(0);value=S.factor((m+opt)*(T-opt*s/(1+r*opt)));unit=S.factor((m+1)*(T-s/(1+r)))
  rows.append({'edge':[i,j],'r':str(r),'s':str(s),'A':str(A),'B':str(B),'radicand':str(rad),'tstar':str(opt),'minimum_scaled':str(value),'unit_minus_baseline_scaled':str(unit-m*T)})
result={'m':str(m),'Ttheta':str(T),'objective_factor':str(2*(1-theta)/n),'baseline_scaled':str(m*T),'rows':rows}
Path(__file__).with_name('result.json').write_text(json.dumps(result,indent=2),encoding='utf-8');print(json.dumps(result,indent=2))
