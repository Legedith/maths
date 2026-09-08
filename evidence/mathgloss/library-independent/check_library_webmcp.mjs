import assert from 'node:assert/strict';
import { createHash } from 'node:crypto';
import { readFileSync, writeFileSync } from 'node:fs';
import { pathToFileURL } from 'node:url';

const ROOT = 'D:/CodexWorkspaces/mathematics-atlas';
const PROJECT = `${ROOT}/project`;
const AUDIT = `${ROOT}/library-audit-work`;
const EXPECTED_FREEZE_HASH = '68bd8c6f8ff2dfaa1c1b26b1d4c030025ae1a6d84004767c8b537939f09ef316';
const EXPECTED_OBSERVATION_HASH = 'beb6db553da7d76693c3d706cf156dfeb886c260f7a0825bd90678875da158f6';
const hash = (data) => createHash('sha256').update(data).digest('hex');

assert.equal(
  hash(readFileSync(`${PROJECT}/evidence/mathgloss/library-integration-freeze.json`)),
  EXPECTED_FREEZE_HASH,
);
const observationBytes = readFileSync(
  `${PROJECT}/evidence/mathgloss/library-webmcp-observations.json`,
);
assert.equal(hash(observationBytes), EXPECTED_OBSERVATION_HASH);
const observations = JSON.parse(observationBytes.toString('utf8'));
assert.equal(observations.implementation_freeze_sha256, EXPECTED_FREEZE_HASH);

const { conceptLibraryTool } = await import(
  pathToFileURL(`${PROJECT}/lib/use-concept-library-tools.ts`).href
);
const calls = [];
const sentinel = {
  query: 'Fourier',
  resource: 'All',
  page: 1,
  records: [],
  total: 0,
  pageSize: 20,
  pages: 0,
  catalogRecords: 4814,
  catalogLinks: 7217,
  resources: [],
};
const tool = conceptLibraryTool(async (input) => {
  calls.push(input);
  return { ...sentinel, ...input };
});
assert.equal(tool.name, 'search_learning_resources');
assert.equal(tool.inputSchema.type, 'object');
assert.deepEqual(tool.inputSchema.required, ['query']);
assert.equal(tool.inputSchema.additionalProperties, false);
assert.equal(tool.inputSchema.properties.query.maxLength, 500);
assert.equal(tool.inputSchema.properties.resource.minLength, 1);
assert.equal(tool.inputSchema.properties.resource.maxLength, 80);
assert.equal(tool.inputSchema.properties.page.type, 'integer');
assert.equal(tool.inputSchema.properties.page.minimum, 1);
assert.equal(tool.inputSchema.properties.page.maximum, 1000000);
assert.deepEqual(tool.annotations, {
  readOnlyHint: false,
  untrustedContentHint: true,
});
assert.match(tool.description, /unreviewed/);
assert.match(tool.description, /miss does not establish novelty/);

const returned = await tool.execute({ query: '  Fourier  ' });
assert.deepEqual(calls, [{ query: 'Fourier', resource: 'All', page: 1 }]);
assert.equal(returned.query, 'Fourier');
assert.equal(returned.resource, 'All');
assert.equal(returned.page, 1);
for (const invalid of [
  { query: true },
  { query: '', page: 0 },
  { query: '', resource: '' },
  { query: '', extra: 1 },
]) {
  assert.throws(() => tool.execute(invalid));
}
assert.equal(calls.length, 1, 'invalid inputs must not reach the search action');

const componentSource = readFileSync(
  `${PROJECT}/components/concept-library.tsx`,
  'utf8',
);
const hookSource = readFileSync(
  `${PROJECT}/lib/use-concept-library-tools.ts`,
  'utf8',
);
assert.match(componentSource, /useConceptLibraryTools\(runSearch\)/);
assert.match(componentSource, /void runSearch\(next\)\.catch/);
assert.match(componentSource, /setQuery\(request\.query\)/);
assert.match(componentSource, /setResource\(request\.resource\)/);
assert.match(componentSource, /setResult\(next\)/);
assert.match(componentSource, /search\(\{ query, resource, page: 1 \}\)/);
assert.match(componentSource, /search\(\{ query: word, resource: 'All', page: 1 \}\)/);
assert(!/localStorage|sessionStorage|document\.cookie|sendBeacon/.test(componentSource));
assert.match(hookSource, /execute: \(input: unknown\) => search\(validateLibraryQuery\(input\)\)/);

