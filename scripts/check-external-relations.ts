import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';
import { resolve } from 'node:path';
import { createRelationExplorer, relationApiResponse, validateRelationQuery, type RelationIndex } from '../lib/external-relations.ts';
import type { ConceptIndex } from '../lib/concept-library.ts';

const index = JSON.parse(readFileSync(new URL('../data/mathgloss/relations/relation-index.json', import.meta.url), 'utf8')) as RelationIndex;
const catalog = JSON.parse(readFileSync(new URL('../data/mathgloss/candidate-index.json', import.meta.url), 'utf8')) as ConceptIndex;
const raw = JSON.parse(readFileSync(new URL('../evidence/external-connections/sources/probe/wikidata-response.json', import.meta.url), 'utf8'));
const search = createRelationExplorer(index, catalog);
const args = process.argv.slice(2);
assert(args.length === 0 || (args.length === 2 && args[0] === '--reproduced-dir'), 'Use --reproduced-dir PATH or no arguments.');
if (args.length) {
  for (const name of ['relation-index.json', 'relation-ledger.json', 'relation-summary.json'])
    assert.deepEqual(readFileSync(resolve(args[1], name)), readFileSync(new URL(`../data/mathgloss/relations/${name}`, import.meta.url)), `${name} must reproduce byte for byte`);
}
assert.equal(index.edges.length, 5390);
assert.equal(index.properties.length, 81);
assert.equal(new Set(index.edges.map((edge) => edge.id)).size, 5390);
let selections = 0;
let traversedRows = 0;
for (const concept of catalog.records) {
  const qid = concept.identity_candidate.qid;
  const expected = index.edges.filter((edge) => edge.source.id === qid || edge.target.id === qid);
  for (const direction of ['both', 'incoming', 'outgoing'] as const) {
    const directional = expected.filter((edge) => direction === 'both' || (direction === 'incoming' ? edge.target.id === qid : edge.source.id === qid));
    const first = search({ qid, direction });
    assert.equal(first.total, directional.length);
    assert.equal(first.concept, concept);
    const seen: string[] = [];
    for (let page = 1; page <= Math.max(1, first.pages); page++) {
      const result = search({ qid, direction, page });
      assert(result.edges.length <= 20);
      assert.equal(result.total, directional.length);
      seen.push(...result.edges.map((edge) => edge.id));
      selections++;
    }
    assert.deepEqual(seen, directional.map((edge) => edge.id));
    assert.equal(new Set(seen).size, seen.length);
    traversedRows += seen.length;
  }
  for (const property of new Set(expected.map((edge) => edge.property.id))) {
    const rows = expected.filter((edge) => edge.property.id === property);
    const selected = search({ qid, property });
    assert.equal(selected.total, rows.length);
    assert.deepEqual(selected.edges.map((edge) => edge.id), rows.slice(0, 20).map((edge) => edge.id));
    selections++;
  }
}
assert.equal(Object.keys(index.observations).length, 3);
for (const [edgeId, observation] of Object.entries(index.observations)) {
  const edge = index.edges.find((edge) => edge.id === edgeId)!;
  assert(edge);
  const entity = raw.entities[edge.source.id];
  const exact = entity.claims[edge.property.id].filter((statement: { mainsnak: { datavalue?: { value?: { id?: string } } } }) => statement.mainsnak.datavalue?.value?.id === edge.target.id);
  assert.deepEqual(observation.matching_statements, exact);
  assert.equal(observation.source_entity.lastrevid, entity.lastrevid);
  assert.equal(observation.source_entity.modified, entity.modified);
  assert.equal(observation.source_entity.id, edge.source.id);
  assert.deepEqual(observation.field_presence, exact.map((statement: { id: string }) => ({ statement_id: Object.hasOwn(statement, 'id'), qualifiers: Object.hasOwn(statement, 'qualifiers'), references: Object.hasOwn(statement, 'references') })));
  const result = search({ qid: edge.source.id, property: edge.property.id });
  assert.deepEqual(result.observations[edgeId], observation);
}
const qualified = index.observations['mathgloss-row-175'];
assert.equal(qualified.matching_statements[0].qualifiers?.P518[0].property, 'P518');
assert.deepEqual(qualified.matching_statements[0].qualifiers?.P518[0].datavalue?.value, { 'entity-type': 'item', 'numeric-id': 9085982, id: 'Q9085982' });
assert.equal(qualified.display_labels.Q9085982, 'type IIA string theory');
const invalidInputs = [null, [], {}, { qid: 'Q0' }, { qid: 'Q01' }, { qid: 8366 }, { qid: 'Q8366', page: 0 }, { qid: 'Q8366', page: 1.5 }, { qid: 'Q8366', page: Infinity }, { qid: 'Q8366', page: null }, { qid: 'Q8366', direction: null }, { qid: 'Q8366', property: null }, { qid: 'Q8366', property: 'same' }, { qid: 'Q8366', direction: 'inverse' }, { qid: 'Q8366', extra: true }];
for (const input of invalidInputs) assert.throws(() => validateRelationQuery(input));
for (const input of [{ qid: 'Q999999999999999' }, { qid: 'Q8366', property: 'P999999999999999' }]) assert.throws(() => search(input));
const invalidUrls = ['', '?qid=Q0', '?qid=Q8366&qid=Q8366', '?qid=Q8366&extra=private-query', '?qid=Q8366&page=0', '?qid=Q8366&page=01', '?qid=Q8366&page=1000001', '?qid=Q8366&page=1.5', '?qid=Q8366&direction=inverse', '?qid=Q8366&property=P999999999999999', '?qid=Q8366&property=', '?qid=Q8366&direction=both&direction=incoming', '?qid=Q8366&page=1&page=2'];
for (const suffix of invalidUrls) {
  const response = relationApiResponse(new Request(`https://example.invalid/api/external-relations${suffix}`), search);
  assert.equal(response.status, 400);
  assert.equal(response.headers.get('Cache-Control'), 'no-store');
  const body = await response.text();
  assert(body.length < 100);
  assert(!body.includes('private-query'));
}
for (const suffix of ['?qid=Q8366', '?qid=Q176645&direction=incoming', '?qid=Q1051696&property=P460', '?qid=Q8366&page=1000000']) {
  const response = relationApiResponse(new Request(`https://example.invalid/api/external-relations${suffix}`), search);
  assert.equal(response.status, 200);
  assert.equal(response.headers.get('Cache-Control'), 'no-store');
  const body = await response.json() as { edges: unknown[] };
  assert(Array.isArray(body.edges) && body.edges.length <= 20);
}
console.log(JSON.stringify({ status: 'pass', catalog_concepts: catalog.records.length, source_edges: index.edges.length, selections_checked: selections, paginated_row_visits: traversedRows, exact_probe_overlays: 3, reproduced_files_checked: args.length ? 3 : 0, invalid_inputs: invalidInputs.length + 2, invalid_api_requests: invalidUrls.length, scope: 'Import navigation and preservation checks; no mathematical truth or equivalence is established.' }, null, 2));
