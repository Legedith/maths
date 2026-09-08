import json,hashlib
from pathlib import Path
root=Path('D:/CodexWorkspaces/mathematics-atlas/project');bp=root/'.codex/evidence/runs/kemeny-alternative-repair-v1/bundle.json';b=json.loads(bp.read_text());arts={a['id']:a for a in b['artifacts']};errors=[]
def need(v,msg):
 if not v:errors.append(msg)
def read(p):return json.loads(p.read_text(encoding='utf-8-sig'))
for a in arts.values():
 p=(root/a['path']).resolve();need(p.is_relative_to(root.resolve()),'escape '+a['id']);need(hashlib.sha256(p.read_bytes()).hexdigest()==a['sha256'],'hash '+a['id'])
manifest=read(root/'evidence/kemeny-alternative-repair/copy-manifest.json')
for row in manifest:
 src=Path(row['source']);dst=root/row['destination'];need(src.read_bytes()==dst.read_bytes(),'copy '+str(dst));need(len(dst.read_bytes())==row['bytes'],'bytes '+str(dst));need(hashlib.sha256(dst.read_bytes()).hexdigest()==row['sha256'],'manifest hash '+str(dst))
for c in b['claims']:
 kinds=[]
 for u in c['supports']:
  if 'claim_id' in u:continue
  a=arts[u['artifact_id']];kinds.append(a['kind']);txt=(root/a['path']).read_text(encoding='utf-8-sig');loc=u['locator']
  if loc.startswith('contains:'):need(loc[9:] in txt,c['id']+' contains')
  elif loc.startswith('json:'):
   val=json.loads(txt)
   for step in loc[5:].split('/')[1:]:
    step=step.replace('~1','/').replace('~0','~');val=val[int(step)] if isinstance(val,list) else val[step]
   if 'expected' in u:need(val==u['expected'],c['id']+' expected')
  elif loc.startswith('line:'):
   span=loc[5:].split('-');lo=int(span[0]);hi=int(span[-1]);lines=txt.splitlines();need(1<=lo<=hi<=len(lines),c['id']+' line range')
   if 'expected' in u:need(str(u['expected']) in '\n'.join(lines[lo-1:hi]),c['id']+' line expected')
  else:errors.append('unhandled locator '+loc)
 if c['type']=='methodological':need(any(k in ['code','log'] for k in kinds),c['id']+' methodological lacks code/log')
 if c['type']=='citation':need('source' in kinds,c['id']+' citation lacks source')
 if c['type']=='numerical':need(any('artifact_id' in u and 'expected' in u for u in c['supports']),c['id']+' numerical lacks expected')
claims={c['id']:c for c in b['claims']}
def walk(k,trail):
 need(k not in trail,'cycle '+k)
 if k in trail:return False
 return any(('artifact_id' in u) or walk(u['claim_id'],trail+[k]) for u in claims[k]['supports'])
for k,c in claims.items():
 if c['type']=='conclusion':need(walk(k,[]),k+' no artifact ancestry')
result={'bundle_sha256':hashlib.sha256(bp.read_bytes()).hexdigest(),'artifact_count':len(arts),'copy_count':len(manifest),'claim_count':len(claims),'errors':errors,'pending_checks_expected':all(c['status']=='pending' for c in b['checks'])};Path('inspection.json').write_text(json.dumps(result,indent=2));print(json.dumps(result,indent=2))

