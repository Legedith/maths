import sympy as S,json
from pathlib import Path
p=Path(__file__).resolve().parent;t,theta=S.symbols('t theta',nonnegative=True)
L=S.Matrix([[1,-1,0],[-1,3,-2],[0,-2,2]]);n=3;J=S.ones(n)/n;M=(L+J).inv()-J;v=S.Matrix([1,0,-1]);w=S.Matrix([1,0,1]);d=S.Matrix([1,3,2]);m=3;z=M*v;r=(v.T*z)[0];D=1+r*t;Mt=M-t*z*z.T/D;dt=d+t*w
Lt=L+t*v*v.T
rows=[]
for q in range(3):
    ids=[i for i in range(n) if i!=q]
    h=Lt.extract(ids,ids).inv()*dt.extract(ids,[0]);focused=S.cancel(sum(h)/n)
    predicted=S.cancel(2*(m+t)*Mt[q,q]-(Mt*dt)[q]);assert S.cancel(focused-predicted)==0
    uniform=S.cancel(2*(m+t)*S.trace(Mt)/n)
    objective=S.cancel((1-theta)*uniform+theta*focused)
    curvature=S.factor(S.diff(objective,t,2));rows.append({'focus':q,'focused':str(focused),'uniform':str(uniform),'objective':str(objective),'curvature':str(curvature)})
out={'rows':rows,'r':str(r),'z':[str(x) for x in z],'status':'PASS'}
(p/'result.json').write_text(json.dumps(out,indent=2)+'\n',encoding='utf-8');print(json.dumps(out))
