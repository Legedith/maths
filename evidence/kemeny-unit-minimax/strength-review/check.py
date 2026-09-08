from pathlib import Path
import sympy as S,json,hashlib
p=Path(__file__).parent;src=p.parent/'astra-forbidden-strength-work'
for name,hsh in {'proposal.md':'60459628123dedb3f4300c083ed6dcd4a79ca6f1cd1a9506a02fa409d375f68c','batch2.json':'2dcbe58de0ac5e384c4140a6f1379270ff9d1adfb1b69753b6c3340147e73a17'}.items():assert hashlib.sha256((src/name).read_bytes()).hexdigest()==hsh
old=json.loads((src/'batch2.json').read_text());n=11;hub=10;t=S.Integer(16);theta=S.Rational(9147,9152);labels=[0]*3+[1]*3+[2]*4+[3];A=S.Matrix(n,n,lambda i,j:int(labels[i]!=labels[j]));A[0,hub]=A[hub,0]=0;center=S.eye(n)-S.ones(n)/n
prob=S.ones(n,1)*(1-theta)/n;prob[hub]+=theta;cov=S.diag(*prob)-prob*prob.T
m=sum(A)/2


def inv(adj):
 deg=adj*S.ones(n,1);L=S.diag(*deg)-adj;G=S.zeros(n);G[:hub,:hub]=L[:hub,:hub].inv();M=center*G*center;assert L*M==center;return M
M=inv(A);T=S.trace(M)+n*theta*M[hub,hub];factor=2*(m+t)*t*(1-theta)/n;assert 0<theta<1 and factor>0
rows=[]
for i in range(n):
 for j in range(i+1,n):
  if A[i,j] or (i,j)==(0,hub):continue
  B=A.copy();B[i,j]=B[j,i]=t;N=inv(B);U=S.factor(2*(m+t)*S.trace(N*cov));score=S.factor((T-(S.trace(N)+n*theta*N[hub,hub]))/t)
  name='incident_A' if i==0 else 'untouched_A' if i<3 else 'B' if i<6 else 'C';assert score==S.Rational(old['scores'][name])
  rows.append({'edge':[i,j],'class':name,'score':str(score),'U':str(U)})
assert len(rows)==12;best=min(S.Rational(r['U']) for r in rows);winners=[r['edge'] for r in rows if S.Rational(r['U'])==best];assert winners==old['optimal_edges']
uI=S.Rational(rows[0]['U']);uC=next(S.Rational(r['U']) for r in rows if r['class']=='C');assert S.factor((uC-uI)/factor)==S.Rational(1,4333056)
result={'status':'PASS','m':str(m),'final_volume':str(m+t),'positive_score_to_U_factor':str(factor),'winners':winners,'C_minus_incident_U':str(uC-uI),'rows':rows}
(p/'result.json').write_text(json.dumps(result,indent=2),encoding='utf-8');print(json.dumps(result,indent=2))
