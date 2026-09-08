import subprocess,os,json,time
from pathlib import Path
p=Path(__file__).parent;os.environ['UV_CACHE_DIR']=str(p/'uv-cache');os.environ['UV_PROJECT_ENVIRONMENT']=str(p/'.venv')
a=['uv','run','--isolated','--python','3.12.11','--with','sympy==1.14.0','python',str(p/'check.py')];s=time.monotonic()
try:
 r=subprocess.run(a,capture_output=True,timeout=60,cwd=p);o,e,rc=r.stdout,r.stderr,r.returncode;timed=False
except subprocess.TimeoutExpired as x:o,e,rc,timed=x.stdout or b'',x.stderr or b'',124,True
(p/'stdout.bin').write_bytes(o);(p/'stderr.bin').write_bytes(e);(p/'run.json').write_text(json.dumps({'argv':a,'cwd':str(p),'timeout':60,'timed_out':timed,'rc':rc,'elapsed':time.monotonic()-s},indent=2));print(o.decode());print(e.decode());raise SystemExit(rc)
