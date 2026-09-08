import subprocess,json,os,hashlib
from pathlib import Path
root=Path(__file__).parent; project=root.parent/'project'; checker=project/'experiments/kemeny-multipartite-proof/verify_certificate.py'; cert=checker.parent/'certificate.json'
os.environ['UV_CACHE_DIR']='D:/CodexWorkspaces/mathematics-atlas/uv-cache'
assert hashlib.sha256(checker.read_bytes()).hexdigest()=='7b656d33739a7a77834d1ae47f8115cd830f04bb05638a68a8de73189f747749'
bad=root/'modified-certificate.json'; data=json.loads(cert.read_bytes()); data['terms'][0][1]+=1; bad.write_text(json.dumps(data))
uv='C:/Users/Legedith/.local/bin/uv.exe'; py=root/'.portable-venv/Scripts/python.exe'
cmds=[ [uv,'venv','--python','3.12.11',str(root/'.portable-venv')], [str(py),str(checker),'--certificate',str(cert),'--output',str(root/'portable-valid.json')], [str(py),str(checker),'--certificate',str(bad),'--output',str(root/'portable-invalid.json')], [str(py),'-c','import sys; print(sys.version); print(sys.executable)'] ]
for i,args in enumerate(cmds):
 r=subprocess.run(args,capture_output=True,text=True,encoding='utf8',errors='replace'); (root/f'portable-run-{i}.json').write_text(json.dumps({'argv':args,'cwd':str(Path.cwd()),'stdout':r.stdout,'stderr':r.stderr,'returncode':r.returncode},indent=2)); print(i,r.returncode,r.stdout,r.stderr)
 assert r.returncode==(1 if i==2 else 0)
 if i==2: assert 'certificate differs from the accepted frozen input' in r.stderr
assert not (root/'portable-invalid.json').exists()
paths=[checker,cert,py,root/'portable-valid.json']
(root/'portable-hashes.json').write_text(json.dumps({str(p):hashlib.sha256(p.read_bytes()).hexdigest() for p in paths},indent=2))
