import subprocess,os,json,time
from pathlib import Path
p=Path(__file__).parent;os.environ['UV_CACHE_DIR']=str(p/'uv-cache');os.environ['UV_PROJECT_ENVIRONMENT']=str(p/'.venv')
a=['uv','run','--isolated','--python','3.12.11','--with','sympy==1.14.0','python',str(p/'check2.py')];start=time.monotonic()
try:
 r=subprocess.run(a,cwd=p,capture_output=True,timeout=60);o,e,rc=r.stdout,r.stderr,r.returncode;timed=False
except subprocess.TimeoutExpired as z:o,e,rc,timed=z.stdout or b'',z.stderr or b'',124,True
(p/'batch2-stdout.bin').write_bytes(o);(p/'batch2-stderr.bin').write_bytes(e);(p/'batch2-run.json').write_text(json.dumps({'argv':a,'cwd':str(p),'timeout':60,'returncode':rc,'timed_out':timed,'elapsed':time.monotonic()-start},indent=2),encoding='utf-8');print(o.decode());print(e.decode());raise SystemExit(rc)

