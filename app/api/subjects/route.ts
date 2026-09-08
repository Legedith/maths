import { subjectCatalog } from '@/lib/subject-data';

const headers = { 'Cache-Control': 'no-store' };
export function GET(request: Request): Response {
  const params = new URL(request.url).searchParams;
  const allowed = ['code', 'q', 'parent', 'page'];
  if ([...params.keys()].some(key => !allowed.includes(key)) || allowed.some(key => params.getAll(key).length > 1))
    return Response.json({ error: 'Use each supported parameter once.' }, { status: 400, headers });
  try {
    if (params.has('code')) {
      if (params.size !== 1) throw new Error('Use a code alone for subject details.');
      return Response.json(subjectCatalog.detail(params.get('code')), { headers });
    }
    const page = params.get('page') ?? '1';
    if (!/^[1-9][0-9]{0,6}$/.test(page)) throw new Error('Page must be a positive integer.');
    return Response.json(subjectCatalog.search({ query: params.get('q') ?? '', parent: params.get('parent') ?? undefined, page: Number(page) }), { headers });
  } catch (error) {
    return Response.json({ error: error instanceof Error ? error.message : 'Invalid subject request.' }, { status: 400, headers });
  }
}
