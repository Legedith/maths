import subprocess,json,os
from pathlib import Path
p=Path(__file__).parent
env=os.environ.copy()
env.update(UV_CACHE_DIR='D:/uv-cache',UV_PYTHON_INSTALL_DIR='D:/uv-python',UV_PROJECT_ENVIRONMENT=str(p/'.venv'))
argv=['uv','run','--frozen','--project',str(p),'python',str(p/'verify_weighted_repair.py'),'--weighted-certificate',str(p/'uniform-weighted.json'),'--noop-certificate',str(p/'uniform-noop.json'),'--output',str(p/'check-02.json')]
(p/'attempt2-argv.json').write_text(json.dumps(argv,indent=2))
try:
 r=subprocess.run(argv,env=env,capture_output=True,timeout=90)
 (p/'attempt2-stdout.txt').write_bytes(r.stdout)
 (p/'attempt2-stderr.txt').write_bytes(r.stderr)
 (p/'attempt2-rc.txt').write_text(str(r.returncode)+'\n')
 print(r.returncode)
except subprocess.TimeoutExpired as exc:
 (p/'attempt2-stdout.txt').write_bytes(exc.stdout or b'')
 (p/'attempt2-stderr.txt').write_bytes(exc.stderr or b'')
 (p/'attempt2-rc.txt').write_text('timeout90s\n')
 raise
