import raw from '@/data/mathgloss/candidate-index.json';
import { searchConceptLibrary, type ConceptIndex } from '@/lib/concept-library';

const headers = { 'Cache-Control': 'no-store' };

export function GET(request: Request): Response {
  const params = new URL(request.url).searchParams;
  if (
    [...params.keys()].some(
      (key) => !['q', 'resource', 'page'].includes(key),
    ) ||
    ['q', 'resource', 'page'].some((key) => params.getAll(key).length > 1)
  )
    return Response.json(
      { error: 'Use one query, resource and page value.' },
      { status: 400, headers },
    );
  const page = params.get('page') ?? '1';
  if (!/^[1-9][0-9]{0,6}$/.test(page))
    return Response.json(
      { error: 'Page must be a positive integer.' },
      { status: 400, headers },
    );
  try {
    const result = searchConceptLibrary(raw as ConceptIndex, {
      query: params.get('q') ?? '',
      resource: params.get('resource') ?? 'All',
      page: Number(page),
    });
    return Response.json(result, { headers });
  } catch {
    return Response.json(
      {
        error:
          'Use a query of at most 500 characters and an available resource and page.',
      },
      { status: 400, headers },
    );
  }
}
