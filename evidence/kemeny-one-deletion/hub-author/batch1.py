import sympy as s, itertools,json,time
from pathlib import Path
a,b,c=s.symbols('a b c'); x,y,z=s.symbols('x y z')
n=[1,1,a-2,b,c,1]
def coeff(e):
    adj=s.zeros(6)
    for i,j in itertools.combinations(range(6),2):
        edge=(i<3 and j in (3,4,5)) or (i,j) in [(3,4),(3,5),(4,5)]
        if (i,j)==(0,5): edge=False
        if (i,j)==(0,1): edge=bool(e)
        if edge: adj[i,j]=n[j];adj[j,i]=n[i]
    d=[sum(adj.row(i)) for i in range(6)]
    L=s.diag(*d)-adj
    out=[]
    for k in (1,2):
        v=0
        for omitted in itertools.combinations(range(6),k):
            keep=[i for i in range(6) if i not in omitted]
            v+=s.prod(d[i] for i in omitted)*L.extract(keep,keep).det(method='domain-ge')
        out.append(s.factor(v))
    return out
q0=coeff(0);q1=coeff(1)
print('q0',q0,flush=True);print('q1',q1,flush=True)
N=s.factor(q1[1]*q0[0]-q0[1]*q1[0]); print('N=',N,flush=True)
P=s.Poly(s.expand(-N.subs({a:x+3,b:x+y+3,c:x+z+3})),x,y,z)
terms=P.terms(); summary={'terms':len(terms),'min_coefficient':str(min(P.coeffs())),'constant':str(P.TC()),'all_positive':all(v>0 for v in P.coeffs()),'degree':P.total_degree()}
Path('symbolic.json').write_text(json.dumps({'q0':list(map(str,q0)),'q1':list(map(str,q1)),'N':str(N),'summary':summary,'negative_N_shift_terms':[[list(m),str(v)] for m,v in terms]},indent=2))
print(summary,flush=True)
