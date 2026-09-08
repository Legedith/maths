import subprocess,os,time,json
from pathlib import Path
p=Path(__file__).parent;argv=['uv','run','--isolated','--with','sympy==1.14.0','python',str(p/'check2.py')];t=time.time()
try:
 r=subprocess.run(argv,capture_output=True,timeout=60);stdout,stderr,rc=r.stdout,r.stderr,r.returncode;timed=False
except subprocess.TimeoutExpired as e:stdout=e.stdout or b'';stderr=e.stderr or b'';rc=None;timed=True
(p/'batch2-stdout.bin').write_bytes(stdout);(p/'batch2-stderr.bin').write_bytes(stderr);meta={'argv':argv,'cwd':os.getcwd(),'rc':rc,'timeout':60,'timed_out':timed,'elapsed':time.time()-t};(p/'batch2-run.json').write_text(json.dumps(meta,indent=2));print(json.dumps(meta));print(stdout.decode(errors='replace'));print(stderr.decode(errors='replace'))

