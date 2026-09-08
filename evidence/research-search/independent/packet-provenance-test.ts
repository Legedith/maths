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
      score: 0.6,
      paper: { paper_id: '2222.2222v2', title: 'Second paper' },
    },
  ],
};
const normalized = normalizeResearchSearch(
  raw,
  'audit query',
  '2026-09-08T00:00:00.000Z',
);
const packet = researchPacket(normalized, normalized.hits[1]);

assert.equal(packet.query, 'audit query');
assert.equal(packet.retrieved_at, '2026-09-08T00:00:00.000Z');
assert.equal(packet.provider, 'TheoremSearch');
assert.equal(packet.result.theoremId, 102);
assert.equal(packet.result.sloganId, 202);
assert.equal(packet.result.statement, 'SECOND EXTRACTED BODY');
assert.equal(packet.result.generatedSummary, 'SECOND GENERATED SUMMARY');

const normalizedHit = normalized.hits[1] as unknown as Record<string, unknown>;
const packetRecord = packet as unknown as Record<string, unknown>;
assert.equal('similarity' in normalizedHit, false);
assert.equal('score' in normalizedHit, false);
assert.equal('rank' in normalizedHit, false);
assert.equal('rank' in packetRecord, false);
assert.equal('request' in packetRecord, false);
assert.equal('endpoint' in packetRecord, false);

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
    theoremId: packet.result.theoremId,
    sloganId: packet.result.sloganId,
    extractedBody: packet.result.statement,
    generatedSummary: packet.result.generatedSummary,
    paper: packet.result.paper,
    sourceUrl: packet.result.sourceUrl,
  },
  observedOmissionsFromDocumentedProviderResponse: {
    resultRank: true,
    similarity: true,
    score: true,
    requestResultLimit: true,
    providerEndpoint: true,
  },
  note:
    'This is an observation about retrieval provenance. It does not judge mathematical truth, search relevance, or the provider.',
};
writeFileSync('packet-provenance-report.json', JSON.stringify(report, null, 2) + '\n');
console.log(JSON.stringify(report, null, 2));
