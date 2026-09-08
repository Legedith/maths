// Functional source projection and server-rendering checks; no browser or visual QA.
import assert from 'node:assert/strict';
import { createHash } from 'node:crypto';
import { existsSync, mkdirSync, readFileSync, writeFileSync } from 'node:fs';
import { registerHooks } from 'node:module';
import { dirname, resolve } from 'node:path';
import { fileURLToPath, pathToFileURL } from 'node:url';
import ts from 'typescript';
import React from 'react';
import { renderToStaticMarkup } from 'react-dom/server';

const root = resolve(dirname(fileURLToPath(import.meta.url)), '..');
const args = process.argv.slice(2);
assert.ok(args.length === 2 && args[0] === '--output', 'Usage: node scripts/check-boolean-rank.mjs --output PATH');
const output = resolve(args[1]);
assert.ok(!existsSync(output), 'Use a fresh report path');
const hooks = registerHooks({
  resolve(specifier, context, nextResolve) {
    if (specifier.startsWith('@/')) {
      const target = resolve(root, specifier.slice(2));
      const match = [target, `${target}.ts`, `${target}.tsx`].find(existsSync);
      assert.ok(match, `Unresolved application import ${specifier}`);
      return nextResolve(pathToFileURL(match).href, context);
    }
    return nextResolve(specifier, context);
  },
  load(url, context, nextLoad) {
    if (url.startsWith(pathToFileURL(root).href) && /\.tsx?$/.test(url) && !url.includes('/node_modules/')) {
      const source = readFileSync(fileURLToPath(url), 'utf8');
      return {
        format: 'module', shortCircuit: true,
        source: ts.transpileModule(source, { compilerOptions: {
          target: ts.ScriptTarget.ESNext, module: ts.ModuleKind.ESNext,
          jsx: ts.JsxEmit.ReactJSX, verbatimModuleSyntax: true,
        } }).outputText,
      };
    }
    return nextLoad(url, context);
  },
});
const { atlas } = await import('../lib/atlas.ts');
const { Connection, AtlasMap, colors } = await import('../components/atlas-map.tsx');
const { GET } = await import('../app/api/atlas/route.ts');
const projection = JSON.parse(readFileSync(resolve(root, 'evidence/boolean-rank/integration-projection.json'), 'utf8'));
const hash = (file) => createHash('sha256').update(readFileSync(resolve(root, file))).digest('hex');
for (const input of projection.inputs) assert.equal(hash(input.path), input.sha256, input.path);
const checks = [];
const check = (name, fn) => { fn(); checks.push({ name, passed: true }); };
check('schema and exact release collection counts', () => {
  assert.equal(atlas.schema_version, '1.1');
  for (const [key, count] of Object.entries(projection.counts)) assert.equal(atlas[key].length, count, key);
});
check('retained corrected source records projected without omitted edge detail', () => {
  for (const expected of projection.relationships) {
    assert.deepEqual(atlas.edges.find((edge) => edge.id === expected.id), expected, expected.id);
  }
});
check('new concepts, supporting edges and learning journeys match frozen projection', () => {
  for (const [key, values] of Object.entries(projection.additions)) {
    for (const expected of values) assert.deepEqual(atlas[key].find((item) => item.id === expected.id), expected);
  }
});
const response = GET();
assert.equal(response.status, 200);
assert.deepEqual(await response.json(), atlas);
checks.push({ name: 'API preserves every semantic edge field', passed: true });

const escape = (value) => renderToStaticMarkup(React.createElement('span', null, value)).replace(/^<span>|<\/span>$/g, '');
const renders = [];
for (const edge of projection.relationships) {
  const html = renderToStaticMarkup(React.createElement(Connection, { edge, select() {} }));
  check(`${edge.id}: all semantic details appear in actual rendered component`, () => {
    const texts = [edge.source_scope, ...Object.values(edge.witness_translation),
      edge.local_boundary_case.case, ...edge.local_boundary_case.adopted_conventions,
      edge.local_boundary_case.argument, edge.local_boundary_case.result, ...edge.notation_boundaries];
    for (const value of texts) assert.ok(html.includes(escape(value)), `${edge.id}: ${value}`);
    assert.ok(html.includes('Atlas convention for the zero case'));
    assert.ok(!html.includes(edge.curation_record.artifact_sha256), 'Keep hashes out of learner prose');
  });
  renders.push({ edge: edge.id, html });
}
let coordinateCount = 0;
for (const node of atlas.nodes) {
  assert.ok(colors[node.cluster], node.cluster);
  const html = renderToStaticMarkup(React.createElement(AtlasMap, {
    selected: node.id, select() {}, destination: 'laplacian', setDestination() {},
    pathFrom: node.id, setPathFrom() {},
  }));
  assert.ok(!/\b(?:NaN|Infinity)\b/.test(html), `${node.id}: finite rendered coordinates`);
  const viewBox = html.match(/viewBox="0 0 (\d+) (\d+)"/);
  assert.ok(viewBox, node.id);
  const width = Number(viewBox[1]), height = Number(viewBox[2]);
  for (const match of html.matchAll(/<circle\b[^>]*\bcx="([^"]+)"[^>]*\bcy="([^"]+)"/g)) {
    const x = Number(match[1]), y = Number(match[2]);
    assert.ok(x >= 0 && x <= width && y >= 0 && y <= height, `${node.id}: circle bounds`);
    coordinateCount++;
  }
  for (const match of html.matchAll(/<text\b[^>]*\by="([^"]+)"[^>]*>([\s\S]*?)<\/text>/g)) {
    let baseline = Number(match[1]);
    for (const span of match[2].matchAll(/<tspan\b[^>]*\bdy="([^"]+)"/g)) {
      baseline += Number(span[1]);
      assert.ok(baseline >= 0 && baseline <= height, `${node.id}: label baseline bounds`);
    }
  }
}
checks.push({ name: 'all selectable concepts have finite rendered geometry, circle and text baseline bounds and known colors', passed: true });
hooks.deregister();
const report = {
  schema_version: 'boolean-rank-integration-functional-v1', passed: true,
  checks, check_count: checks.length, rendered_connections: renders.length,
  rendered_maps: atlas.nodes.length, checked_circle_centers: coordinateCount,
  scope: 'Pinned projection, actual component server output, API handler and coordinate bounds only. No mathematical proof, browser interaction, visual quality, retrieval performance, discovery or practical impact is certified.',
};
mkdirSync(dirname(output), { recursive: true });
writeFileSync(output, JSON.stringify(report, null, 2) + '\n');
writeFileSync(output.replace(/\.json$/, '') + '-rendered.json', JSON.stringify(renders, null, 2) + '\n');
console.log(JSON.stringify(report, null, 2));
