from fractions import Fraction as F
from itertools import combinations
from pathlib import Path
import json, hashlib, platform
p=Path(__file__).resolve().parent
src=p.parent/'astra-full-unit-minimax-work'
hashes=[]
for manifest in ('hashes.json','input-hashes.json'):
    for row in json.loads((src/manifest).read_text(encoding='utf-8-sig')):
        actual=hashlib.sha256(Path(row['Path']).read_bytes()).hexdigest()
        assert actual==row['Hash'].lower()
        hashes.append({'path':row['Path'],'sha256':actual})
n=10; hub=9; labels=[0]*3+[1]*3+[2]*3+[3]
old={e for e in combinations(range(n),2) if labels[e[0]]!=labels[e[1]]}-{(0,hub)}
missing=sorted(set(combinations(range(n),2))-old)
assert len(old)==35 and len(missing)==10
def inverse(mat):
    aug=[list(row)+[F(i==j) for j in range(n)] for i,row in enumerate(mat)]
    for i in range(n):
        q=next(j for j in range(i,n) if aug[j][i])
        aug[i],aug[q]=aug[q],aug[i]
        d=aug[i][i];aug[i]=[x/d for x in aug[i]]
        for j in range(n):
            if j!=i:
                d=aug[j][i];aug[j]=[a-d*b for a,b in zip(aug[j],aug[i])]
    return [r[n:] for r in aug]
lines={}
for edge in missing:
    L=[[F(0) for j in range(n)] for i in range(n)]
    for i,j in old|{edge}:
        L[i][i]+=1;L[j][j]+=1;L[i][j]-=1;L[j][i]-=1
    inv=inverse([[x+F(1,n) for x in row] for row in L])
    M=[[x-F(1,n) for x in row] for row in inv]
    assert all(sum(L[i][k]*M[k][j] for k in range(n))==F(i==j)-F(1,n) for i in range(n) for j in range(n))
    lines[edge]=(sum(M[i][i] for i in range(n)),n*M[hub][hub])
assert lines[(0,1)]==lines[(0,2)]==(F(10021,8680),F(2547,2480))
assert lines[(0,9)]==(F(81,70),F(9,10))
lo=F(0);hi=F(21,500);mid=(lo+hi)/2
def value(e,t):a,b=lines[e];return a+b*t
def oracle(t):return min(value(e,t) for e in missing)
regrets={e:max(value(e,t)/oracle(t)-1 for t in (lo,hi)) for e in missing}
winners=[e for e in missing if regrets[e]==min(regrets.values())]
midw=[e for e in missing if value(e,mid)==oracle(mid)]
assert winners==[(0,1),(0,2)] and midw==[(0,9)]
assert regrets[(0,1)]==F(23305,10372104)<regrets[(0,9)]==F(23,10021)
author=json.loads((src/'result.json').read_text())
for name,e in [('incident',(0,1)),('restoration',(0,9))]:
    assert [str(x) for x in lines[e]]==author['lines'][name]
    assert str(value(e,mid))==author['midpoint_values'][name]
    assert str(value(e,lo)*value(e,hi))==author['products'][name]
    assert str(regrets[e])==author['worst_relative_regrets'][name]
tau=(lines[(0,9)][0]-lines[(0,1)][0])/(lines[(0,1)][1]-lines[(0,9)][1])
assert tau==F(46,2205) and lo<tau<mid<hi
out={'status':'PASS','python':platform.python_version(),'matrices':len(lines),'old_edges':len(old),'interval':[str(lo),str(hi)],'tau':str(tau),'midpoint_winners':midw,'minimax_winners':winners,'rows':[{'edge':e,'line':[str(x) for x in lines[e]],'endpoint_regrets':[str(value(e,t)/oracle(t)-1) for t in (lo,hi)],'worst_regret':str(regrets[e])} for e in missing],'input_hashes':hashes}
with (p/'result.json').open('x',encoding='utf-8') as f:json.dump(out,f,indent=2);f.write('\n')
print(json.dumps({'status':'PASS','matrices':len(lines),'minimax_winners':winners}))
