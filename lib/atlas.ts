import raw from '@/data/atlas.json';
export type Evidence = { source: string; locator: string };
export type AtlasNode = { id: string; label: string; kind: string; domains: string[]; cluster: string; x: number; y: number; summary: string; explanation: string; formula?: string; level: string; aliases: string[]; assumptions: string[]; evidence: Evidence[]; status: string };
export type AtlasEdge = { id: string; from: string; to: string; type: string; statement: string; assumptions: string[]; status: string; evidence: Evidence[] };
export type AtlasSource = { id: string; title: string; author: string; year: number; url: string; locator: string; note: string };
export type Journey = { id: string; title: string; description: string; steps: { node: string; prompt: string }[] };
export type Opportunity = { id: string; title: string; kind: string; difficulty: string; description: string; acceptance: string[]; nodes: string[]; status: string };
export const atlas = raw as { schema_version: string; title: string; scope: string; domains: string[]; sources: AtlasSource[]; nodes: AtlasNode[]; edges: AtlasEdge[]; journeys: Journey[]; opportunities: Opportunity[] };
export const nodeById = Object.fromEntries(atlas.nodes.map(n => [n.id, n]));
export const sourceById = Object.fromEntries(atlas.sources.map(s => [s.id, s]));
export function searchNodes(query: string, domain = 'All') {
  const terms = query.toLowerCase().trim().split(/\s+/).filter(Boolean);
  return atlas.nodes.filter(n => domain === 'All' || n.domains.includes(domain)).map(n => {
    const title = [n.label, ...n.aliases].join(' ').toLowerCase();
    const body = [n.summary, n.explanation, ...n.domains].join(' ').toLowerCase();
    const score = terms.reduce((sum, t) => sum + (title.includes(t) ? 4 : body.includes(t) ? 1 : 0), 0);
    return { node: n, score };
  }).filter(r => !terms.length || r.score > 0).sort((a, b) => b.score - a.score);
}
