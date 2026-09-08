from __future__ import annotations

import hashlib
import json
from pathlib import Path

from copy_reviewed_evidence import BASE, PROJECT, contained, copy_one


source_root = BASE / 'msc-product-review-work'
target_root = PROJECT / 'evidence/msc-classification/product-review'
manifest_path = source_root / 'publication-manifest.json'
assert hashlib.sha256(manifest_path.read_bytes()).hexdigest() == '276f99ecee69ce233746961a0edba709cf4634f7e6198a5831ae4dd0e7c49e3c'
assert not target_root.exists()
manifest = json.loads(manifest_path.read_text(encoding='utf-8-sig'))
plan = []
for row in manifest['copy_records']:
    assert row['copy'] is True
    source = contained(source_root, row['path'])
    assert source.stat().st_size == row['bytes']
    assert hashlib.sha256(source.read_bytes()).hexdigest() == row['sha256']
    plan.append((source, contained(target_root, row['path'])))
for name in ['publication-manifest.json', 'review-seal.json']:
    if all(destination.name != name for _, destination in plan):
        plan.append((source_root / name, target_root / name))
records = []
for source, destination in plan:
    copy_one(source, destination, records)
report = {'schema_version': 'msc-publication-copy-v2', 'producer': 'root', 'files': records, 'external_records': manifest.get('external_records', []), 'scope': 'Exact copies of the independently sealed browser review. External records remain linked to their separately published or local frozen artifacts.'}
with (PROJECT / 'evidence/msc-classification/publication-copy-02.json').open('x', encoding='utf-8', newline='\n') as stream:
    json.dump(report, stream, indent=2)
    stream.write('\n')
print(json.dumps({'copied': len(records), 'target': str(target_root)}))
