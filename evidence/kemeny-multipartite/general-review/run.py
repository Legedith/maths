import subprocess,json,os,sys
from pathlib import Path
root=Path(__file__).parent
os.environ['UV_CACHE_DIR']='D:/CodexWorkspaces/mathematics-atlas/uv-cache'
commands=[['C:/Users/Legedith/.local/bin/uv.exe','venv',str(root/'.venv')],['C:/Users/Legedith/.local/bin/uv.exe','pip','install','--python',str(root/'.venv/Scripts/python.exe'),'sympy==1.14.0'],[str(root/'.venv/Scripts/python.exe'),str(root/'evaluate.py')]]
for i,args in enumerate(commands):
 r=subprocess.run(args,capture_output=True,text=True,encoding='utf-8',errors='replace')
 (root/f'run-{i}.json').write_text(json.dumps({'argv':args,'cwd':str(Path.cwd()),'stdout':r.stdout,'stderr':r.stderr,'returncode':r.returncode},indent=2))
 print(i,r.returncode,r.stdout,r.stderr,flush=True)
 if r.returncode: sys.exit(r.returncode)
