from fractions import Fraction as F
from pathlib import Path
import json
p=Path(__file__).resolve().parent
a,b,c=3,3,4;n=11;d=8;e=7;t=F(16)
k=F(70,88);W=F(n*(n-1)+d*(d-1),n*n*d*d)
D=d*d*k+t*(2*d*k+1)
I=(2*k+F(2,d)+W/k)/D;lam=1/(n*k*D);C=F(2,e*(e+2*t))
sigma=(C-I)/lam;theta=(sigma+1)/2
assert 0<sigma<theta<1 and C-I-lam<0
scores={'incident_A':I+theta*lam,'untouched_A':F(2,d*(d+2*t)),'B':F(2,d*(d+2*t)),'C':C}
assert scores['incident_A']>max(scores[k] for k in ('untouched_A','B','C'))
out={'parts':[a,b,c],'t':str(t),'sigma':str(sigma),'theta':str(theta),'endpoint_gap':str(C-I-lam),'scores':{k:str(v) for k,v in scores.items()},'incident_minus_C':str(scores['incident_A']-C),'optimal_edges':[[0,1],[0,2]],'restoration_forbidden':True,'status':'counterexample_verified'}
(p/'batch2.json').write_text(json.dumps(out,indent=2)+'\n',encoding='utf-8');print(json.dumps(out))
