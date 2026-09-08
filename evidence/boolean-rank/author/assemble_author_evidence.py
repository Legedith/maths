"""Assemble typed author evidence; keep every independent gate pending."""
import hashlib
import json
import shutil
from pathlib import Path

BASE = Path('D:/CodexWorkspaces/mathematics-atlas')
WORK = BASE / 'boolean-rank-integration-work'
PROJECT = BASE / 'project'
TARGET = PROJECT / 'evidence/boolean-rank/author'


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


names = ['claims-draft.json', 'contract-v1.md', 'integrate_data.py',
         'freeze_implementation.py', 'normalize_generated_files.py', 'check_http.py',
         'implementation-freeze-v1.json', 'implementation-freeze-v2.json',
         'newline-correction.json', 'assemble_author_evidence.py']
names += [str(path.relative_to(WORK)) for folder in ['logs', 'results', 'history']
          for path in (WORK / folder).rglob('*') if path.is_file()
          and path.name != 'http-02-home.html']
for name in sorted(set(names)):
    source, target = WORK / name, TARGET / name
    target.parent.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(source, target)
report = {
    'copied_author_files': len(set(names)),
    'gate_status': 'pending_independent_product_review',
    'omitted_local_raw_body': {'path': str(WORK / 'results/http-02-home.html'), 'sha256': sha(WORK / 'results/http-02-home.html'), 'reason': 'Retained locally for route review; not needed as a public page snapshot.'},
    'role_pilot_and_teaching_example_included': False,
}
(TARGET / 'assembly-record.json').write_bytes((json.dumps(report, indent=2) + '\n').encode())
bundle_path = PROJECT / '.codex/evidence/runs/boolean-rank-integration-v1/bundle.json'
bundle = json.loads(bundle_path.read_bytes())
paths = {item['path'] for item in json.loads((WORK / 'implementation-freeze-v2.json').read_bytes())['files']}
paths.update(str(path.relative_to(PROJECT)).replace('\\', '/') for path in (PROJECT / 'evidence/boolean-rank').rglob('*') if path.is_file())
artifact_by_path = {}
artifacts = []
for index, name in enumerate(sorted(paths), 1):
    path = PROJECT / name
    if name == 'docs/boolean-rank-contract.md':
        kind = 'spec'
    elif name.startswith('evidence/boolean-rank/source-review/'):
        kind = 'source' if name.endswith(('corrected-records-v1.json', 'source-assessment.json')) else 'report'
    elif '/logs/' in name:
        kind = 'log'
    elif '/results/' in name:
        kind = 'result'
    elif path.suffix in {'.py', '.ts', '.tsx', '.mjs'}:
        kind = 'test' if '/test' in name or '/check-' in name else 'code'
    else:
        kind = 'report'
    record = {'id': f'A{index:03d}', 'kind': kind, 'path': name, 'sha256': sha(path), 'producer': '/root'}
    if name.startswith('evidence/boolean-rank/source-review/') and not name.endswith('corrected-records-v1.json'):
        record['producer'] = '/root/sol_symmetry_audit'
    elif '/design/' in name:
        record['producer'] = '/root/sol_atlas_audit'
    artifacts.append(record)
    artifact_by_path[name] = record['id']


def support(path, locator=None, expected=None):
    value = {'artifact_id': artifact_by_path[path]}
    if locator is not None:
        value['locator'] = locator
    if expected is not None:
        value['expected'] = expected
    return value


def claim(id_, type_, statement, supports):
    return {'id': id_, 'type': type_, 'statement': statement, 'status': 'supported', 'supports': supports}


prefix = 'evidence/boolean-rank/author/'
claims = [
    claim('C001', 'citation', 'R1-R4 retain known source-admitted translations and explicit local zero conventions; no novelty is claimed.', [
        support('evidence/boolean-rank/source-review/corrected-records-v1.json', 'json:/novelty', 'All four relationships are known. The zero conventions are explicit definitions and elementary local checks, not a claimed discovery.'),
        support('evidence/boolean-rank/source-review/correction-review.json', 'json:/bridge_decisions'),
    ]),
    claim('C002', 'numerical', 'The curated corpus has 40 nodes, 52 edges, 11 sources, six journeys, six opportunities and seven graph examples.', [
        support(prefix + 'results/validation-01.json', 'json:/counts', {'nodes': 40, 'edges': 52, 'sources': 11, 'journeys': 6, 'opportunities': 6, 'examples': 7}),
    ]),
    claim('C003', 'numerical', 'The author component/API check passed nine scoped checks, rendering four admitted connections and all 40 selected-concept maps.', [
        support(prefix + 'results/functional-01.json', 'json:/check_count', 9),
        support(prefix + 'results/functional-01.json', 'json:/rendered_connections', 4),
        support(prefix + 'results/functional-01.json', 'json:/rendered_maps', 40),
    ]),
    claim('C004', 'numerical', 'Fifteen lexical sanity cases and 1600 ordered navigation-pair checks passed.', [
        support(prefix + 'results/navigation-01.json', 'json:/retrieval_sanity_cases', 15),
        support(prefix + 'results/navigation-01.json', 'json:/navigation_pairs', 1600),
    ]),
    claim('C005', 'methodological', 'The implementation carries source scope, bidirectional witness translations, local boundary arguments, notation distinctions and retained curation identity through the typed model and connection display.', [
        support('lib/atlas.ts', 'contains:witness_translation?'),
        support('components/atlas-map.tsx', 'contains:Atlas convention for the zero case'),
        support(prefix + 'logs/boolean-functional-01.json', 'json:/returncode', 0),
    ]),
    claim('C006', 'methodological', 'The initial full Python suite, typecheck, lint and build passed; the final corpus tests also passed after two malformed-path cases were added.', [
        support(prefix + f'logs/{name}.json', 'json:/returncode', 0)
        for name in ['boolean-pytest-01', 'boolean-types-01', 'boolean-lint-01', 'boolean-build-01', 'boolean-corpus-tests-02']
    ]),
    claim('C007', 'methodological', 'Actual local HTTP routes returned the canonical API object and the broadened home-page scope.', [
        support(prefix + 'check_http.py', 'contains:actual != expected'),
        support(prefix + 'results/http-02.json', 'json:/passed', True),
        support(prefix + 'logs/boolean-http-02.json', 'json:/returncode', 0),
    ]),
]
bundle['artifacts'], bundle['claims'] = artifacts, claims
bundle['task_spec_artifact_id'] = artifact_by_path['docs/boolean-rank-contract.md']
bundle['evaluator_command'] = 'node scripts/check-boolean-rank.mjs --output work/boolean-rank-functional.json'
bundle['limitations'] = [
    'Independent final product review is pending; this bundle cannot pass or authorize publication yet.',
    'Known translations under specified conditions only; no new theorem, algorithm, formal proof, universal coverage or practical-impact result.',
    'Structural and lexical checks do not establish source entailment or semantic retrieval quality. Navigation paths do not compose implications.',
    'Server-rendered text/geometry and local HTTP checks do not establish browser interaction, visual quality, accessibility or deployed behavior.',
    'The first typecheck preceded corpus integration. Build01 preceded a value-preserving LF correction; a final exact-tree build is required before publication.',
    'The source records preserve historical pending wording; their separate later correction review records semantic admission.',
    'The finite teaching example, stopped role-mining software run and pending Kemeny proof are separate tasks.',
]
bundle_path.write_bytes((json.dumps(bundle, indent=2) + '\n').encode())
print(json.dumps({'artifacts': len(artifacts), 'claims': len(claims), 'checks': 'all_pending', 'bundle_sha256': sha(bundle_path)}, indent=2))
