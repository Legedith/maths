import subprocess,json,hashlib
from pathlib import Path
r=Path(__file__).parent;p=r.parent/'project';args=['D:/CodexWorkspaces/mathematics-atlas/astra-all-deletions-review-work/.venv/Scripts/python.exe',str(r/'check_assembly.py')];v=subprocess.run(args,capture_output=True,text=True,encoding='utf8',errors='replace');(r/'assembly-replay.json').write_text(json.dumps({'argv':args,'cwd':str(Path.cwd()),'stdout':v.stdout,'stderr':v.stderr,'returncode':v.returncode},indent=2));print(v.stdout);assert v.returncode==0
b=json.loads((p/'.codex/evidence/runs/kemeny-single-failure-v1/bundle.json').read_bytes());ids={'A067','A077','A123','A135','A178','A180','A196','A208','A210'}
for a in b['artifacts']:
 if a['id'] in ids:print(a['id'],a['path'])
(r/'reviewed-bundle-sha256.txt').write_text(hashlib.sha256((p/'.codex/evidence/runs/kemeny-single-failure-v1/bundle.json').read_bytes()).hexdigest())
