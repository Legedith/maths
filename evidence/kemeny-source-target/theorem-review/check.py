import sympy as S
import json
from pathlib import Path
t,theta=S.symbols('t theta',nonnegative=True)
W=S.Matrix([[0,1,t],[1,0,2],[t,2,0]])
d=W*S.ones(3,1);P=S.diag(*[1/x for x in d])*W
H=S.zeros(3)
for q in range(3):
    idx=[i for i in range(3) if i!=q]
    hh=(S.eye(2)-P.extract(idx,idx)).inv()*S.ones(2,1)
    for i,val in zip(idx,hh):H[i,q]=S.cancel(val)
U=S.cancel(sum(H)/9)
expected=[(8*t+22)/(9*t+6),(4*t*t+9*t+4)/(9*t+6),(7*t+10)/(9*t+6)]
rows=[]
for q in range(3):
    F=S.cancel(sum(H[:,q])/3)
    assert S.cancel(F-expected[q])==0
    obj=S.cancel((1-theta)*U+theta*F)
    rows.append({'q':q,'focus':str(F),'objective':str(obj),'curvature':str(S.factor(S.diff(obj,t,2)))})
assert S.cancel(U-(4*t*t+24*t+36)/(27*t+18))==0
obj=(1-theta)*U+theta*expected[1]
assert S.cancel(S.diff(obj,t,2).subs(theta,S.Rational(99,100))+S.Rational(199,225)/(3*t+2)**3)==0
# General quotient derivatives, independent of graph-specific expressions.
a0,a1,a2,r=S.symbols('a0 a1 a2 r')
f=(a0+a1*t+a2*t*t)/(1+r*t)
assert S.cancel(S.diff(f,t)-(a1-r*a0+2*a2*t+r*a2*t*t)/(1+r*t)**2)==0
assert S.cancel(S.diff(f,t,2)-2*(a2-r*a1+r*r*a0)/(1+r*t)**3)==0
result={'status':'PASS','method':'direct transition first-step grounded systems','rows':rows,'general_derivative_identities':2,'concavity_99_100':True}
with Path(__file__).with_name('result.json').open('x',encoding='utf-8',newline='\n') as stream:json.dump(result,stream,indent=2,sort_keys=True);stream.write('\n')
print(json.dumps({'status':'PASS','direct_focus_columns':3}))
