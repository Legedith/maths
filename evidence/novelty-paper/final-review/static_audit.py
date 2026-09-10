from pathlib import Path
import json,hashlib
P=Path('D:/CodexWorkspaces/mathematics-atlas/project');S=Path(__file__).parent
bpath=P/'.codex/evidence/runs/novelty-investigation-v1/bundle.json';b=json.loads(bpath.read_bytes());digest=hashlib.sha256(bpath.read_bytes()).hexdigest()
assert digest=='03e80d0b039dd2131af3bdf5379761930da66cbcab8e8aee6406ab6a18f7eecb'
arts={a['id']:a for a in b['artifacts']};claims={c['id']:c for c in b['claims']}
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
for a in arts.values():
 p=(P/a['path']).resolve();assert p.is_relative_to(P.resolve()) and sha(p)==a['sha256'],a['id']
count=0
def check(cid,seen):
 global count
 assert cid not in seen
 for s in claims[cid]['supports']:
  if 'claim_id' in s:check(s['claim_id'],seen|{cid});continue
  count+=1;t=(P/arts[s['artifact_id']]['path']).read_text(encoding='utf-8');loc=s['locator']
  if loc.startswith('contains:'):assert loc[9:] in t
  elif loc.startswith('line:'):
   n=list(map(int,loc[5:].split('-')));assert 1<=n[0]<=n[-1]<=len(t.splitlines())
   if 'expected' in s:assert str(s['expected']) in '\n'.join(t.splitlines()[n[0]-1:n[-1]])
  elif loc.startswith('json:'):
   obj=json.loads(t)
   for k in (loc[5:].lstrip('/').split('/') if loc[5:] else []):
    k=k.replace('~1','/').replace('~0','~');obj=obj[int(k)] if isinstance(obj,list) else obj[k]
   if 'expected' in s:assert obj==s['expected']
  else:raise AssertionError(loc)
for cid in claims:check(cid,set())
for aid in ['A027','A037','A049','A053','A058','A064']:
 p=P/arts[aid]['path'];r=json.loads(p.read_bytes());assert r['returncode']==0 and not r['timed_out']
 for stream in ['stdout','stderr']:
  q=p.parent/r[stream]['path'];assert sha(q)==r[stream]['sha256'] and q.stat().st_size==r[stream]['bytes']
for new,old in [('A062','A008'),('A068','A011')]:assert (P/arts[new]['path']).read_bytes()==(P/arts[old]['path']).read_bytes()
v=json.loads((P/arts['A057']['path']).read_bytes());author=json.loads((P/arts['A033']['path']).read_bytes());review=json.loads((P/arts['A043']['path']).read_bytes())
assert v['rows']==author['rows'] and len(v['rows'])==89
# Independent reviewer uses a smaller row schema; compare k, K and delta directly.
for x,y in zip(v['rows'],review['rows']):
 for key in ['k','K','delta']:assert x[key]==y[key]
assert v['code_sha256']==sha(P/arts['A137']['path'])
for a in json.loads((P/arts['A100']['path']).read_bytes()):
 p=Path(a['path']);assert sha(p)==a['sha256'] and p.stat().st_size==a['bytes']
res=dict(status='pass',bundle_sha256=digest,artifact_count=len(arts),claim_count=len(claims),recursive_supports=count,canonical_logs=6,portable_rows=89)
(S/'static-results.json').write_text(json.dumps(res,indent=2)+'\n');print(json.dumps(res))
