import subprocess,os,json,time
from pathlib import Path
p=Path(__file__).resolve().parent;env=os.environ.copy();env.update(UV_CACHE_DIR=str(p/'uv-cache'),UV_PROJECT_ENVIRONMENT=str(p/'.venv'),UV_PYTHON_INSTALL_DIR='D:/uv-python')
a=['uv','run','--isolated','--python','3.12.11','--with','sympy==1.14.0','python',str(p/'check2.py')];start=time.monotonic()
try:r=subprocess.run(a,cwd=p,env=env,capture_output=True,timeout=60);o,e,rc=r.stdout,r.stderr,r.returncode
except subprocess.TimeoutExpired as z:o,e,rc=z.stdout or b'',z.stderr or b'',124
(p/'batch2-stdout.bin').write_bytes(o);(p/'batch2-stderr.bin').write_bytes(e);(p/'batch2-run.json').write_text(json.dumps({'argv':a,'cwd':str(p),'rc':rc,'elapsed':time.monotonic()-start,'timeout':60,'environment':{k:env[k] for k in ('UV_CACHE_DIR','UV_PROJECT_ENVIRONMENT','UV_PYTHON_INSTALL_DIR')}},indent=2)+'\n',encoding='utf-8');print(o.decode());print(e.decode());raise SystemExit(rc)
