import {
  normalizeResearchSearch,
  validateResearchQuery,
} from '@/lib/research-search';
export async function GET(request: Request) {
  let query: string;
  try {
    query = validateResearchQuery(new URL(request.url).searchParams.get('q'));
  } catch (error) {
    return Response.json({ error: (error as Error).message }, { status: 400 });
  }
  try {
    const response = await fetch('https://api.theoremsearch.com/search', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        Accept: 'application/json',
      },
      body: JSON.stringify({ query, n_results: 8 }),
      signal: AbortSignal.timeout(15000),
      redirect: 'manual',
    });
    if (!response.ok || !response.body)
      throw new Error('The research service is unavailable. Try again later.');
    const reader = response.body.getReader();
    const parts: Uint8Array[] = [];
    let bytes = 0;
    try {
      while (true) {
        const chunk = await reader.read();
        if (chunk.done) break;
        bytes += chunk.value.byteLength;
        if (bytes > 512000)
          throw new Error(
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
      headers: { 'Cache-Control': 'public, max-age=300' },
    });
  } catch (error) {
    const message =
      error instanceof Error && error.name === 'TimeoutError'
        ? 'TheoremSearch did not respond in time. Try again later.'
        : error instanceof Error
          ? error.message
          : 'Research search failed.';
    return Response.json({ error: message }, { status: 502 });
  }
}
