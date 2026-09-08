import subprocess,json,hashlib,os,time
from pathlib import Path
p=Path(__file__).parent;src=p.parent/'workload-action-portable-work';script=p/'verify_action_choice.py'
assert hashlib.sha256(script.read_bytes()).hexdigest()=='fff7fffc1453b00e9d4d2cca7e815e088f0a5da793e7da0f884ba762ce8f21ce'
assert hashlib.sha256((src/'result.json').read_bytes()).hexdigest()=='42a1da543576b44036eb2b55521e0e873aa8825fdb6a2c7e53fdfac2efa886f1'
env=os.environ.copy();env.update(UV_CACHE_DIR=str(p/'uv-cache'),UV_PROJECT_ENVIRONMENT=str(p/'.venv'),UV_PYTHON_INSTALL_DIR='D:/uv-python')
argv=['uv','run','--project',str(p),'--frozen','python',str(script),'--output',str(p/'fresh.json')]
records=[]
for attempt in [1,2]:
 start=time.monotonic()
 try:r=subprocess.run(argv,cwd=p,env=env,capture_output=True,timeout=60);o,e,rc=r.stdout,r.stderr,r.returncode
 except subprocess.TimeoutExpired as ex:o,e,rc=ex.stdout or b'',ex.stderr or b'',124
 (p/f'attempt{attempt}.stdout.bin').write_bytes(o);(p/f'attempt{attempt}.stderr.bin').write_bytes(e);meta={'argv':argv,'cwd':str(p),'rc':rc,'timeout':60,'elapsed':time.monotonic()-start,'environment':{k:env[k] for k in ['UV_CACHE_DIR','UV_PROJECT_ENVIRONMENT','UV_PYTHON_INSTALL_DIR']}};(p/f'attempt{attempt}.json').write_text(json.dumps(meta,indent=2),encoding='utf-8');records.append(meta)
 if attempt==1:
  assert rc==0
  raw=(p/'fresh.json').read_bytes();assert raw==(src/'result.json').read_bytes();saved=hashlib.sha256(raw).hexdigest()
 else:
  assert rc==2 and b'output already exists' in e;assert hashlib.sha256((p/'fresh.json').read_bytes()).hexdigest()==saved
result={'status':'PASS','fresh_byte_equality':True,'existing_output_rc':2,'existing_output_unchanged':True,'result_sha256':saved,'attempts':records}
(p/'comparison.json').write_text(json.dumps(result,indent=2),encoding='utf-8');print(json.dumps(result,indent=2))
