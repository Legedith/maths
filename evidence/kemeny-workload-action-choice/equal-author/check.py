from fractions import Fraction as F
import json
from pathlib import Path
rows=[]
for a,b,c in [(3,3,3),(3,3,4),(3,3,100)]:
 n=a+b+c+1;d=n-a;m=a*b+a*c+b*c+a+b+c-1;k=F((n-1)*(d-1),n*d);W=F(n*(n-1)+d*(d-1),n*n*d*d);R=W/k;Z=d*(d+2)*k+1;T=sum(F(q-1,n-q) for q in [a,b,c])+F(3,n)+R;hh=F(n-1,n*n)+1/(n*n*k)
 lines={'restore':(R/n,1/(n*n*k)),'uv':((2*k+F(2,d)+R)/(n*Z),1/(n*n*k*Z)),'untouched_A':(F(2,n*d*(d+2)),F(0)),'B':(F(2,n*(n-b)*(n-b+2)),F(0)),'C':(F(2,n*(n-c)*(n-c+2)),F(0))}
 for th in [F(0),F(1,10),F(1,2),F(9,10)]:
  base=2*m*(1-th)*(T/n+th*hh);values={e:2*(m+1)*(1-th)*(T/n+th*hh-A-th*B) for e,(A,B) in lines.items()};best=min(values.values());rows.append({'parts':[a,b,c],'theta':str(th),'baseline':str(base),'candidate_U':{e:str(v) for e,v in values.items()},'best_edges_orbits':[e for e,v in values.items() if v==best],'improvement':str(base-best),'restore_improves':values['restore']<base,'best_improves':best<base})
Path(__file__).with_name('result.json').write_text(json.dumps({'rows':rows},indent=2),encoding='utf-8');print(json.dumps(rows,indent=2))
