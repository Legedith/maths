import subprocess,json,os,sys,hashlib
from pathlib import Path
root=Path(__file__).parent; os.environ['UV_CACHE_DIR']='D:/CodexWorkspaces/mathematics-atlas/uv-cache'; uv='C:/Users/Legedith/.local/bin/uv.exe'; py=root/'.venv/Scripts/python.exe'
commands=[[uv,'venv','--python','3.12.11',str(root/'.venv')],[uv,'pip','install','--python',str(py),'sympy==1.14.0'],[str(py),str(root/'evaluate.py')]]
for i,args in enumerate(commands):
 r=subprocess.run(args,capture_output=True,text=True,encoding='utf8',errors='replace'); (root/f'run-{i}.json').write_text(json.dumps({'argv':args,'cwd':str(Path.cwd()),'stdout':r.stdout,'stderr':r.stderr,'returncode':r.returncode},indent=2)); print(i,r.returncode,r.stdout,r.stderr,flush=True)
 if r.returncode: sys.exit(r.returncode)
