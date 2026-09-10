import sympy as S,json
from pathlib import Path
t=S.symbols('t',positive=True);rows=[]
for name,edges,source in [('star',[(0,1),(1,2),(1,3)],3),('path',[(0,1),(1,2),(2,3)],1)]:
    L=S.zeros(4)
    for i,j in edges:
        L[i,i]+=1;L[j,j]+=1;L[i,j]-=1;L[j,i]-=1
    v=S.Matrix([1,0,-1,0]);Lt=L+t*v*v.T;d=Lt.diagonal().T;hits=[];slopes=[]
    for b in range(4):
        idx=[i for i in range(4) if i!=b]
        h=Lt.extract(idx,idx).inv()*d.extract(idx,[0])
        f=S.Integer(0) if source==b else S.cancel(h[idx.index(source)])
        hits.append(str(f));slopes.append(S.limit(f/t,t,S.oo))
    assert (all(x==0 for x in slopes)) if name=='star' else slopes[3]>0
    rows.append({'graph':name,'edges':edges,'source':source,'pair':[0,2],'hitting':hits,'linear_slopes':list(map(str,slopes))})
with Path(__file__).with_name('result.json').open('x',encoding='utf-8',newline='\n') as f:json.dump(rows,f,indent=2,sort_keys=True);f.write('\n')
print(json.dumps(rows))
