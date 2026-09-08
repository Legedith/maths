import subprocess,json,os,hashlib
from pathlib import Path
r=Path(__file__).parent; p=r.parent/'project'; stage=p/'experiments/kemeny-one-deletion-proof'; uv='C:/Users/Legedith/.local/bin/uv.exe'
os.environ['UV_CACHE_DIR']='D:/CodexWorkspaces/mathematics-atlas/uv-cache'; os.environ['UV_PROJECT_ENVIRONMENT']=str(r/'.portable-venv')
bad=r/'portable-modified-symbolic.json'; data=json.loads((stage/'symbolic.json').read_bytes()); data['negative_N_shift_terms'][0][1]=str(int(data['negative_N_shift_terms'][0][1])+1); bad.write_text(json.dumps(data))
base=[uv,'run','--project',str(stage),'--frozen','python']
commands=[base+[str(stage/'verify_certificate.py'),'--certificate',str(stage/'symbolic.json'),'--output',str(r/'portable-valid.json')],base+[str(stage/'verify_certificate.py'),'--certificate',str(bad),'--output',str(r/'portable-invalid.json')],base+['-c','import sys; print(sys.version); print(sys.executable)']]
for i,args in enumerate(commands):
 v=subprocess.run(args,capture_output=True,text=True,encoding='utf8',errors='replace'); (r/f'portable-replay-{i}.json').write_text(json.dumps({'argv':args,'cwd':str(Path.cwd()),'env':{'UV_PROJECT_ENVIRONMENT':os.environ['UV_PROJECT_ENVIRONMENT'],'UV_CACHE_DIR':os.environ['UV_CACHE_DIR']},'stdout':v.stdout,'stderr':v.stderr,'returncode':v.returncode},indent=2)); print(i,v.returncode,v.stdout,v.stderr)
 assert v.returncode==(1 if i==1 else 0)
 if i==1: assert 'certificate differs from frozen proof input' in v.stderr
assert not (r/'portable-invalid.json').exists()
paths=[stage/n for n in ['verify_certificate.py','symbolic.json','pyproject.toml','uv.lock','.python-version']]+[p/'docs/kemeny-one-deletion-contract.md',r/'portable-valid.json',r/'.portable-venv/Scripts/python.exe']
(r/'portable-hashes.json').write_text(json.dumps({str(f):hashlib.sha256(f.read_bytes()).hexdigest() for f in paths},indent=2))
