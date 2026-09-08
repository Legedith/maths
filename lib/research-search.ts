export type ResearchHit = {
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
  hits: ResearchHit[];
  scope: string;
};
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
    throw new Error('The research service returned an unsupported response.');
  const hits = raw.theorems.slice(0, 8).map((value: unknown): ResearchHit => {
    if (!value || typeof value !== 'object' || Array.isArray(value))
      throw new Error(
        'The research service returned an unsupported statement.',
      );
    const hit = value as Record<string, unknown>;
    if (
      !Number.isSafeInteger(hit.theorem_id) ||
      (hit.theorem_id as number) < 0 ||
      typeof hit.body !== 'string'
    )
      throw new Error(
        'The research service returned an unsupported statement.',
      );
    const paper =
      hit.paper && typeof hit.paper === 'object' && !Array.isArray(hit.paper)
        ? (hit.paper as Record<string, unknown>)
        : {};
    return {
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
        year: Number.isSafeInteger(paper.year) ? (paper.year as number) : null,
      },
      sourceUrl: sourceUrl(hit.link) ?? sourceUrl(paper.link),
    };
  });
  return {
    provider: 'TheoremSearch',
    query,
    retrievedAt,
    hits,
    scope:
      'External semantic retrieval. Generated summaries and extracted statements are distinct; neither has been reviewed or proved applicable by this atlas. A search miss does not establish novelty.',
  };
}
export function researchPacket(result: ResearchSearchResult, hit: ResearchHit) {
  return {
    schema_version: '1.0',
    kind: 'unreviewed_retrieval_packet',
    provider: result.provider,
    query: result.query,
    retrieved_at: result.retrievedAt,
    result: hit,
    review_required: [
      'Read the original source and inherited definitions.',
      'Record each material assumption and convention.',
      'Write an explicit structured claim before running mathematical checks.',
    ],
    scope: result.scope,
  };
}
