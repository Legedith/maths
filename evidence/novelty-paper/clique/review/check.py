import sympy as s
import json,sys,hashlib
from pathlib import Path
assert sys.version_info[:3]==(3,12,11)
assert s.__version__=='1.14.0'
rows=[]; z=s.symbols('z'); a=90;b=10;n=a+b
for k in range(2,91):
    sizes=[k,a-k,b] if k<a else [k,b]
    Q=s.Matrix([[s.Rational(k-1,b+k-1),0,s.Rational(b,b+k-1)],[0,0,1],[s.Rational(k,a),s.Rational(a-k,a),0]]) if k<a else s.Matrix([[s.Rational(k-1,b+k-1),s.Rational(b,b+k-1)],[1,0]])
    poly=s.Poly((s.eye(Q.rows)-Q).charpoly(z).as_expr(),z)
    # Nonzero Laplacian eigenvalues reciprocal sum: - coefficient z^2 / coefficient z.
    reciprocal=-poly.nth(2)/poly.nth(1)
    K=reciprocal+s.Rational((k-1)*(b+k-1),b+k)+(b-1)+(a-k-1 if k<a else 0)
    delta=K-s.Rational(197,2)
    corrected=s.Rational(k*(k-1)*(4*a-3*b+2-5*k),2*(2*a*b+k*(k-1))*(b+k))
    assert delta==corrected
    rows.append({'k':k,'K':str(K),'delta':str(delta)})
direct={}
for k in [28,33]:
    A=s.zeros(n)
    for i in range(n):
        for j in range(i):
            if (i>=a)!=(j>=a) or (i<k and j<k): A[i,j]=A[j,i]=1
    d=A*s.ones(n,1);vol=sum(d)
    P=s.diag(*[1/x for x in d])*A
    fundamental=s.eye(n)-P+s.ones(n,1)*(d/vol).T
    K=s.trace(fundamental.inv(method='DM'))-1
    assert K==s.Rational(rows[k-2]['K'])
    direct[str(k)]={'K':str(K),'volume':str(vol)}
best=max(s.Rational(row['delta']) for row in rows)
out={'pass':True,'rows':rows,'maximizers':[row['k'] for row in rows if s.Rational(row['delta'])==best],'direct_full_matrix':direct,'gap':str(s.Rational(rows[26]['delta'])-s.Rational(rows[31]['delta'])),'python':sys.version,'sympy':s.__version__,'code_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest()}
assert out['maximizers']==[28]
with Path('result.json').open('x',encoding='utf-8',newline='\n') as f: json.dump(out,f,sort_keys=True,indent=2);f.write('\n')
print(json.dumps({k:v for k,v in out.items() if k!='rows'},sort_keys=True))
