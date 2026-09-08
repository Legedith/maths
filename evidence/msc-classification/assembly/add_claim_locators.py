from __future__ import annotations

import copy
import hashlib
import json
from pathlib import Path

BASE = Path('D:/CodexWorkspaces/mathematics-atlas')
PROJECT = BASE / 'project'
WORK = BASE / 'msc-product-work'
path = PROJECT / '.codex/evidence/runs/msc-classification-v1/bundle.json'
prior_hash = 'ebf6ccdebf606a1890964ed32253a706a3573312e4377dfdd2a1aaf35633f52f'
assert hashlib.sha256(path.read_bytes()).hexdigest() == prior_hash
bundle = json.loads(path.read_text(encoding='utf-8'))
prior = copy.deepcopy(bundle)
artifacts = {row['id']: row for row in bundle['artifacts']}
claims = {row['id']: row for row in bundle['claims']}
added = {}

def add(claim_id, artifact_id, locator, expected=None):
    record = {'artifact_id': artifact_id, 'locator': locator}
    source = PROJECT / artifacts[artifact_id]['path']
    text = source.read_text(encoding='utf-8-sig')
    if locator.startswith('json:'):
        value = json.loads(text)
        for part in locator[6:].split('/'):
            key = part.replace('~1', '/').replace('~0', '~')
            value = value[int(key)] if isinstance(value, list) else value[key]
        if expected is not None:
            assert value == expected, (claim_id, locator)
        record['expected'] = value
    else:
        assert locator.startswith('contains:')
        assert locator[9:] in text, (claim_id, locator)
    assert record not in claims[claim_id]['supports']
    claims[claim_id]['supports'].append(record)
    added.setdefault(claim_id, []).append(record)

add('C001', 'A159', 'json:/sources/2/url', 'https://raw.githubusercontent.com/TIBHannover/MSC2020_SKOS/33972ddb6a72c3660a6e499ee5f881b57fa92d41/msc-2020-suggestion4.ttl')
add('C001', 'A012', 'contains:Changes: conversion to JSON navigation records; parent derivation from classification-code structure')
add('C001', 'A001', 'contains:The generated files must remain byte-identical to the independently reviewed adapter outputs. The official CSV supplies display labels and descriptions; raw suggested-RDF labels/parents and discrepancy flags remain inspectable.')
add('C003', 'A050', 'json:/checks/2/decision')
add('C005', 'A092', 'json:/checks')
add('C005', 'A092', 'json:/limitation', 'Functional source/navigation/API checks; no semantic-equivalence or visual-browser evaluation.')
add('C007', 'A164', "contains:value.normalize('NFKC').toLowerCase()")
add('C007', 'A164', 'contains:const decorate = (relation: SubjectReference) => ({ ...relation, from: endpoint(relation.from_uri), to: endpoint(relation.to_uri) });')
add('C007', 'A170', 'json:/checks/2/decision')
add('C007', 'A170', 'json:/limitations/4', 'No classification record or lexical result is certified as a proof, semantic equivalence, prerequisite, exhaustive account of mathematics, novelty result or open-problem determination.')
add('C009', 'A170', 'json:/checks/0/decision')
add('C009', 'A170', 'json:/limitations/3', 'No browser DOM, screenshot, responsive-layout, assistive-technology or general visual evaluation was performed or claimed.')

assert bundle['artifacts'] == prior['artifacts']
assert bundle['checks'] == prior['checks']
for before, after in zip(prior['claims'], bundle['claims'], strict=True):
    assert {k: v for k, v in before.items() if k != 'supports'} == {k: v for k, v in after.items() if k != 'supports'}
    assert after['supports'][:len(before['supports'])] == before['supports']
payload = (json.dumps(bundle, ensure_ascii=False, indent=2) + '\n').encode('utf-8')
digest = hashlib.sha256(payload).hexdigest()
correction = {'schema_version': 'msc-additive-claim-locators-v1', 'producer': 'root', 'prior_bundle_sha256': prior_hash, 'candidate_bundle_sha256': digest, 'change': 'Added exact locators for clauses identified by independent promotion review. Claim statements, original supports, all 265 artifact records and bytes, and all four check decisions remain unchanged.', 'additions': added}
with (WORK / 'claim-locator-correction-03.json').open('x', encoding='utf-8', newline='\n') as output:
    json.dump(correction, output, ensure_ascii=False, indent=2)
    output.write('\n')
with (WORK / 'bundle-final-candidate-03.json').open('xb') as output:
    output.write(payload)
path.write_bytes(payload)
print(json.dumps({'sha256': digest, 'artifacts': len(bundle['artifacts']), 'claims': len(bundle['claims']), 'added_supports': sum(map(len, added.values()))}))
