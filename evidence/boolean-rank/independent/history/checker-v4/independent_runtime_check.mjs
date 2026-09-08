import assert from 'node:assert/strict';
import { createRequire } from 'node:module';
import { existsSync, mkdirSync, readFileSync, writeFileSync } from 'node:fs';
import { registerHooks } from 'node:module';
import { dirname, resolve } from 'node:path';
import { fileURLToPath, pathToFileURL } from 'node:url';


const args = process.argv.slice(2);
const options = {};
for (let i = 0; i < args.length; i += 2) options[args[i]] = args[i + 1];
assert.deepEqual(
  Object.keys(options).sort(),
  ['--http-origin', '--output-dir', '--project-root'],
  'Usage: node independent_runtime_check.mjs --project-root PATH --output-dir PATH --http-origin URL',
);
const project = resolve(options['--project-root']);
const output = resolve(options['--output-dir']);
const httpOrigin = options['--http-origin'];
assert.ok(!existsSync(output), 'Use a fresh --output-dir');
mkdirSync(output, { recursive: true });

const projectRequire = createRequire(pathToFileURL(resolve(project, 'package.json')));
const ts = (await import(pathToFileURL(projectRequire.resolve('typescript')).href)).default;
const reactModuleUrl = pathToFileURL(projectRequire.resolve('react')).href;
const React = (await import(reactModuleUrl)).default;
const { renderToStaticMarkup } = await import(pathToFileURL(projectRequire.resolve('react-dom/server')).href);
const projectUrl = pathToFileURL(project + '/').href;
const hooks = registerHooks({
  resolve(specifier, context, nextResolve) {
    let target = null;
    if (specifier.startsWith('@/')) {
      target = resolve(project, specifier.slice(2));
    } else if (
      specifier.startsWith('.') &&
      context.parentURL?.startsWith(projectUrl)
    ) {
      target = fileURLToPath(new URL(specifier, context.parentURL));
    }
    if (target) {
      const match = [target, `${target}.ts`, `${target}.tsx`, `${target}.js`, `${target}.mjs`].find(existsSync);
      assert.ok(match, `Unresolved application import ${specifier}`);
      return nextResolve(pathToFileURL(match).href, context);
    }
    return nextResolve(specifier, context);
  },
  load(url, context, nextLoad) {
    if (url.startsWith(projectUrl) && /\.tsx?$/.test(url) && !url.includes('/node_modules/')) {
      const source = readFileSync(fileURLToPath(url), 'utf8');
      const transpiled = ts.transpileModule(source, {
        compilerOptions: {
          target: ts.ScriptTarget.ESNext,
          module: ts.ModuleKind.ESNext,
          jsx: ts.JsxEmit.React,
          jsxFactory: '__AuditReact.createElement',
          jsxFragmentFactory: '__AuditReact.Fragment',
          verbatimModuleSyntax: true,
        },
      }).outputText;
      return {
        format: 'module',
        shortCircuit: true,
        source: url.endsWith('.tsx')
          ? `import __AuditReact from ${JSON.stringify(reactModuleUrl)};\n${transpiled}`
          : transpiled,
      };
    }
    return nextLoad(url, context);
  },
});

const { atlas, searchNodes } = await import(pathToFileURL(resolve(project, 'lib/atlas.ts')).href);
const { AtlasMap, Connection, colors } = await import(pathToFileURL(resolve(project, 'components/atlas-map.tsx')).href);
const { GET } = await import(pathToFileURL(resolve(project, 'app/api/atlas/route.ts')).href);
const { atlasTools } = await import(pathToFileURL(resolve(project, 'lib/use-atlas-tools.ts')).href);

const checks = [];
async function check(name, fn) {
  try {
    const detail = await fn();
    checks.push({ name, passed: true, detail: detail ?? null });
  } catch (error) {
    checks.push({ name, passed: false, error: error instanceof Error ? error.stack : String(error) });
  }
}

const edges = Object.fromEntries(atlas.edges.map((edge) => [edge.id, edge]));
const sources = Object.fromEntries(atlas.sources.map((source) => [source.id, source]));
const relationIds = ['boolean-rank-r1', 'boolean-rank-r2', 'boolean-rank-r3', 'boolean-rank-r4'];
const escape = (value) => renderToStaticMarkup(React.createElement('span', null, value)).replace(/^<span>|<\/span>$/g, '');

await check('actual API handler preserves the entire atlas value and cache policy', async () => {
  const response = GET();
  assert.equal(response.status, 200);
  assert.equal(response.headers.get('cache-control'), 'public, max-age=3600');
  assert.deepEqual(await response.json(), atlas);
  return { schema_version: atlas.schema_version, bytes: Buffer.byteLength(JSON.stringify(atlas)) };
});

