import json,hashlib
from pathlib import Path
r=Path('D:/CodexWorkspaces/mathematics-atlas/project');bp=r/'.codex/evidence/runs/kemeny-weighted-repair-v1/bundle.json';b=json.loads(bp.read_text(encoding='utf-8'));arts={a['id']:a for a in b['artifacts']};errors=[]
def check(v,msg):
 if not v:errors.append(msg)
for a in arts.values():
 p=(r/a['path']).resolve();check(p.is_relative_to(r.resolve()),'escape '+a['id']);check(hashlib.sha256(p.read_bytes()).hexdigest()==a['sha256'],'hash '+a['id'])
manifest=json.loads((r/'evidence/kemeny-weighted-repair/copy-manifest.json').read_text())
for row in manifest:
 src=Path(row['source']);dst=r/row['destination'];check(src.read_bytes()==dst.read_bytes(),'copy '+str(dst));check(len(dst.read_bytes())==row['bytes'],'size '+str(dst));check(hashlib.sha256(dst.read_bytes()).hexdigest()==row['sha256'],'copyhash '+str(dst))
for c in b['claims']:
 kinds=[]
 for u in c['supports']:
  if 'claim_id' in u:continue
  a=arts[u['artifact_id']];kinds.append(a['kind']);loc=u['locator']
  try:txt=(r/a['path']).read_text(encoding='utf-8')
  except UnicodeDecodeError as e:errors.append(c['id']+' '+a['id']+' strict UTF8 fails '+str(e));continue
  if loc.startswith('contains:'):check(loc[9:] in txt,c['id']+' '+a['id']+' contains')
  elif loc.startswith('json:'):
   val=json.loads(txt)
   for step in loc[5:].split('/')[1:]:
    step=step.replace('~1','/').replace('~0','~');val=val[int(step)] if isinstance(val,list) else val[step]
   if 'expected' in u:check(val==u['expected'],c['id']+' expected')
  elif loc.startswith('line:'):
   nums=loc[5:].split('-');lo,hi=int(nums[0]),int(nums[-1]);check(1<=lo<=hi<=len(txt.splitlines()),c['id']+' line')
  else:errors.append('unknown locator '+loc)
 if c['type']=='methodological':check(any(k in ['code','log'] for k in kinds),c['id']+' lacks code/log')
 if c['type']=='citation':check('source' in kinds,c['id']+' lacks source')
 if c['type']=='numerical':check(any('artifact_id' in u and 'expected' in u for u in c['supports']),c['id']+' lacks expected')
claims={c['id']:c for c in b['claims']}
def walk(k,trail):
 check(k not in trail,'cycle '+k)
 if k in trail:return False
 resolved=[]
 for u in claims[k]['supports']:resolved.append(True if 'artifact_id' in u else walk(u['claim_id'],trail+[k]))
 return any(resolved)
for k,c in claims.items():
 if c['type']=='conclusion':check(walk(k,[]),k+' ancestry')
res={'bundle_sha256':hashlib.sha256(bp.read_bytes()).hexdigest(),'artifacts':len(arts),'copies':len(manifest),'claims':len(claims),'errors':errors};Path('inspection.json').write_text(json.dumps(res,indent=2));print(json.dumps(res,indent=2))
