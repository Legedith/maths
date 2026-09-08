"""Serial root integration of the sealed design, with admitted input pins."""
import copy
import hashlib
import json
from pathlib import Path

BASE = Path('D:/CodexWorkspaces/mathematics-atlas')
PROJECT = BASE / 'project'
DESIGN_DIR = BASE / 'boolean-rank-integration-design-work'


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


if digest(DESIGN_DIR / 'publication-manifest.json') != '92af0789482d416b51785f96ff2fd492243720e3cfa977724c195a40e944830b':
    raise ValueError('Design manifest changed after seal')
design_path = DESIGN_DIR / 'integration-design.json'
if digest(design_path) != '9f4cf1d0549ac691b01ec195f033a49884258246e1611293085c898dc0b55ea2':
    raise ValueError('Design changed after seal')
design = json.loads(design_path.read_text(encoding='utf-8'))
source_dir = PROJECT / 'evidence/boolean-rank/source-review'
pins = {
    'corrected-records-v1.json': '0ba1c19b75b0b37fcd29214d3ad5565aca747481aba779084e23367b0a110fd2',
    'correction-review.json': '13bff50ecbd050f359a7948996197e9b09a12c5a5305fedb4aa40804cefcbad0',
}
for name, expected in pins.items():
    if digest(source_dir / name) != expected:
        raise ValueError(f'Pinned source changed: {name}')
atlas_path = PROJECT / 'data/atlas.json'
if digest(atlas_path) != '6d0b37a4f7bdd7181b45d464bb5ea5f038cd097e33d56140c8beb74a3158276d':
    raise ValueError('Start from the frozen source corpus; do not rerun over an integration')
atlas = json.loads(atlas_path.read_text(encoding='utf-8'))
before = copy.deepcopy(atlas)
nodes = copy.deepcopy(design['nodes'])
for i, node in enumerate(nodes):
    node['x'], node['y'] = 100 + 100 * i, 500
edges = copy.deepcopy(design['relationships'])
for edge in edges:
    record_id = edge.pop('curation_record_id')
    edge['curation_record'] = {
        'id': record_id,
        'artifact': 'evidence/boolean-rank/source-review/corrected-records-v1.json',
        'artifact_sha256': pins['corrected-records-v1.json'],
        'independent_review': 'evidence/boolean-rank/source-review/correction-review.json',
        'independent_review_sha256': pins['correction-review.json'],
    }
    edge['source_scope'] = edge['source_scope'].replace('S1', 'Javadi, Maleki and Omoomi').replace('S2', 'Karchmer, Newman, Saks and Wigderson')
supporting = copy.deepcopy(design['supporting_navigation_edges'])
for edge in supporting:
    edge.pop('purpose', None)
atlas['schema_version'] = '1.1'
atlas['scope'] = 'Laplacians and networks; Boolean relations, covers and communication'
atlas['nodes'].extend(nodes)
atlas['edges'].extend(edges + supporting)
atlas['sources'].extend(design['source_records'])
atlas['journeys'].extend(design['journeys'])
counts = {'nodes': 40, 'edges': 52, 'sources': 11, 'journeys': 6, 'opportunities': 6, 'examples': 7}
for key, count in counts.items():
    if len(atlas[key]) != count or atlas[key][:len(before[key])] != before[key]:
        raise ValueError(f'Count or preserved record mismatch: {key}')
for key in before.keys() - counts.keys() - {'schema_version', 'scope'}:
    if before[key] != atlas[key]:
        raise ValueError(f'Unexpected top-level change: {key}')
projection = {
    'schema_version': 'boolean-rank-integration-projection-v1',
    'status': 'implementation_projection_pending_independent_review',
    'inputs': [{'path': f'evidence/boolean-rank/source-review/{name}', 'sha256': value} for name, value in pins.items()],
    'design_sha256': digest(design_path),
    'base_corpus_sha256': '6d0b37a4f7bdd7181b45d464bb5ea5f038cd097e33d56140c8beb74a3158276d',
    'counts': counts,
    'relationships': edges,
    'additions': {'nodes': nodes, 'edges': supporting, 'sources': design['source_records'], 'journeys': design['journeys']},
    'design_adjustments': [
        'Source scope names the primary authors instead of the local S1/S2 shorthand.',
        'Finite x/y presentation metadata assigned; current renderer computes positions independently.',
        'Supporting edge purpose is retained in design advice rather than added as an undocumented API field.',
    ],
    'scope': 'Known mathematical translations under exact conventions. No formal verification, novelty, practical impact or source equivalence outside the admitted conditions is claimed.',
}
atlas_path.write_text(json.dumps(atlas, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
projection_path = PROJECT / 'evidence/boolean-rank/integration-projection.json'
projection_path.write_text(json.dumps(projection, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
readme = PROJECT / 'README.md'
content = readme.read_text(encoding='utf-8')
content = content.replace('with eight retrieval sanity cases.', 'with fifteen retrieval sanity cases.')
readme.write_text(content, encoding='utf-8')
print(json.dumps({'counts': counts, 'atlas_sha256': digest(atlas_path), 'projection_sha256': digest(projection_path), 'existing_records_value_identical': True}, indent=2))
