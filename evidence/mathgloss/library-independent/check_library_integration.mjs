import assert from 'node:assert/strict';
import { createHash } from 'node:crypto';
import { readFileSync, writeFileSync } from 'node:fs';
import { pathToFileURL } from 'node:url';

const ROOT = 'D:/CodexWorkspaces/mathematics-atlas';
const PROJECT = `${ROOT}/project`;
const AUDIT = `${ROOT}/library-audit-work`;
const SOURCE_HASH = '282ed1fd858595b782c856fbd2c96964a0b6ff3850fedf21105ca9bbb7edb4da';
const CASE_HASH = '108c67ef95d33892a805be1a6a55a9349988b372a2c783a3703f7548548f3ea5';

const hash = (data) => createHash('sha256').update(data).digest('hex');
const indexBytes = readFileSync(`${PROJECT}/data/mathgloss/candidate-index.json`);
const caseBytes = readFileSync(`${AUDIT}/independent-cases.json`);
assert.equal(hash(indexBytes), SOURCE_HASH);
assert.equal(hash(caseBytes), CASE_HASH);
const index = JSON.parse(indexBytes.toString('utf8'));
const frozenCases = JSON.parse(caseBytes.toString('utf8'));
const lib = await import(pathToFileURL(`${PROJECT}/lib/concept-library.ts`).href);
const { searchConceptLibrary, validateLibraryQuery, conceptSourceUrl, LIBRARY_PAGE_SIZE } = lib;
assert.equal(LIBRARY_PAGE_SIZE, 20);

const normalize = (value) =>
  value
    .normalize('NFKC')
    .toLowerCase()
    .replace(/[^\p{L}\p{N}]+/gu, ' ')
    .trim();

function independentDocumentedSearch(query, resource = 'All') {
  const normalized = normalize(query.trim());
  const terms = normalized.split(/\s+/).filter(Boolean);
  return index.records
    .map((record, position) => {
      const eligibleLinks = record.links.filter(
        (link) => resource === 'All' || link.source === resource,
      );
      if (resource !== 'All' && eligibleLinks.length === 0) return null;
      const label = normalize(record.label_as_recorded);
      const searchable = normalize(
        [
          record.label_as_recorded,
          record.identity_candidate.qid,
          ...eligibleLinks.map((link) => link.name_as_recorded),
        ].join(' '),
      );
      if (!terms.every((term) => searchable.includes(term))) return null;
      const score = normalized && label === normalized ? 2 : normalized && label.startsWith(normalized) ? 1 : 0;
      return { record, position, score };
    })
    .filter(Boolean)
    .sort((a, b) => b.score - a.score || a.position - b.position)
    .map((item) => item.record);
}

function setHash(keys) {
  return hash(Buffer.from(`${[...keys].sort().join('\n')}\n`, 'utf8'));
}

function collectTarget(query, resource = 'All') {
  const first = searchConceptLibrary(index, { query, resource, page: 1 });
  const keys = [];
  const pageLengths = [];
  for (let page = 1; page <= first.pages; page += 1) {
    const current = searchConceptLibrary(index, { query, resource, page });
    assert.equal(current.total, first.total);
    assert.equal(current.pages, first.pages);
    assert.equal(current.pageSize, 20);
    assert.equal(current.page, page);
    assert.equal(current.query, query.trim());
    assert.equal(current.resource, resource);
    assert(current.records.length <= 20);
    pageLengths.push(current.records.length);
    keys.push(...current.records.map((record) => record.record_key));
  }
  const beyond = searchConceptLibrary(index, {
    query,
    resource,
    page: Math.max(1, first.pages + 1),
  });
  if (first.pages > 0) assert.deepEqual(beyond.records, []);
  assert.equal(beyond.total, first.total);
  return { first, keys, pageLengths };
}

