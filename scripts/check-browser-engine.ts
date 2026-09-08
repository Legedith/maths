import { readFileSync, mkdirSync, writeFileSync } from 'node:fs';
import assert from 'node:assert/strict';
import { analyzeGraph } from '../lib/exact-graph.ts';
const fixtures = JSON.parse(readFileSync('fixtures/frozen.json', 'utf8'));
const records = readFileSync('evidence/baseline/records.jsonl', 'utf8')
  .trim()
  .split('\n')
  .map((line) => JSON.parse(line));
for (const record of records)
  assert.deepEqual(analyzeGraph(record.input), record.result, record.id);
const supplemental = readFileSync('evidence/supplemental/records.jsonl', 'utf8')
  .trim()
  .split('\n')
  .map((line) => JSON.parse(line));
for (const record of supplemental)
  assert.deepEqual(analyzeGraph(record.input), record.result, record.id);
for (const fixture of fixtures.valid) {
  const result = analyzeGraph(fixture.input);
  for (const [key, value] of Object.entries(fixture.expected))
    assert.deepEqual(result[key as keyof typeof result], value, fixture.id);
}
for (const fixture of fixtures.invalid)
  assert.throws(() => analyzeGraph(fixture.input), Error, fixture.id);
const report = {
  passed: true,
  record_count: records.length,
  supplemental_record_count: supplemental.length,
  valid_fixtures: fixtures.valid.length,
  invalid_fixtures: fixtures.invalid.length,
  fields_compared: 'all public outputs',
  arithmetic:
    'BigInt reduced fractions; no floating-point mathematical results',
  runtime: process.version,
  limitations: [
    'JavaScript cannot distinguish an integral JSON number spelled 1.0 from 1. Python rejects native float objects.',
    'Port uses the same mathematical decomposition; cross-language agreement alone is not an independent proof.',
  ],
};
mkdirSync('evidence/browser-engine', { recursive: true });
writeFileSync(
  'evidence/browser-engine/summary.json',
  JSON.stringify(report, null, 2) + '\n',
);
console.log(JSON.stringify(report, null, 2));
