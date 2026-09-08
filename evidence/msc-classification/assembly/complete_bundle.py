from __future__ import annotations

import hashlib
import json
from pathlib import Path

BASE = Path('D:/CodexWorkspaces/mathematics-atlas')
PROJECT = BASE / 'project'
WORK = BASE / 'msc-product-work'
bundle_path = PROJECT / '.codex/evidence/runs/msc-classification-v1/bundle.json'
bundle = json.loads((WORK / 'bundle-draft-01.json').read_text(encoding='utf-8'))
for row in bundle['artifacts']:
    assert hashlib.sha256((PROJECT / row['path']).read_bytes()).hexdigest() == row['sha256'], row['path']
by_path = {row['path']: row['id'] for row in bundle['artifacts']}
new_paths = sorted({path.relative_to(PROJECT).as_posix() for path in (PROJECT / 'evidence/msc-classification/product-review').rglob('*') if path.is_file()} | {'docs/subject-browser-verification.md', 'evidence/msc-classification/publication-copy-02.json'})
for relative in new_paths:
    assert relative not in by_path
    path = PROJECT / relative
    kind = 'log' if path.suffix == '.bin' or '/logs/' in relative else 'code' if path.suffix == '.py' else 'report' if path.suffix == '.md' else 'result'
    identifier = f'A{len(bundle["artifacts"])+1:03d}'
    bundle['artifacts'].append({'id': identifier, 'kind': kind, 'path': relative, 'sha256': hashlib.sha256(path.read_bytes()).hexdigest(), 'producer': '/root/sol_atlas_audit' if '/product-review/' in relative else 'root'})
    by_path[relative] = identifier
product_path = 'evidence/msc-classification/product-review/final-msc-product-audit.json'
adapter_path = 'evidence/msc-classification/adapter-review/final-audit.json'
source_path = 'evidence/msc-classification/source-review/final-audit.json'
product = json.loads((PROJECT / product_path).read_text(encoding='utf-8-sig'))
adapter = json.loads((PROJECT / adapter_path).read_text(encoding='utf-8-sig'))
assert product['recommendation'] == 'PASS_FOR_SCOPED_SUBJECT_BROWSER_PRODUCT'
assert product['unresolved_substantive_findings'] == []
assert adapter['recommendation'] == 'PASS_FOR_SCOPED_DATA_ADAPTER'
for check in bundle['checks']:
    p = next(item for item in product['checks'] if item['id'] == check['id'])
    a = next(item for item in adapter['checks'] if item['id'] == check['id'])
    assert p['status'] in {'PASS', 'PASS_SCOPED'} and a['status'] == 'PASS'
    check.update({'status': 'pass', 'auditor': '/root/sol_symmetry_audit (source/adapter) and /root/sol_atlas_audit (product)', 'evidence': [by_path[source_path], by_path[adapter_path], by_path[product_path]], 'note': 'Transcribes the sealed independent source/adapter and product decisions. Product source verification is scoped to the separately approved exact adapter bytes; together these reviews cover the raw-source-to-browser chain. Their stated limits remain in force.'})
bundle['claims'].append({'id': 'C009', 'type': 'numerical', 'statement': 'The independently reviewed browser run issued 971 HTTP requests and the final product audit has no unresolved substantive findings. This is functional HTTP and source-to-product verification, not general visual evaluation.', 'status': 'supported', 'supports': [{'artifact_id': by_path[product_path], 'locator': 'json:/verified_observations/independent_http_requests', 'expected': 971}, {'artifact_id': by_path[product_path], 'locator': 'json:/unresolved_substantive_findings', 'expected': []}]})
bundle['limitations'][0] = 'Final release promotion remains subject to the separate independent claim/provenance acknowledgement; no author self-certification is substituted for the sealed reviews.'
old = WORK / 'bundle-initial.json'
assert not old.exists()
old.write_bytes(bundle_path.read_bytes())
payload = (json.dumps(bundle, ensure_ascii=False, indent=2) + '\n').encode('utf-8')
bundle_path.write_bytes(payload)
snapshot = WORK / 'bundle-final-candidate-01.json'
with snapshot.open('xb') as stream:
    stream.write(payload)
print(json.dumps({'artifacts': len(bundle['artifacts']), 'claims': len(bundle['claims']), 'sha256': hashlib.sha256(payload).hexdigest(), 'checks': [row['status'] for row in bundle['checks']]}))
