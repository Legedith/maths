import assert from 'node:assert/strict';
import { createHash } from 'node:crypto';
import { readFileSync, writeFileSync } from 'node:fs';
import { pathToFileURL } from 'node:url';

const ROOT = 'D:/CodexWorkspaces/mathematics-atlas';
const PROJECT = `${ROOT}/project`;
const AUDIT = `${ROOT}/library-audit-work`;
const FREEZE = `${PROJECT}/evidence/mathgloss/library-integration-freeze.json`;
const EXPECTED_FREEZE_HASH = '68bd8c6f8ff2dfaa1c1b26b1d4c030025ae1a6d84004767c8b537939f09ef316';
const hash = (data) => createHash('sha256').update(data).digest('hex');
const freezeBytes = readFileSync(FREEZE);
assert.equal(hash(freezeBytes), EXPECTED_FREEZE_HASH);
const freeze = JSON.parse(freezeBytes.toString('utf8'));

function frozenHashes() {
  return Object.fromEntries(
    Object.entries(freeze.file_sha256).map(([path, expected]) => {
      const actual = hash(readFileSync(`${PROJECT}/${path}`));
      assert.equal(actual, expected, path);
      return [path, actual];
    }),
  );
}

const before = frozenHashes();
const route = await import(
  pathToFileURL(`${PROJECT}/app/api/concept-library/route.ts`).href
);
assert.deepEqual(Object.keys(route).sort(), ['GET']);
const sourceIndex = JSON.parse(
  readFileSync(`${PROJECT}/data/mathgloss/candidate-index.json`, 'utf8'),
);
const sourceByKey = new Map(
  sourceIndex.records.map((record) => [record.record_key, record]),
);

async function request(search = '') {
  const response = route.GET(
    new Request(`http://audit.invalid/api/concept-library${search}`),
  );
  const text = await response.text();
  return { response, text, body: JSON.parse(text) };
}

function checkHeaders(result) {
  assert.equal(result.response.headers.get('cache-control'), 'no-store');
  assert.match(result.response.headers.get('content-type') ?? '', /application\/json/);
}

const validResults = [];
for (const [id, search, expected] of [
  ['default', '', { status: 200, total: 4814, page: 1, count: 20 }],
  [
    'unicode-qid',
    '?q=%EF%BC%B1%EF%BC%91%EF%BC%90%EF%BC%92%EF%BC%98%EF%BC%92%EF%BC%90%EF%BC%99',
    { status: 200, total: 1, page: 1, count: 1 },
  ],
  [
    'mathlib-page-2',
    '?q=&resource=Mathlib&page=2',
    { status: 200, total: 308, page: 2, count: 20 },
  ],
  ['miss', '?q=compact%20Hausdorff', { status: 200, total: 0, page: 1, count: 0 }],
  ['beyond-last', '?q=Q1028209&page=2', { status: 200, total: 1, page: 2, count: 0 }],
]) {
  const result = await request(search);
  checkHeaders(result);
  assert.equal(result.response.status, expected.status, id);
  assert.equal(result.body.total, expected.total, id);
  assert.equal(result.body.page, expected.page, id);
  assert.equal(result.body.records.length, expected.count, id);
  assert.equal(result.body.pageSize, 20, id);
  assert.equal(result.body.catalogRecords, 4814, id);
  assert.equal(result.body.catalogLinks, 7217, id);
  for (const record of result.body.records) {
    assert.deepEqual(record, sourceByKey.get(record.record_key), `${id}:${record.record_key}`);
  }
  if (id === 'unicode-qid') {
    assert.equal(result.body.records[0].identity_candidate.qid, 'Q1028209');
    assert.equal(result.body.records[0].label_as_recorded, 'Deutsch\u2013Jozsa algorithm');
    assert(!result.text.includes('\uFFFD'));
  }
  if (id === 'mathlib-page-2')
    assert(
      result.body.records.every((record) =>
        record.links.some((link) => link.source === 'Mathlib'),
      ),
    );
  validResults.push({ id, status: result.response.status, bytes: Buffer.byteLength(result.text), total: result.body.total, count: result.body.records.length });
}

