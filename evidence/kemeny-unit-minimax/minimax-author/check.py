from fractions import Fraction as F
from pathlib import Path
import json
p=Path(__file__).resolve().parent
a=b=c=3;n=10;d=7;k=F(27,35);W=F(90+42,100*49);R=W/k;Z=d*(d+2)*k+1
I=(2*k+F(2,d)+R)/Z;lR=1/(n*k);lI=lR/Z
T=F(6,7)+F(3,10)+R;hh=F(9,100)+1/(100*k)
def A(t):return T-I+t*(n*hh-lI)
def B(t):return T-R+t*(n*hh-lR)
lo=F(0);hi=F(21,500);mid=(lo+hi)/2;tau=(I-R)/(lR-lI)
assert lo<tau<mid<hi and B(mid)<A(mid)
RA=A(hi)/B(hi)-1;RB=B(lo)/A(lo)-1
assert A(lo)<B(lo) and B(hi)<A(hi) and RA<RB
out={'parts':[3,3,3],'interval':[str(lo),str(hi)],'midpoint':str(mid),'tau':str(tau),'lines':{'incident':[str(A(0)),str(A(1)-A(0))],'restoration':[str(B(0)),str(B(1)-B(0))]},'midpoint_values':{'incident':str(A(mid)),'restoration':str(B(mid))},'worst_relative_regrets':{'incident':str(RA),'restoration':str(RB)},'products':{'incident':str(A(lo)*A(hi)),'restoration':str(B(lo)*B(hi))},'midpoint_winner':'restoration','minimax_orbit':'incident-u A','status':'PASS'}
(p/'result.json').write_text(json.dumps(out,indent=2)+'\n',encoding='utf-8');print(json.dumps(out))
