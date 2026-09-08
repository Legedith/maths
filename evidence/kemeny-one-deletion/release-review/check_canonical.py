import json,hashlib
from pathlib import Path
p=Path('D:/CodexWorkspaces/mathematics-atlas/project');i=p/'evidence/kemeny-one-deletion/integration';out=[]
for stem,res,review in [('one-deletion-01','check-01.json','astra-one-deletion-review-work/portable-valid.json'),('all-deletions-01','all-deletions-01.json','astra-all-deletions-review-work/portable-valid.json'),('optimal-repair-01','optimal-repair-01.json','astra-postfailure-review-work/portable-result.json')]:
 log=json.loads((i/f'attempt-{stem}.json').read_bytes());assert log['returncode']==0 and not log['timed_out']
 for stream in ['stdout','stderr']:
  raw=(i/log[stream]['path']).read_bytes();assert len(raw)==log[stream]['bytes'] and hashlib.sha256(raw).hexdigest()==log[stream]['sha256']
 val=json.loads((i/res).read_bytes());assert val==json.loads((p.parent/review).read_bytes());assert val==json.loads((i/log['stdout']['path']).read_bytes());out.append({'case':stem,'canonical_equals_independent_replay':True,'rc':0})
Path(__file__).with_name('canonical-result.json').write_text(json.dumps(out,indent=2));print(out)
