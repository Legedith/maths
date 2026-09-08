"""Prepare typed claims; product gates remain pending until independent review."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path

BASE = Path('D:/CodexWorkspaces/mathematics-atlas')
PROJECT = BASE / 'project'
WORK = BASE / 'msc-product-work'


def read_json(path: Path):
    return json.loads(path.read_text(encoding='utf-8-sig'))


def main():
    bundle = read_json(PROJECT / '.codex/evidence/runs/msc-classification-v1/bundle.json')
    assert len(bundle['artifacts']) == 1 and not bundle['claims']
    freeze = read_json(WORK / 'preexecution-freeze-03.json')
    paths = {row['path'] for row in freeze['files']}
    paths.update(path.relative_to(PROJECT).as_posix() for base in ['data/msc', 'experiments/msc-index', 'evidence/msc-classification'] for path in (PROJECT / base).rglob('*') if path.is_file() and '.venv' not in path.parts and '__pycache__' not in path.parts)
    paths.add('package.json')
    paths.add('package-lock.json')
    for row in freeze['files']:
        assert hashlib.sha256((PROJECT / row['path']).read_bytes()).hexdigest() == row['sha256'], row['path']
    existing = {row['path']: row['id'] for row in bundle['artifacts']}
    for relative in sorted(paths - set(existing)):
        path = PROJECT / relative
        actor = '/root/sol_symmetry_audit' if '/source-review/' in relative or '/adapter-review/' in relative else 'root'
        if relative == 'experiments/msc-index/inputs/source-manifest.json' or relative.startswith('experiments/msc-index/inputs/raw/') or relative.endswith('LICENSE-CC-BY-NC-SA-4.0.md'):
            kind = 'source'
        elif path.suffix == '.bin' or '/logs/' in relative or path.name.endswith('.jsonl'):
            kind = 'log'
        elif path.suffix in {'.py', '.ts', '.tsx', '.css'}:
            kind = 'test' if 'check-' in path.name or 'check_' in path.name else 'code'
        elif 'contract' in path.name or 'freeze' in path.name:
            kind = 'spec'
        elif path.suffix == '.md':
            kind = 'report'
        else:
            kind = 'result'
        identifier = f'A{len(bundle["artifacts"])+1:03d}'
        bundle['artifacts'].append({'id': identifier, 'kind': kind, 'path': relative, 'sha256': hashlib.sha256(path.read_bytes()).hexdigest(), 'producer': actor})
        existing[relative] = identifier
    def support(path, locator, expected=None):
        result = {'artifact_id': existing[path], 'locator': locator}
        if expected is not None:
            result['expected'] = expected
        return result
    summary = 'data/msc/summary.json'
    audit = 'evidence/msc-classification/adapter-review/final-audit.json'
    bundle['claims'] = [
        {'id': 'C001', 'type': 'citation', 'statement': 'The importer reuses the recorded official MSC2020 CSV and a pinned suggested SKOS serialization; it does not author a new classification.', 'status': 'supported', 'supports': [support('experiments/msc-index/inputs/source-manifest.json', 'json:/sources/0/url', 'https://msc2020.org/MSC_2020.csv'), support('experiments/msc-index/inputs/source-manifest.json', 'json:/repository_revision', '33972ddb6a72c3660a6e499ee5f881b57fa92d41')]},
        {'id': 'C002', 'type': 'numerical', 'statement': 'The selected import contains 6603 subject records in 63 top-level areas, with 3083 retained references and 415 scope records.', 'status': 'supported', 'supports': [support(summary, 'json:/subjects', 6603), support(summary, 'json:/hierarchy_levels/1', 63), support(summary, 'json:/references', 3083), support(summary, 'json:/scope_records', 415)]},
        {'id': 'C003', 'type': 'numerical', 'statement': 'Independent reconstruction verifies eight hierarchy disagreement records, 120 exact label differences and 2271 RDF scope-note records. Comparison flags are not findings of semantic source error.', 'status': 'supported', 'supports': [support(audit, 'json:/verified_counts/hierarchy_disagreements', 8), support(audit, 'json:/verified_counts/exact_label_differences', 120), support(audit, 'json:/verified_counts/rdf_scope_notes', 2271)]},
        {'id': 'C004', 'type': 'methodological', 'statement': 'The independently executed portable importer replay reproduces all three selected output files exactly and reconstructs their content from the pinned local sources.', 'status': 'supported', 'supports': [support('evidence/msc-classification/adapter-review/logs/canonical-replay-01.json', 'json:/returncode', 0), support('evidence/msc-classification/adapter-review/results/independent-check.json', 'json:/all_pass', True), support(audit, 'json:/recommendation', 'PASS_FOR_SCOPED_DATA_ADAPTER')]},
        {'id': 'C005', 'type': 'numerical', 'statement': 'The final author functional check has 55 passing checks and zero failures, including complete catalogue traversal, valid API comparisons and invalid requests. It does not measure semantic retrieval or visual quality.', 'status': 'supported', 'supports': [support('evidence/msc-classification/product-history/checks-02.json', 'json:/passed', 55), support('evidence/msc-classification/product-history/checks-02.json', 'json:/failed', 0)]},
        {'id': 'C006', 'type': 'numerical', 'statement': 'The existing Python regression suite reports 155 passing tests. The corrected TypeScript and lint checks and the production build returned zero.', 'status': 'supported', 'supports': [support('evidence/msc-classification/product-history/logs/attempt-msc-regression-pytest-01.stdout.bin', 'contains:155 passed'), support('evidence/msc-classification/product-history/logs/attempt-msc-tsc-02.json', 'json:/returncode', 0), support('evidence/msc-classification/product-history/logs/attempt-msc-lint-02.json', 'json:/returncode', 0), support('evidence/msc-classification/product-history/logs/attempt-msc-production-build-01.json', 'json:/returncode', 0)]},
        {'id': 'C007', 'type': 'methodological', 'statement': 'Subject search uses explicit lexical normalization and AND term matching with 24-record pages; reference output preserves source direction and scopes. No semantic-equivalence or prerequisite assertion is introduced.', 'status': 'supported', 'supports': [support('lib/subject-index.ts', 'contains:SUBJECT_PAGE_SIZE = 24'), support('lib/subject-index.ts', 'contains:terms.every(term => text.includes(term))'), support('lib/subject-index.ts', 'contains:outgoing: out.map(decorate), incoming: back.map(decorate)'), support('docs/subject-browser-contract.md', 'contains:no automatic crosswalk is asserted')]},
        {'id': 'C008', 'type': 'conclusion', 'statement': 'The imported layer supplies source-preserving classification navigation, separately from the reviewed Atlas mathematics. These verified import and functional results do not establish universal coverage, discovery, publication novelty or real-world impact.', 'status': 'supported', 'supports': [{'claim_id': 'C001'}, {'claim_id': 'C002'}, {'claim_id': 'C003'}, {'claim_id': 'C004'}, {'claim_id': 'C005'}, {'claim_id': 'C007'}]},
    ]
    bundle['evaluator_command'] = 'uv run --project experiments/msc-index --frozen python experiments/msc-index/import_msc.py --source-root experiments/msc-index/inputs --output-dir work/msc-index-run'
    bundle['limitations'] = ['Independent product review and final promotion are pending.', 'The pinned suggested RDF serialization is not silently treated as the official version of record.', 'The upstream placeholder xsd:date produces a retained RDFLib warning; the importer does not use that date.', 'No semantic-equivalence, prerequisite, novelty, universal-coverage or real-world-impact claim.', 'No general visual or responsive browser audit. Historical audit commands retain their original staging paths; the portable importer command is documented separately.']
    destination = WORK / 'bundle-draft-01.json'
    with destination.open('x', encoding='utf-8', newline='\n') as stream:
        json.dump(bundle, stream, ensure_ascii=False, indent=2)
        stream.write('\n')
    print(json.dumps({'path': str(destination), 'artifacts': len(bundle['artifacts']), 'claims': len(bundle['claims']), 'integrity_checks': 'pending_independent_product_review'}))


if __name__ == '__main__':
    main()
