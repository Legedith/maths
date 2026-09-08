import sympy as S,json,hashlib
from fractions import Fraction as F
from itertools import combinations,product
from pathlib import Path
p=Path('D:/CodexWorkspaces/mathematics-atlas/kemeny-robustness-work')
def read(q):return json.loads(q.read_text(encoding='utf-8-sig'))
for name,expected in [('proposal.md','e905e3501e6ce7f6faddf2ee08770a4db5c4d58a125f1048bfb9a3e38c0b03b5'),('check.py','c6ca55ac065e8ed75ff16680dfddea2a3d32e4e0054fe2ee7836bfe2bbe83625'),('result.json','13d3f0af59ccae1e848fe2c1c79d87cca1539b3e304fc6c8d3994ab0af5b09e0')]:assert hashlib.sha256((p/name).read_bytes()).hexdigest()==expected
manifest=read(p/'hashes.json')
for x in manifest:assert hashlib.sha256((p/x['path']).read_bytes()).hexdigest()==x['sha256'];assert (p/x['path']).stat().st_size==x['bytes']
old=read(p/'result.json');assert old['interval']==['-1/10','1/10'];assert old['continuous_contexts']==96 and old['comparison_count']==3896 and not old['failing_comparisons']
records={(tuple(r['parts']),F(r['theta']),r['old_edge_type']):r for r in old['records']};assert len(records)==len(old['records'])==96
count=interior=matrices=diagnostics=0;d=F(1,10);summary=[]
for a,b,c in [(3,3,3),(3,3,4),(3,4,5),(4,4,6)]:
 n=a+b+c+1;labs=[0]*a+[1]*b+[2]*c+[3];h=n-1
 edges={ij for ij in combinations(range(n),2) if labs[ij[0]]!=labs[ij[1]]}-{(0,h)}
 missing=sorted(set(combinations(range(n),2))-edges);L=S.zeros(n)
 for i,j in edges:L[i,i]+=1;L[j,j]+=1;L[i,j]-=1;L[j,i]-=1
 J=S.ones(n)/n;data={};laps={}
 for e in missing:
  v=S.eye(n)[:,e[0]]-S.eye(n)[:,e[1]];Le=L+v*v.T;P=(Le+J).inv()-J
  assert Le*P==S.eye(n)-J
  data[e]=[[F(x) for x in P.row(i)] for i in range(n)];laps[e]=Le;matrices+=1
 reps={'u-B':(0,a),'u-C':(0,a+b),'Aother-B':(1,a),'Aother-C':(1,a+b),'B-C':(a,a+b),'h-Aother':(1,h),'h-B':(a,h),'h-C':(a+b,h)}
 # Every existing edge is in one of these classes; class cardinalities sum to m.
 sizes=[b,c,(a-1)*b,(a-1)*c,b*c,a-1,b,c];assert sum(sizes)==len(edges);assert set(reps.values())<=edges
 for theta in [F(0),F(1,10),F(1,2)]:
  T={e:sum(M[i][i] for i in range(n))+n*theta*M[h][h] for e,M in data.items()};O={e for e,t in T.items() if t==min(T.values())};outside=set(missing)-O
  expected={(0,j) for j in range(1,a)} if theta==0 and a==b==c else set(combinations(range(a+b,h),2)) if theta==0 else {(0,h)}
  assert O==expected
  for typ,f in reps.items():
   record=records[( (a,b,c),theta,typ)];assert record['n']==n and record['m']==len(edges) and record['old_edge']==list(f);assert record['all_missing_edges']==[list(e) for e in missing];assert set(map(tuple,record['nominal_optimal_set']))==O
   stat={}
   for e,M in data.items():
    z=[row[f[0]]-row[f[1]] for row in M];r=z[f[0]]-z[f[1]];s=sum(x*x for x in z)+n*theta*z[h]*z[h];assert 0<r<=1 and s>0;stat[e]=(T[e],r,s)
   certs={(tuple(z['incumbent']),tuple(z['outsider'])):z for z in record['comparisons']};assert len(certs)==len(record['comparisons'])==len(O)*len(outside);assert set(certs)==set(product(O,outside))
   for (i,j),cert in certs.items():
    ti,ri,si=stat[i];tj,rj,sj=stat[j];assert list(map(F,cert['incumbent_T_r_s']))==[ti,ri,si];assert list(map(F,cert['outsider_T_r_s']))==[tj,rj,sj]
    def value(x):return ((tj-x*sj/(1+x*rj))-(ti-x*si/(1+x*ri)))*(1+x*rj)*(1+x*ri)
    lo,mid,hi=value(-d),value(F(0)),value(d);coeff=[mid,(hi-lo)/(2*d),(hi+lo-2*mid)/(2*d*d)];assert coeff==list(map(F,cert['coefficients']))
    aa,bb,cc=coeff;args=[-d,d]
    if cc>0 and -d<-bb/(2*cc)<d:args.append(-bb/(2*cc));interior+=1
    val,at=min((aa+bb*x+cc*x*x,x) for x in args);assert val>0;assert val==F(cert['minimum']) and at==F(cert['minimum_at']);assert args==list(map(F,cert['checked_arguments']));assert cert['strictly_positive'] is True;count+=1
   if (a,b,c)==(3,3,3) and theta==0 and typ=='u-B':
    for e in [min(O),min(outside)]:
     tt,rr,ss=stat[e];v=S.eye(n)[:,f[0]]-S.eye(n)[:,f[1]]
     for x in [-d,d]:
      Px=(laps[e]+S.Rational(x.numerator,x.denominator)*v*v.T+J).inv()-J
      assert F(S.trace(Px))==tt-x*ss/(1+x*rr);diagnostics+=1
  summary.append({'parts':[a,b,c],'theta':str(theta),'nominal_best_count':len(O),'pairs_per_oldedge':len(O)*len(outside)})
assert count==3896 and interior==old['quadratics_with_interior_vertex']==0
print(json.dumps({'status':'pass','full_centered_candidate_inverses':matrices,'contexts':len(records),'quadratics':count,'interior_vertices':interior,'direct_perturbed_inverses':diagnostics,'summary':summary,'hashes':len(manifest),'sympy':S.__version__},indent=2))
