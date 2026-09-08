import sympy as S,json
from pathlib import Path
p=Path(__file__).parent
old=json.loads((p/'result.json').read_text(encoding='utf-8'))
a,b,c=S.symbols('a b c',positive=True);x,y,z=S.symbols('x y z',nonnegative=True)
n=a+b+c+1;d=b+c+1;e=a+b+1;m=a*b+a*c+b*c+a+b+c-1
k=(n-1)*(d-1)/(n*d);W=(n*(n-1)+d*(d-1))/(n*n*d*d)
den=e*(e+2)*(a+c+1)*d*d*n*n
terms=[2*m/(e*(e+2)),-2*(n-1)*k/(e*(e+2)),-(a-1)/d,-(b-1)/(a+c+1),-(c-1)/e,-3/n,(n-1)*W]
def common_numerator(parts,D):
 dp=S.Poly(D,a,b,c);total=S.Poly(0,a,b,c)
 for term in parts:
  N,Q=S.fraction(term)
  total+=S.Poly(N,a,b,c)*dp.exquo(S.Poly(Q,a,b,c))
 return total.as_expr()
numerator=common_numerator(terms,den)
local={'a':a,'b':b,'c':c}
assert S.Poly(numerator-S.sympify(old['certificates']['crossing']['numerator'],locals=local),a,b,c).is_zero
assert S.Poly(den-S.sympify(old['certificates']['crossing']['denominator_factored'],locals=local),a,b,c).is_zero
# Formal exact cancellation independent of the large substitution.
N,K,V,M,T=S.symbols('N K V M T',nonzero=True);C=S.symbols('C');hh=(N-1)/N**2+1/(N**2*K)
assert S.cancel((M+1)*C-(T+V/K)-N*hh*(N*K*C-N*V)-(C*(M-(N-1)*K)-T+(N-1)*V))==0
sden=(b+c)*(a+b+c)*n
snum=common_numerator([(m+1)/(n*k),-(n-1)/n,-1/(n*k)],sden)
assert S.Poly(snum-S.sympify(old['certificates']['restoration_slope']['numerator'],locals=local),a,b,c).is_zero
out={}
for name,poly,sub in [('cross_b_equal_a',numerator,{a:x+3,b:x+3,c:x+4+z}),('cross_b_greater_a',numerator,{a:x+3,b:x+4+y,c:x+4+y+z}),('restoration_slope',snum,{a:x+3,b:x+3+y,c:x+3+y+z})]:
 q=S.Poly(poly.subs(sub,simultaneous=True),x,y,z)
 coeffs=[{'powers':list(ex),'coefficient':str(v)} for ex,v in q.terms()]
 assert all(v>0 for ex,v in q.terms()) and q.coeff_monomial(1)>0,name
 out[name]={'terms':coeffs,'constant':str(q.coeff_monomial(1)),'term_count':len(coeffs)}
 print(name,len(coeffs),q.coeff_monomial(1),flush=True)
result={'status':'PASS','formal_crossing_identity':True,'intermediate_numerators_independently_reconstructed':True,'denominator_crossing':str(S.factor(den)),'denominator_slope':str(S.factor(sden)),'certificates':out}
(p/'batch2.json').write_text(json.dumps(result,indent=2),encoding='utf-8')
