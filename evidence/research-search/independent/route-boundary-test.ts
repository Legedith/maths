import assert from 'node:assert/strict';
import { createHash } from 'node:crypto';
import { readFileSync, writeFileSync } from 'node:fs';

const ROUTE_PATH =
  'D:/CodexWorkspaces/mathematics-atlas/project/app/api/research-search/route.ts';
const ADAPTER_PATH =
  'D:/CodexWorkspaces/mathematics-atlas/project/lib/research-search.ts';
const { GET } = await import(`file:///${ROUTE_PATH}`);

type FetchCall = { input: string; init: RequestInit | undefined };

const checks: Array<Record<string, unknown>> = [];
const originalFetch = globalThis.fetch;

function bytes(value: string): Uint8Array {
  return new TextEncoder().encode(value);
}

async function responseJson(response: Response): Promise<Record<string, unknown>> {
  return (await response.json()) as Record<string, unknown>;
}

function useFetch(implementation: typeof fetch): void {
  globalThis.fetch = implementation;
}

try {
  for (const [name, url] of [
    ['missing', 'http://audit.local/api/research-search'],
    ['whitespace', 'http://audit.local/api/research-search?q=%20%20'],
    ['over-500', `http://audit.local/api/research-search?q=${'x'.repeat(501)}`],
  ]) {
    let called = false;
    useFetch(async () => {
      called = true;
      throw new Error('must not fetch');
    });
    const response = await GET(new Request(url));
    assert.equal(response.status, 400);
    assert.equal(called, false);
    const body = await responseJson(response);
    assert.match(String(body.error), /1.500 characters/);
    checks.push({ name: `query-${name}`, status: response.status, passed: true });
  }

  let captured: FetchCall | null = null;
  useFetch(async (input, init) => {
    captured = { input: String(input), init };
    return new Response(
      JSON.stringify({
        theorems: [
          {
            theorem_id: 7,
            slogan_id: 8,
            body: 'EXTRACTED BODY',
            slogan: 'GENERATED SUMMARY',
            link: 'javascript:alert(1)',
            paper: {
              paper_id: '1234.5678v1',
              title: 'Paper',
              link: 'http://arxiv.org/abs/1234.5678v1',
            },
            score: 0.91,
            similarity: 0.91,
          },
        ],
      }),
      { status: 200, headers: { 'Content-Type': 'application/json' } },
    );
  });
  const valid = await GET(
    new Request('http://audit.local/api/research-search?q=%20test%20query%20'),
  );
  assert.equal(valid.status, 200);
  assert.equal(valid.headers.get('cache-control'), 'public, max-age=300');
  const validBody = await responseJson(valid);
  const hit = (validBody.hits as Array<Record<string, unknown>>)[0];
  assert.equal(validBody.query, 'test query');
  assert.equal(hit.statement, 'EXTRACTED BODY');
  assert.equal(hit.generatedSummary, 'GENERATED SUMMARY');
  assert.equal(hit.sourceUrl, 'https://arxiv.org/abs/1234.5678v1');
  assert.equal('score' in hit, false);
  assert.equal('similarity' in hit, false);
  assert.equal(captured?.input, 'https://api.theoremsearch.com/search');
  assert.equal(captured?.init?.method, 'POST');
  assert.equal(captured?.init?.redirect, 'manual');
  assert.deepEqual(JSON.parse(String(captured?.init?.body)), {
    query: 'test query',
    n_results: 8,
  });
  assert.ok(captured?.init?.signal instanceof AbortSignal);
  checks.push({
    name: 'valid-request-and-field-separation',
    status: valid.status,
    cacheControl: valid.headers.get('cache-control'),
    normalizedFields: Object.keys(hit).sort(),
    passed: true,
  });

  for (const [name, upstream] of [
    ['upstream-503', new Response('unavailable', { status: 503 })],
    ['upstream-redirect', new Response(null, { status: 302 })],
    ['missing-body', new Response(null, { status: 200 })],
  ] as const) {
    useFetch(async () => upstream);
    const response = await GET(
      new Request('http://audit.local/api/research-search?q=test'),
    );
    assert.equal(response.status, 502);
    assert.deepEqual(await responseJson(response), {
      error: 'The research service is unavailable. Try again later.',
    });
    checks.push({ name, status: response.status, passed: true });
  }

  useFetch(async () => new Response('{not-json', { status: 200 }));
  const invalidJson = await GET(
    new Request('http://audit.local/api/research-search?q=test'),
  );
  assert.equal(invalidJson.status, 502);
  const invalidJsonBody = await responseJson(invalidJson);
  assert.match(String(invalidJsonBody.error), /JSON|position|token/i);
  checks.push({
    name: 'invalid-json',
    status: invalidJson.status,
    returnedError: invalidJsonBody.error,
    passed: true,
  });

  useFetch(async () => new Response('{}', { status: 200 }));
  const malformed = await GET(
    new Request('http://audit.local/api/research-search?q=test'),
  );
  assert.equal(malformed.status, 502);
  assert.deepEqual(await responseJson(malformed), {
    error: 'The research service returned an unsupported response.',
  });
  checks.push({ name: 'malformed-provider-shape', status: malformed.status, passed: true });

  const minimal = JSON.stringify({ theorems: [] });
  assert.ok(bytes(minimal).byteLength < 512000);
  const exactLimit = minimal + ' '.repeat(512000 - bytes(minimal).byteLength);
  assert.equal(bytes(exactLimit).byteLength, 512000);
  useFetch(async () => new Response(bytes(exactLimit), { status: 200 }));
  const atLimit = await GET(
    new Request('http://audit.local/api/research-search?q=test'),
  );
  assert.equal(atLimit.status, 200);
  assert.equal((await responseJson(atLimit)).hits instanceof Array, true);
  checks.push({ name: 'body-exactly-512000-bytes', status: atLimit.status, passed: true });

  const aboveLimit = exactLimit + ' ';
  assert.equal(bytes(aboveLimit).byteLength, 512001);
  useFetch(async () => new Response(bytes(aboveLimit), { status: 200 }));
  const overLimit = await GET(
    new Request('http://audit.local/api/research-search?q=test'),
  );
  assert.equal(overLimit.status, 502);
  assert.deepEqual(await responseJson(overLimit), {
    error: 'This query returned too much data. Try a more specific description.',
  });
  checks.push({ name: 'body-512001-bytes', status: overLimit.status, passed: true });

  useFetch(async () => {
    throw new DOMException('The operation was aborted due to timeout', 'TimeoutError');
  });
  const timeout = await GET(
    new Request('http://audit.local/api/research-search?q=test'),
  );
  assert.equal(timeout.status, 502);
  assert.deepEqual(await responseJson(timeout), {
    error: 'TheoremSearch did not respond in time. Try again later.',
  });
  checks.push({ name: 'timeout', status: timeout.status, passed: true });

  useFetch(async () => {
    throw new TypeError('fetch failed: audit-internal-detail');
  });
  const networkFailure = await GET(
    new Request('http://audit.local/api/research-search?q=test'),
  );
  assert.equal(networkFailure.status, 502);
  const networkBody = await responseJson(networkFailure);
  assert.equal(networkBody.error, 'fetch failed: audit-internal-detail');
  checks.push({
    name: 'network-error-message-forwarding',
    status: networkFailure.status,
    returnedError: networkBody.error,
    passed: true,
  });
} finally {
  globalThis.fetch = originalFetch;
}

const sha256 = (path: string): string =>
  createHash('sha256').update(readFileSync(path)).digest('hex');
const report = {
  passed: true,
  subject: {
    route: { path: ROUTE_PATH, sha256: sha256(ROUTE_PATH) },
    adapter: { path: ADAPTER_PATH, sha256: sha256(ADAPTER_PATH) },
  },
  runtime: process.version,
  checks,
  scope:
    'Actual route module with mocked upstream transport; verifies HTTP, byte, timeout, request, field-separation, and error-message boundaries without contacting the provider.',
};
writeFileSync('route-boundary-report.json', JSON.stringify(report, null, 2) + '\n');
console.log(JSON.stringify(report, null, 2));
