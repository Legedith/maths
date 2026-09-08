from pathlib import Path
import sympy as s,json,sys
p=Path(__file__).parent;row=json.loads((p/'result.json').read_text(encoding='utf-8'))['first_counterexample'];a,b,c=row['parts'];n=a+b+c+1
base=s.zeros(n)
for w in row['all_old_weights_gradients']:
 i,j=w['edge'];base[i,j]=base[j,i]=s.Rational(w['weight'])
theta=s.Rational(row['theta']);law=s.ones(n,1)*(1-theta)/n;law[n-1]+=theta
actual=[]
for rec in row['all_missing_U']:
 i,j=rec['edge'];adj=base.copy();adj[i,j]=adj[j,i]=1;deg=adj*s.ones(n,1);pi=deg/sum(deg);P=s.diag(*[1/v for v in deg])*adj;Z=(s.eye(n)-P+s.ones(n,1)*pi.T).inv()
 H=s.Matrix(n,n,lambda i,j:(Z[j,j]-Z[i,j])/pi[j]);U=(law.T*H*law)[0]
 assert U==s.Rational(rec['U']);actual.append({'edge':rec['edge'],'U':str(U)})
best=min(s.Rational(v['U']) for v in actual);winners=[v['edge'] for v in actual if s.Rational(v['U'])==best]
assert winners==row['new_optimizer_set']
out={'parts':row['parts'],'theta':row['theta'],'epsilon':row['epsilon'],'all_direct_hitting_U':actual,'winners':winners,'match':True,'python':sys.version,'sympy':s.__version__}
(p/'direct-result.json').write_text(json.dumps(out,indent=2),encoding='utf-8');print(json.dumps(out,indent=2))

