import subprocess,os,json,time,hashlib,difflib
from pathlib import Path
p=Path(__file__).parent;root=p.parent/'kemeny-robustness-work'
os.environ['UV_CACHE_DIR']=str(p/'uv-cache');os.environ['UV_PROJECT_ENVIRONMENT']=str(p/'.venv')
original=root/'check.py';script=p/'verify_continuous_perturbation.py';baseline=root/'result.json'
assert hashlib.sha256(original.read_bytes()).hexdigest()=='c6ca55ac065e8ed75ff16680dfddea2a3d32e4e0054fe2ee7836bfe2bbe83625'
assert hashlib.sha256(baseline.read_bytes()).hexdigest()=='13d3f0af59ccae1e848fe2c1c79d87cca1539b3e304fc6c8d3994ab0af5b09e0'
(p/'changes.diff').write_text(''.join(difflib.unified_diff(original.read_text(encoding='utf-8').splitlines(True),script.read_text(encoding='utf-8').splitlines(True),fromfile='accepted/check.py',tofile='verify_continuous_perturbation.py')),encoding='utf-8')
output=p/'replay.json';assert not output.exists()
a=['uv','run','--isolated','--python','3.12.11','python',str(script),'--output',str(output)]
def run(name):
 start=time.monotonic()
 try:
  r=subprocess.run(a,cwd=p,capture_output=True,timeout=60);o,e,rc=r.stdout,r.stderr,r.returncode;timed=False
 except subprocess.TimeoutExpired as x:o,e,rc,timed=x.stdout or b'',x.stderr or b'',124,True
 (p/(name+'.stdout.bin')).write_bytes(o);(p/(name+'.stderr.bin')).write_bytes(e)
 (p/(name+'.json')).write_text(json.dumps({'argv':a,'cwd':str(p),'timeout':60,'timed_out':timed,'returncode':rc,'elapsed':time.monotonic()-start},indent=2),encoding='utf-8')
 return rc,e
rc,e=run('attempt1');assert rc==0 and not e
actual=json.loads(output.read_text(encoding='utf-8'));expected=json.loads(baseline.read_text(encoding='utf-8'));assert actual.pop('implementation_sha256')==hashlib.sha256(script.read_bytes()).hexdigest();expected.pop('implementation_sha256');assert actual==expected
before=hashlib.sha256(output.read_bytes()).hexdigest();rc,e=run('attempt2-existing');assert rc!=0 and b'Use a fresh attempt output, never overwrite evidence.' in e;assert hashlib.sha256(output.read_bytes()).hexdigest()==before
result={'mathematical_fields_equal':True,'ignored_fields':['implementation_sha256'],'canonical_rc':0,'existing_output_rc':rc,'existing_output_unchanged':True,'script_sha256':hashlib.sha256(script.read_bytes()).hexdigest(),'replay_sha256':before,'scope':'Implementation preparation only; independent interface review pending'}
(p/'comparison.json').write_text(json.dumps(result,indent=2),encoding='utf-8');print(json.dumps(result,indent=2))
