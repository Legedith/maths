import subprocess,json,hashlib,difflib,time,os
from pathlib import Path
p=Path(__file__).parent;root=p.parent;src=root/'astra-continuous-portable-work';old=root/'kemeny-robustness-work';script=p/'verify_continuous_perturbation.py'
assert hashlib.sha256(script.read_bytes()).hexdigest()=='6625373266410d302527d509516bb7df6c9a397573f42ba85798d9fe089853bb'
assert hashlib.sha256((old/'check.py').read_bytes()).hexdigest()=='c6ca55ac065e8ed75ff16680dfddea2a3d32e4e0054fe2ee7836bfe2bbe83625'
assert hashlib.sha256((old/'result.json').read_bytes()).hexdigest()=='13d3f0af59ccae1e848fe2c1c79d87cca1539b3e304fc6c8d3994ab0af5b09e0'
diff=''.join(difflib.unified_diff((old/'check.py').read_text().splitlines(True),script.read_text().splitlines(True),fromfile='accepted/check.py',tofile='verify_continuous_perturbation.py'))
assert diff==(src/'changes.diff').read_text()
argv=['uv','run','--isolated','--python','3.12.11','python',str(script),'--output',str(p/'cli-output.json')];start=time.time()
try:
 r=subprocess.run(argv,capture_output=True,timeout=60);stdout,stderr,rc=r.stdout,r.stderr,r.returncode;timed=False
except subprocess.TimeoutExpired as ex:stdout=ex.stdout or b'';stderr=ex.stderr or b'';rc=None;timed=True
(p/'cli-stdout.bin').write_bytes(stdout);(p/'cli-stderr.bin').write_bytes(stderr);meta={'argv':argv,'cwd':os.getcwd(),'rc':rc,'timed_out':timed,'timeout':60,'elapsed':time.time()-start};(p/'cli-run.json').write_text(json.dumps(meta,indent=2),encoding='utf-8');assert rc==0
actual=json.loads((p/'cli-output.json').read_text());expected=json.loads((old/'result.json').read_text());assert actual.pop('implementation_sha256')==hashlib.sha256(script.read_bytes()).hexdigest();expected.pop('implementation_sha256');assert actual==expected
result={'status':'PASS','exact_diff_match':True,'all_fields_equal_except_implementation_hash':True,'source_script_sha256':hashlib.sha256(script.read_bytes()).hexdigest(),'run':meta}
(p/'cli-comparison.json').write_text(json.dumps(result,indent=2),encoding='utf-8');print(json.dumps(result,indent=2))
