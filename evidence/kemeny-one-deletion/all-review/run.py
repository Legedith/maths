import subprocess,json,os,sys
from pathlib import Path
r=Path(__file__).parent; os.environ['UV_CACHE_DIR']='D:/CodexWorkspaces/mathematics-atlas/uv-cache'; uv='C:/Users/Legedith/.local/bin/uv.exe'; py=r/'.venv/Scripts/python.exe'
commands=[[uv,'venv','--python','3.12.11',str(r/'.venv')],[uv,'pip','install','--python',str(py),'sympy==1.14.0'],[str(py),str(r/'evaluate.py')]]
for i,args in enumerate(commands):
 p=subprocess.run(args,capture_output=True,text=True,encoding='utf8',errors='replace'); (r/f'run-{i}.json').write_text(json.dumps({'argv':args,'cwd':str(Path.cwd()),'stdout':p.stdout,'stderr':p.stderr,'returncode':p.returncode},indent=2)); print(i,p.returncode,p.stdout,p.stderr,flush=True)
 if p.returncode: sys.exit(p.returncode)
