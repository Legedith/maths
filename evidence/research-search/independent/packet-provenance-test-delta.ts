import assert from 'node:assert/strict';
import { createHash } from 'node:crypto';
import { readFileSync, writeFileSync } from 'node:fs';
import {
  normalizeResearchSearch,
  researchPacket,
} from 'file:///D:/CodexWorkspaces/mathematics-atlas/project/lib/research-search.ts';

const ADAPTER_PATH =
  'D:/CodexWorkspaces/mathematics-atlas/project/lib/research-search.ts';
const raw = {
  theorems: [
    {
      theorem_id: 101,
      slogan_id: 201,
      name: 'First',
      body: 'FIRST EXTRACTED BODY',
      slogan: 'FIRST GENERATED SUMMARY',
      similarity: 0.9,
      score: 0.8,
      paper: { paper_id: '1111.1111v1', title: 'First paper' },
    },
    {
      theorem_id: 102,
      slogan_id: 202,
      name: 'Second',
      body: 'SECOND EXTRACTED BODY',
      slogan: 'SECOND GENERATED SUMMARY',
      similarity: 0.7,
      score: -0.6,
      paper: {
        paper_id: '2222.2222v2',
        title: 'Second paper',
        link: 'http://arxiv.org/abs/2222.2222v2',
      },
    },
  ],
};
const normalized = normalizeResearchSearch(
  raw,
  'audit query',
  '2026-09-08T00:00:00.000Z',
);
const packet = researchPacket(normalized, normalized.hits[1]);

assert.equal(packet.schema_version, '1.1');
assert.equal(packet.query, 'audit query');
assert.equal(packet.retrieved_at, '2026-09-08T00:00:00.000Z');
assert.equal(packet.provider, 'TheoremSearch');
assert.equal(packet.retained_result_count, 2);
assert.deepEqual(packet.request, {
  method: 'POST',
  endpoint: 'https://api.theoremsearch.com/search',
  parameters: { query: 'audit query', n_results: 8 },
});
assert.equal(packet.result.rank, 2);
assert.equal(packet.result.similarity, 0.7);
assert.equal(packet.result.score, -0.6);
assert.equal(packet.result.theoremId, 102);
assert.equal(packet.result.sloganId, 202);
assert.equal(packet.result.statement, 'SECOND EXTRACTED BODY');
assert.equal(packet.result.generatedSummary, 'SECOND GENERATED SUMMARY');
assert.equal(packet.result.paper.id, '2222.2222v2');
assert.equal(packet.result.sourceUrl, 'https://arxiv.org/abs/2222.2222v2');

for (const invalid of [Number.NaN, Number.POSITIVE_INFINITY, Number.NEGATIVE_INFINITY, '0.1']) {
  const hit = normalizeResearchSearch(
    { theorems: [{ ...raw.theorems[0], similarity: invalid, score: invalid }] },
    'audit query',
    'now',
  ).hits[0];
  assert.equal(hit.similarity, null);
  assert.equal(hit.score, null);
}

const report = {
  passed: true,
  subject: {
    path: ADAPTER_PATH,
    sha256: createHash('sha256').update(readFileSync(ADAPTER_PATH)).digest('hex'),
  },
  preserved: {
    provider: packet.provider,
    query: packet.query,
    retrievedAt: packet.retrieved_at,
    exactRequest: packet.request,
    retainedResultCount: packet.retained_result_count,
    rank: packet.result.rank,
    similarity: packet.result.similarity,
    score: packet.result.score,
    theoremId: packet.result.theoremId,
    sloganId: packet.result.sloganId,
    extractedBody: packet.result.statement,
    generatedSummary: packet.result.generatedSummary,
    paper: packet.result.paper,
    sourceUrl: packet.result.sourceUrl,
  },
  invalidRankingValuesMapToNull: true,
  note:
    'This verifies retrieval provenance fields from a raw second-ranked provider-shaped result. It does not judge mathematical truth, search relevance, or the provider.',
};
writeFileSync('packet-provenance-delta-report.json', JSON.stringify(report, null, 2) + '\n');
console.log(JSON.stringify(report, null, 2));
