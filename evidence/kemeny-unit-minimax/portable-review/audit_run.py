from pathlib import Path
import hashlib,json,subprocess,os,time
p=Path(__file__).parent;src=p.parent/'unit-minimax-portable-work'
sha=lambda q:hashlib.sha256(q.read_bytes()).hexdigest()
assert sha(p/'verify_unit_minimax.py')=='39100ca08b809d629341326eab55f27278b29ef73243b0a6061003f5a6872a6a'
assert sha(src/'result.json')=='e7d260218dd6ed48700fff61417311d2b10f48f30ec15ef3e8287644a07bcc60'
assert sha(p.parent/'project/docs/kemeny-unit-minimax-contract.md')=='19d4aac28a4df98d217a8a2c57cc8b4a345facaff0e408ef074f30830de0075e'
for row in json.loads((src/'input-hashes.json').read_text(encoding='utf-8-sig')):assert sha(Path(row['Path']))==row['Hash'].lower()
for name in ('verify_unit_minimax.py','pyproject.toml','uv.lock'):assert (p/name).read_bytes()==(src/name).read_bytes()
env=os.environ.copy();env.pop('PYTHONOPTIMIZE',None);env['UV_CACHE_DIR']=str(p/'uv-cache');env['UV_PROJECT_ENVIRONMENT']=str(p/'.venv');env['UV_PYTHON_INSTALL_DIR']='D:/uv-python'
out=p/'fresh-result.json';assert not out.exists()
argv=['uv','run','--frozen','python','verify_unit_minimax.py','--output','fresh-result.json']
for i in (1,2):
 start=time.monotonic()
 try:
  r=subprocess.run(argv,cwd=p,env=env,capture_output=True,timeout=60);rc=r.returncode;stdout=r.stdout;stderr=r.stderr;timed=False
 except subprocess.TimeoutExpired as e:
  rc=124;stdout=e.stdout or b'';stderr=e.stderr or b'';timed=True
 (p/f'run{i}-stdout.bin').write_bytes(stdout);(p/f'run{i}-stderr.bin').write_bytes(stderr)
 (p/f'run{i}.json').write_text(json.dumps({'argv':argv,'cwd':str(p),'rc':rc,'elapsed':time.monotonic()-start,'timeout':60,'timed_out':timed,'assertions_enabled':True,'environment':{k:env[k] for k in ('UV_CACHE_DIR','UV_PROJECT_ENVIRONMENT','UV_PYTHON_INSTALL_DIR')}},indent=2),encoding='utf-8')
 assert rc==(0 if i==1 else 2)
 assert out.read_bytes()==(src/'result.json').read_bytes()
 if i==2:assert b'output already exists' in stderr
raw=out.read_bytes();raw.decode('utf-8');assert b'\r' not in raw and raw.endswith(b'\n')
data=json.loads(raw);assert len(data['midpoint_witness']['candidates'])==10 and len(data['strength_scope_counterexample']['candidates'])==12
summary={'status':'PASS','attempts':2,'fresh_rc':0,'rejection_rc':2,'result_sha256':sha(out),'byte_identical':True,'utf8_lf':True,'all_input_hashes_match':True,'coefficient_counts':[{k:len(v['terms']) for k,v in row['polynomials'].items()} for row in data['unequal_unit_gap']['shifts']]}
(p/'result.json').write_text(json.dumps(summary,indent=2)+'\n',encoding='utf-8');print(json.dumps(summary,indent=2))

