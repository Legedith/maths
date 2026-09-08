import sympy as s,itertools,json,time
from pathlib import Path
a,b,c=s.symbols('a b c'); x,y,z=s.symbols('x y z'); n=a+b+c+1
# Cells identify original parts, singleton u and h, and optional inserted pair.
def quotient_K(name):
 if name in ('restore','uv'):
  sizes=[1,1,a-2,b,c,1];parts=[0,0,0,1,2,3];pair=None;u=0;h=5
 else:
  sizes=[1,2,a-3,b,c,1] if name=='untouched_A' else [1,a-1,2,b-2,c,1]
  parts=[0,0,0,1,2,3] if name=='untouched_A' else [0,0,1,1,2,3]
  pair=1 if name=='untouched_A' else 2;u=0;h=5
 R=s.Matrix(6,6,lambda i,j: sizes[j] if parts[i]!=parts[j] else 0)
 if name!='restore':R[u,h]=R[h,u]=0
 if name=='uv': R[0,1]=R[1,0]=1
 if pair is not None:R[pair,pair]=1
 d=list(R*s.ones(6,1));L=s.diag(*d)-R
 coeff=[]
 for k in (1,2):
  terms=[]
  for S in itertools.combinations(range(6),k):
   J=[i for i in range(6) if i not in S]
   terms.append(s.prod(d[i] for i in S)*L.extract(J,J).det(method='domain-ge'))
  coeff.append(s.factor(sum(terms)))
 value=n-6+coeff[1]/coeff[0]
 if pair is not None:value-=1/(d[pair]+1)
 return s.cancel(value)
vals={}
for name in ['restore','uv','untouched_A','B']:
 vals[name]=quotient_K(name);print('computed',name,flush=True)
vals['C']=vals['B'].subs({b:c,c:b},simultaneous=True)
prior=json.loads(Path(__file__).with_name('batch1.json').read_text())
for row in prior[:2]:
 sub=dict(zip((a,b,c),row['parts']))
 for key in ('uv','untouched_A','B','C'):
  assert s.cancel((vals[key]-vals['restore']).subs(sub))==s.Rational(row['deltas'][key])-s.Rational(row['deltas']['restore'])
results={}
for left,right in [('uv','restore'),('untouched_A','restore'),('B','restore'),('C','restore'),('uv','untouched_A')]:
 diff=s.factor(vals[left]-vals[right]);num,den=s.fraction(diff)
 pp=s.Poly(s.expand(num.subs({a:3+x,b:3+x+y,c:3+x+z})),x,y,z)
 qq=s.Poly(s.expand(den.subs({a:3+x,b:3+x+y,c:3+x+z})),x,y,z)
 results[left+' minus '+right]={'difference':str(diff),'numerator_terms':len(pp.terms()),'numerator_min':str(min(pp.coeffs())),'numerator_constant':str(pp.coeff_monomial(1)),'denominator_min':str(min(qq.coeffs())),'denominator_constant':str(qq.coeff_monomial(1)),'positive_coefficients':all(v>0 for v in pp.coeffs()) and all(v>0 for v in qq.coeffs()),'numerator_certificate':[[list(e),str(v)] for e,v in pp.terms()],'denominator_certificate':[[list(e),str(v)] for e,v in qq.terms()]}
 print(left,right,results[left+' minus '+right]['positive_coefficients'],len(pp.terms()),flush=True)
Path(__file__).with_name('batch2.json').write_text(json.dumps({'values':{k:str(v) for k,v in vals.items()},'comparisons':results},indent=2))
