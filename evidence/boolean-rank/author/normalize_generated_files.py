"""Correct Windows output newlines without changing parsed source values."""
import hashlib
import json
from pathlib import Path

BASE = Path('D:/CodexWorkspaces/mathematics-atlas')
PROJECT = BASE / 'project'
WORK = BASE / 'boolean-rank-integration-work'


def sha(data):
    return hashlib.sha256(data).hexdigest()


records = []
for name in ['data/atlas.json', 'README.md', 'evidence/boolean-rank/integration-projection.json']:
    path = PROJECT / name
    before = path.read_bytes()
    after = before.replace(b'\r\n', b'\n')
    if name.endswith('.json') and json.loads(before) != json.loads(after):
        raise ValueError('JSON changed during newline correction')
    if before.decode().splitlines() != after.decode().splitlines():
        raise ValueError('Text lines changed')
    path.write_bytes(after)
    records.append({'path': name, 'before_sha256': sha(before), 'after_sha256': sha(after), 'text_lines_unchanged': True, 'json_value_unchanged': name.endswith('.json')})
report = {
    'scope': 'Line endings only for three root-generated files. Pinned source/design artifacts are unchanged.',
    'reason': 'Python write_text default newline translation introduced CRLF against the LF base source.',
    'records': records,
    'preserved_attempt_01': 'history/attempt-01',
}
(WORK / 'newline-correction.json').write_bytes((json.dumps(report, indent=2) + '\n').encode())
freeze = json.loads((WORK / 'implementation-freeze-v1.json').read_text())
freeze['schema_version'] = 'boolean-rank-implementation-freeze-v2'
freeze['supersedes'] = {'path': 'implementation-freeze-v1.json', 'sha256': sha((WORK / 'implementation-freeze-v1.json').read_bytes())}
freeze['correction'] = {'path': 'newline-correction.json', 'sha256': sha((WORK / 'newline-correction.json').read_bytes())}
for record in freeze['files']:
    data = (PROJECT / record['path']).read_bytes()
    if record['path'] not in [item['path'] for item in records] and sha(data) != record['sha256']:
        raise ValueError(f'Unexpected concurrent change: {record["path"]}')
    record['sha256'], record['bytes'] = sha(data), len(data)
target = WORK / 'implementation-freeze-v2.json'
if target.exists():
    raise FileExistsError(target)
target.write_bytes((json.dumps(freeze, indent=2) + '\n').encode())
print(json.dumps({'freeze': str(target), 'sha256': sha(target.read_bytes()), 'changed_files': len(records), 'semantic_changes': False}, indent=2))
