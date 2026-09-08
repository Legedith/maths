export type FormalHit = {
  name: string;
  module: string;
  statement: string;
  description: string | null;
  url: string;
};
export type FormalSearchResult = {
  provider: 'Loogle';
  query: string;
  upstreamQuery: string;
  count: number;
  hits: FormalHit[];
  retrievedAt: string;
  scope: string;
};
export function validateFormalQuery(value: unknown): string {
  if (typeof value !== 'string' || !value.trim() || value.trim().length > 120)
    throw new Error(
      'Enter a declaration name or fragment, up to 120 characters.',
    );
  return value.trim();
}
export function normalizeLoogle(
  raw: unknown,
  query: string,
  retrievedAt: string,
): FormalSearchResult {
  if (!raw || typeof raw !== 'object' || Array.isArray(raw))
    throw new Error('Loogle returned an unsupported response.');
  const data = raw as Record<string, unknown>;
  if (
    !Array.isArray(data.hits) ||
    typeof data.count !== 'number' ||
    !Number.isInteger(data.count) ||
    data.count < 0
  )
    throw new Error('Loogle could not return a result for this query.');
  const hits = data.hits.slice(0, 40).map((value: unknown) => {
    if (!value || typeof value !== 'object' || Array.isArray(value))
      throw new Error('Loogle returned an unsupported declaration.');
    const hit = value as Record<string, unknown>;
    if (
      typeof hit.name !== 'string' ||
      typeof hit.module !== 'string' ||
      typeof hit.type !== 'string' ||
      !/^[A-Za-z0-9_.]+$/.test(hit.module) ||
      !hit.module.startsWith('Mathlib.')
    )
      throw new Error('Loogle returned an unsupported declaration.');
    return {
      name: hit.name,
      module: hit.module,
      statement: hit.type,
      description: typeof hit.doc === 'string' ? hit.doc : null,
      url: `https://leanprover-community.github.io/mathlib4_docs/${hit.module.replaceAll('.', '/')}.html#${encodeURIComponent(hit.name)}`,
    };
  });
  return {
    provider: 'Loogle',
    query,
    upstreamQuery: JSON.stringify(query),
    count: data.count,
    hits,
    retrievedAt,
    scope:
      'Live name-substring retrieval from the Loogle Mathlib index. These are external search results, not reviewed Atlas connections or a pinned local Lean proof run.',
  };
}
