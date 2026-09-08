from pathlib import Path
import hashlib,json
r=Path(__file__).parent;a=r.parent/'astra-all-deletions-recovery-work'
files=[a/n for n in ['proof.md','method.md','uB.json','rB.json','BC.json','uh.json','rh.json','Bh.json','source.diff','recovery-ledger.json']]+[r.parent/'astra-all-deletions-work/plan.md',r.parent/'kemeny-discovery-round-1-work/all-deletions-recovery-amendment.md']+[p for p in r.iterdir() if p.is_file() and p.name!='hashes.json']
(r/'hashes.json').write_text(json.dumps({str(p):hashlib.sha256(p.read_bytes()).hexdigest() for p in files},indent=2))
print('report',hashlib.sha256((r/'report.md').read_bytes()).hexdigest());print('result',hashlib.sha256((r/'result.json').read_bytes()).hexdigest())
