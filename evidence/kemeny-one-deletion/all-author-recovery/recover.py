import subprocess,sys,json,time,difflib,hashlib
from pathlib import Path
before=Path('batch2-before.py').read_text();after=Path('batch2.py').read_text()
Path('source.diff').write_text(''.join(difflib.unified_diff(before.splitlines(True),after.splitlines(True),fromfile='frozen/batch2.py',tofile='recovery/batch2.py')))
Path('input-hashes.json').write_text(json.dumps({p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in map(Path,['batch1.py','batch2-before.py','batch2.py','amendment.md','recover.py'])},indent=2))
ledger=[]
for case in ['uB','rB','BC','uh','rh','Bh']:
 argv=[sys.executable,'batch2.py',case];start=time.time()
 try:
  r=subprocess.run(argv,stdout=subprocess.PIPE,stderr=subprocess.PIPE,text=True,timeout=300)
  stdout,stderr,rc=r.stdout,r.stderr,r.returncode
 except subprocess.TimeoutExpired as ex:
  stdout=ex.stdout or '';stderr=ex.stderr or '';rc=124
  if isinstance(stdout,bytes):stdout=stdout.decode(errors='replace')
  if isinstance(stderr,bytes):stderr=stderr.decode(errors='replace')
 elapsed=time.time()-start
 Path(case+'.stdout').write_text(stdout);Path(case+'.stderr').write_text(stderr)
 item={'case':case,'argv':argv,'seconds':elapsed,'rc':rc}
 if rc==0:
  cert=json.loads(Path(case+'.json').read_text());item.update(numerator_positive=cert['numerator_positive'],denominator_positive=cert['denominator_positive'])
 ledger.append(item);Path('recovery-ledger.json').write_text(json.dumps(ledger,indent=2));print(item,flush=True);print(stdout,flush=True)
status=0 if all(r['rc']==0 and r.get('numerator_positive') and r.get('denominator_positive') for r in ledger) else 1
Path('aggregate.rc').write_text(str(status));sys.exit(status)
