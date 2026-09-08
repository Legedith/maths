import type { ConceptIndex, ConceptRecord } from './concept-library';

export type RelationEndpoint = { id: string; label: string };
export type ExternalEdge = {
  id: string;
  source: RelationEndpoint;
  property: RelationEndpoint;
  target: RelationEndpoint;
  record: number;
  line_start: number;
  line_end: number;
  review_status: 'unreviewed_external_assertion';
  legacy_statement_metadata: 'not_retrieved';
};
export type WikidataSnak = {
  snaktype: string;
  property: string;
  datavalue?: { type: string; value: unknown };
};
export type WikidataStatement = {
  id: string;
  rank: string;
  qualifiers?: Record<string, WikidataSnak[]>;
  references?: unknown[];
  [key: string]: unknown;
};
export type RelationObservation = {
  requested_url: string;
  retrieved_at_utc: string;
  raw_response_sha256: string;
  source_entity: { id: string; lastrevid: number; modified: string };
  matching_statements: WikidataStatement[];
  field_presence: { statement_id: boolean; qualifiers: boolean; references: boolean }[];
  display_labels: Record<string, string>;
};
export type RelationIndex = {
  schema_version: string;
  source: Record<string, unknown>;
  summary: { total_rows: number; included_rows: number; excluded_rows: number; endpoint_count: number; property_count: number };
  properties: { id: string; label: string; count: number }[];
  edges: ExternalEdge[];
  observations: Record<string, RelationObservation>;
};
export type RelationQuery = {
  qid: string;
  property: string;
  direction: 'both' | 'incoming' | 'outgoing';
  page: number;
};
export type RelationResult = RelationQuery & {
  concept: ConceptRecord;
  edges: ExternalEdge[];
  observations: Record<string, RelationObservation>;
  total: number;
  pages: number;
  pageSize: number;
  properties: { id: string; label: string; count: number }[];
  availableProperties: RelationIndex['properties'];
  coverage: RelationIndex['summary'];
};
export const RELATION_PAGE_SIZE = 20;
export const MATHGLOSS_RELATION_SOURCE = 'https://github.com/MathGloss/MathGloss/blob/b8f659605486f80f2816515f525af2c395c711fa/data/relations/graph_edges.csv';

export function validateRelationQuery(value: unknown): RelationQuery {
  if (!value || typeof value !== 'object' || Array.isArray(value))
    throw new Error('Use a concept and relation filters.');
  const input = value as Record<string, unknown>;
  if (Object.keys(input).some((key) => !['qid', 'property', 'direction', 'page'].includes(key)))
    throw new Error('Unsupported relation field.');
  if (typeof input.qid !== 'string' || !/^Q[1-9][0-9]{0,14}$/.test(input.qid))
    throw new Error('Choose a concept by its Wikidata QID.');
  const property = input.property === undefined ? 'All' : input.property;
  if (typeof property !== 'string' || (property !== 'All' && !/^P[1-9][0-9]{0,14}$/.test(property)))
    throw new Error('Choose an available relation type.');
  const direction = input.direction === undefined ? 'both' : input.direction;
  if (direction !== 'both' && direction !== 'incoming' && direction !== 'outgoing')
    throw new Error('Choose incoming, outgoing or both directions.');
  const page = input.page === undefined ? 1 : input.page;
  if (typeof page !== 'number' || !Number.isSafeInteger(page) || page < 1 || page > 1000000)
    throw new Error('Choose a page from 1 to 1000000.');
  return { qid: input.qid, property, direction, page };
}

export function createRelationExplorer(index: RelationIndex, catalog: ConceptIndex) {
  const concepts = new Map(catalog.records.map((record) => [record.identity_candidate.qid, record]));
  const adjacency = new Map<string, ExternalEdge[]>();
  for (const edge of index.edges) {
    for (const id of new Set([edge.source.id, edge.target.id])) {
      const rows = adjacency.get(id) ?? [];
      rows.push(edge);
      adjacency.set(id, rows);
    }
  }
  const knownProperties = new Set(index.properties.map((property) => property.id));
  return (input: unknown): RelationResult => {
    const query = validateRelationQuery(input);
    const concept = concepts.get(query.qid);
    if (!concept) throw new Error('Choose a concept in the library.');
    if (query.property !== 'All' && !knownProperties.has(query.property))
      throw new Error('Choose an available relation type.');
    const incident = adjacency.get(query.qid) ?? [];
    const counts = new Map<string, number>();
    for (const edge of incident) counts.set(edge.property.id, (counts.get(edge.property.id) ?? 0) + 1);
    const matches = incident.filter((edge) =>
      (query.property === 'All' || query.property === edge.property.id) &&
      (query.direction === 'both' || (query.direction === 'incoming' ? edge.target.id === query.qid : edge.source.id === query.qid)));
    const edges = matches.slice((query.page - 1) * RELATION_PAGE_SIZE, query.page * RELATION_PAGE_SIZE);
    return {
      ...query, concept, edges,
      observations: Object.fromEntries(edges.filter((edge) => index.observations[edge.id]).map((edge) => [edge.id, index.observations[edge.id]])),
      total: matches.length, pages: Math.ceil(matches.length / RELATION_PAGE_SIZE), pageSize: RELATION_PAGE_SIZE,
      properties: index.properties.filter((property) => counts.has(property.id)).map((property) => ({ ...property, count: counts.get(property.id)! })),
      availableProperties: index.properties, coverage: index.summary,
    };
  };
}

export function relationApiResponse(request: Request, search: (input: unknown) => RelationResult): Response {
  const headers = { 'Cache-Control': 'no-store' };
  const params = new URL(request.url).searchParams;
  const keys = ['qid', 'property', 'direction', 'page'];
  const invalid = () => Response.json({ error: 'Use one library QID and valid relation filters.' }, { status: 400, headers });
  if ([...params.keys()].some((key) => !keys.includes(key)) || keys.some((key) => params.getAll(key).length > 1)) return invalid();
  const page = params.get('page') ?? '1';
  if (!/^[1-9][0-9]{0,6}$/.test(page)) return invalid();
  try {
    return Response.json(search({ qid: params.get('qid'), property: params.get('property') ?? 'All', direction: params.get('direction') ?? 'both', page: Number(page) }), { headers });
  } catch {
    return invalid();
  }
}
