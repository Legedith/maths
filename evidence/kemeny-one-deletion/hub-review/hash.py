from pathlib import Path
import hashlib,json
r=Path(__file__).parent; a=r.parent/'astra-damage-symbolic-work'
files=[r.parent/'kemeny-discovery-round-1-work/one-deletion-proof-contract.md']+[a/n for n in ['proof.md','symbolic.json','checks.json','plan.md','batch2-plan.md','batch1.py','batch2.py']]+[p for p in r.iterdir() if p.is_file() and p.name!='hashes.json']+[r/'.venv/Scripts/python.exe']
(r/'hashes.json').write_text(json.dumps({str(p):hashlib.sha256(p.read_bytes()).hexdigest() for p in files},indent=2))
for p in [a/'proof.md',a/'symbolic.json',r/'evaluate.py',r/'result.json',r/'report.md']: print(p.name,hashlib.sha256(p.read_bytes()).hexdigest())
