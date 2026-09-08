import json,hashlib
from pathlib import Path
from fractions import Fraction as F
root=Path('D:/CodexWorkspaces/mathematics-atlas/project');out={}
base=F(751,90)
for name,value,delta in [('restore',F(1458,175),F(-41,3150)),('uv',F(90189,10850),F(-1567,48825)),('untouched',F(1462,175),F(31,3150))]:assert value-base==delta;out[name]=str(delta)
r,s,T,m=F(2,7),F(2,49),F(751,630),35
threshold=(m*s-T)/(r*T-s);assert threshold==F(1043,1322);assert r*T-s>0 and T-m*s<0
pairs=[('experiments/kemeny-one-deletion-proof/verify_uniform_repair.py','evidence/kemeny-uniform-repair/portable-review/verify_uniform_repair.py'),('evidence/kemeny-uniform-repair/integration/check-01.json','evidence/kemeny-uniform-repair/portable-review/replay.json'),('experiments/kemeny-one-deletion-proof/verify_certificate.py','evidence/kemeny-uniform-repair/portable-review/verify_certificate.py'),('experiments/kemeny-one-deletion-proof/verify_all_deletions.py','evidence/kemeny-uniform-repair/portable-review/verify_all_deletions.py')]
for a,b in pairs:assert (root/a).read_bytes()==(root/b).read_bytes()
Path('arithmetic.json').write_text(json.dumps({'table_deltas':out,'weighted_threshold':str(threshold),'open_interval_confirmed':True,'four_portable_byte_pairs_match':True},indent=2));print('PASS exact table/threshold and reused portable bytes')
