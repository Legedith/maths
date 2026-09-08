import sympy as s,json
from pathlib import Path
a,b,c,x,y,z=s.symbols('a b c x y z');n=a+b+c+1;d=n-a;k=(n-1)*(d-1)/(n*d);W=(n*(n-1)+d*(d-1))/(n*n*d*d)
rs={'restore':((1-k)/k,W/k**2),'uv':(2/d+1/(d*d*k),2/d**2+2/(d**3*k)+W/(d*d*k*k)),'untouched_A':(2/d,2/d**2),'B':(2/(n-b),2/(n-b)**2),'C':(2/(n-c),2/(n-c)**2)}
for row in json.loads(Path('D:/CodexWorkspaces/mathematics-atlas/astra-uniform-noop-work/batch1.json').read_text()):
 sub=dict(zip((a,b,c),row['parts']))
 for name,(r,ss) in rs.items():assert s.cancel(r.subs(sub))==s.Rational(row['orbits'][name]['r']);assert s.cancel(ss.subs(sub))==s.Rational(row['orbits'][name]['s'])
out={}
for i,j,sub in [('uv','restore',{a:3+x,b:3+x+y,c:3+x+z}),('uv','untouched_A',{a:3+x,b:3+x+y,c:3+x+z}),('B','uv',{a:3+x,b:4+x+y,c:3+x+z})]:
 ri,si=rs[i];rj,sj=rs[j]
 for mode,expr in [('intercept',si-sj),('slope',si*rj-sj*ri)]:
  expr=s.factor(expr);num,den=s.fraction(expr);pp=s.Poly(s.expand(num.subs(sub)),x,y,z);qq=s.Poly(s.expand(den.subs(sub)),x,y,z)
  out[i+'>'+j+':'+mode]={'expr':str(expr),'num_count':len(pp.terms()),'num_min':str(min(pp.coeffs())),'num_constant':str(pp.coeff_monomial(1)),'den_min':str(min(qq.coeffs())),'den_constant':str(qq.coeff_monomial(1)),'positive':all(v>0 for v in pp.coeffs()) and all(v>0 for v in qq.coeffs()),'num_terms':[[list(e),str(v)] for e,v in pp.terms()],'den_terms':[[list(e),str(v)] for e,v in qq.terms()]}
  print(i,j,mode,out[i+'>'+j+':'+mode]['positive'],len(pp.terms()),flush=True)
# Full weighted hitting matrices, independent of scalar r/s derivation.
labs=[0]*4+[1]*4+[2]*6+[3];nn=len(labs);A=s.Matrix(nn,nn,lambda i,j:int(labs[i]!=labs[j]));A[0,nn-1]=A[nn-1,0]=0;deg=A*s.ones(nn,1);m=sum(deg)/2;LL=s.diag(*list(deg))-A;J=s.ones(nn)/nn;T=s.trace((LL+J).inv()-J);checks=[]
for t in map(s.Rational,['1/10','12','100']):
 scores={}
 for name,(i,j) in {'restore':(0,nn-1),'uv':(0,1),'untouched_A':(1,2),'B':(4,5),'C':(8,9)}.items():
  X=A.copy();X[i,j]=X[j,i]=t;dd=X*s.ones(nn,1);pi=dd/sum(dd);P=s.diag(*[1/v for v in dd])*X;Z=(s.eye(nn)-P+s.ones(nn,1)*pi.T).inv();M=s.Matrix(nn,nn,lambda i,j:(Z[j,j]-Z[i,j])/pi[j]);U=sum(M)/nn**2
  r,ss=[s.cancel(v.subs({a:4,b:4,c:6})) for v in rs[name]];assert U==2*(m+t)/nn*(T-t*ss/(1+t*r));scores[name]=U
 checks.append({'t':str(t),'U':{j:str(v) for j,v in scores.items()},'best':[j for j,v in scores.items() if v==min(scores.values())]})
Path(__file__).with_name('batch2.json').write_text(json.dumps({'comparisons':out,'weighted_matrix_checks':checks},indent=2))
