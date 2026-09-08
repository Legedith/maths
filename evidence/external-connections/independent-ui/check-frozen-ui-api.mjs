import assert from 'node:assert/strict';
import { createHash } from 'node:crypto';
import { readFileSync } from 'node:fs';
import { dirname, join, resolve } from 'node:path';
import { spawnSync } from 'node:child_process';
import { fileURLToPath, pathToFileURL } from 'node:url';

const auditDir = dirname(fileURLToPath(import.meta.url));
const project = resolve(auditDir, '../../project');
const read = (relative) => readFileSync(join(project, relative));
const json = (relative) => JSON.parse(read(relative).toString('utf8'));
const sha256 = (bytes) => createHash('sha256').update(bytes).digest('hex');

const freezePath = 'evidence/external-connections/application-freeze.json';
const freezeBytes = read(freezePath);
assert.equal(sha256(freezeBytes), '51033889d3d1b7666349fd51d97b56cf5c9fe014f17817ae671ffa91d934547c');
const freeze = JSON.parse(freezeBytes.toString('utf8'));
const freezeMismatches = [];
for (const entry of freeze.files) {
  const bytes = read(entry.path);
  if (bytes.length !== entry.bytes || sha256(bytes) !== entry.sha256)
    freezeMismatches.push(entry.path);
}
assert.deepEqual(freezeMismatches, []);

const relationModule = await import(pathToFileURL(join(project, 'lib/external-relations.ts')).href);
const { createRelationExplorer, relationApiResponse, validateRelationQuery } = relationModule;
const index = json('data/mathgloss/relations/relation-index.json');
const catalog = json('data/mathgloss/candidate-index.json');
const search = createRelationExplorer(index, catalog);

assert.equal(index.edges.length, 5390);
assert.equal(index.properties.length, 81);
assert.equal(index.summary.total_rows, 9159);
assert.equal(index.summary.included_rows, 5390);
assert.equal(index.summary.excluded_rows, 3769);
assert.equal(index.summary.endpoint_count, 3372);
assert.equal(index.summary.property_count, 81);
assert.equal(new Set(index.edges.map((edge) => edge.id)).size, index.edges.length);
assert(index.edges.every((edge, offset) => offset === 0 || index.edges[offset - 1].record < edge.record));
assert(index.properties.every((property, offset) => offset === 0 || Number(index.properties[offset - 1].id.slice(1)) < Number(property.id.slice(1))));
assert.equal(index.properties.reduce((sum, property) => sum + property.count, 0), index.edges.length);

const adjacency = new Map();
for (const edge of index.edges) {
  for (const qid of new Set([edge.source.id, edge.target.id])) {
    const rows = adjacency.get(qid) ?? [];
    rows.push(edge);
    adjacency.set(qid, rows);
  }
}
const expectedPropertyCounts = (incident) => {
  const counts = new Map();
  for (const edge of incident)
    counts.set(edge.property.id, (counts.get(edge.property.id) ?? 0) + 1);
  return index.properties
    .filter((property) => counts.has(property.id))
    .map((property) => ({ ...property, count: counts.get(property.id) }));
};

let querySelections = 0;
let pageVisits = 0;
let returnedEdgeVisits = 0;
for (const concept of catalog.records) {
  const qid = concept.identity_candidate.qid;
  const incident = adjacency.get(qid) ?? [];
  const properties = ['All', ...new Set(incident.map((edge) => edge.property.id))];
  const propertyCounts = expectedPropertyCounts(incident);
  for (const property of properties) {
    for (const direction of ['both', 'incoming', 'outgoing']) {
      const expected = incident.filter((edge) =>
        (property === 'All' || edge.property.id === property) &&
        (direction === 'both' || (direction === 'incoming' ? edge.target.id === qid : edge.source.id === qid))
      );
      const first = search({ qid, property, direction, page: 1 });
      assert.equal(first.concept, concept);
      assert.equal(first.total, expected.length);
      assert.equal(first.pages, Math.ceil(expected.length / 20));
      assert.equal(first.pageSize, 20);
      assert.deepEqual(first.properties, propertyCounts);
      assert.deepEqual(first.availableProperties, index.properties);
      assert.deepEqual(first.coverage, index.summary);
      const seen = [];
      for (let page = 1; page <= Math.max(1, first.pages); page++) {
        const result = page === 1 ? first : search({ qid, property, direction, page });
        const expectedPage = expected.slice((page - 1) * 20, page * 20);
        assert.deepEqual(result.edges.map((edge) => edge.id), expectedPage.map((edge) => edge.id));
        assert(result.edges.every((edge) => edge.source.id === qid || edge.target.id === qid));
        assert(result.edges.every((edge) => property === 'All' || edge.property.id === property));
        assert(result.edges.every((edge) => direction === 'both' || (direction === 'incoming' ? edge.target.id === qid : edge.source.id === qid)));
        const expectedObservations = Object.fromEntries(expectedPage.filter((edge) => index.observations[edge.id]).map((edge) => [edge.id, index.observations[edge.id]]));
        assert.deepEqual(result.observations, expectedObservations);
        seen.push(...result.edges.map((edge) => edge.id));
        pageVisits++;
        returnedEdgeVisits += result.edges.length;
      }
      assert.deepEqual(seen, expected.map((edge) => edge.id));
      assert.equal(new Set(seen).size, seen.length);
      querySelections++;
    }
  }
}

