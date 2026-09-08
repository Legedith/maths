import subprocess,json,os,hashlib
from pathlib import Path
r=Path(__file__).parent; p=r.parent/'project'; stage=p/'experiments/kemeny-one-deletion-proof'; uv='C:/Users/Legedith/.local/bin/uv.exe'
os.environ['UV_CACHE_DIR']='D:/CodexWorkspaces/mathematics-atlas/uv-cache';os.environ['UV_PROJECT_ENVIRONMENT']=str(r/'.portable-venv')
bad=r/'portable-bad';bad.mkdir(exist_ok=True)
for f in (stage/'all-deletions').glob('*.json'): (bad/f.name).write_bytes(f.read_bytes())
data=json.loads((bad/'uB.json').read_bytes());data['negative_numerator_terms'][0][1]=str(int(data['negative_numerator_terms'][0][1])+1);(bad/'uB.json').write_text(json.dumps(data))
base=[uv,'run','--project',str(stage),'--frozen','python'];commands=[base+[str(stage/'verify_all_deletions.py'),'--certificates',str(stage/'all-deletions'),'--output',str(r/'portable-valid.json')],base+[str(stage/'verify_all_deletions.py'),'--certificates',str(bad),'--output',str(r/'portable-invalid.json')],base+['-c','import sys;print(sys.version);print(sys.executable)']]
for i,args in enumerate(commands):
 out=subprocess.run(args,capture_output=True,text=True,encoding='utf8',errors='replace');(r/f'portable-replay-{i}.json').write_text(json.dumps({'argv':args,'cwd':str(Path.cwd()),'environment':{'UV_CACHE_DIR':os.environ['UV_CACHE_DIR'],'UV_PROJECT_ENVIRONMENT':os.environ['UV_PROJECT_ENVIRONMENT']},'stdout':out.stdout,'stderr':out.stderr,'returncode':out.returncode},indent=2));print(i,out.returncode,out.stdout,out.stderr)
 assert out.returncode==(1 if i==1 else 0)
 if i==1:assert 'changed frozen certificate' in out.stderr
assert not (r/'portable-invalid.json').exists()
files=[stage/'verify_all_deletions.py',stage/'verify_certificate.py',stage/'pyproject.toml',stage/'uv.lock',r/'portable-valid.json',r/'.portable-venv/Scripts/python.exe']+list((stage/'all-deletions').glob('*.json'))
(r/'portable-hashes.json').write_text(json.dumps({str(f):hashlib.sha256(f.read_bytes()).hexdigest() for f in files},indent=2))