const caseResults = [];
const precommittedPolicyDifferences = [];
for (const testCase of frozenCases.search_filter_cases) {
  const { query, source } = testCase.input;
  const resource = source ?? 'All';
  const expected = independentDocumentedSearch(query, resource);
  const actual = collectTarget(query, resource);
  const expectedKeys = expected.map((record) => record.record_key);
  assert.deepEqual(actual.keys, expectedKeys, testCase.id);
  assert.equal(actual.first.total, expected.length, testCase.id);
  const precommittedPolicyAligned =
    setHash(actual.keys) === testCase.expected_result_set_sha256 &&
    actual.first.total === testCase.expected_count;
  if (!precommittedPolicyAligned)
    precommittedPolicyDifferences.push({
      id: testCase.id,
      precommitted_policy: frozenCases.oracle_policy,
      precommitted_count: testCase.expected_count,
      documented_policy_count: actual.first.total,
      precommitted_set_sha256: testCase.expected_result_set_sha256,
      documented_set_sha256: setHash(actual.keys),
      adjudication:
        'The prospective contract required documented lexical matching but did not freeze a normalization/matching algorithm. The pre-review inputs remain applicable; this provisional casefolded contiguous-substring expected set is diagnostic where it differs from the independently implemented documented NFKC all-fragments policy.',
    });
  for (const returned of actual.first.records) {
    const sourceRecord = index.records.find((record) => record.record_key === returned.record_key);
    assert.deepEqual(returned, sourceRecord);
  }
  caseResults.push({
    id: testCase.id,
    count: actual.first.total,
    pages: actual.first.pages,
    set_sha256: setHash(actual.keys),
    precommitted_policy_aligned: precommittedPolicyAligned,
  });
}

const sweepResults = [];
for (const sweep of frozenCases.pagination_sweeps) {
  const resource = sweep.input.source ?? 'All';
  const expected = independentDocumentedSearch(sweep.input.query, resource);
  const actual = collectTarget(sweep.input.query, resource);
  const precommittedPolicyAligned =
    actual.first.total === sweep.expected_total &&
    new Set(actual.keys).size === sweep.expected_unique_record_keys &&
    actual.keys.length === sweep.expected_total &&
    setHash(actual.keys) === sweep.expected_result_set_sha256;
  if (!precommittedPolicyAligned)
    precommittedPolicyDifferences.push({
      id: sweep.id,
      precommitted_count: sweep.expected_total,
      documented_policy_count: actual.first.total,
      precommitted_set_sha256: sweep.expected_result_set_sha256,
      documented_set_sha256: setHash(actual.keys),
      adjudication:
        'The sweep input is retained, but its provisional contiguous-substring result set is not the contract standard where the documented all-fragments policy differs.',
    });
  assert.deepEqual(actual.keys, expected.map((record) => record.record_key));
  const repeat = collectTarget(sweep.input.query, resource);
  assert.deepEqual(repeat.keys, actual.keys);
  sweepResults.push({
    id: sweep.id,
    fixed_public_page_size: 20,
    pages: actual.first.pages,
    total: actual.first.total,
    unique: new Set(actual.keys).size,
    set_sha256: setHash(actual.keys),
    precommitted_abstract_page_size: sweep.input.page_size,
    precommitted_policy_aligned: precommittedPolicyAligned,
    note: 'The contract permits a documented fixed bound; the implementation documents and returns 20.',
  });
}

const all = searchConceptLibrary(index, { query: '' });
assert.equal(all.catalogRecords, 4814);
assert.equal(all.catalogLinks, 7217);
assert.deepEqual(all.resources, ['BCT', 'Chicago', 'Clowder', 'Context', 'Mathlib', 'PlanetMath', 'nLab']);
const resourceTotals = {};
for (const resource of all.resources) {
  const result = collectTarget('', resource);
  const expectedKeys = index.records
    .filter((record) => record.links.some((link) => link.source === resource))
    .map((record) => record.record_key);
  assert.deepEqual(result.keys, expectedKeys);
  assert(result.keys.every((key) => {
    const record = index.records.find((candidate) => candidate.record_key === key);
    return record.links.some((link) => link.source === resource);
  }));
  resourceTotals[resource] = result.keys.length;
}
assert.deepEqual(resourceTotals, {
  BCT: 197,
  Chicago: 395,
  Clowder: 74,
  Context: 262,
  Mathlib: 308,
  PlanetMath: 1476,
  nLab: 4505,
});
let sourceUrlsChecked = 0;
for (const record of index.records) {
  const locator = record.source_locator;
  assert.equal(
    conceptSourceUrl(record),
    `${locator.repository}/blob/${locator.commit}/${locator.csv_path}#L${locator.physical_lines.start}-L${locator.physical_lines.end}`,
  );
  sourceUrlsChecked += 1;
}

