import sympy as s,json
from pathlib import Path
a,b,c=s.symbols('a b c'); x,y,z=s.symbols('x y z')
r=json.loads(Path('symbolic.json').read_text()); rows=[]
for aa,bb,cc in [(3,3,3),(3,4,5),(4,4,6)]:
    parts=[0]*aa+[1]*bb+[2]*cc+[3]; n=len(parts); kval=[]
    for e in (0,1):
        A=s.zeros(n)
        for i in range(n):
            for j in range(i+1,n):
                if parts[i]!=parts[j]: A[i,j]=A[j,i]=1
        A[0,n-1]=A[n-1,0]=0
        if e:A[0,1]=A[1,0]=1
        d=A*s.ones(n,1); vol=sum(d); P=s.diag(*[1/v for v in d])*A
        pi=d.T/vol
        K=s.trace((s.eye(n)-P+s.ones(n,1)*pi).inv())-1
        q=[s.sympify(t).subs({a:aa,b:bb,c:cc}) for t in r['q'+str(e)]]
        reduced=q[1]/q[0]+n-6
        assert K==reduced
        kval.append(K)
        rows.append({'tuple':[aa,bb,cc],'e':e,'full_K':str(K),'quotient_K_plus_modes':str(reduced),'equal':True})
    delta=kval[1]-kval[0]; assert delta<0
    print((aa,bb,cc),'Delta=',delta,flush=True)
terms=r['negative_N_shift_terms']; poly=sum(s.Integer(v)*x**m[0]*y**m[1]*z**m[2] for m,v in terms)
assert s.expand(poly+s.sympify(r['N']).subs({a:x+3,b:x+y+3,c:x+z+3}))==0
assert all(s.Integer(v)>0 for m,v in terms)
Path('checks.json').write_text(json.dumps({'full_matrix_checks':rows,'certificate_identity':True,'coefficient_positivity':True},indent=2))
print('PASS six full-matrix equalities, three negative deltas, coefficient certificate identity',flush=True)
