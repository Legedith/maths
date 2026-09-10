import sympy as S,json,hashlib,sys
from pathlib import Path
B=Path('D:/CodexWorkspaces/mathematics-atlas');A=B/'astra-hitting-growth-explore-work'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
pins={}
for r in json.loads((A/'hashes.json').read_text(encoding='utf-8-sig')):
 p=Path(r['Path']);assert sha(p)==r['Hash'].lower();pins[str(p)]=sha(p)
pins[str(A/'hashes.json')]=sha(A/'hashes.json')
assert pins[str(A/'hashes.json')]=='7b8365b88862cc91ad077944ca102bdc85b3163dd8ab766e97fdf5e0e8bc8289'
logger=B/'project/experiments/kemeny-three-part-proof/run_logged.py';pins[str(logger)]=sha(logger)
assert pins[str(logger)]=='b6f4c329387705b2adf67f7dd3f806bbcd0a5906d476f5214fe8278d5ea5bfa6'
log=json.loads((A/'logs/attempt-growth01.json').read_text());assert log['returncode']==0 and not log['timed_out']
for k in ['stdout','stderr']:
 p=A/'logs'/log[k]['path'];assert sha(p)==log[k]['sha256'] and len(p.read_bytes())==log[k]['bytes']
t=S.symbols('t',nonnegative=True);hs=S.symbols('h0:4');out=[]
auth=json.loads((A/'result.json').read_text())
for index,(name,edges,source) in enumerate([('star',[(0,1),(1,2),(1,3)],3),('path',[(0,1),(1,2),(2,3)],1)]):
 W=S.zeros(4)
 for i,j in edges:W[i,j]=W[j,i]=1
 W[0,2]=W[2,0]=t
 row={'graph':name,'hitting':[],'slopes':[]}
 for b in range(4):
  eq=[hs[b]]+[hs[i]-1-sum(W[i,j]*hs[j] for j in range(4))/sum(W[i,j] for j in range(4)) for i in range(4) if i!=b]
  sol=S.solve(eq,hs);assert all(S.cancel(e.subs(sol))==0 for e in eq)
  f=S.cancel(sol[hs[source]]);expected=S.sympify(auth[index]['hitting'][b],locals={'t':t});assert S.cancel(f-expected)==0
  slope=S.limit(f/t,t,S.oo);assert str(slope)==auth[index]['linear_slopes'][b]
  row['hitting'].append(str(f));row['slopes'].append(str(slope))
 out.append(row)
assert out[0]['slopes']==['0']*4 and out[1]['slopes']==['0','0','0','2']
assert sys.version_info[:3]==(3,12,11) and S.__version__=='1.14.0'
result={'status':'pass','method':'directed transition first-step equations','rows':out,'input_hashes':pins,'python':sys.version,'sympy':S.__version__,'code_sha256':sha(Path(__file__))}
with Path('result.json').open('x',encoding='utf-8',newline='\n') as f:json.dump(result,f,indent=2,sort_keys=True);f.write('\n')
print('PASS all eight exact hitting functions and slopes; manifest and raw hashes')
