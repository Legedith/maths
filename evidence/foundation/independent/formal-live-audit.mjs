import assert from 'node:assert/strict';
import { createHash } from 'node:crypto';
import { writeFile } from 'node:fs/promises';
import { normalizeLoogle, validateFormalQuery } from 'file:///D:/CodexWorkspaces/mathematics-atlas/project/lib/formal-search.ts';
const query = validateFormalQuery('lapMatrix');
const url = new URL('https://loogle.lean-lang.org/json');
url.searchParams.set('q', JSON.stringify(query));
const response = await fetch(url, { headers: { Accept: 'application/json' }, redirect: 'manual', signal: AbortSignal.timeout(10000) });
assert.equal(response.status, 200);
assert.equal(response.redirected, false);
const body = new Uint8Array(await response.arrayBuffer());
assert.ok(body.byteLength <= 512000);
const rawText = new TextDecoder().decode(body);
await writeFile('formal-live-response.json', rawText);
await writeFile('formal-live-headers.txt', [...response.headers].map(([k,v]) => `${k}: ${v}`).join('\n') + '\n');
const normalized = normalizeLoogle(JSON.parse(rawText), query, new Date().toISOString());
const hit = normalized.hits.find((h) => h.name === 'SimpleGraph.lapMatrix');
assert.ok(hit);
assert.ok(normalized.count >= normalized.hits.length);
assert.equal(normalized.upstreamQuery, '"lapMatrix"');
const docs = await fetch(hit.url, { redirect: 'follow', signal: AbortSignal.timeout(10000) });
assert.equal(docs.status, 200);
const docsText = await docs.text();
assert.ok(docsText.includes('SimpleGraph.lapMatrix'));
for (const bad of [null, [], 3, '', ' '.repeat(5), 'x'.repeat(121)]) assert.throws(() => validateFormalQuery(bad));
for (const bad of [null, {count:-1,hits:[]}, {count:1,hits:[null]}, {count:1,hits:[{name:'x',module:'../../evil',type:'x'}]}]) assert.throws(() => normalizeLoogle(bad,'x','date'));
const report = {
  passed: true,
  endpoint: url.toString(),
  http_status: response.status,
  response_bytes: body.byteLength,
  response_sha256: createHash('sha256').update(body).digest('hex'),
  upstream_count: normalized.count,
  retained_hits: normalized.hits.length,
  required_hit: hit.name,
  required_hit_module: hit.module,
  documentation_url: hit.url,
  documentation_status: docs.status,
  scope: 'Direct live API and adapter normalization; no browser UI or WebMCP runtime claim.'
};
await writeFile('formal-live-audit.json', JSON.stringify(report,null,2)+'\n');
console.log(JSON.stringify(report,null,2));
