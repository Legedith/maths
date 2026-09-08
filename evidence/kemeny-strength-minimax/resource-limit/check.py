import sys,json
from pathlib import Path
import sympy as S
p=Path(__file__).resolve().parent
sys.path.insert(0,str(p.parent/'strength-minimax-portable-work'))
from strength_minimax import solve,compare,encode_certificate
lab=[0]*3+[1]*4+[2]*4+[3]
edges=[(i,j,1) for i in range(12) for j in range(i+1,12) if lab[i]!=lab[j] and (i,j)!=(0,11)]
allowed=[(i,j) for i in range(12) for j in range(i+1,12) if (i,j,1) not in edges]
res=solve(12,edges,11,(0,'9/10'),allowed)
O=res['oracle_endpoint_f'];T=res['T_endpoints'];m=res['old_volume']
base=[m*t/o-1 for t,o in zip(T,O)]
assert compare(base[1],base[0])>0
g=next(g for g in res['classes'] if (3,4) in g['edges'])
derivatives=[a/o for a,o in zip(g['A_endpoints'],O)]
assert compare(derivatives[0])<0 and compare(derivatives[1])>0
assert compare(g['optimum']['strength'])==0
result={'status':'PASS','graph':[3,4,4],'interval':['0','9/10'],'baseline_endpoint_regrets':base,'active_endpoints':['right'],'endpoint_oracles_f':O,'BC_normalized_derivatives':derivatives,'BC_optimal_strength':g['optimum']['strength'],'global_actions':res['global_actions'],'scope':'per-edge unnecessary-condition counterexample, not global no-action example'}
(p/'result.json').write_text(json.dumps(encode_certificate(result),indent=2,sort_keys=True)+'\n',encoding='utf-8');print('PASS: BC edge optimum zero with negative inactive endpoint derivative')