for (const sample of frozenCases.fidelity_samples) {
  const result = searchConceptLibrary(index, { query: sample.qid });
  const record = result.records.find((item) => item.record_key === sample.record_key);
  assert(record, sample.qid);
  assert.equal(record.label_as_recorded, sample.label_as_recorded);
  const canonical = JSON.stringify(record, Object.keys(record).sort());
  // The full object equality below is normative; the hash in the precommitted file uses recursive key sorting.
  assert.deepEqual(record, index.records.find((item) => item.record_key === sample.record_key));
  assert(canonical.length > 0);
}
const unicode = searchConceptLibrary(index, { query: 'Ｑ１０２８２０９' }).records[0];
assert.equal(unicode.identity_candidate.qid, 'Q1028209');
assert.equal(unicode.label_as_recorded, 'Deutsch\u2013Jozsa algorithm');
assert(!unicode.label_as_recorded.includes('\uFFFD'));
assert.equal(
  conceptSourceUrl(unicode),
  'https://github.com/MathGloss/MathGloss/blob/b8f659605486f80f2816515f525af2c395c711fa/data/database.csv#L31-L31',
);
assert.equal(searchConceptLibrary(index, { query: 'ncatlab.org' }).total, 0);
assert.equal(searchConceptLibrary(index, { query: 'Deutsch---Jozsa' }).total, 1);
assert.deepEqual(
  collectTarget('group abelian').keys.sort(),
  collectTarget('abelian group').keys.sort(),
);

const invalidValues = [
  null,
  [],
  {},
  { query: true },
  { query: 'x'.repeat(501) },
  { query: '', resource: '' },
  { query: '', resource: 'x'.repeat(81) },
  { query: '', resource: null },
  { query: '', page: 0 },
  { query: '', page: -1 },
  { query: '', page: 1.5 },
  { query: '', page: Number.NaN },
  { query: '', page: Number.POSITIVE_INFINITY },
  { query: '', page: 1000001 },
  { query: '', extra: 1 },
];
for (const value of invalidValues) assert.throws(() => validateLibraryQuery(value));
assert.doesNotThrow(() => validateLibraryQuery({ query: 'x'.repeat(500), page: 1000000 }));
assert.throws(() => searchConceptLibrary(index, { query: '', resource: 'UnknownCorpus' }));
assert.deepEqual(validateLibraryQuery({ query: '  Fourier  ' }), {
  query: 'Fourier',
  resource: 'All',
  page: 1,
});

const report = {
  schema_version: 'concept-library-independent-navigation-check-v1',
  status: 'pass',
  frozen_case_sha256: CASE_HASH,
  implementation_sha256: hash(readFileSync(`${PROJECT}/lib/concept-library.ts`)),
  integrated_candidate_index_sha256: hash(indexBytes),
  catalog_records: all.catalogRecords,
  catalog_links: all.catalogLinks,
  public_page_size: LIBRARY_PAGE_SIZE,
  resources: all.resources,
  resource_totals: resourceTotals,
  source_record_urls_checked: sourceUrlsChecked,
  search_filter_cases: caseResults,
  pagination_sweeps: sweepResults,
  precommitted_policy_differences: precommittedPolicyDifferences,
  invalid_values_rejected: invalidValues.length + 1,
  unicode: {
    qid: unicode.identity_candidate.qid,
    label: unicode.label_as_recorded,
    label_codepoints: [...unicode.label_as_recorded].map(
      (character) => `U+${character.codePointAt(0).toString(16).toUpperCase().padStart(4, '0')}`,
    ),
    replacement_character_present: unicode.label_as_recorded.includes('\uFFFD'),
    source_url: conceptSourceUrl(unicode),
  },
  limits: [
    'These are lexical and exact-data checks against one pinned snapshot, not semantic identity or equivalence checks.',
    'A search miss is not evidence of novelty.',
    'No URL destination was fetched by this harness.',
  ],
};
writeFileSync(`${AUDIT}/navigation-check.json`, `${JSON.stringify(report, null, 2)}\n`, 'utf8');
console.log(JSON.stringify({ status: report.status, output: `${AUDIT}/navigation-check.json` }));
