import assert from 'node:assert/strict';
import { createHash } from 'node:crypto';
import { readFileSync } from 'node:fs';
import {
  searchConceptLibrary,
  validateLibraryQuery,
  conceptSourceUrl,
  type ConceptIndex,
} from '../lib/concept-library.ts';

const bytes = readFileSync(
  new URL('../data/mathgloss/candidate-index.json', import.meta.url),
);
assert.equal(
  createHash('sha256').update(bytes).digest('hex'),
  '282ed1fd858595b782c856fbd2c96964a0b6ff3850fedf21105ca9bbb7edb4da',
);
const index = JSON.parse(bytes.toString('utf8')) as ConceptIndex;
assert.equal(index.records.length, 4814);
assert.equal(
  index.records.reduce((sum, record) => sum + record.links.length, 0),
  7217,
);

const first = searchConceptLibrary(index, { query: '' });
const seen: string[] = [];
for (let page = 1; page <= first.pages; page++) {
  const result = searchConceptLibrary(index, { query: '', page });
  assert.equal(result.total, 4814);
  assert(result.records.length <= 20);
  seen.push(...result.records.map((record) => record.record_key));
}
assert.deepEqual(
  seen,
  index.records.map((record) => record.record_key),
);
assert.equal(new Set(seen).size, 4814);

for (const [query, qid] of [
  ['deutsch jozsa', 'Q1028209'],
  ['Ｑ１０２８２０９', 'Q1028209'],
  ['discrete fourier', 'Q1006032'],
  ['Turing', 'Q163310'],
  ['abelian group', 'Q181296'],
  ['conditional probability', 'Q327069'],
]) {
  const result = searchConceptLibrary(index, { query });
  assert(
    result.records.some((record) => record.identity_candidate.qid === qid),
    `${query} should retrieve ${qid}`,
  );
}
const unicode = searchConceptLibrary(index, { query: 'Q1028209' }).records[0];
assert.equal(unicode.label_as_recorded, 'Deutsch\u2013Jozsa algorithm');
assert(!unicode.label_as_recorded.includes('\uFFFD'));
assert(conceptSourceUrl(unicode).endsWith('/data/database.csv#L31-L31'));

for (const resource of first.resources) {
  const result = searchConceptLibrary(index, { query: '', resource });
  assert(
    result.records.every((record) =>
      record.links.some((link) => link.source === resource),
    ),
  );
  assert.equal(
    result.total,
    index.records.filter((record) =>
      record.links.some((link) => link.source === resource),
    ).length,
  );
}
assert.equal(
  searchConceptLibrary(index, { query: 'no-mathematical-record-735113' }).total,
  0,
);
for (const input of [
  null,
  [],
  { query: true },
  { query: 'x'.repeat(501) },
  { query: '', page: 0 },
  { query: '', page: true },
  { query: '', page: 1.5 },
  { query: '', page: Infinity },
  { query: '', extra: 1 },
  { query: '', resource: null },
]) {
  assert.throws(() => validateLibraryQuery(input));
}
assert.throws(() =>
  searchConceptLibrary(index, { query: '', resource: 'invented-resource' }),
);
console.log(
  JSON.stringify(
    {
      status: 'pass',
      catalog_records: 4814,
      retained_links: 7217,
      full_pagination_records: seen.length,
      pages: first.pages,
      resources: first.resources,
      source_hash_verified: true,
      scope:
        'Integration and lexical navigation checks; no semantic identity or mathematical novelty claim.',
    },
    null,
    2,
  ),
);
