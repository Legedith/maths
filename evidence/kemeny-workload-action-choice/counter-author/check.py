import sympy as S,json
from pathlib import Path
a,b,c=S.symbols('a b c',positive=True)
x,y,z=S.symbols('x y z',nonnegative=True)
n=a+b+c+1;d=b+c+1;e=a+b+1
m=a*b+a*c+b*c+a+b+c-1
k=(n-1)*(d-1)/(n*d)
W=(n*(n-1)+d*(d-1))/(n*n*d*d)
T0=(a-1)/d+(b-1)/(a+c+1)+(c-1)/e+3/n
T=T0+W/k;hh=(n-1)/(n*n)+1/(n*n*k)
C=2/(e*(e+2));R=W/k;tau=n*k*C-n*W
cross=(m+1)*C-T-n*hh*tau
simple=C*(m-(n-1)*k)-T0+(n-1)*W
assert S.cancel(cross-simple)==0
slope=(m+1)/(n*k)-n*hh
items={}
for name,expr in [('crossing',simple),('restoration_slope',slope)]:
 num,den=S.fraction(S.cancel(expr))
 print(name,'denominator',S.factor(den),flush=True)
 polynomial=S.Poly(S.expand(num.subs({a:x+3,b:x+y+3,c:x+y+z+3},simultaneous=True)),x,y,z)
 terms=[{'powers':list(powers),'coefficient':str(v)} for powers,v in polynomial.terms()]
 negative=[v for v in terms if S.Rational(v['coefficient'])<0]
 items[name]={'numerator':str(S.expand(num)),'denominator_factored':str(S.factor(den)),'shift':'a=x+3,b=x+y+3,c=x+y+z+3','terms':terms,'constant':str(polynomial.coeff_monomial(1)),'negative_terms':negative,'coefficient_certificate_pass':not negative and polynomial.coeff_monomial(1)>0}
 print(name,'terms',len(terms),'negative',len(negative),'constant',polynomial.coeff_monomial(1),flush=True)
result={'identities':'PASS','certificates':items,'status':'PASS' if all(v['coefficient_certificate_pass'] for v in items.values()) else 'coefficient_obstruction'}
def default(v):return bool(v) if v in [S.true,S.false] else str(v)
Path(__file__).with_name('result.json').write_text(json.dumps(result,indent=2,default=default),encoding='utf-8')