const sourceIndex = JSON.parse(
  readFileSync(`${PROJECT}/data/mathgloss/candidate-index.json`, 'utf8'),
);
const byQid = new Map(
  sourceIndex.records.map((record) => [record.identity_candidate.qid, record]),
);
const firstObservation = observations.observations[0];
const observedSource = byQid.get(firstObservation.returned.qid);
assert(observedSource);
assert.equal(firstObservation.returned.label, observedSource.label_as_recorded);
assert.deepEqual(
  firstObservation.returned.physical_lines,
  observedSource.source_locator.physical_lines,
);
assert.equal(firstObservation.returned.label, 'Deutsch\u2013Jozsa algorithm');
assert(!firstObservation.returned.label.includes('\uFFFD'));
assert.equal(firstObservation.visible_query, firstObservation.input.query);
assert.match(firstObservation.visible_heading, /^1 matching records/);
assert.equal(
  firstObservation.source_link,
  'https://github.com/MathGloss/MathGloss/blob/b8f659605486f80f2816515f525af2c395c711fa/data/database.csv#L31-L31',
);
const invalidObservation = observations.observations[1];
assert.equal(invalidObservation.visible_query_after_failure, firstObservation.visible_query);
assert.equal(
  invalidObservation.visible_heading_after_failure,
  firstObservation.visible_heading,
);
const mathlibObservation = observations.observations[2];
assert.equal(mathlibObservation.returned.total, 308);
assert.equal(mathlibObservation.returned.page, 2);
assert.equal(mathlibObservation.returned.pages, 16);
assert.equal(mathlibObservation.returned.record_count, 20);
assert.equal(mathlibObservation.returned.every_record_has_mathlib, true);
assert.equal(mathlibObservation.visible_query, '');
assert.match(mathlibObservation.visible_heading, /^308 matching records in Mathlib$/);

const report = {
  schema_version: 'concept-library-independent-webmcp-contract-check-v1',
  status: 'pass',
  freeze_sha256: EXPECTED_FREEZE_HASH,
  hook_sha256: hash(Buffer.from(hookSource)),
  component_sha256: hash(Buffer.from(componentSource)),
  root_observation_sha256: EXPECTED_OBSERVATION_HASH,
  tool: {
    name: tool.name,
    input_schema: tool.inputSchema,
    annotations: tool.annotations,
    valid_action_calls: calls.length,
    invalid_inputs_blocked_before_action: 4,
  },
  shared_state_static_alignment: {
    ordinary_form_calls_runSearch: true,
    webmcp_registers_same_runSearch: true,
    runSearch_updates_visible_query_resource_result: true,
    ordinary_submit_resets_page_one: true,
    example_search_resets_resource_and_page: true,
  },
  observation_source_check: {
    observer: 'root implementation integrator; independently checked here against the frozen source and code contract',
    unicode_qid_record_exact: true,
    invalid_input_state_unchanged: true,
    mathlib_page_two_counts_and_visible_state_aligned: true,
  },
  annotation_note:
    'readOnlyHint false is consistent with the intentional visible client-state update. The API itself remains GET-only and no persistent or external data mutation was found. untrustedContentHint true is appropriate for imported labels and links.',
  limits: [
    'The browser observations were produced by the root integrator, not this reviewer; this check independently verifies their artifact hash, source values and alignment with the frozen code path.',
    'This checks tool and visible-state semantics, not broad browser layout or destination content.',
  ],
};
writeFileSync(`${AUDIT}/webmcp-contract-check.json`, `${JSON.stringify(report, null, 2)}\n`, 'utf8');
console.log(JSON.stringify({ status: report.status, output: `${AUDIT}/webmcp-contract-check.json` }));
