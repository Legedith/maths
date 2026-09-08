from __future__ import annotations

import hashlib
import json
from pathlib import Path

BASE = Path('D:/CodexWorkspaces/mathematics-atlas')
PROJECT = BASE / 'project'
WORK = BASE / 'msc-product-work'
REVIEW = BASE / 'msc-promotion-review-work'
DEST = PROJECT / 'evidence/msc-classification/promotion-review'
bundle_path = PROJECT / '.codex/evidence/runs/msc-classification-v1/bundle.json'
prior_hash = 'f57ccfddf20064d1df481e289925f09b66657ce604f1047d8dce8ba9ba8d9e49'
manifest_hash = 'eab4bb969fabf3f15bb0e1097d06451ea9627efa2efd44fe032e2dabf0921a9a'
assert hashlib.sha256(bundle_path.read_bytes()).hexdigest() == prior_hash
manifest_path = REVIEW / 'publication-manifest.json'
assert hashlib.sha256(manifest_path.read_bytes()).hexdigest() == manifest_hash
manifest = json.loads(manifest_path.read_text(encoding='utf-8-sig'))
assert manifest['recommendation'] == 'PASS_FOR_SCOPED_MSC_PROMOTION_EVIDENCE'
assert manifest['unresolved_findings'] == 0
bundle = json.loads(bundle_path.read_text(encoding='utf-8'))
plan = []
for record in manifest['copy_records']:
    source = (REVIEW / record['path']).resolve()
    destination = (DEST / record['path']).resolve()
    assert source.is_relative_to(REVIEW.resolve()) and destination.is_relative_to(DEST.resolve())
    raw = source.read_bytes()
    assert len(raw) == record['bytes']
    assert hashlib.sha256(raw).hexdigest() == record['sha256']
    plan.append((source, destination, '/root/sol_symmetry_worker'))
plan.append((manifest_path, DEST / manifest_path.name, '/root/sol_symmetry_worker'))
for name in ['add_claim_locators.py', 'claim-locator-correction-03.json', 'append_promotion_review.py']:
    plan.append((WORK / name, PROJECT / 'evidence/msc-classification/assembly' / name, 'root'))
for attempt in ['attempt-msc-gate-02', 'attempt-msc-gate-03']:
    for suffix in ['.json', '.stdout.bin', '.stderr.bin']:
        source = WORK / 'gate-logs' / (attempt + suffix)
        plan.append((source, PROJECT / 'evidence/msc-classification/assembly' / source.name, 'root'))
assert len({str(dest) for _, dest, _ in plan}) == len(plan)
assert not any(dest.exists() for _, dest, _ in plan)
records = []
for source, destination, producer in plan:
    raw = source.read_bytes()
    destination.parent.mkdir(parents=True, exist_ok=True)
    with destination.open('xb') as output:
        output.write(raw)
    relative = destination.relative_to(PROJECT).as_posix()
    digest = hashlib.sha256(raw).hexdigest()
    kind = 'code' if destination.suffix == '.py' else 'log' if destination.suffix == '.bin' or '/logs/' in relative else 'report' if 'review.json' in relative or destination.suffix == '.md' else 'result'
    bundle['artifacts'].append({'id': f'A{len(bundle["artifacts"])+1:03d}', 'kind': kind, 'path': relative, 'sha256': digest, 'producer': producer})
    records.append({'source': str(source), 'path': relative, 'bytes': len(raw), 'sha256': digest, 'producer': producer})
receipt = {'schema_version': 'msc-final-additive-promotion-v1', 'producer': 'root', 'independently_reviewed_candidate_sha256': prior_hash, 'review_manifest_sha256': manifest_hash, 'change': 'Append exact sealed independent promotion artifacts and retained assembly correction/check history. All prior artifact records, nine claims and supports, four check records and limitations remain unchanged.', 'files': records}
receipt_path = PROJECT / 'evidence/msc-classification/publication-copy-03.json'
with receipt_path.open('x', encoding='utf-8', newline='\n') as output:
    json.dump(receipt, output, indent=2)
    output.write('\n')
bundle['artifacts'].append({'id': f'A{len(bundle["artifacts"])+1:03d}', 'kind': 'report', 'path': receipt_path.relative_to(PROJECT).as_posix(), 'sha256': hashlib.sha256(receipt_path.read_bytes()).hexdigest(), 'producer': 'root'})
payload = (json.dumps(bundle, ensure_ascii=False, indent=2) + '\n').encode('utf-8')
with (WORK / 'bundle-final-candidate-04.json').open('xb') as output:
    output.write(payload)
bundle_path.write_bytes(payload)
print(json.dumps({'sha256': hashlib.sha256(payload).hexdigest(), 'artifacts': len(bundle['artifacts']), 'claims': len(bundle['claims']), 'copied': len(records)}))
