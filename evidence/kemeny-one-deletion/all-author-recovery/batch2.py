import sympy as s,json,subprocess,sys,time,runpy
from pathlib import Path
from batch1 import quotient,coeff,CASES,a,b,c,x,y,z

def symbolic(case):
 q=[]
 for e in (0,1):
  L,d,labels=quotient(case,e);q.append(coeff(L,d));print(case,e,'coefficients complete',flush=True)
 delta=s.cancel(q[1][1]/q[1][0]-q[0][1]/q[0][0]);N,D=s.fraction(delta)
 P=s.Poly(s.expand(-N.subs({a:x+3,b:x+y+3,c:x+z+3})),x,y,z)
 T=s.Poly(s.expand(D.subs({a:x+3,b:x+y+3,c:x+z+3})),x,y,z)
 out={'case':case,'q':[[str(t) for t in row] for row in q],'N':str(N),'D':str(D),'negative_numerator_terms':[[list(m),str(v)] for m,v in P.terms()],'denominator_terms':[[list(m),str(v)] for m,v in T.terms()],'numerator_positive':bool(all(v>0 for v in P.coeffs()) and P.TC()>0),'denominator_positive':bool(all(v>0 for v in T.coeffs()) and T.TC()>0),'numerator_constant':str(P.TC()),'denominator_constant':str(T.TC())}
 Path(case+'.json').write_text(json.dumps(out,indent=2));print(case,'NUMERATOR',out['numerator_positive'],len(P.terms()),'DENOMINATOR',out['denominator_positive'],len(T.terms()),flush=True)
if len(sys.argv)>1:symbolic(sys.argv[1])
else:
 runpy.run_path('batch1.py',run_name='__main__')
 ledger=[]
 for case in CASES:
  try:
   r=subprocess.run([sys.executable,'batch2.py',case],stdout=subprocess.PIPE,stderr=subprocess.STDOUT,text=True,timeout=300)
   Path(case+'.log').write_text(r.stdout);Path(case+'.rc').write_text(str(r.returncode));print(r.stdout,flush=True);ledger.append({'case':case,'rc':r.returncode})
  except subprocess.TimeoutExpired as ex:
   raw=ex.stdout or b'';Path(case+'.log').write_bytes(raw if isinstance(raw,bytes) else raw.encode());Path(case+'.rc').write_text('timeout');ledger.append({'case':case,'rc':'timeout'});print(case,'TIMEOUT',flush=True)
  Path('ledger.json').write_text(json.dumps(ledger,indent=2))

