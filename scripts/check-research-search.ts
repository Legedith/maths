import assert from 'node:assert/strict';
import { mkdirSync, writeFileSync } from 'node:fs';
import {
  normalizeResearchSearch,
  researchPacket,
  researchRequest,
  validateResearchQuery,
} from '../lib/research-search.ts';
assert.equal(
  validateResearchQuery('  compact Hausdorff  '),
  'compact Hausdorff',
);
for (const invalid of ['', '   ', null, 2, 'x'.repeat(501)])
  assert.throws(() => validateResearchQuery(invalid));
const raw = {
  theorems: [
    {
      theorem_id: 123,
      slogan_id: 456,
      name: 'A statement',
      body: 'exact extracted body',
      slogan: 'generated summary',
      similarity: 0.8,
      score: 0.7,
      paper: {
        paper_id: '1234.56789v1',
        title: 'Paper',
        authors: ['Author'],
        source: 'arXiv',
        link: 'http://arxiv.org/abs/1234.56789v1',
      },
    },
  ],
};
const result = normalizeResearchSearch(raw, 'query', '2026-09-08T00:00:00Z');
assert.equal(result.hits[0].statement, 'exact extracted body');
assert.equal(result.hits[0].generatedSummary, 'generated summary');
assert.equal(result.hits[0].sourceUrl, 'https://arxiv.org/abs/1234.56789v1');
assert.equal(
  researchPacket(result, result.hits[0]).kind,
  'unreviewed_retrieval_packet',
);
assert.deepEqual(researchPacket(result, result.hits[0]).result, result.hits[0]);
const rankedRaw = {
  theorems: [
    raw.theorems[0],
    { ...raw.theorems[0], theorem_id: 789, similarity: 0.4, score: -0.2 },
  ],
};
const rankedResult = normalizeResearchSearch(rankedRaw, 'ranked query', 'now');
const secondPacket = researchPacket(rankedResult, rankedResult.hits[1]);
assert.equal(secondPacket.result.rank, 2);
assert.equal(secondPacket.result.similarity, rankedRaw.theorems[1].similarity);
assert.equal(secondPacket.result.score, rankedRaw.theorems[1].score);
assert.deepEqual(secondPacket.request, {
  method: 'POST',
  endpoint: 'https://api.theoremsearch.com/search',
  parameters: { query: 'ranked query', n_results: 8 },
});
assert.deepEqual(secondPacket.request, researchRequest('ranked query'));
assert.equal(secondPacket.retained_result_count, 2);
assert.equal(secondPacket.schema_version, '1.1');
for (const invalidScore of [
  null,
  '0.9',
  Number.NaN,
  Number.POSITIVE_INFINITY,
]) {
  const hit = normalizeResearchSearch(
    {
      theorems: [
        { ...raw.theorems[0], similarity: invalidScore, score: invalidScore },
      ],
    },
    'q',
    'now',
  ).hits[0];
  assert.equal(hit.similarity, null);
  assert.equal(hit.score, null);
}
assert.equal(
  normalizeResearchSearch({ theorems: [] }, 'q', 'now').hits.length,
  0,
);
for (const invalid of [
  null,
  [],
  {},
  { theorems: [null] },
  { theorems: [{ theorem_id: true, body: 'x' }] },
  { theorems: [{ theorem_id: 2 ** 54, body: 'x' }] },
  { theorems: [{ theorem_id: 1 }] },
])
  assert.throws(() => normalizeResearchSearch(invalid, 'q', 'now'));
for (const link of [
  'javascript:alert(1)',
  'data:text/html,hi',
  'file:///private',
  'https://user:password@example.org/',
  '/relative',
  'not a url',
]) {
  const hit = { theorem_id: 1, body: 'body', link };
  assert.equal(
    normalizeResearchSearch({ theorems: [hit] }, 'q', 'now').hits[0].sourceUrl,
    null,
  );
}
assert.equal(
  normalizeResearchSearch(
    { theorems: [{ theorem_id: 1, body: 'x', paper: null }] },
    'q',
    'now',
  ).hits[0].generatedSummary,
  null,
);
assert.equal(
  normalizeResearchSearch(
    { theorems: Array(12).fill(raw.theorems[0]) },
    'q',
    'now',
  ).hits.length,
  8,
);
const report = {
  passed: true,
  checks: [
    'query bounds',
    'summary/body separation',
    'source packet provenance',
    'raw provider rank/score/similarity and exact request preservation',
    'unsafe-link rejection',
    'nullable metadata',
    'malformed response rejection',
    'stable safe identifiers',
    'result cap',
    'empty results',
  ],
  scope:
    'Adapter and source-packet boundary tests; no claim about mathematical truth, search accuracy or browser behavior.',
};
mkdirSync('evidence/research-search', { recursive: true });
writeFileSync(
  'evidence/research-search/adapter-tests.json',
  JSON.stringify(report, null, 2) + '\n',
);
console.log(JSON.stringify(report, null, 2));
