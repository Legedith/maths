from pathlib import Path
import hashlib,json
from collections import Counter
S=Path('D:/CodexWorkspaces/mathematics-atlas/kemeny-source-target-work')
P=S.parent/'project'; O=Path(__file__).parent
head='ba90dd8fceb136cc757b06b9511e3aebc9b515fb'
art=[]
def record(p,kind):
 b=p.read_bytes(); art.append(dict(id=f'A{len(art)+1:03}',kind=kind,path=str(p),sha256=hashlib.sha256(b).hexdigest()));return b
def js(p,kind='log'):return json.loads(record(p,kind))
def sha(b):return hashlib.sha256(b).hexdigest()
status=js(S/'ci-status-01.json');raw=record(S/'ci-status-01.stdout.bin','source')
assert sha(raw)==status['stdout_sha256'];assert sha(record(S/'ci-status-01.stderr.bin','log'))==status['stderr_sha256'];assert status['returncode']==0
runs=json.loads(raw)['workflow_runs'];assert len(runs)==12
assert Counter(r['event'] for r in runs)=={'push':6,'pull_request':6}
assert all(r['head_sha']==head and r['status']=='completed' and r['conclusion']=='success' for r in runs)
assert all(Counter(r['name'] for r in runs if r['event']==e)==Counter(r['name'] for r in runs if r['event']=='push') for e in ['pull_request'])
assert len(set(r['name'] for r in runs))==6
reference=record(P/'evidence/kemeny-source-target/integration/check-01.json','result');assert sha(reference)=='cbb643c5f3fb79f2df2af5d51744c56ae4908bd5aaba66b82bacfdf3ed0fcfc7'
comparison=js(S/'ci-download-comparison.json','result');record(S/'ci.py','code')
for rid in [34276950678,34276943554]:
 d=js(S/f'ci-download-{rid}.json');assert d['returncode']==0
 for stream in ['stdout','stderr']:assert sha(record(S/f'ci-download-{rid}.{stream}.bin','log'))==d[f'{stream}_sha256']
 dest=S/'ci'/str(rid);b=record(dest/'check.json','result');assert b==reference
 check=json.loads(b);assert check['runtime']=={'python':'3.12.11','sympy':'1.14.0'}
 assert check['direct_first_step_comparisons']==30 and check['symbolic_identities']==3 and len(check['root_degeneracies'])==7 and check['invalid_rejections']==7
 assert set(check['module_hashes'])=={'source_target_minimax.py','verify_source_target.py','exact_support.py'}
 for name,digest in check['module_hashes'].items():assert sha(record(P/'experiments/kemeny-source-target-proof'/name,'code'))==digest
 log=js(dest/'logs/attempt-source-target.json');assert log['returncode']==0 and log['timed_out'] is False and log['timeout_seconds']==90
 assert log['argv'][:6]==['uv','run','--project','experiments/kemeny-source-target-proof','--frozen','python']
 for stream in ['stdout','stderr']:
  b=record(dest/'logs'/log[stream]['path'],'log');assert sha(b)==log[stream]['sha256'] and len(b)==log[stream]['bytes']
 record(dest/'logs/attempts.jsonl','log')
 for f in d['files']:
  b=(dest/f['path']).read_bytes();assert sha(b)==f['sha256'] and len(b)==f['bytes']
workflow=record(P/'.github/workflows/kemeny-three-part.yml','code').decode()
assert 'uv run --project experiments/kemeny-source-target-proof --frozen python' in workflow
bundle=record(P/'.codex/evidence/runs/kemeny-source-target-v1/bundle.json','report');assert sha(bundle)=='3aa645f02fcd789f62c05b1e6d3e1a8c7824f4d395f8bb17e34196192247f93e'
checks=[
 dict(id='reproduction',status='pass',type='numerical',note='Two downloaded hosted check.json artifacts independently byte-compared with integration/check-01.json; SHA256 cbb643c5f3fb79f2df2af5d51744c56ae4908bd5aaba66b82bacfdf3ed0fcfc7. Both JSON pointers /direct_first_step_comparisons=30, /symbolic_identities=3, /invalid_rejections=7 and /root_degeneracies length=7.'),
 dict(id='specification_compliance',status='pass',type='conclusion',note='Raw ci-status-01.stdout.bin JSON /workflow_runs contains exactly 12 completed successful records, six unique workflows each on push and pull_request, all /head_sha equal the audited head. Scope is the retained PR16 hosted CI packet.'),
 dict(id='source_verification',status='pass',type='citation',note='Raw gh API stdout SHA matches ci-status-01.json /stdout_sha256. Both download receipt /returncode=0 and stream SHA256 values match retained bytes. Artifact file hashes match receipt /files; no live GitHub refresh was performed.'),
 dict(id='implementation_alignment',status='pass',type='methodological',note='Both outputs /module_hashes have exactly three entries, independently matching experiments/kemeny-source-target-proof files. Runtime /runtime pins Python 3.12.11 and SymPy 1.14.0. Raw attempt logs /argv use child uv, /returncode=0, /timed_out=false, /timeout_seconds=90. Workflow kemeny-three-part.yml lines 199-215 uses outer uv and retains artifacts.')]
for c in checks:c['auditor']='independent Astra wrap verifier';c['evidence']=[a['id'] for a in art]
verdict=dict(status='PASS',head=head,checks=checks,limitations=['Audit of retained hosted CI packet; no proof rerun or live API refresh.','Does not attest novelty, practical impact, all-mathematics completion, or a later release head.'])
(O/'ci-verdict.json').write_text(json.dumps(verdict,indent=2)+'\n')
(O/'ci-review.md').write_text('# PR16 hosted CI audit\n\nPASS for head `'+head+'`.\n\n'+'\n\n'.join('**'+c['id']+' (pass):** '+c['note'] for c in checks)+'\n\nAudited bundle SHA256: `'+sha(bundle)+'`.\n\nNo proof evaluator was rerun. This review covers retained hosted CI evidence only, not novelty, practical impact, later heads, or completion of mathematics. Exact input paths and independently computed hashes are in ci-manifest.json.\n')
record(O/'ci-verdict.json','report');record(O/'ci-review.md','report');record(Path(__file__),'code')
(O/'ci-manifest.json').write_text(json.dumps(dict(schema_version='1.0',artifacts=art),indent=2)+'\n')
print(json.dumps(dict(status='PASS',artifacts=len(art),checks=len(checks))))
