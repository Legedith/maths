import json,hashlib
from fractions import Fraction as F
from pathlib import Path
root=Path('D:/CodexWorkspaces/mathematics-atlas');out=Path(__file__).parent
inputs={'astra-workload-effect-work/result.json':'f7de3722c44e98b2205f0aadc48329640d9688a79c081d3176c95fce07faa64e','astra-workload-effect-review-work/review.md':'9988c53d13c275d8dd00a4c987cc89aea972014697d55efaa51239d5ebbb8d65'}
for name,h in inputs.items():assert hashlib.sha256((root/name).read_bytes()).hexdigest()==h
rows=[]
for row in json.loads((root/'astra-workload-effect-work/result.json').read_text())['rows']:
 scores=[(rec['edge'],F(rec['U'])) for rec in row['all_missing_edge_U']];star=min(v for e,v in scores);opt=[e for e,v in scores if v==star];outside=[(e,v) for e,v in scores if v>star];runner=min(v for e,v in outside);radius=(runner-star)/(runner+star)
 assert star==F(row['forced_optimal']) and opt==row['forced_optimal_edges']
 rows.append({'parts':row['parts'],'theta':row['theta'],'optimal_edges':opt,'nearest_outside_edges':[e for e,v in outside if v==runner],'Ustar':str(star),'Uoutside':str(runner),'strict_epsilon_radius':str(radius),'radius_at_least_one_percent':radius>=F(1,100),'one_percent_strictly_certified':radius>F(1,100)})
result={'inputs':inputs,'rows':rows,'H2_all_radii_at_least_one_percent':all(r['radius_at_least_one_percent'] for r in rows),'scope':'radii certify sufficient simultaneous perturbation bounds, not failure thresholds'}
(out/'result.json').write_text(json.dumps(result,indent=2),encoding='utf-8');print(json.dumps(result,indent=2))
