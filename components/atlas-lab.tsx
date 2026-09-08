'use client';
/* The labelled inline SVG is the image; an HTML img cannot contain these vectors. */
/* oxlint-disable jsx-a11y/prefer-tag-over-role */
import { Play, Download, CheckCircle2, FlaskConical } from 'lucide-react';
import { Button } from '@/components/ui/button';
import {
  NativeSelect,
  NativeSelectOption,
} from '@/components/ui/native-select';
import { type GraphInput, type GraphResult } from '@/lib/exact-graph';
export const presets: { name: string; input: GraphInput }[] = [
  {
    name: 'Triangle',
    input: {
      n: 3,
      edges: [
        [0, 1],
        [1, 2],
        [0, 2],
      ],
      source: 0,
      target: 1,
    },
  },
  {
    name: 'Square',
    input: {
      n: 4,
      edges: [
        [0, 1],
        [1, 2],
        [2, 3],
        [0, 3],
      ],
      source: 0,
      target: 1,
    },
  },
  {
    name: 'Triangle with a bridge',
    input: {
      n: 4,
      edges: [
        [0, 1],
        [1, 2],
        [0, 2],
        [2, 3],
      ],
      source: 2,
      target: 3,
    },
  },
  {
    name: 'Path: non-edge terminals',
    input: {
      n: 3,
      edges: [
        [0, 1],
        [1, 2],
      ],
      source: 0,
      target: 2,
    },
  },
  {
    name: 'Complete graph on six vertices',
    input: {
      n: 6,
      edges: Array.from({ length: 6 }, (_, u) =>
        Array.from(
          { length: 5 - u },
          (_, j) => [u, u + j + 1] as [number, number],
        ),
      ).flat(),
      source: 0,
      target: 1,
    },
  },
];
function download(value: unknown, filename: string) {
  const url = URL.createObjectURL(
    new Blob([JSON.stringify(value, null, 2)], { type: 'application/json' }),
  );
  const link = document.createElement('a');
  link.href = url;
  link.download = filename;
  link.click();
  setTimeout(() => URL.revokeObjectURL(url), 1000);
}
export function AtlasLab({
  input,
  change,
  result,
  error,
  run,
  select,
}: {
  input: GraphInput;
  change: (input: GraphInput) => void;
  result: GraphResult | null;
  error: string;
  run: () => void;
  select: (id: string) => void;
}) {
  const vertices = Array.from({ length: input.n }, (_, i) => i);
  const possible = vertices.flatMap((u) =>
    vertices.filter((v) => v > u).map((v) => [u, v] as [number, number]),
  );
  const exists = (u: number, v: number) =>
    input.edges.some(([a, b]) => Math.min(a, b) === u && Math.max(a, b) === v);
  const toggle = (u: number, v: number) =>
    change({
      ...input,
      edges: exists(u, v)
        ? input.edges.filter(
            ([a, b]) => !(Math.min(a, b) === u && Math.max(a, b) === v),
          )
        : [...input.edges, [u, v]],
    });
  const positions = vertices.map((i) => ({
    x: 180 + 110 * Math.cos((2 * Math.PI * i) / input.n - Math.PI / 2),
    y: 155 + 100 * Math.sin((2 * Math.PI * i) / input.n - Math.PI / 2),
  }));
  return (
    <section className="content-page lab-page">
      <div className="page-heading">
        <span className="eyebrow">
          <FlaskConical size={15} /> EXACT EXPERIMENT
        </span>
        <h1>One graph. Three ways to understand it.</h1>
        <p>
          Send a unit current through a network, follow a random walker, and
          count spanning trees. Compare the answers.
        </p>
      </div>
      <div className="lab-layout">
        <div className="lab-editor">
          <label className="field-label">
            Start with an example
            <NativeSelect
              value=""
              onChange={(e) => {
                const p = presets[Number(e.target.value)];
                if (p) change(structuredClone(p.input));
              }}
            >
              <NativeSelectOption value="" disabled>
                Choose an example
              </NativeSelectOption>
              {presets.map((p, i) => (
                <NativeSelectOption value={i} key={p.name}>
                  {p.name}
                </NativeSelectOption>
              ))}
            </NativeSelect>
          </label>
          <div className="terminal-fields">
            <label>
              Vertices
              <NativeSelect
                value={input.n}
                onChange={(e) => {
                  const n = Number(e.target.value);
                  change({
                    n,
                    edges: input.edges.filter(([u, v]) => u < n && v < n),
                    source: 0,
                    target: 1,
                  });
                }}
              >
                {[2, 3, 4, 5, 6].map((n) => (
                  <NativeSelectOption key={n} value={n}>
                    {n}
                  </NativeSelectOption>
                ))}
              </NativeSelect>
            </label>
            {(['source', 'target'] as const).map((key) => (
              <label key={key}>
                {key === 'source' ? 'Source' : 'Target'}
                <NativeSelect
                  value={input[key]}
                  onChange={(e) =>
                    change({ ...input, [key]: Number(e.target.value) })
                  }
                >
                  {vertices.map((v) => (
                    <NativeSelectOption value={v} key={v}>
                      {v}
                    </NativeSelectOption>
                  ))}
                </NativeSelect>
              </label>
            ))}
          </div>
          <svg
            className="lab-graph"
            viewBox="0 0 360 310"
            role="img"
            aria-label={`Input graph with ${input.n} vertices and ${input.edges.length} edges`}
          >
            {input.edges.map(([u, v]) => (
              <line
                key={`${u}-${v}`}
                x1={positions[u].x}
                y1={positions[u].y}
                x2={positions[v].x}
                y2={positions[v].y}
                stroke="#a2b5ce"
                strokeWidth="3"
              />
            ))}
            {vertices.map((v) => (
              <g key={v}>
                <circle
                  cx={positions[v].x}
                  cy={positions[v].y}
                  r="19"
                  fill={
                    v === input.source
                      ? '#176bd0'
                      : v === input.target
                        ? '#8057b0'
                        : '#fff'
                  }
                  stroke="#176bd0"
                  strokeWidth="2"
                />
                <text
                  x={positions[v].x}
                  y={positions[v].y + 5}
                  textAnchor="middle"
                  fill={
                    v === input.source || v === input.target
                      ? '#fff'
                      : '#176bd0'
                  }
                  fontSize="15"
                  fontWeight="600"
                >
                  {v}
                </text>
              </g>
            ))}
          </svg>
          <fieldset className="edge-toggles">
            <legend>Add or remove edges</legend>
            {possible.map(([u, v]) => (
              <label key={`${u}-${v}`}>
                <input
                  type="checkbox"
                  checked={exists(u, v)}
                  onChange={() => toggle(u, v)}
                />
                {u}–{v}
              </label>
            ))}
          </fieldset>
          <p className="fine-print">
            Connected, undirected, simple graphs only. Every edge has
            conductance 1. Source and target must differ.
          </p>
          <Button className="run-button" onClick={run}>
            <Play size={16} /> Run exact computation
          </Button>
          {error && (
            <p role="alert" className="error-message">
              {error}
            </p>
          )}
        </div>
        <div className="lab-output" aria-live="polite">
          {!result ? (
            <div className="empty-lab">
              <FlaskConical size={32} />
              <h2>Ready to test your graph</h2>
              <p>
                Run the computation to get exact fractions and independently
                enumerated tree counts.
              </p>
            </div>
          ) : (
            <>
              <div className="result-heading">
                <h2>Computed from your graph</h2>
                <Button
                  variant="outline"
                  size="sm"
                  onClick={() =>
                    download(
                      {
                        input,
                        result,
                        scope:
                          'Exact finite computation; reproduces established identities, not a proof of a new general theorem.',
                      },
                      'atlas-experiment.json',
                    )
                  }
                >
                  <Download size={15} /> Export
                </Button>
              </div>
              <div className="result-metrics">
                <div>
                  <span>Effective resistance</span>
                  <strong>{result.resistance}</strong>
                  <small>Voltage drop per unit current</small>
                </div>
                <div>
                  <span>Expected commute</span>
                  <strong>{result.commute}</strong>
                  <small>
                    {result.hit_forward} steps out + {result.hit_backward} back
                  </small>
                </div>
                <div>
                  <span>Spanning trees</span>
                  <strong>{result.spanning_tree_count}</strong>
                  <small>Counted by exhaustive subsets</small>
                </div>
              </div>
              <div className="identity-card">
                <CheckCircle2 size={20} />
                <div>
                  <h3>Commute time = 2 × edges × resistance</h3>
                  <p>
                    {result.commute} = 2 × {result.edges.length} × (
                    {result.resistance})
                  </p>
                  <button onClick={() => select('commute-resistance')}>
                    Explore the theorem →
                  </button>
                </div>
              </div>
              <div className="identity-card">
                <CheckCircle2 size={20} />
                <div>
                  <h3>
                    {result.edge_probability === null
                      ? 'The terminals are not an edge'
                      : 'Edge inclusion probability = resistance'}
                  </h3>
                  <p>
                    {result.edge_probability === null
                      ? 'There is no existing edge between these terminals to count in a spanning tree. Resistance and commute time still apply.'
                      : `${result.tree_edge_count} of ${result.spanning_tree_count} spanning trees contain the selected edge: probability ${result.edge_probability}.`}
                  </p>
                  <button onClick={() => select('edge-probability')}>
                    Explore the assumptions →
                  </button>
                </div>
              </div>
              <details className="calculation-details">
                <summary>Inspect the exact calculation</summary>
                <p>
                  Target voltage is grounded at zero. Potentials: [
                  {result.potentials.join(', ')}].
                </p>
                <p>Laplacian matrix:</p>
                <pre>
                  {result.laplacian
                    .map((row) =>
                      row.map((n) => String(n).padStart(3)).join(' '),
                    )
                    .join('\n')}
                </pre>
                <p>
                  Resistance uses a rational linear solve. Hitting times use
                  separate first-step equations. Spanning trees use subset
                  connectivity, without using the resistance answer.
                </p>
                <pre>{JSON.stringify(result.checks, null, 2)}</pre>
              </details>
              <p className="fine-print">
                These checks establish this finite computation. They reproduce
                known cross-domain identities; they do not establish a new
                theorem. The Python and browser solvers share the mathematical
                decomposition, including a generic equation-solving pattern.
              </p>
            </>
          )}
        </div>
      </div>
    </section>
  );
}
