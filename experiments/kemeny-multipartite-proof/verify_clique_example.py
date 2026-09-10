"""Portable exact replay of the independently audited K90,10 example correction."""
from fractions import Fraction as F
from pathlib import Path
import argparse,json,hashlib,sys

def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
parser=argparse.ArgumentParser(description="Exact K90,10 clique-size correction certificate")
parser.add_argument('--output',type=Path,required=True)
args=parser.parse_args()
args.output.parent.mkdir(parents=True,exist_ok=True)
assert sys.version_info[:3]==(3,12,11)
a,b=90,10;base=F(197,2);rows=[]
for k in range(2,91):
 d=b+k-1
 if k<a:
  Q=[[F(k-1,d),F(0),F(b,d)],[F(0),F(0),F(1)],[F(k,a),F(a-k,a),F(0)]]
  M=[[F(i==j)-Q[i][j] for j in range(3)] for i in range(3)]
  c=sum(M[i][i] for i in range(3));prod=sum(M[i][i]*M[j][j]-M[i][j]*M[j][i] for i in range(3) for j in range(i+1,3))
  quotient=c/prod;zeros=(a-k-1)+(b-1)
 else:
  Q=[[F(k-1,d),F(b,d)],[F(1),F(0)]]
  quotient=1/(2-Q[0][0]-Q[1][1]);zeros=b-1
 assert all(sum(row)==1 for row in Q)
 modes=F((k-1)*d,d+1)+zeros
 kval=quotient+modes;delta=kval-base
 th35=F(k*(k-1),2*a*b+k*(k-1))*(F(4*a-3,2)-F(2*a*b*(k-1),k*b))-F(k-1,b+k)
 corrected=F(k*(k-1)*(4*a-3*b+2-5*k),2*(k*(k-1)+2*a*b)*(b+k))
 printed=F(k*(k-1)*(4*a-3*b+2-5*k),2*(k*(k-1)+2*a*b)*(a+b+k-1))
 assert delta==th35==corrected
 rows.append({'k':k,'Q':[[str(x) for x in row] for row in Q],'quotient_contribution':str(quotient),'omitted_contribution':str(modes),'K':str(kval),'delta':str(delta),'theorem35':str(th35),'corrected':str(corrected),'printed':str(printed),'printed_matches':printed==delta})
best=max(F(row['delta']) for row in rows);bestprinted=max(F(row['printed']) for row in rows)
result={'status':'pass','count':89,'rows':rows,'maximizers':[r['k'] for r in rows if F(r['delta'])==best],'max_delta':str(best),'printed_maximizers':[r['k'] for r in rows if F(r['printed'])==bestprinted],'delta28_minus_delta33':str(F(rows[26]['delta'])-F(rows[31]['delta'])),'printed_mismatch_count':sum(not r['printed_matches'] for r in rows),'python':sys.version,'code_sha256':sha(Path(__file__))}
with args.output.open('x',encoding='utf-8',newline='\n') as f:json.dump(result,f,indent=2,sort_keys=True);f.write('\n')
print(json.dumps({k:v for k,v in result.items() if k not in ['rows','input_hashes']},sort_keys=True))
