import {
  normalizeResearchSearch,
  researchRequest,
  ResearchSearchError,
  validateResearchQuery,
} from '@/lib/research-search';
export async function GET(request: Request) {
  let query: string;
  try {
    query = validateResearchQuery(new URL(request.url).searchParams.get('q'));
  } catch {
    return Response.json(
      { error: 'Describe a mathematical idea in 1–500 characters.' },
      { status: 400, headers: { 'Cache-Control': 'no-store' } },
    );
  }
  try {
    const specification = researchRequest(query);
    const response = await fetch(specification.endpoint, {
      method: specification.method,
      headers: {
        'Content-Type': 'application/json',
        Accept: 'application/json',
      },
      body: JSON.stringify(specification.parameters),
      signal: AbortSignal.timeout(15000),
      redirect: 'manual',
    });
    if (!response.ok || !response.body)
      throw new ResearchSearchError(
        'The research service is unavailable. Try again later.',
      );
    const reader = response.body.getReader();
    const parts: Uint8Array[] = [];
    let bytes = 0;
    try {
      while (true) {
        const chunk = await reader.read();
        if (chunk.done) break;
        bytes += chunk.value.byteLength;
        if (bytes > 512000)
          throw new ResearchSearchError(
            'This query returned too much data. Try a more specific description.',
          );
        parts.push(chunk.value);
      }
    } finally {
      await reader.cancel();
    }
    const body = new Uint8Array(bytes);
    let at = 0;
    for (const part of parts) {
      body.set(part, at);
      at += part.byteLength;
    }
    const result = normalizeResearchSearch(
      JSON.parse(new TextDecoder().decode(body)),
      query,
      new Date().toISOString(),
    );
    return Response.json(result, {
      headers: { 'Cache-Control': 'no-store' },
    });
  } catch (error) {
    const message =
      error instanceof Error && error.name === 'TimeoutError'
        ? 'TheoremSearch did not respond in time. Try again later.'
        : error instanceof ResearchSearchError
          ? error.message
          : 'The research service response could not be read. Try again later.';
    return Response.json(
      { error: message },
      { status: 502, headers: { 'Cache-Control': 'no-store' } },
    );
  }
}
