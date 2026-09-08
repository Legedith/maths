from fractions import Fraction as F
from pathlib import Path
import sympy as s,json,sys
def inverse(adj):
 n=adj.rows;L=s.diag(*list(adj*s.ones(n,1)))-adj;J=s.ones(n)/n;X=(L+J).inv()-J
 return [[F(int(X[i,j].p),int(X[i,j].q)) for j in range(n)] for i in range(n)]
dot=lambda x,y:sum((a*b for a,b in zip(x,y)),F(0))
def update(M,e):
 i,j=e;n=len(M);z=[M[k][i]-M[k][j] for k in range(n)];r=z[i]-z[j]
 return [[M[k][l]-z[k]*z[l]/(1+r) for l in range(n)] for k in range(n)]
def Q(M,theta):return (1-theta)*(sum(M[i][i] for i in range(len(M)))/len(M)+theta*M[-1][-1])
def sval(M,e,theta):
 i,j=e;z=[row[i]-row[j] for row in M];return (1-theta)*(dot(z,z)/len(M)+theta*z[-1]**2)
rows=[]
for a,b,c in [(3,3,3),(3,3,4),(3,4,5),(4,4,6)]:
 labs=[0]*a+[1]*b+[2]*c+[3];n=len(labs);h=n-1;restore=(0,h)
 adj=s.Matrix(n,n,lambda i,j:int(labs[i]!=labs[j]));adj[0,h]=adj[h,0]=0
 old=[(i,j) for i in range(n) for j in range(i+1,n) if adj[i,j]];missing=[(i,j) for i in range(n) for j in range(i+1,n) if not adj[i,j]]
 M=inverse(adj);post={e:update(M,e) for e in missing}
 for theta in [F(1,10),F(1,2)]:
  nominal={e:Q(X,theta) for e,X in post.items()};minimum=min(nominal.values())
  assert [e for e,v in nominal.items() if v==minimum]==[restore]
  runner=min((v,e) for e,v in nominal.items() if e!=restore)[1]
  gradients={f:-sval(post[runner],f,theta)+sval(post[restore],f,theta) for f in old}
  for eps in [F(1,100),F(1,10)]:
   weights={f:1-eps*((g>0)-(g<0)) for f,g in gradients.items()}
   X=adj.copy()
   for (i,j),w in weights.items():X[i,j]=X[j,i]=s.Rational(w.numerator,w.denominator)
   Mp=inverse(X);vol=sum(weights.values());values={e:2*(vol+1)*Q(update(Mp,e),theta) for e in missing}
   best=min(values.values());winners=[e for e,v in values.items() if v==best]
   gap=(values[runner]-values[restore])/(2*(vol+1));oldgap=nominal[runner]-nominal[restore]
   rows.append({'parts':[a,b,c],'theta':str(theta),'epsilon':str(eps),'restore':list(restore),'nominal_runner':list(runner),'nominal_Q_gap':str(oldgap),'perturbed_Q_gap':str(gap),'target_margin_lowered':gap<oldgap,'outside_winner':any(e!=restore for e in winners),'new_optimizer_set':[list(e) for e in winners],'optimal_U':str(best),'restore_U':str(values[restore]),'target_runner_U':str(values[runner]),'volume_before_insertion':str(vol),'all_old_weights_gradients':[{'edge':list(e),'weight':str(weights[e]),'gradient':str(gradients[e])} for e in old],'all_missing_U':[{'edge':list(e),'U':str(v)} for e,v in values.items()],'nominal_Q':[{'edge':list(e),'Q':str(v)} for e,v in nominal.items()]})
bad=[row for row in rows if row['outside_winner']]
summary={str(e):{'cases':sum(r['epsilon']==str(e) for r in rows),'outside_failures':sum(r['epsilon']==str(e) and r['outside_winner'] for r in rows)} for e in [F(1,100),F(1,10)]}
out={'rows':rows,'summary':summary,'all_target_margins_lowered':all(r['target_margin_lowered'] for r in rows),'first_counterexample':bad[0] if bad else None,'python':sys.version,'sympy':s.__version__}
Path(__file__).with_name('result.json').write_text(json.dumps(out,indent=2),encoding='utf-8')
print(json.dumps({'summary':summary,'all_target_margins_lowered':out['all_target_margins_lowered'],'first_counterexample':bad[0] if bad else None},indent=2))

