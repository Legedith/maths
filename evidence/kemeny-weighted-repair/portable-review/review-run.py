import subprocess,os,json,hashlib
from pathlib import Path
p=Path(__file__).parent;src=Path('D:/CodexWorkspaces/mathematics-atlas/weighted-portable-work')
def read(f):return json.loads(f.read_text(encoding='utf-8-sig'))
checked=[]
for row in read(src/'hashes.json'):
 f=Path(row['Path']);assert hashlib.sha256(f.read_bytes()).hexdigest()==row['Hash'].lower();checked.append(str(f))
for name in ['verify_weighted_repair.py','verify_uniform_repair.py','verify_all_deletions.py','verify_certificate.py','uniform-weighted.json','uniform-noop.json','pyproject.toml','uv.lock','.python-version']:assert (p/name).read_bytes()==(src/name).read_bytes()
assert hashlib.sha256((p/'verify_weighted_repair.py').read_bytes()).hexdigest()=='71e0efbf26f28b4c8b73662fc26e5f123dd285a0f81f266fd50463125b9ccd0d'
assert (src/'attempt1-rc.txt').read_text().strip()==''
assert (src/'attempt2-rc.txt').read_text().strip()=='0'
assert (src/'attempt2-stderr.txt').read_bytes()==b''
assert (src/'check-01.json').read_bytes()==(src/'check-02.json').read_bytes()
Path('input-checks.json').write_text(json.dumps({'worker_hashes_checked':checked,'copies_identical':True,'attempt1_rc_unknown':True,'attempt2_rc_zero_empty_stderr':True,'worker_outputs_equal':True},indent=2))
env=os.environ.copy();env.update(UV_CACHE_DIR=str(p/'uv-cache'),UV_PROJECT_ENVIRONMENT=str(p/'.venv'),UV_PYTHON_INSTALL_DIR='D:/uv-python')
for name,cert,out in [('valid',p/'uniform-weighted.json',p/'replay.json'),('reject',p/'modified.json',p/'rejected-output.json')]:
 if name=='reject':cert.write_bytes((p/'uniform-weighted.json').read_bytes()+b' ')
 argv=['uv','run','--frozen','--project',str(p),'python',str(p/'verify_weighted_repair.py'),'--weighted-certificate',str(cert),'--noop-certificate',str(p/'uniform-noop.json'),'--output',str(out)]
 (p/(name+'-argv.json')).write_text(json.dumps(argv,indent=2))
 try:r=subprocess.run(argv,capture_output=True,env=env,timeout=90);stdout,stderr,rc=r.stdout,r.stderr,r.returncode
 except subprocess.TimeoutExpired as e:stdout,stderr,rc=e.stdout or b'',e.stderr or b'',124
 (p/(name+'.stdout')).write_bytes(stdout);(p/(name+'.stderr')).write_bytes(stderr);(p/(name+'.rc')).write_text(str(rc))
 if name=='valid':assert rc==0;assert out.read_bytes()==(src/'check-02.json').read_bytes()
 else:assert rc==1 and not out.exists() and b'changed frozen uniform certificate' in stderr
 print(name,'expected outcome',rc,flush=True)
Path('result.json').write_text(json.dumps({'pass':True,'replay_exactly_worker_canonical':True,'nine_identities':9,'changed_weighted_certificate_rejected':True,'scope':'portable changed code only; generic analytic proof reused'},indent=2))
