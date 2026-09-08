from fractions import Fraction as F
from itertools import combinations_with_replacement
import json, sympy as s
from pathlib import Path
out=Path(__file__).parent

def delta(q,x):
 n=sum(q); a=n-x; g=sum(k*(n-k) for k in q); h=sum(k*(n-k)**2 for k in q); t=g-x*a
 return 2*( -F(g,2*a)+F(x-2,2)+F(h-x*a*a,g*n)+F((x-2)*t,2*g)+F((n-2)*t*t,2*g*n*a)+F(g-a,a*(a+2)))/(g+2)
rows=[]; bad1=[]; bad2=[]
for q in combinations_with_replacement(range(3,15),3):
 for p in range(1,11):
  ds=[delta(q+(1,)*p,x) for x in q]
  if any(ds[i]>ds[i+1] or (q[i]<q[i+1] and ds[i]==ds[i+1]) for i in range(2)): bad1.append([q,p,list(map(str,ds))])
  nxt=delta(q+(1,)*(p+1),q[0])
  if nxt>=ds[0]: bad2.append([q,p,str(ds[0]),str(nxt)])
  rows.append([q,p,list(map(str,ds)),str(nxt)])
n,g,h,x,y=s.symbols('n g h x y'); a=n-x; t=g-x*a
B=-g/(2*a)+(x-2)/2+(h-x*a*a)/(g*n)+(x-2)*t/(2*g)+(n-2)*t*t/(2*g*n*a)+(g-a)/(a*(a+2))
expr=s.factor(B); diff=s.factor((B-B.subs(x,y))/(x-y))
report={'grid_cases':len(rows),'H1_counterexamples':bad1,'H2_counterexample_count':len(bad2),'H2_first':bad2[:5],'B_simplified':str(expr),'divided_difference':str(diff)}
(out/'batch1-raw.json').write_text(json.dumps(rows)); (out/'batch1-result.json').write_text(json.dumps(report,indent=2)); print(json.dumps(report,indent=2))
