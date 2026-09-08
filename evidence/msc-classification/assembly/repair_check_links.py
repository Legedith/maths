from __future__ import annotations

import hashlib
import json
from pathlib import Path

BASE = Path('D:/CodexWorkspaces/mathematics-atlas')
PROJECT = BASE / 'project'
WORK = BASE / 'msc-product-work'
bundle_path = PROJECT / '.codex/evidence/runs/msc-classification-v1/bundle.json'
assert hashlib.sha256(bundle_path.read_bytes()).hexdigest() == '57516686bab492c0a48b04534d8e8f6907b75245d47c2657d6fbad83a12beb4a'
bundle = json.loads(bundle_path.read_text(encoding='utf-8'))
by_path = {row['path']: row['id'] for row in bundle['artifacts']}
links = {
    'specification_compliance': ['docs/subject-browser-contract.md', 'experiments/msc-index/contract-v1.md'],
    'source_verification': ['experiments/msc-index/inputs/source-manifest.json', 'experiments/msc-index/inputs/raw/official.csv', 'experiments/msc-index/inputs/raw/suggestion4.ttl', 'data/msc/LICENSE-CC-BY-NC-SA-4.0.md'],
    'implementation_alignment': ['lib/subject-index.ts', 'experiments/msc-index/import_msc.py', 'evidence/msc-classification/adapter-review/logs/canonical-replay-01.json'],
}
for check in bundle['checks']:
    check['evidence'].extend(by_path[path] for path in links.get(check['id'], []))
    check['note'] += ' Direct typed specification, source and implementation evidence is linked alongside the independent reports.'
assembly = PROJECT / 'evidence/msc-classification/assembly'
copies = [(path, assembly / path.name) for path in sorted((WORK / 'gate-logs').glob('attempt-msc-gate-01*'))]
copies.extend((WORK / name, assembly / name) for name in ['prepare_bundle_draft.py', 'complete_bundle.py', 'copy_product_review.py', 'repair_check_links.py'])
for source, destination in copies:
    with destination.open('xb') as stream:
        stream.write(source.read_bytes())
    relative = destination.relative_to(PROJECT).as_posix()
    bundle['artifacts'].append({'id': f'A{len(bundle["artifacts"])+1:03d}', 'kind': 'code' if destination.suffix == '.py' else 'log', 'path': relative, 'sha256': hashlib.sha256(destination.read_bytes()).hexdigest(), 'producer': 'root'})
correction = {'schema_version': 'typed-evidence-link-correction-v1', 'producer': 'root', 'prior_bundle_sha256': '57516686bab492c0a48b04534d8e8f6907b75245d47c2657d6fbad83a12beb4a', 'failure': 'Gate 01 required direct spec/source/code-or-log artifacts in the corresponding check evidence lists; only independent reports had been linked.', 'change': 'Added references to already hashed and independently reviewed artifacts, plus retained packaging code and failure logs. No existing artifact bytes, claim statements, product code or data changed.', 'independent_semantic_decisions': 'The same sealed source, adapter and product reports remain the basis of the four decisions.'}
correction_path = assembly / 'check-evidence-link-correction.json'
with correction_path.open('x', encoding='utf-8', newline='\n') as stream:
    json.dump(correction, stream, indent=2)
    stream.write('\n')
bundle['artifacts'].append({'id': f'A{len(bundle["artifacts"])+1:03d}', 'kind': 'report', 'path': correction_path.relative_to(PROJECT).as_posix(), 'sha256': hashlib.sha256(correction_path.read_bytes()).hexdigest(), 'producer': 'root'})
payload = (json.dumps(bundle, ensure_ascii=False, indent=2) + '\n').encode('utf-8')
bundle_path.write_bytes(payload)
with (WORK / 'bundle-final-candidate-02.json').open('xb') as stream:
    stream.write(payload)
print(json.dumps({'artifacts': len(bundle['artifacts']), 'claims': len(bundle['claims']), 'sha256': hashlib.sha256(payload).hexdigest()}))
