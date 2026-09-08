from pathlib import Path
import os,subprocess,json,time
p=Path(__file__).resolve().parent
env=dict(os.environ,UV_CACHE_DIR=str(p.parent/'uv-cache'),UV_PROJECT_ENVIRONMENT=str(p/'.venv'))
cmd=['uv','run','--isolated','--python','3.12.11','python',str(p/'check.py')]
t=time.monotonic()
try:
    r=subprocess.run(cmd,cwd=p,env=env,capture_output=True,timeout=60);rc=r.returncode;out=r.stdout;err=r.stderr
except subprocess.TimeoutExpired as e:
    rc=124;out=e.stdout or b'';err=e.stderr or b''
(p/'stdout.bin').write_bytes(out);(p/'stderr.bin').write_bytes(err)
(p/'run.json').write_text(json.dumps({'argv':cmd,'cwd':str(p),'rc':rc,'elapsed':time.monotonic()-t,'timeout_seconds':60,'environment':{k:env[k] for k in ('UV_CACHE_DIR','UV_PROJECT_ENVIRONMENT')}},indent=2)+'\n',encoding='utf-8')
print((p/'run.json').read_text());raise SystemExit(rc)