await check('actual connection tool returns full R1 and R3 edge records', async () => {
  const actionCalls = [];
  const actions = {
    researchSearch() { throw new Error('not called'); },
    formalSearch() { throw new Error('not called'); },
    search(query, domain) { actionCalls.push(['search', query, domain]); },
    show(id) { actionCalls.push(['show', id]); },
    path(from, to) { actionCalls.push(['path', from, to]); },
    run() { throw new Error('not called'); },
  };
  const tools = atlasTools(actions);
  const pathTool = tools.find((tool) => tool.name === 'find_connection');
  assert.ok(pathTool);
  for (const [from, to, expectedId] of [
    ['boolean-rank', 'one-support-rectangle-cover', 'boolean-rank-r1'],
    ['one-support-rectangle-cover', 'nondeterministic-communication-s2', 'boolean-rank-r3'],
  ]) {
    const result = await pathTool.execute({ from, to });
    assert.equal(result.kind, 'navigation_only');
    assert.equal(result.edges.length, 1);
    assert.deepEqual(result.edges[0], edges[expectedId]);
    for (const field of ['source_scope', 'witness_translation', 'local_boundary_case', 'notation_boundaries', 'curation_record']) {
      assert.ok(Object.hasOwn(result.edges[0], field), `${expectedId}: ${field}`);
    }
  }
  assert.throws(() => pathTool.execute({ from: 'missing', to: 'boolean-rank' }), /Unknown concept ID/);
  assert.throws(() => pathTool.execute({ from: 'boolean-rank', to: 'one-support-rectangle-cover', extra: true }), /Unsupported input field/);
  return { registered_tools: tools.map((tool) => tool.name), action_calls: actionCalls };
});

await check('actual lexical search reaches all seven added concepts', () => {
  const cases = [
    ['Boolean relation matrix', 'boolean-relation-matrix'],
    ['Boolean rank', 'boolean-rank'],
    ['rectangle cover', 'one-support-rectangle-cover'],
    ['fixed-side biclique', 'fixed-bipartition-biclique-cover'],
    ['nondeterministic communication depth', 'nondeterministic-communication-s2'],
    ['local Boolean rank', 'local-boolean-rank'],
    ['vertex biclique load', 'local-biclique-cover'],
  ];
  for (const [query, identifier] of cases) {
    assert.ok(searchNodes(query).some((row) => row.node.id === identifier), `${query}: ${identifier}`);
  }
  assert.equal(searchNodes('boolean rank', 'Physics').length, 0);
  return { cases: cases.length };
});

const renderedConnections = [];
await check('actual connection rendering exposes every semantic value and source locator', () => {
  for (const identifier of relationIds) {
    const edge = edges[identifier];
    const html = renderToStaticMarkup(React.createElement(Connection, { edge, select() {} }));
    const visible = [
      edge.source_scope,
      edge.witness_translation.forward,
      edge.witness_translation.reverse,
      edge.witness_translation.result,
      edge.local_boundary_case.case,
      ...edge.local_boundary_case.adopted_conventions,
      edge.local_boundary_case.argument,
      edge.local_boundary_case.result,
      ...edge.notation_boundaries,
      sources[edge.evidence[0].source].author,
      edge.evidence[0].locator,
    ];
    for (const value of visible) assert.ok(html.includes(escape(value)), `${identifier}: missing ${value}`);
    for (const heading of ['What the source establishes', 'How to translate a solution', 'Atlas convention for the zero case', 'Keep these meanings separate']) {
      assert.ok(html.includes(heading), `${identifier}: ${heading}`);
    }
    assert.ok(html.includes(`href="${sources[edge.evidence[0].source].url}"`));
    assert.ok(!html.includes(edge.curation_record.artifact));
    assert.ok(!html.includes(edge.curation_record.artifact_sha256));
    assert.ok(!html.includes(edge.curation_record.independent_review_sha256));
    renderedConnections.push({ id: identifier, html });
  }
  return { rendered_connections: renderedConnections.length };
});

