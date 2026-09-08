import subprocess,sys,time,json
from pathlib import Path
argv=[sys.executable,'evaluate.py'];start=time.time()
try:
 r=subprocess.run(argv,capture_output=True,timeout=180);out,err,rc=r.stdout,r.stderr,r.returncode
except subprocess.TimeoutExpired as e:out,err,rc=e.stdout or b'',e.stderr or b'',124
Path('stdout.txt').write_bytes(out);Path('stderr.txt').write_bytes(err);Path('execution.json').write_text(json.dumps({'argv':argv,'seconds':time.time()-start,'rc':rc},indent=2));print(out.decode());print(err.decode());sys.exit(rc)
