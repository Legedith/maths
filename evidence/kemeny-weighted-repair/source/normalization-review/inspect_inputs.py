from pathlib import Path
import hashlib
import json

base = Path('D:/CodexWorkspaces/mathematics-atlas')
source = base/'astra-strength-priority-work'
rows = json.loads((source/'hashes.json').read_bytes())
checks = []
for row in rows:
    path = Path(row['Path'])
    assert path.parent.resolve() == source.resolve()
    digest = hashlib.sha256(path.read_bytes()).hexdigest()
    assert digest == row['Hash'].lower()
    checks.append({'path':str(path), 'sha256':digest, 'matches_frozen_input':True})
primary = (source/'raw-follow.json').read_text(encoding='utf-8-sig')
assert 'L71@P1' in primary and 'L72@P1' in primary
out = {'status':'PASS', 'scope':'Seven input hashes and retained primary-locator availability only; semantic reading is documented in review.md.', 'inputs':checks}
(Path(__file__).parent/'input-check.json').write_bytes((json.dumps(out,indent=2)+'\n').encode())
print(json.dumps(out,indent=2))
