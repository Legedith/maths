'use client';
/* SVG nodes need explicit roles; HTML buttons cannot directly replace SVG groups. */
/* oxlint-disable jsx-a11y/prefer-tag-over-role */
import { ArrowUpRight, BookOpen } from 'lucide-react';
import {
  NativeSelect,
  NativeSelectOption,
} from '@/components/ui/native-select';
import {
  atlas,
  nodeById,
  sourceById,
  connectionPath,
  type AtlasEdge,
} from '@/lib/atlas';
export const colors: Record<string, string> = {
  foundations: '#72b7ff',
  physics: '#ffb573',
  probability: '#bd9bff',
  algorithms: '#5bdbc4',
  applications: '#f09abf',
};
export function Connection({
  edge,
  select,
}: {
  edge: AtlasEdge;
  select: (id: string) => void;
}) {
  return (
    <article className="connection">
      <div className="edge-direction">
        <button onClick={() => select(edge.from)}>
          {nodeById[edge.from].label}
        </button>
        <span aria-label="to"> → </span>
        <button onClick={() => select(edge.to)}>
          {nodeById[edge.to].label}
        </button>
      </div>
      <span className="relation-type">{edge.type.replaceAll('_', ' ')}</span>
      <p>{edge.statement}</p>
      <details>
        <summary>Assumptions & evidence</summary>
        <ul>
          {edge.assumptions.map((a) => (
            <li key={a}>{a}</li>
          ))}
        </ul>
        {edge.source_scope && (
          <section aria-label="Source scope">
            <h4>What the source establishes</h4>
            <p>{edge.source_scope}</p>
          </section>
        )}
        {edge.witness_translation && (
          <section aria-label="Translation in both directions">
            <h4>How to translate a solution</h4>
            <p><strong>Forward. </strong>{edge.witness_translation.forward}</p>
            <p><strong>Reverse. </strong>{edge.witness_translation.reverse}</p>
            <p>{edge.witness_translation.result}</p>
          </section>
        )}
        {edge.local_boundary_case && (
          <section aria-label="Atlas convention for the zero case">
            <h4>Atlas convention for the zero case</h4>
            <p>{edge.local_boundary_case.case}</p>
            <ul>
              {edge.local_boundary_case.adopted_conventions.map((convention) => (
                <li key={convention}>{convention}</li>
              ))}
            </ul>
            <p>{edge.local_boundary_case.argument}</p>
            <p>{edge.local_boundary_case.result}</p>
            <p className="fine-print">
              This boundary case uses the Atlas definitions and argument above.
            </p>
          </section>
        )}
        {edge.notation_boundaries && (
          <section aria-label="Notation and scope distinctions">
            <h4>Keep these meanings separate</h4>
            <ul>
              {edge.notation_boundaries.map((boundary) => (
                <li key={boundary}>{boundary}</li>
              ))}
            </ul>
          </section>
        )}
        {edge.evidence.map((v, i) => (
          <a
            key={i}
            href={sourceById[v.source].url}
            target="_blank"
            rel="noreferrer"
          >
            {sourceById[v.source].author} · {v.locator} ↗
          </a>
        ))}
      </details>
    </article>
  );
}
export function ConceptDetail({
  selected,
  select,
}: {
  selected: string;
  select: (id: string) => void;
}) {
  const node = nodeById[selected],
    connections = atlas.edges.filter(
      (e) => e.from === selected || e.to === selected,
    );
  return (
    <aside className="detail-panel" aria-label="Selected concept">
      <div className="detail-top">
        <span className="eyebrow">
          {node.kind} · {node.level}
        </span>
        <span className="sourced">Source backed</span>
      </div>
      <h2>{node.label}</h2>
      <p className="node-summary">{node.summary}</p>
      {node.formula && <div className="formula">{node.formula}</div>}
      <p className="explanation">{node.explanation}</p>
      <details className="node-assumptions">
        <summary>When this applies</summary>
        <ul>
          {node.assumptions.map((a) => (
            <li key={a}>{a}</li>
          ))}
        </ul>
      </details>
      <h3>
        Connections to follow <span>{connections.length}</span>
      </h3>
      {connections.map((edge) => (
        <Connection key={edge.id} edge={edge} select={select} />
      ))}
      <h3>Read the source</h3>
      {node.evidence.map((v, i) => (
        <a
          className="source-link"
          key={i}
          href={sourceById[v.source].url}
          target="_blank"
          rel="noreferrer"
        >
          <BookOpen size={17} />
          <span>
            {sourceById[v.source].title}
            <small>
              {sourceById[v.source].author} · {v.locator}
            </small>
          </span>
          <ArrowUpRight size={15} />
        </a>
      ))}
      <p className="fine-print">
        Source backed means a cited reference supports this entry. It does not
        mean the entry has been formally verified in Lean.
      </p>
    </aside>
  );
}
function wrapLabel(label: string) {
  if (label.length <= 24) return [label];
  const words = label.split(' '),
    lines = [''];
  for (const word of words) {
    if (lines.at(-1)!.length + word.length > 24) lines.push(word);
    else lines[lines.length - 1] += `${lines.at(-1) ? ' ' : ''}${word}`;
  }
  return lines;
}
export function AtlasMap({
  selected,
  select,
  destination,
  setDestination,
  pathFrom,
  setPathFrom,
}: {
  selected: string;
  select: (id: string) => void;
  destination: string;
  setDestination: (id: string) => void;
  pathFrom: string;
  setPathFrom: (id: string) => void;
}) {
  const edges = atlas.edges.filter(
    (e) => e.from === selected || e.to === selected,
  );
  const neighbors = [...new Set(edges.flatMap((e) => [e.from, e.to]))].filter(
    (id) => id !== selected,
  );
  const positions: Record<string, { x: number; y: number }> = {
    [selected]: { x: 420, y: 335 },
  };
  neighbors.forEach((id, i) => {
    const angle = (2 * Math.PI * i) / neighbors.length - Math.PI / 2;
    positions[id] = {
      x: 420 + 280 * Math.cos(angle),
      y: 315 + 235 * Math.sin(angle),
    };
  });
  const path = connectionPath(pathFrom, destination);
  return (
    <div className="map-and-detail">
      <section className="map-panel" aria-label="Interactive concept map">
        <div className="map-topline">
          <span>
            <span className="live-dot" /> {nodeById[selected].label}
          </span>
          <span>
            {neighbors.length} direct neighbors · {atlas.nodes.length} concepts
            in the curated map
          </span>
        </div>
        <svg
          className="knowledge-graph"
          viewBox="0 0 840 660"
          role="group"
          aria-label={`Direct connections of ${nodeById[selected].label}`}
        >
          <defs>
            <pattern
              id="dots"
              width="24"
              height="24"
              patternUnits="userSpaceOnUse"
            >
              <circle cx="1" cy="1" r="1" fill="#27364a" />
            </pattern>
            <marker
              id="arrow"
              viewBox="0 0 10 10"
              refX="8"
              refY="5"
              markerWidth="7"
              markerHeight="7"
              orient="auto-start-reverse"
            >
              <path d="M 0 0 L 10 5 L 0 10 z" fill="#668aad" />
            </marker>
          </defs>
          <rect width="840" height="660" fill="url(#dots)" />
          {edges.map((e) => {
            const a = positions[e.from],
              b = positions[e.to];
            const len = Math.hypot(b.x - a.x, b.y - a.y),
              dx = (b.x - a.x) / len,
              dy = (b.y - a.y) / len;
            return (
              <line
                key={e.id}
                x1={a.x + dx * 34}
                y1={a.y + dy * 34}
                x2={b.x - dx * 36}
                y2={b.y - dy * 36}
                stroke="#466784"
                strokeWidth="1.5"
                markerEnd="url(#arrow)"
              />
            );
          })}
          {[selected, ...neighbors].map((id) => {
            const n = nodeById[id],
              p = positions[id],
              active = id === selected;
            return (
              <g
                key={id}
                className="map-node"
                role="button"
                tabIndex={0}
                aria-label={`Explore ${n.label}`}
                aria-pressed={active}
                onClick={() => select(id)}
                onKeyDown={(e) => {
                  if (e.key === 'Enter' || e.key === ' ') {
                    e.preventDefault();
                    select(id);
                  }
                }}
              >
                <title>{n.summary}</title>
                <circle
                  cx={p.x}
                  cy={p.y}
                  r={active ? 31 : 23}
                  fill={active ? colors[n.cluster] : '#111f32'}
                  stroke={colors[n.cluster]}
                  strokeWidth={active ? 3 : 2}
                />
                <circle
                  cx={p.x}
                  cy={p.y}
                  r="5"
                  fill={active ? '#102039' : colors[n.cluster]}
                />
                <text
                  x={p.x}
                  y={p.y + 48}
                  textAnchor="middle"
                  fill="#ebf1fa"
                  fontSize="16"
                  fontWeight={active ? 650 : 450}
                >
                  {wrapLabel(n.label).map((line, i) => (
                    <tspan key={i} x={p.x} dy={i ? 20 : 0}>
                      {line}
                    </tspan>
                  ))}
                </text>
              </g>
            );
          })}
        </svg>
        <div className="map-legend">
          {Object.entries(colors).map(([name, color]) => (
            <span key={name}>
              <i style={{ background: color }} />
              {name}
            </span>
          ))}
        </div>
        <div className="map-caption">
          Arrows follow each named relation. Position and distance are for
          navigation.
        </div>
        <div className="path-finder">
          <h3>Connect two ideas</h3>
          <div className="path-controls">
            <label>
              From
              <NativeSelect
                value={pathFrom}
                onChange={(e) => setPathFrom(e.target.value)}
              >
                {atlas.nodes.map((n) => (
                  <NativeSelectOption key={n.id} value={n.id}>
                    {n.label}
                  </NativeSelectOption>
                ))}
              </NativeSelect>
            </label>
            <span>→</span>
            <label>
              To
              <NativeSelect
                value={destination}
                onChange={(e) => setDestination(e.target.value)}
              >
                {atlas.nodes.map((n) => (
                  <NativeSelectOption key={n.id} value={n.id}>
                    {n.label}
                  </NativeSelectOption>
                ))}
              </NativeSelect>
            </label>
          </div>
          <p className="fine-print">
            Shortest navigation path, allowing travel both ways. This does not
            combine the relations into a proof.
          </p>
          {path === null ? (
            <p>No path is recorded in this region.</p>
          ) : path.length === 0 ? (
            <p>
              Both ends are the same concept. Choose a different destination.
            </p>
          ) : (
            <div className="path-results">
              {path.map((edge) => (
                <Connection key={edge.id} edge={edge} select={select} />
              ))}
            </div>
          )}
        </div>
      </section>
      <ConceptDetail selected={selected} select={select} />
    </div>
  );
}
