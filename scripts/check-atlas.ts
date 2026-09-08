import { mkdirSync, writeFileSync } from 'node:fs';
import assert from 'node:assert/strict';
import { atlas, connectionPath, searchNodes } from '../lib/atlas.ts';
// Curated retrieval sanity cases, not a held-out semantic search benchmark.
const queries = [
  { query: 'Laplacian', contains: 'laplacian' },
  { query: 'resistance', contains: 'effective-resistance' },
  { query: 'random walk', contains: 'random-walk' },
  { query: 'segmentation', contains: 'image-segmentation' },
  { query: 'effective-resistance', contains: 'effective-resistance' },
  { query: 'commute-resistance', contains: 'commute-resistance' },
  { query: 'matrix-tree', contains: 'matrix-tree' },
  { query: 'random-walk', contains: 'random-walk' },
];
for (const c of queries)
  assert.ok(
    searchNodes(c.query).some((r) => r.node.id === c.contains),
    c.query,
  );
assert.equal(searchNodes('zzzz-not-a-concept-123').length, 0);
assert.ok(
  searchNodes('', 'Computer science').every((r) =>
    r.node.domains.includes('Computer science'),
  ),
);
let paths = 0;
for (const from of atlas.nodes)
  for (const to of atlas.nodes) {
    const path = connectionPath(from.id, to.id);
    assert.notEqual(path, null, `${from.id} to ${to.id}`);
    let current = from.id;
    for (const edge of path!) {
      assert.ok(edge.from === current || edge.to === current);
      current = edge.from === current ? edge.to : edge.from;
    }
    assert.equal(current, to.id);
    paths++;
  }
assert.throws(() => connectionPath('missing', 'laplacian'));
const report = {
  passed: true,
  retrieval_sanity_cases: queries.length,
  navigation_pairs: paths,
  method:
    'Lexical substring scoring: IDs/title/aliases 4, other indexed text 1 per term; AND matching. Breadth-first undirected navigation.',
  limitations: [
    'Curated cases demonstrate indexed rediscovery, not semantic recall or novelty detection.',
    'A traversal path is not a logical composition of its mathematical relations.',
  ],
};
mkdirSync('evidence/corpus', { recursive: true });
writeFileSync(
  'evidence/corpus/search-and-paths.json',
  JSON.stringify(report, null, 2) + '\n',
);
console.log(JSON.stringify(report, null, 2));