const invalidCases = [
  ['unsupported-field', '?extra=1'],
  ['duplicate-q', '?q=a&q=b'],
  ['duplicate-resource', '?resource=nLab&resource=BCT'],
  ['duplicate-page', '?page=1&page=2'],
  ['page-zero', '?page=0'],
  ['page-negative', '?page=-1'],
  ['page-fraction', '?page=1.5'],
  ['page-nonnumeric', '?page=abc'],
  ['page-leading-zero', '?page=01'],
  ['page-eight-digits', '?page=10000000'],
  ['page-over-validator-max', '?page=1000001'],
  ['unknown-resource', '?resource=UnknownCorpus'],
  ['empty-resource', '?resource='],
  ['oversized-resource', `?resource=${'x'.repeat(81)}`],
  ['oversized-query', `?q=${'x'.repeat(501)}`],
];
const invalidResults = [];
for (const [id, search] of invalidCases) {
  const result = await request(search);
  checkHeaders(result);
  assert.equal(result.response.status, 400, id);
  assert.deepEqual(Object.keys(result.body), ['error'], id);
  assert.equal(typeof result.body.error, 'string', id);
  assert(result.body.error.length <= 100, id);
  assert(Buffer.byteLength(result.text) <= 160, id);
  assert(!/[A-Z]:[\\/]/.test(result.text), id);
  assert(!/stack|traceback|node_modules|candidate-index/i.test(result.text), id);
  if (id === 'oversized-query') assert(!result.text.includes('x'.repeat(20)));
  invalidResults.push({ id, status: result.response.status, bytes: Buffer.byteLength(result.text), error: result.body.error });
}

const repeatA = await request('?q=abelian%20group&resource=Chicago&page=1');
const repeatB = await request('?q=abelian%20group&resource=Chicago&page=1');
assert.equal(repeatA.text, repeatB.text);
assert.equal(repeatA.body.total, 2);
assert(
  repeatA.body.records.every((record) =>
    record.links.some((link) => link.source === 'Chicago'),
  ),
);
const after = frozenHashes();
assert.deepEqual(after, before);

const routeSource = readFileSync(
  `${PROJECT}/app/api/concept-library/route.ts`,
  'utf8',
);
assert(!/\b(fetch|writeFile|appendFile|unlink|rename|rm)\s*\(/.test(routeSource));
assert.match(routeSource, /Cache-Control['"]?: ['"]no-store/);

const report = {
  schema_version: 'concept-library-independent-route-check-v1',
  status: 'pass',
  freeze_sha256: EXPECTED_FREEZE_HASH,
  route_sha256: hash(Buffer.from(routeSource)),
  frozen_files_checked_before_and_after: Object.keys(before).length,
  state_mutation_detected: false,
  exported_handlers: Object.keys(route).sort(),
  valid_cases: validResults,
  invalid_cases: invalidResults,
  deterministic_repeat: {
    query: 'abelian group',
    resource: 'Chicago',
    total: repeatA.body.total,
    byte_identical: repeatA.text === repeatB.text,
  },
  cache_control: 'no-store',
  response_boundary: {
    maximum_observed_error_bytes: Math.max(...invalidResults.map((item) => item.bytes)),
    arbitrary_input_echoed: false,
    filesystem_or_stack_disclosed: false,
  },
  privacy_and_read_only_notes: [
    'The route exports only GET, performs no fetch or filesystem mutation, and all 24 frozen files stayed byte-identical.',
    'No-store prevents response caching, and the static route code sends no query to MathGloss or another provider.',
    'Because the API uses GET, user query text is present in the same-origin request URL and may be observable to ordinary same-origin access logging; no stronger secrecy claim is made.',
  ],
};
writeFileSync(`${AUDIT}/route-check.json`, `${JSON.stringify(report, null, 2)}\n`, 'utf8');
console.log(JSON.stringify({ status: report.status, output: `${AUDIT}/route-check.json` }));
