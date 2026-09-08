import { normalizeLoogle, validateFormalQuery } from '@/lib/formal-search';
export async function GET(request: Request) {
  let query: string;
  try {
    query = validateFormalQuery(new URL(request.url).searchParams.get('q'));
  } catch (error) {
    return Response.json({ error: (error as Error).message }, { status: 400 });
  }
  try {
    // The fixed provider URL prevents caller-controlled upstream destinations.
    const url = new URL('https://loogle.lean-lang.org/json');
    url.searchParams.set('q', JSON.stringify(query));
    const response = await fetch(url, {
      signal: AbortSignal.timeout(10000),
      headers: { Accept: 'application/json' },
      redirect: 'manual',
    });
    if (!response.ok || !response.body)
      throw new Error(
        'The external search service is unavailable. Try again later.',
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
          throw new Error(
            'This query returned too much data. Try a longer name fragment.',
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
    const result = normalizeLoogle(
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
        ? 'Loogle did not respond in time. Try again later.'
        : error instanceof Error
          ? error.message
          : 'External search failed.';
    return Response.json({ error: message }, { status: 502 });
  }
}
