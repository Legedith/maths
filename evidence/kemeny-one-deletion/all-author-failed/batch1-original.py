import sympy as s,itertools,json
from pathlib import Path
a,b,c=s.symbols('a b c'); x,y,z=s.symbols('x y z')
CASES={'uB':('u','j'),'rB':('r','j'),'BC':('j','k'),'uh':('u','h'),'rh':('r','h'),'Bh':('j','h')}
def quotient(case,e):
    pair=CASES[case]; labels=['u','v']+(['r'] if 'r' in pair else [])+(['j'] if 'j' in pair else [])+(['k'] if 'k' in pair else [])+['A','B','C','h']
    part={'u':0,'v':0,'r':0,'j':1,'k':2,'A':0,'B':1,'C':2,'h':3}
    sizes={q:1 for q in labels};sizes.update(A=a-2-('r' in pair),B=b-('j' in pair),C=c-('k' in pair))
    R=s.zeros(len(labels))
    for i,j in itertools.combinations(range(len(labels)),2):
        q,w=labels[i],labels[j]; edge=part[q]!=part[w]
        if set((q,w))==set(pair):edge=False
        if set((q,w))=={'u','v'}:edge=bool(e)
        if edge:R[i,j]=sizes[w];R[j,i]=sizes[q]
    d=[sum(R.row(i)) for i in range(R.rows)]
    return s.diag(*d)-R,d,labels

def coeff(L,d):
    out=[];m=L.rows
    for k in (1,2):
        v=0
        for omit in itertools.combinations(range(m),k):
            keep=[i for i in range(m) if i not in omit]
            v+=s.prod(d[i] for i in omit)*L.extract(keep,keep).det(method='domain-ge')
        out.append(s.factor(v))
    return out
if __name__=='__main__':
 rows=[]
 for aa,bb,cc in [(3,3,3),(3,4,5),(4,4,6)]:
  for case,pair in CASES.items():
   vals=[]
   for e in (0,1):
    parts=[0]*aa+[1]*bb+[2]*cc+[3];n=len(parts);A=s.zeros(n);ids={'u':0,'v':1,'r':2,'j':aa,'k':aa+bb,'h':n-1}
    for i,j in itertools.combinations(range(n),2):
     if parts[i]!=parts[j]:A[i,j]=A[j,i]=1
    i,j=map(ids.get,pair);A[i,j]=A[j,i]=0
    if e:A[0,1]=A[1,0]=1
    d=A*s.ones(n,1);P=s.diag(*[1/v for v in d])*A;pi=d.T/sum(d)
    K=s.trace((s.eye(n)-P+s.ones(n,1)*pi).inv())-1
    L,dd,labels=quotient(case,e);sub={a:aa,b:bb,c:cc};L=L.subs(sub);dd=[s.sympify(v).subs(sub) for v in dd];q=coeff(L,dd);kq=q[1]/q[0]+n-L.rows
    assert K==kq,(case,aa,bb,cc,e,K,kq)
    vals.append(K)
   delta=vals[1]-vals[0];rows.append({'tuple':[aa,bb,cc],'case':case,'Delta':str(delta),'full_quotient_equal':True});print(rows[-1],flush=True)
   Path('checks.json').write_text(json.dumps(rows,indent=2))
   assert delta<0,('COUNTEREXAMPLE',rows[-1])
 print('PASS 36 full/quotient comparisons and 18 negative differences',flush=True)
