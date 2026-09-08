import json,hashlib
from pathlib import Path
p=Path('D:/CodexWorkspaces/mathematics-atlas/project');r=p.parent/'astra-single-failure-release-review-work';b=json.loads((p/'.codex/evidence/runs/kemeny-single-failure-v1/bundle.json').read_bytes());m=json.loads((p/'evidence/kemeny-one-deletion/copy-manifest.json').read_bytes())
errors=[]
for e in m:
 for q in [Path(e['source']),p/e['destination']]:
  if not q.is_file() or hashlib.sha256(q.read_bytes()).hexdigest()!=e['sha256'] or q.stat().st_size!=e['bytes']:errors.append(str(q))
arts={a['id']:a for a in b['artifacts']};claims={c['id']:c for c in b['claims']}
for a in b['artifacts']:
 q=p/a['path']
 if not q.is_file() or hashlib.sha256(q.read_bytes()).hexdigest()!=a['sha256']:errors.append(a['id'])
def visit(cid,seen):
 assert cid not in seen
 for z in claims[cid]['supports']:
  if 'claim_id' in z:visit(z['claim_id'],seen|{cid});continue
  a=arts[z['artifact_id']];text=(p/a['path']).read_text(encoding='utf-8-sig');loc=z['locator']
  if loc.startswith('contains:'):assert loc[9:] in text,(cid,loc)
  elif loc.startswith('json:'):
   val=json.loads(text)
   for t in loc[6:].split('/') if loc[6:] else []:val=val[int(t)] if isinstance(val,list) else val[t.replace('~1','/').replace('~0','~')]
   if 'expected' in z:assert val==z['expected'],cid
  elif loc.startswith('line:'):
   nums=loc[5:].split('-');start=int(nums[0]);end=int(nums[-1]);lines=text.splitlines();assert 1<=start<=end<=len(lines)
   if 'expected' in z:assert str(z['expected']) in '\n'.join(lines[start-1:end])
  else: raise AssertionError(loc)
for cid in claims:visit(cid,set())
summary={'manifest_copies':len(m),'artifacts':len(arts),'claims':len(claims),'errors':errors,'claim_summaries':[{'id':c['id'],'statement':c['statement'],'supports':c['supports']} for c in claims.values()]}
(r/'assembly-result.json').write_text(json.dumps(summary,indent=2));print(json.dumps({k:v for k,v in summary.items() if k!='claim_summaries'},indent=2))
for c in claims.values():print(c['id'],c['statement'],[(z.get('artifact_id',z.get('claim_id')),z.get('locator','')) for z in c['supports']])
assert not errors
