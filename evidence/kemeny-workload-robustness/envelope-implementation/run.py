import subprocess,json,os,time,hashlib
from pathlib import Path
p=Path(__file__).parent;os.environ['UV_CACHE_DIR']=str(p/'uv-cache');os.environ['UV_PROJECT_ENVIRONMENT']=str(p/'.venv')
source=p.parent/'astra-weight-workload-family-work/proposal.md';assert hashlib.sha256(source.read_bytes()).hexdigest()=='973868b9277394cb1fe6a1e3abfc659481ff19a8c3a7e77b7bb96cb5e0254850'
a=['uv','run','--frozen','python','verify_workload_envelope.py','--output','result.json'];s=time.monotonic()
try:
 r=subprocess.run(a,cwd=p,capture_output=True,timeout=60);o,e,rc=r.stdout,r.stderr,r.returncode;timed=False
except subprocess.TimeoutExpired as x:o,e,rc,timed=x.stdout or b'',x.stderr or b'',124,True
(p/'attempt1.stdout.bin').write_bytes(o);(p/'attempt1.stderr.bin').write_bytes(e);(p/'attempt1.json').write_text(json.dumps({'argv':a,'cwd':str(p),'timeout':60,'timed_out':timed,'returncode':rc,'elapsed':time.monotonic()-s},indent=2),encoding='utf-8');print(o.decode());print(e.decode());raise SystemExit(rc)
