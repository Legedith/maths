import assert from 'node:assert/strict';
import { mkdirSync, writeFileSync } from 'node:fs';
import { normalizeLoogle, validateFormalQuery } from '../lib/formal-search.ts';
const name = 'SimpleGraph.lapMatrix';
const result = normalizeLoogle(
  {
    count: 1,
    hits: [
      {
        name,
        module: 'Mathlib.Combinatorics.SimpleGraph.LapMatrix',
        type: '(R : Type) : Matrix V V R',
        doc: null,
      },
    ],
  },
  'lapMatrix',
  '2026-09-08T00:00:00Z',
);
assert.equal(
  result.hits[0].url,
  'https://leanprover-community.github.io/mathlib4_docs/Mathlib/Combinatorics/SimpleGraph/LapMatrix.html#SimpleGraph.lapMatrix',
);
assert.equal(result.upstreamQuery, '"lapMatrix"');
assert.deepEqual(
  normalizeLoogle({ count: 0, hits: [] }, 'zzzz', 'date').hits,
  [],
);
for (const bad of [null, [], 3, '', ' '.repeat(5), 'x'.repeat(121)])
  assert.throws(() => validateFormalQuery(bad));
for (const bad of [
  null,
  { count: -1, hits: [] },
  { count: 1, hits: [null] },
  { count: 1, hits: [{ name, module: '../../evil', type: 'x' }] },
  { count: 1, hits: [{ name, module: 'https://evil.test', type: 'x' }] },
])
  assert.throws(() => normalizeLoogle(bad, 'x', 'date'));
mkdirSync('evidence/reuse', { recursive: true });
const report = {
  passed: true,
  checks: [
    'query boundary',
    'empty results',
    'upstream schema',
    'fixed documentation URL host',
    'path traversal rejection',
    'substring query quoting',
  ],
  scope:
    'Adapter boundary tests. Live service and browser state are separate checks.',
};
writeFileSync(
  'evidence/reuse/adapter-tests.json',
  JSON.stringify(report, null, 2) + '\n',
);
console.log(JSON.stringify(report, null, 2));
