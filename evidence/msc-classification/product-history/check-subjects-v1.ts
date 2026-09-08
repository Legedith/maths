import assert from 'node:assert/strict';
import { createHash } from 'node:crypto';
import { mkdirSync, readFileSync, writeFileSync } from 'node:fs';
import { dirname, resolve } from 'node:path';
import { createSubjectCatalog, type SubjectIndex, type ReferenceIndex } from '../lib/subject-index.ts';

const args = process.argv.slice(2);
const option = (name: string) => args.includes(name) ? args[args.indexOf(name) + 1] : undefined;
const output = option('--output'), origin = option('--http-origin');
const checks: { name: string; passed: boolean; detail?: string }[] = [];
const check = (name: string, action: () => void) => { action(); checks.push({ name, passed: true }); };
const load = (name: string, hash: string) => {
  const bytes = readFileSync(new URL(`../data/msc/${name}`, import.meta.url));
  assert.equal(createHash('sha256').update(bytes).digest('hex'), hash);
  return JSON.parse(bytes.toString('utf8'));
};
let failure: unknown;
try {
  const index = load('subjects.json', '32fb0eddc9f189e68b9fa312e8e29c399deee65d4d282d1e61235be33a22400e') as SubjectIndex;
  const references = load('references.json', '75ecd4b71056274ad342c72a5324770e2257e0ff3a88662dfe457c9127b4bc35') as ReferenceIndex;
  const catalog = createSubjectCatalog(index, references);
  check('catalogue totals', () => assert.deepEqual(catalog.stats, { subjects: 6603, topLevels: 63, references: 3083 }));
  const allCodes: string[] = [];
  const first = catalog.search({ query: '', parent: 'all' });
  for (let page = 1; page <= first.pages; page++) {
    const result = catalog.search({ query: '', parent: 'all', page });
    assert(result.records.length <= 24);
    allCodes.push(...result.records.map(row => row.code));
  }
  check('all catalogue pages retain every source record in order', () => assert.deepEqual(allCodes, index.subjects.map(row => row.code)));
  const expectedChildren = new Map<string | null, string[]>();
  for (const row of index.subjects) { const list = expectedChildren.get(row.navigation_parent_code) ?? []; list.push(row.code); expectedChildren.set(row.navigation_parent_code, list); }
  const traversed: string[] = [];
  for (const [parent, expected] of expectedChildren) {
    const request = { query: '', parent: parent ?? 'root' };
    const result = catalog.search(request), actual: string[] = [];
    for (let page = 1; page <= result.pages; page++) actual.push(...catalog.search({ ...request, page }).records.map(row => row.code));
    assert.deepEqual(actual, expected); traversed.push(...actual);
  }
  check('all parent pages retain every subject exactly once', () => { assert.equal(new Set(traversed).size, 6603); assert.equal(traversed.length, 6603); });
  let outgoing = 0, incoming = 0;
  for (const source of index.subjects) {
    const detail = catalog.detail(source.code);
    assert.deepEqual(detail.subject, source);
    assert.equal(detail.childCount, expectedChildren.get(source.code)?.length ?? 0);
    assert.equal(source.is_leaf, detail.childCount === 0);
    assert.equal(detail.ancestors.length + 1, source.hierarchy_level);
    outgoing += detail.outgoing.length; incoming += detail.incoming.length;
  }
  check('every detail retains its subject and exact hierarchy depth', () => { assert.equal(outgoing, 3083); assert.equal(incoming, 3082); });
  for (const query of ['68Q25', '６８Ｑ２５']) check(`code search ${query}`, () => assert(catalog.search({ query }).records.some(row => row.code === '68Q25')));
  check('all three conditional references retain scopes', () => { const result = catalog.detail('03B45'); assert.equal(result.outgoing.length, 3); assert(result.outgoing.every(row => row.scope_records.length === 1 && row.scope_records[0].scopes.length > 0)); });
  check('collection target stays a 62-member collection', () => { const result = catalog.detail('00A15'); assert.equal(result.collections.length, 1); assert.equal(result.collections[0].members.length, 62); assert(result.outgoing.some(row => row.target_kind === 'collection')); });
  check('dual-parent source record is preserved', () => { const row = catalog.detail('32-00').subject; assert.equal(row.hierarchy_level, 2); assert.equal(row.is_leaf, true); assert.equal(row.navigation_parent_code, '32-XX'); assert.equal(row.rdf_broader_uris.length, 2); assert.equal(row.hierarchy_disagreement, true); });
  check('label differences stay marked', () => assert.equal(catalog.detail('01A16').subject.exact_label_difference, true));
  const invalid = [null, [], {}, { query: null }, { query: 'x'.repeat(301) }, { query: '', parent: null }, { query: '', parent: '99-XX' }, { query: '', parent: '../68-XX' }, { query: '', page: null }, { query: '', page: 0 }, { query: '', page: 1.5 }, { query: '', page: 1000001 }, { query: '', extra: true }];
  invalid.forEach((request, i) => check(`invalid search ${i + 1}`, () => assert.throws(() => catalog.search(request))));
  [null, '', '68-xx', '99-XX', '../68-XX'].forEach((code, i) => check(`invalid detail ${i + 1}`, () => assert.throws(() => catalog.detail(code))));
  check('empty result page is explicit', () => assert.equal(catalog.search({ query: 'not-a-real-subject-xyz' }).records.length, 0));
  if (origin) {
    const httpCases: [string, unknown][] = [
      ['/api/subjects', catalog.search({ query: '' })],
      ['/api/subjects?q=68Q25', catalog.search({ query: '68Q25' })],
      ['/api/subjects?parent=68-XX&page=2', catalog.search({ query: '', parent: '68-XX', page: 2 })],
      ...['03B45', '00A15', '32-00', '01A16', '68Q25'].map(code => [`/api/subjects?code=${code}`, catalog.detail(code)] as [string, unknown]),
    ];
    for (const [path, expected] of httpCases) {
      const response = await fetch(new URL(path, origin));
      assert.equal(response.status, 200); assert.equal(response.headers.get('cache-control'), 'no-store');
      assert.deepEqual(await response.json(), expected); checks.push({ name: `HTTP exact response ${path}`, passed: true });
    }
    for (const query of ['code=99-XX', 'code=68-XX&q=x', 'q=x&q=y', 'code=68-XX&code=03B45', 'page=0', 'page=01', 'page=1.5', 'page=1000001', 'parent=99-XX', 'unknown=x', `q=${'x'.repeat(301)}`]) {
      const response = await fetch(new URL(`/api/subjects?${query}`, origin));
      assert.equal(response.status, 400); assert.equal(response.headers.get('cache-control'), 'no-store');
      checks.push({ name: `HTTP rejected ${query.length > 80 ? 'oversized query' : query}`, passed: true });
    }
    for (const [path, status] of [['/subjects', 200], ['/subjects/68-XX', 200], ['/subjects/03B45', 200], ['/subjects/00A15', 200], ['/subjects/32-00', 200], ['/subjects/01A16', 200], ['/subjects/99-XX', 404]] as const) {
      const response = await fetch(new URL(path, origin)); assert.equal(response.status, status); await response.arrayBuffer(); checks.push({ name: `server route ${path}`, passed: true });
    }
  }
} catch (error) { failure = error; checks.push({ name: 'verification failure', passed: false, detail: String(error) }); }
const result = { schema_version: 'msc-product-checks-v1', status: failure ? 'fail' : 'pass', checks, passed: checks.filter(row => row.passed).length, failed: checks.filter(row => !row.passed).length, http_origin: origin ?? null, limitation: 'Functional source/navigation/API checks; no semantic-equivalence or visual-browser evaluation.' };
if (output) { mkdirSync(dirname(resolve(output)), { recursive: true }); writeFileSync(output, JSON.stringify(result, null, 2) + '\n', { encoding: 'utf8', flag: 'wx' }); }
console.log(JSON.stringify(result));
if (failure) { console.error(failure); process.exitCode = 1; }
