import raw from '../data/atlas.json' with { type: 'json' };
export type Evidence = { source: string; locator: string };
export type AtlasNode = {
  id: string;
  label: string;
  kind: string;
  domains: string[];
  cluster: string;
  x: number;
  y: number;
  summary: string;
  explanation: string;
  formula?: string;
  level: string;
  aliases: string[];
  assumptions: string[];
  evidence: Evidence[];
  status: string;
};
export type AtlasEdge = {
  id: string;
  from: string;
  to: string;
  type: string;
  statement: string;
  assumptions: string[];
  status: string;
  evidence: Evidence[];
  source_scope?: string;
  witness_translation?: {
    forward: string;
    reverse: string;
    result: string;
  };
  local_boundary_case?: {
    case: string;
    adopted_conventions: string[];
    argument: string;
    result: string;
    evidence_basis: 'atlas_local_definition_and_proof';
  };
  notation_boundaries?: string[];
  curation_record?: {
    id: 'R1' | 'R2' | 'R3' | 'R4';
    artifact: string;
    artifact_sha256: string;
    independent_review: string;
    independent_review_sha256: string;
  };
};
export type AtlasSource = {
  id: string;
  title: string;
  author: string;
  year: number;
  url: string;
  locator: string;
  note: string;
};
export type Journey = {
  id: string;
  title: string;
  description: string;
  steps: { node: string; prompt: string }[];
};
export type Opportunity = {
  id: string;
  title: string;
  kind: string;
  difficulty: string;
  description: string;
  acceptance: string[];
  nodes: string[];
  status: string;
};
export type AtlasExample = {
  id: string;
  kind: 'example';
  fixture: string;
  artifact: string;
  status: 'finite-computation';
  concepts: string[];
};
if (raw.schema_version !== '1.1') throw new Error('Unsupported Atlas schema.');
export const atlas = raw as {
  schema_version: '1.1';
  title: string;
  scope: string;
  domains: string[];
  sources: AtlasSource[];
  nodes: AtlasNode[];
  edges: AtlasEdge[];
  journeys: Journey[];
  opportunities: Opportunity[];
  examples: AtlasExample[];
};
export const nodeById = Object.fromEntries(atlas.nodes.map((n) => [n.id, n]));
export const sourceById = Object.fromEntries(
  atlas.sources.map((s) => [s.id, s]),
);
export function searchNodes(query: string, domain = 'All') {
  const normalize = (text: string) =>
    text
      .toLowerCase()
      .replace(/[^\p{L}\p{N}]+/gu, ' ')
      .trim();
  const terms = normalize(query).split(/\s+/).filter(Boolean);
  return atlas.nodes
    .filter((n) => domain === 'All' || n.domains.includes(domain))
    .map((n) => {
      const title = normalize([n.id, n.label, ...n.aliases].join(' '));
      const body = normalize(
        [n.summary, n.explanation, ...n.domains].join(' '),
      );
      const score = terms.reduce(
        (sum, t) => sum + (title.includes(t) ? 4 : body.includes(t) ? 1 : 0),
        0,
      );
      return {
        node: n,
        score,
        matches: terms.every((t) => title.includes(t) || body.includes(t)),
      };
    })
    .filter((r) => r.matches)
    .sort((a, b) => b.score - a.score);
}

export function connectionPath(from: string, to: string): AtlasEdge[] | null {
  if (!Object.hasOwn(nodeById, from) || !Object.hasOwn(nodeById, to))
    throw new Error('Choose two concepts in this atlas.');
  if (from === to) return [];
  const queue: { id: string; path: AtlasEdge[] }[] = [{ id: from, path: [] }];
  const seen = new Set([from]);
  for (let i = 0; i < queue.length; i++) {
    for (const edge of atlas.edges) {
      const other =
        edge.from === queue[i].id
          ? edge.to
          : edge.to === queue[i].id
            ? edge.from
            : null;
      if (!other || seen.has(other)) continue;
      const path = [...queue[i].path, edge];
      if (other === to) return path;
      seen.add(other);
      queue.push({ id: other, path });
    }
  }
  return null;
}

export const domains = [
  ...new Set(atlas.nodes.flatMap((n) => n.domains)),
].sort();
