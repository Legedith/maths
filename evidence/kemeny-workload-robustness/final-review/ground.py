import json,hashlib
from pathlib import Path
p=Path(__file__).resolve().parent
root=p.parent/'project'
sha=lambda f:hashlib.sha256(f.read_bytes()).hexdigest()
bundlepath=root/'.codex/evidence/runs/kemeny-workload-robustness-v1/bundle.json'
b=json.loads(bundlepath.read_text(encoding='utf-8'))
assert sha(bundlepath)=='a6d3eb931d27ebefa64dcb16e773be856dc506a2c714b80343edb2912443330b'
for a in b['artifacts']:assert sha(root/a['path'])==a['sha256'],a['id']
copies=json.loads((root/'evidence/kemeny-workload-robustness/copy-manifest.json').read_text(encoding='utf-8'))
for c in copies:
 assert sha(Path(c['source']))==sha(root/c['destination'])==c['sha256']
 assert (root/c['destination']).stat().st_size==c['bytes']
base=root/'evidence/kemeny-workload-robustness'
assert (base/'integration/envelope-02.json').read_bytes()==(base/'envelope-portable-review/replay.json').read_bytes()
assert (base/'integration/continuous-01.json').read_bytes()==(base/'adversary-and-cli-review/cli-output.json').read_bytes()
for name,rc in [('envelope-01',1),('envelope-02',0),('continuous-01',0)]:
 assert json.loads((base/f'integration/logs/attempt-{name}.json').read_text(encoding='utf-8'))['returncode']==rc
for f,stage in [('verify_workload_envelope.py','astra-workload-portable-work'),('verify_continuous_perturbation.py','astra-continuous-portable-work')]:
 assert (root/'experiments/kemeny-workload-proof'/f).read_bytes()==(p.parent/stage/f).read_bytes()
r={'bundle_sha256':sha(bundlepath),'artifacts_verified':len(b['artifacts']),'claims':len(b['claims']),'copies_verified':len(copies),'canonical_independent_byte_matches':2,'unchanged_portable_scripts':2,'retained_returncodes':[1,0,0],'status':'PASS'}
(p/'ground-result.json').write_text(json.dumps(r,indent=2)+'\n',encoding='utf-8')
print(json.dumps(r))