const geometry = [];
await check('all selected-node server renders have finite bounded circles, lines and text baselines', () => {
  for (const node of atlas.nodes) {
    assert.ok(colors[node.cluster], `${node.id}: missing color`);
    const html = renderToStaticMarkup(React.createElement(AtlasMap, {
      selected: node.id,
      select() {},
      destination: 'laplacian',
      setDestination() {},
      pathFrom: node.id,
      setPathFrom() {},
    }));
    assert.ok(!/\b(?:NaN|Infinity)\b/.test(html), `${node.id}: nonfinite output`);
    const viewBox = html.match(/viewBox="0 0 ([\d.]+) ([\d.]+)"/);
    assert.ok(viewBox, `${node.id}: viewBox`);
    const width = Number(viewBox[1]);
    const height = Number(viewBox[2]);
    assert.ok(html.includes(`<rect width="${width}" height="${height}"`), `${node.id}: background bounds`);
    let circleCount = 0;
    let lineCount = 0;
    let baselineCount = 0;
    for (const match of html.matchAll(/<circle\b[^>]*\bcx="([^"]+)"[^>]*\bcy="([^"]+)"/g)) {
      const x = Number(match[1]);
      const y = Number(match[2]);
      assert.ok(Number.isFinite(x) && Number.isFinite(y));
      assert.ok(x >= 0 && x <= width && y >= 0 && y <= height, `${node.id}: circle out of bounds`);
      circleCount++;
    }
    for (const match of html.matchAll(/<line\b[^>]*\bx1="([^"]+)"[^>]*\by1="([^"]+)"[^>]*\bx2="([^"]+)"[^>]*\by2="([^"]+)"/g)) {
      const values = match.slice(1).map(Number);
      assert.ok(values.every(Number.isFinite), `${node.id}: nonfinite line`);
      assert.ok(values[0] >= 0 && values[0] <= width && values[2] >= 0 && values[2] <= width);
      assert.ok(values[1] >= 0 && values[1] <= height && values[3] >= 0 && values[3] <= height);
      lineCount++;
    }
    for (const match of html.matchAll(/<text\b[^>]*\by="([^"]+)"[^>]*>([\s\S]*?)<\/text>/g)) {
      let baseline = Number(match[1]);
      assert.ok(Number.isFinite(baseline));
      for (const span of match[2].matchAll(/<tspan\b[^>]*\bdy="([^"]+)"/g)) {
        baseline += Number(span[1]);
        assert.ok(Number.isFinite(baseline) && baseline >= 0 && baseline <= height, `${node.id}: text baseline`);
        baselineCount++;
      }
    }
    assert.ok(circleCount >= 2 && lineCount >= 1 && baselineCount >= 1, `${node.id}: incomplete geometry parse`);
    geometry.push({ node: node.id, width, height, circleCount, lineCount, baselineCount });
  }
  return {
    rendered_maps: geometry.length,
    circles: geometry.reduce((sum, row) => sum + row.circleCount, 0),
    lines: geometry.reduce((sum, row) => sum + row.lineCount, 0),
    text_baselines: geometry.reduce((sum, row) => sum + row.baselineCount, 0),
  };
});

await check('live HTTP API and home response agree with frozen product', async () => {
  const apiResponse = await fetch(new URL('/api/atlas', httpOrigin), { signal: AbortSignal.timeout(10_000) });
  assert.equal(apiResponse.status, 200);
  assert.equal(apiResponse.headers.get('cache-control'), 'public, max-age=3600');
  const body = await apiResponse.json();
  assert.deepEqual(body, atlas);
  const homeResponse = await fetch(new URL('/', httpOrigin), { signal: AbortSignal.timeout(10_000) });
  assert.equal(homeResponse.status, 200);
  const home = await homeResponse.text();
  assert.ok(home.includes('NETWORKS &amp; BOOLEAN RELATIONS'));
  assert.ok(home.includes('40 concepts'));
  assert.ok(home.includes('11 sources'));
  return { origin: httpOrigin, api_bytes: Buffer.byteLength(JSON.stringify(body)), home_bytes: Buffer.byteLength(home) };
});

hooks.deregister();
writeFileSync(resolve(output, 'rendered-connections.json'), JSON.stringify(renderedConnections, null, 2) + '\n');
writeFileSync(resolve(output, 'geometry.json'), JSON.stringify(geometry, null, 2) + '\n');
const failed = checks.filter((row) => !row.passed);
const report = {
  schema_version: 'boolean-rank-independent-runtime-check-v1',
  auditor: {
    identity: '/root/sol_atlas_audit',
    role: 'independent product auditor and earlier integration-design author',
    implementation_author: false,
  },
  passed: failed.length === 0,
  counts: { checks: checks.length, passed: checks.length - failed.length, failed: failed.length },
  checks,
  scope: 'Actual TypeScript loader, API handler, connection tool, lexical search, server-rendered connection text, SVG coordinate bounds, and existing live HTTP server. No browser DOM, screenshots, visual quality, source-paper proof, retrieval quality, novelty, or impact is certified.',
};
writeFileSync(resolve(output, 'independent-runtime-check.json'), JSON.stringify(report, null, 2) + '\n');
console.log(JSON.stringify({ passed: report.passed, ...report.counts }));
process.exitCode = report.passed ? 0 : 1;
