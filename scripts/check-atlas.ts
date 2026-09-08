import { mkdirSync, writeFileSync } from 'node:fs';
import assert from 'node:assert/strict';
import { dirname } from 'node:path';
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
  { query: 'Boolean relation matrix', contains: 'boolean-relation-matrix' },
  { query: 'Boolean rank', contains: 'boolean-rank' },
  { query: 'rectangle cover', contains: 'one-support-rectangle-cover' },
  { query: 'fixed-bipartition-biclique-cover', contains: 'fixed-bipartition-biclique-cover' },
  { query: 'nondeterministic-communication-s2', contains: 'nondeterministic-communication-s2' },
  { query: 'local Boolean rank', contains: 'local-boolean-rank' },
  { query: 'local biclique', contains: 'local-biclique-cover' },
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
const args = process.argv.slice(2);
if (args.length !== 0 && (args.length !== 2 || args[0] !== '--output')) {
  throw new Error('Usage: node scripts/check-atlas.ts [--output PATH]');
}
const output = args[1] ?? 'evidence/corpus/search-and-paths.json';
mkdirSync(dirname(output), { recursive: true });
writeFileSync(
  output,
  JSON.stringify(report, null, 2) + '\n',
);
console.log(JSON.stringify(report, null, 2));