for (const invalid of [
  null, [], {}, { qid: 'Q0' }, { qid: 'Q01' }, { qid: 8366 },
  { qid: 'Q8366', property: null }, { qid: 'Q8366', direction: null },
  { qid: 'Q8366', page: null }, { qid: 'Q8366', page: 0 },
  { qid: 'Q8366', page: 1.5 }, { qid: 'Q8366', page: Infinity },
  { qid: 'Q8366', property: 'P0' }, { qid: 'Q8366', direction: 'inverse' },
  { qid: 'Q8366', extra: true }
]) assert.throws(() => validateRelationQuery(invalid));
assert.throws(() => search({ qid: 'Q999999999999999' }));
assert.throws(() => search({ qid: 'Q8366', property: 'P999999999999999' }));

const validApiQueries = [
  'qid=Q8366',
  'qid=Q11348&property=P279&direction=incoming&page=2',
  'qid=Q1051696&property=P460&direction=outgoing&page=1',
  'qid=Q28649150&property=P460&direction=incoming&page=1',
  'qid=Q8366&page=1000000'
];
let validApiRequests = 0;
for (const query of validApiQueries) {
  const response = relationApiResponse(new Request(`https://example.invalid/api/external-relations?${query}`), search);
  assert.equal(response.status, 200);
  assert.equal(response.headers.get('Cache-Control'), 'no-store');
  const result = await response.json();
  assert(Array.isArray(result.edges));
  assert(result.edges.length <= 20);
  validApiRequests++;
}
const farPage = await relationApiResponse(new Request('https://example.invalid/api/external-relations?qid=Q8366&page=1000000'), search).json();
assert(farPage.total > 0 && farPage.edges.length === 0 && farPage.page > farPage.pages);

const invalidApiQueries = [
  '', 'qid=Q0', 'qid=Q8366&qid=Q8366', 'qid=Q8366&extra=private-query',
  'qid=Q8366&page=0', 'qid=Q8366&page=01', 'qid=Q8366&page=1000001',
  'qid=Q8366&page=1.5', 'qid=Q8366&direction=inverse',
  'qid=Q8366&property=P999999999999999', 'qid=Q8366&property=',
  'qid=Q8366&direction=both&direction=incoming', 'qid=Q8366&page=1&page=2'
];
for (const query of invalidApiQueries) {
  const response = relationApiResponse(new Request(`https://example.invalid/api/external-relations${query ? `?${query}` : ''}`), search);
  assert.equal(response.status, 400);
  assert.equal(response.headers.get('Cache-Control'), 'no-store');
  const body = await response.text();
  assert(body.length < 100);
  assert(!body.includes('private-query'));
}

assert.deepEqual(Object.keys(index.observations).sort(), ['mathgloss-row-175', 'mathgloss-row-23', 'mathgloss-row-26']);
const observed = index.observations['mathgloss-row-175'];
assert.deepEqual(observed.field_presence, [{ statement_id: true, qualifiers: true, references: false }]);
assert.deepEqual(observed.source_entity, { id: 'Q1051696', lastrevid: 2429536034, modified: '2025-11-14T14:42:12Z' });
assert.equal(observed.display_labels.P460, 'said to be the same as');
assert.equal(observed.display_labels.P518, 'applies to part');
assert.equal(observed.display_labels.Q9085982, 'type IIA string theory');
const p518 = observed.matching_statements[0].qualifiers.P518[0];
assert.equal(p518.property, 'P518');
assert.equal(p518.datavalue.value.id, 'Q9085982');

const component = read('components/external-connections.tsx').toString('utf8');
for (const requiredText of [
  "Object.hasOwn(statement, 'qualifiers')",
  'empty container in the dated response',
  'An empty value list was supplied.',
  'observation.source_entity.lastrevid',
  'observation.source_entity.modified',
  'observation.requested_url',
  'visibleResult.current',
  'window.history.replaceState',
  'The previous selection is shown and its URL has been restored.',
  'result.total > 0 && !result.edges.length',
  'Open the first page',
  'Said to be the same as',
  'not a proof of equivalence',
  'edge.source.label',
  'edge.property.label',
  'edge.property.id',
  'edge.target.label'
]) assert(component.includes(requiredText), `missing UI contract text/code: ${requiredText}`);
assert(component.includes('.slice(0, 6)'));
assert(component.includes('The full list follows.'));

const priorPage = join(project, 'evidence/external-connections/app-page-before.tsx');
const currentPage = join(project, 'app/page.tsx');
const diff = spawnSync('git', ['diff', '--no-index', '--unified=0', '--', priorPage, currentPage], { encoding: 'utf8' });
assert.equal(diff.status, 1);
const diffLines = diff.stdout.split(/\r?\n/);
const removedLines = diffLines.filter((line) => line.startsWith('-') && !line.startsWith('---'));
const addedLines = diffLines.filter((line) => line.startsWith('+') && !line.startsWith('+++'));
assert.deepEqual(removedLines, []);
assert.equal(addedLines.length, 6);
assert(addedLines.some((line) => line.includes('href="/connections"')));
assert(addedLines.some((line) => line.includes('Explore external connections')));

