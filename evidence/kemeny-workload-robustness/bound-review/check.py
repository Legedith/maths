from pathlib import Path
from fractions import Fraction as F
import json,hashlib,sys
root=Path('D:/CodexWorkspaces/mathematics-atlas');out=Path(__file__).parent
author=root/'astra-link-robust-bound-work'
assert hashlib.sha256((author/'proposal.md').read_bytes()).hexdigest()=='fffdd5e73582bf7ed4b396b47f4433f7e139891302a17cd189d90313a30a73e5'
src=root/'astra-workload-effect-work/result.json'
assert hashlib.sha256(src.read_bytes()).hexdigest()=='f7de3722c44e98b2205f0aadc48329640d9688a79c081d3176c95fce07faa64e'
decl=json.loads((author/'result.json').read_text(encoding='utf-8'))['rows'];rows=[]
for old,claim in zip(json.loads(src.read_text(encoding='utf-8'))['rows'],decl):
 scores={tuple(v['edge']):F(v['U']) for v in old['all_missing_edge_U']}
 levels=sorted(set(scores.values()));best,nextbest=levels[:2]
 ratio=nextbest/best;radius=(ratio-1)/(ratio+1)
 opt=sorted(e for e,v in scores.items() if v==best);near=sorted(e for e,v in scores.items() if v==nextbest)
 assert radius==F(claim['strict_epsilon_radius']) and [list(e) for e in opt]==claim['optimal_edges'] and [list(e) for e in near]==claim['nearest_outside_edges']
 assert (radius>F(1,100))==claim['one_percent_strictly_certified']
 rows.append({'parts':old['parts'],'theta':old['theta'],'radius':str(radius),'one_percent':radius>F(1,100)})
assert len(rows)==len(decl)==8
# Read-only hash checks for actual source returns and reused source attestations.
checks=[]
for file in [root/'astra-link-robust-priority-work/hashes.json',root/'astra-link-robust-priority-work/reused-input-hashes.json']:
 for entry in json.loads(file.read_text(encoding='utf-8-sig')):
  p=Path(entry['Path']);actual=hashlib.sha256(p.read_bytes()).hexdigest()
  assert actual==entry['Hash'].lower()
  checks.append({'path':str(p),'sha256':actual})
result={'radii':rows,'source_hashes':checks,'python':sys.version}
(out/'result.json').write_text(json.dumps(result,indent=2),encoding='utf-8');print(json.dumps(result,indent=2))

