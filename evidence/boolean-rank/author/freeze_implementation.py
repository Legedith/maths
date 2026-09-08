"""Retain the reviewed design packet and freeze the root's implementation."""
import hashlib
import json
import shutil
import subprocess
from pathlib import Path

BASE = Path('D:/CodexWorkspaces/mathematics-atlas')
PROJECT = BASE / 'project'
WORK = BASE / 'boolean-rank-integration-work'
DESIGN = BASE / 'boolean-rank-integration-design-work'


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


manifest_path = DESIGN / 'publication-manifest.json'
if digest(manifest_path) != '92af0789482d416b51785f96ff2fd492243720e3cfa977724c195a40e944830b':
    raise ValueError('Unexpected design manifest')
manifest = json.loads(manifest_path.read_text(encoding='utf-8'))
for record in manifest['copy_records']:
    source = (DESIGN / record['path']).resolve()
    destination = (PROJECT / 'evidence/boolean-rank/design' / record['path']).resolve()
    if not source.is_relative_to(DESIGN) or not destination.is_relative_to(PROJECT / 'evidence/boolean-rank/design'):
        raise ValueError('Unsafe manifest path')
    if digest(source) != record['sha256']:
        raise ValueError(f'Changed source: {source}')
    if record.get('copy'):
        destination.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(source, destination)
files = set()
for args in [['git', 'diff', '--name-only'], ['git', 'ls-files', '--others', '--exclude-standard']]:
    files.update(subprocess.run(args, cwd=PROJECT, capture_output=True, check=True, text=True).stdout.splitlines())
files.update(['package.json', 'package-lock.json', 'pyproject.toml', 'uv.lock', 'app/api/atlas/route.ts', 'lib/use-atlas-tools.ts', 'components/ui/native-select.tsx', 'lib/utils.ts', 'tsconfig.json'])
files = sorted(path for path in files if not path.startswith('.codex/') and (PROJECT / path).is_file())
freeze = {
    'schema_version': 'boolean-rank-implementation-freeze-v1',
    'base_commit': '08434cb8f3a0923a7b781503cec64a86878cf171',
    'producer': '/root',
    'status': 'author_checks_passed_independent_product_review_pending',
    'files': [{'path': name, 'sha256': digest(PROJECT / name), 'bytes': (PROJECT / name).stat().st_size} for name in files],
    'author_attempts': ['boolean-integrate-01', 'boolean-types-01', 'boolean-validate-01', 'boolean-pytest-01', 'boolean-functional-01', 'boolean-navigation-01', 'boolean-lint-01', 'boolean-corpus-tests-02'],
    'limits': ['Final mathematical source and implementation gates are not self-certified.', 'Historical release evidence remains unchanged.', 'The first typecheck preceded the data append; the production build and independent review follow the frozen integration.'],
}
target = WORK / 'implementation-freeze-v1.json'
if target.exists():
    raise FileExistsError(target)
target.write_text(json.dumps(freeze, indent=2) + '\n', encoding='utf-8')
print(json.dumps({'path': str(target), 'sha256': digest(target), 'files': len(files)}, indent=2))
