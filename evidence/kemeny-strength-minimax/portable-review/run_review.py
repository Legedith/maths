from pathlib import Path
import hashlib,json,subprocess,os,time
p=Path(__file__).parent;src=p.parent/'strength-minimax-portable-work'
sha=lambda q:hashlib.sha256(q.read_bytes()).hexdigest()
for name,h in {'strength_minimax.py':'11152f62717a691450361c4227a70eb7674e65b1c3bb3d5889464956898ad1a9','verify_strength_minimax.py':'4b648d90676f564b2ae12aa39b0ee1be7144f547e39bda3671b3f1813d22ae01','result.json':'734c9f73753f2ab07232ab8dbf2a1583b42565e88623f9b50d7779aba904665b'}.items():assert sha(src/name)==h
for row in json.loads((src/'input-hashes.json').read_text(encoding='utf-8-sig')):assert sha(Path(row['Path']))==row['Hash'].lower()
for name in ('strength_minimax.py','verify_strength_minimax.py','pyproject.toml','uv.lock'):assert (p/name).read_bytes()==(src/name).read_bytes()
env=os.environ.copy();env.pop('PYTHONOPTIMIZE',None);env['UV_CACHE_DIR']=str(p/'uv-cache');env['UV_PROJECT_ENVIRONMENT']=str(p/'.venv');env['UV_PYTHON_INSTALL_DIR']='D:/uv-python'
out=p/'fresh-result.json';assert not out.exists()
argv=['uv','run','--frozen','python','verify_strength_minimax.py','--output','fresh-result.json']
for i in (1,2):
 start=time.monotonic()
 try:
  r=subprocess.run(argv,cwd=p,env=env,capture_output=True,timeout=90);rc=r.returncode;stdout=r.stdout;stderr=r.stderr;timed=False
 except subprocess.TimeoutExpired as e:rc=124;stdout=e.stdout or b'';stderr=e.stderr or b'';timed=True
 (p/f'run{i}-stdout.bin').write_bytes(stdout);(p/f'run{i}-stderr.bin').write_bytes(stderr)
 (p/f'run{i}.json').write_text(json.dumps({'argv':argv,'cwd':str(p),'rc':rc,'elapsed':time.monotonic()-start,'timeout':90,'timed_out':timed,'environment':{k:env[k] for k in ('UV_CACHE_DIR','UV_PROJECT_ENVIRONMENT','UV_PYTHON_INSTALL_DIR')},'assertions_enabled':True},indent=2),encoding='utf-8')
 assert rc==(0 if i==1 else 2)
 assert out.read_bytes()==(src/'result.json').read_bytes()
 if i==2:assert b'output already exists' in stderr
raw=out.read_bytes();raw.decode('utf-8');assert b'\r' not in raw and raw.endswith(b'\n')
data=json.loads(raw);assert sum(data['direct_grounded_objective_checks'].values())==80
summary={'status':'PASS','attempts':2,'replay_rc':0,'rejection_rc':2,'byte_identical':True,'utf8_lf':True,'input_hashes_match':True,'output_sha256':sha(out),'direct_checks':data['direct_grounded_objective_checks'],'invalid_count':data['invalid_inputs_rejected'],'abstract_balance_count':len(data['balance_degeneracies'])}
(p/'result.json').write_text(json.dumps(summary,indent=2)+'\n',encoding='utf-8');print(json.dumps(summary))

