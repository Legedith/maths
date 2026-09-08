export type ResearchHit = {
  rank: number;
  similarity: number | null;
  score: number | null;
  theoremId: number;
  sloganId: number | null;
  name: string;
  statement: string;
  generatedSummary: string | null;
  theoremType: string | null;
  paper: {
    id: string | null;
    title: string;
    authors: string[];
    source: string | null;
    year: number | null;
  };
  sourceUrl: string | null;
};
export type ResearchSearchResult = {
  provider: 'TheoremSearch';
  query: string;
  retrievedAt: string;
  request: ReturnType<typeof researchRequest>;
  hits: ResearchHit[];
  scope: string;
};
export class ResearchSearchError extends Error {}
export function researchRequest(query: string) {
  return {
    method: 'POST' as const,
    endpoint: 'https://api.theoremsearch.com/search',
    parameters: { query, n_results: 8 },
  };
}
export function validateResearchQuery(value: unknown): string {
  if (typeof value !== 'string' || !value.trim() || value.trim().length > 500)
    throw new Error('Describe a mathematical idea in 1–500 characters.');
  return value.trim();
}
function sourceUrl(value: unknown): string | null {
  if (typeof value !== 'string') return null;
  try {
    const url = new URL(value);
    if (url.protocol === 'http:' && url.hostname === 'arxiv.org')
      url.protocol = 'https:';
    return url.protocol === 'https:' && !url.username && !url.password
      ? url.href
      : null;
  } catch {
    return null;
  }
}
const optionalText = (value: unknown): string | null =>
  typeof value === 'string' && value.trim() ? value : null;
export function normalizeResearchSearch(
  raw: unknown,
  query: string,
  retrievedAt: string,
): ResearchSearchResult {
  if (
    !raw ||
    typeof raw !== 'object' ||
    Array.isArray(raw) ||
    !('theorems' in raw) ||
    !Array.isArray(raw.theorems)
  )
    throw new ResearchSearchError(
      'The research service returned an unsupported response.',
    );
  const hits = raw.theorems
    .slice(0, 8)
    .map((value: unknown, index: number): ResearchHit => {
      if (!value || typeof value !== 'object' || Array.isArray(value))
        throw new ResearchSearchError(
          'The research service returned an unsupported statement.',
        );
      const hit = value as Record<string, unknown>;
      if (
        !Number.isSafeInteger(hit.theorem_id) ||
        (hit.theorem_id as number) < 0 ||
        typeof hit.body !== 'string'
      )
        throw new ResearchSearchError(
          'The research service returned an unsupported statement.',
        );
      const paper =
        hit.paper && typeof hit.paper === 'object' && !Array.isArray(hit.paper)
          ? (hit.paper as Record<string, unknown>)
          : {};
      return {
        rank: index + 1,
        similarity:
          typeof hit.similarity === 'number' && Number.isFinite(hit.similarity)
            ? hit.similarity
            : null,
        score:
          typeof hit.score === 'number' && Number.isFinite(hit.score)
            ? hit.score
            : null,
        theoremId: hit.theorem_id as number,
        sloganId:
          Number.isSafeInteger(hit.slogan_id) && (hit.slogan_id as number) >= 0
            ? (hit.slogan_id as number)
            : null,
        name: optionalText(hit.name) ?? `Statement ${String(hit.theorem_id)}`,
        statement: hit.body,
        generatedSummary: optionalText(hit.slogan),
        theoremType: optionalText(hit.theorem_type),
        paper: {
          id: optionalText(paper.paper_id),
          title: optionalText(paper.title) ?? 'Source title unavailable',
          authors: Array.isArray(paper.authors)
            ? paper.authors
                .filter((a): a is string => typeof a === 'string')
                .slice(0, 30)
            : [],
          source: optionalText(paper.source),
          year: Number.isSafeInteger(paper.year)
            ? (paper.year as number)
            : null,
        },
        sourceUrl: sourceUrl(hit.link) ?? sourceUrl(paper.link),
      };
    });
  return {
    provider: 'TheoremSearch',
    query,
    retrievedAt,
    request: researchRequest(query),
    hits,
    scope:
      'External semantic retrieval. Generated summaries and extracted statements are distinct; neither has been reviewed or proved applicable by this atlas. A search miss does not establish novelty.',
  };
}
export function researchPacket(result: ResearchSearchResult, hit: ResearchHit) {
  return {
    schema_version: '1.1',
    kind: 'unreviewed_retrieval_packet',
    provider: result.provider,
    query: result.query,
    retrieved_at: result.retrievedAt,
    request: result.request,
    retained_result_count: result.hits.length,
    result: hit,
    review_required: [
      'Read the original source and inherited definitions.',
      'Record each material assumption and convention.',
      'Write an explicit structured claim before running mathematical checks.',
    ],
    scope: result.scope,
  };
}
