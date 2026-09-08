import json,hashlib
from pathlib import Path
from fractions import Fraction as F
import sympy as S
root=Path('D:/CodexWorkspaces/mathematics-atlas');src=root/'astra-joint-perturb-screen-work';out=Path(__file__).parent
for name,h in {'report.md':'3a62abc44630dfcd56c206ba6e0e517af7d7ccac25c383abd90b48bacc2a900a','result.json':'79e26d6215ab39316658a6480440c2ccc005fbc9bb9df7435628c7c2c91f2171'}.items():assert hashlib.sha256((src/name).read_bytes()).hexdigest()==h
obj=json.loads((src/'result.json').read_text());seen=set();fail=[];direct=[];cache={}
def matrix(n,weights,edge):
 A=S.zeros(n)
 for (i,j),w in weights.items():A[i,j]=A[j,i]=S.Rational(w.numerator,w.denominator)
 i,j=edge;A[i,j]=A[j,i]=1;deg=A*S.ones(n,1);L=S.diag(*deg)-A;G=S.zeros(n);G[:n-1,:n-1]=L[:n-1,:n-1].inv();P=S.eye(n)-S.ones(n)/n;return P*G*P
for row in obj['rows']:
 a,b,c=row['parts'];theta=F(row['theta']);eps=F(row['epsilon']);key=(a,b,c,theta,eps)
 assert (a,b,c) in [(3,3,3),(3,3,4),(3,4,5),(4,4,6)] and theta in [F(1,10),F(1,2)] and eps in [F(1,100),F(1,10)] and key not in seen;seen.add(key)
 n=a+b+c+1;h=n-1;labs=[0]*a+[1]*b+[2]*c+[3];old={(i,j) for i in range(n) for j in range(i+1,n) if labs[i]!=labs[j]}-{(0,h)};missing={(i,j) for i in range(n) for j in range(i+1,n)}-old
 nominal={tuple(r['edge']):F(r['Q']) for r in row['nominal_Q']};vals={tuple(r['edge']):F(r['U']) for r in row['all_missing_U']};assert set(vals)==set(nominal)==missing and len(vals)==len(row['all_missing_U']) and len(nominal)==len(row['nominal_Q'])
 restore=(0,h);assert [e for e,v in nominal.items() if v==min(nominal.values())]==[restore];runner=min((v,e) for e,v in nominal.items() if e!=restore)[1];assert runner==tuple(row['nominal_runner'])
 weights={tuple(r['edge']):F(r['weight']) for r in row['all_old_weights_gradients']};assert set(weights)==old and len(weights)==len(row['all_old_weights_gradients'])
 p=S.ones(n,1)*S.Rational(1-theta.numerator/theta.denominator) if False else S.ones(n,1)*S.Rational((1-theta).numerator,(1-theta).denominator*n);p[h]+=S.Rational(theta.numerator,theta.denominator);C=S.diag(*p)-p*p.T
 ck=(a,b,c,theta)
 if ck not in cache:cache[ck]=[matrix(n,{e:F(1) for e in old},edge) for edge in [restore,runner]]
 MR,MT=cache[ck]
 for rec in row['all_old_weights_gradients']:
  i,j=rec['edge'];zR=MR[:,i]-MR[:,j];zT=MT[:,i]-MT[:,j];g=S.factor((zR.T*C*zR-zT.T*C*zT)[0]);g=F(int(g.p),int(g.q));assert g==F(rec['gradient']);w=F(rec['weight']);assert w==1-eps*((g>0)-(g<0)) and 1-eps<=w<=1+eps
 vol=sum(weights.values());assert vol==F(row['volume_before_insertion']);winners=sorted(e for e,v in vals.items() if v==min(vals.values()));assert winners==[tuple(e) for e in row['new_optimizer_set']]
 bad=any(e!=restore for e in winners);assert bad==row['outside_winner'];gap=(vals[runner]-vals[restore])/(2*(vol+1));oldgap=nominal[runner]-nominal[restore]
 assert gap==F(row['perturbed_Q_gap']) and oldgap==F(row['nominal_Q_gap']) and gap<oldgap and row['target_margin_lowered']
 assert F(row['optimal_U'])==min(vals.values()) and F(row['restore_U'])==vals[restore] and F(row['target_runner_U'])==vals[runner]
 if bad:fail.append(row)
 if key==(3,3,4,F(1,10),F(1,10)):
  for edge in sorted(missing):
   M=matrix(n,weights,edge);u=S.factor(2*S.Rational((vol+1).numerator,(vol+1).denominator)*S.trace(M*C));assert F(int(u.p),int(u.q))==vals[edge];direct.append({'edge':list(edge),'U':str(u)})
assert len(seen)==16 and len(fail)==3 and all(r['theta']=='1/10' and r['epsilon']=='1/10' for r in fail)
assert obj['first_counterexample']==fail[0] and len(direct)==13 and obj['all_target_margins_lowered']
assert obj['summary']=={'1/100':{'cases':8,'outside_failures':0},'1/10':{'cases':8,'outside_failures':3}}
result={'status':'PASS','patterns':16,'gradient_values_independently_checked':True,'summary':obj['summary'],'first_witness_direct_scores':direct}
(out/'adversary-result.json').write_text(json.dumps(result,indent=2),encoding='utf-8');print(json.dumps(result,indent=2))