const viteUrl = pathToFileURL(join(project, 'node_modules/vite/dist/node/index.js')).href;
const { createServer } = await import(viteUrl);
const vite = await createServer({ root: project, configFile: false, logLevel: 'silent', appType: 'custom', server: { middlewareMode: true } });
let tool;
let toolCalls = 0;
let toolInput;
try {
  const hook = await vite.ssrLoadModule('/lib/use-external-relation-tools.ts');
  tool = hook.externalRelationTool(async (input) => {
    toolCalls++;
    toolInput = input;
    return search(input);
  });
  assert.equal(tool.name, 'explore_external_connections');
  assert.deepEqual(tool.annotations, { readOnlyHint: false, untrustedContentHint: true });
  assert.deepEqual(tool.inputSchema.required, ['qid']);
  assert.equal(tool.inputSchema.additionalProperties, false);
  const toolResult = await tool.execute({ qid: 'Q1051696', property: 'P460', direction: 'outgoing', page: 1 });
  assert.deepEqual(toolInput, { qid: 'Q1051696', property: 'P460', direction: 'outgoing', page: 1 });
  assert.equal(toolResult.total, 1);
  assert.equal(toolResult.edges[0].id, 'mathgloss-row-175');
  assert.equal(toolResult.observations['mathgloss-row-175'].matching_statements[0].qualifiers.P518[0].datavalue.value.id, 'Q9085982');
  const callsBeforeInvalid = toolCalls;
  assert.throws(() => tool.execute({ qid: 'Q1051696', property: null }));
  assert.throws(() => tool.execute({ qid: 'Q1051696', extra: true }));
  assert.equal(toolCalls, callsBeforeInvalid);
  await assert.rejects(() => tool.execute({ qid: 'Q1051696', property: 'P999999999999999' }));
} finally {
  await vite.close();
}

const webMcpPath = 'evidence/external-connections/validation/webmcp-observation.json';
const webMcpBytes = read(webMcpPath);
assert.equal(sha256(webMcpBytes), 'd2b6d9c812edd6d998f9fd5bc98338c739d1c23eeee285351f1af515777c170c');
const webMcp = JSON.parse(webMcpBytes.toString('utf8'));
assert.equal(webMcp.application_freeze_sha256, sha256(freezeBytes));
assert.equal(webMcp.registered_tool.name, tool.name);
assert.deepEqual(webMcp.registered_tool.inputSchema, tool.inputSchema);
assert.deepEqual(webMcp.registered_tool.annotations, tool.annotations);
const expectedToolResult = search(webMcp.valid_call.input);
assert.deepEqual(webMcp.valid_call.selected_fields_from_actual_return.edges, expectedToolResult.edges);
assert.deepEqual(webMcp.valid_call.selected_fields_from_actual_return.observations, expectedToolResult.observations);
assert.equal(webMcp.valid_call.selected_fields_from_actual_return.total, expectedToolResult.total);
assert.equal(webMcp.invalid_call.rejected, true);
assert(webMcp.invalid_call.after_url.includes('qid=Q1051696&property=P460&direction=outgoing&page=1'));
assert(webMcp.valid_call.accessibility_readback_exact_excerpts.some((line) => line.includes('applies to part (P518)')));
assert(webMcp.valid_call.accessibility_readback_exact_excerpts.some((line) => line.includes('type IIA string theory (Q9085982)')));

console.log(JSON.stringify({
  schema_version: 'independent-frozen-relation-ui-api-check-v1',
  status: 'pass',
  auditor: '/root/sol_symmetry_audit',
  application_freeze_sha256: sha256(freezeBytes),
  frozen_files_checked: freeze.files.length,
  freeze_mismatches: freezeMismatches,
  catalog_records: catalog.records.length,
  relation_edges: index.edges.length,
  relation_properties: index.properties.length,
  query_selections_checked: querySelections,
  page_visits_checked: pageVisits,
  returned_edge_visits: returnedEdgeVisits,
  valid_api_requests: validApiRequests,
  invalid_api_requests: invalidApiQueries.length,
  invalid_direct_inputs: 17,
  tool_calls_reaching_action: toolCalls,
  exact_probe_overlays: Object.keys(index.observations).length,
  webmcp_observation_sha256: sha256(webMcpBytes),
  webmcp_evidence_scope: 'Root-observed focused browser-host transcript, independently cross-checked against frozen tool code, query result and imported observation; no independent browser replication.',
  home_page_delta: { removed_lines: removedLines.length, added_lines: addedLines.length, connection_link_only: true },
  limits: 'Application/query correctness for the frozen imported index. Whole-row source fidelity and importer reproduction are separately owned; no relation truth, identity, equivalence, completeness, novelty, productivity or broad visual claim.'
}, null, 2));
