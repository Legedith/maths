from pathlib import Path
import subprocess,os,json
p=Path(__file__).parent;env=os.environ.copy();env.update(UV_CACHE_DIR='D:/uv-cache',UV_PYTHON_INSTALL_DIR='D:/uv-python')
argv=['uv','run','--isolated','--python','3.12.11','--with','sympy==1.14.0','python',str(p/'check.py')]
(p/'argv.json').write_text(json.dumps(argv,indent=2),encoding='utf-8')
try:
 r=subprocess.run(argv,env=env,capture_output=True,timeout=60)
 (p/'stdout.txt').write_bytes(r.stdout);(p/'stderr.txt').write_bytes(r.stderr);(p/'rc.txt').write_text(str(r.returncode),encoding='utf-8');print(r.returncode)
except subprocess.TimeoutExpired as e:
 (p/'stdout.txt').write_bytes(e.stdout or b'');(p/'stderr.txt').write_bytes(e.stderr or b'');(p/'rc.txt').write_text('timeout60s',encoding='utf-8');raise

