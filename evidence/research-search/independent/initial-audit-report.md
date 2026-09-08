# Independent research-search UI/API audit — initial findings

Subject: local commit `97b5aaf`, limited to the research-search adapter, route, UI, action wiring, focused checks, documentation and retained observations. Status: **changes required**.

## Findings

1. **P2 — saved packets omit retrieval rank and documented ranking signals.** The adapter preserves the query, retrieval time, IDs, source metadata, extracted body and generated slogan, but drops the provider's documented `similarity` and `score` plus the hit's position. A packet for one hit cannot reconstruct whether it was first or eighth. The existing packet assertion compares against the already lossy normalized hit. Carry rank, finite score/similarity values, and the exact endpoint/method/request parameters into packet provenance; test from a raw provider-shaped value.

2. **P2 — the query response is publicly cacheable and the retention disclosure is incomplete.** The route returns `Cache-Control: public, max-age=300`. The UI says the query goes to TheoremSearch, whose current privacy policy states that it logs query text and filters. Use a private no-store policy and link or concisely state that provider logging policy beside the input.

3. **P3 — unexpected parser and network errors are returned verbatim.** The route returns any non-timeout `Error.message`. The actual-module harness observed both a JSON parser diagnostic and an injected transport diagnostic in its 502 body. Map expected cases to fixed actionable messages and all other exceptions to a bounded generic failure.

## Passing boundaries

The independently rerun adapter checks pass. The actual route accepts 512,000 bytes and rejects 512,001; rejects invalid queries before fetch; handles manual redirects, upstream failures, missing bodies and timeouts; and sends the fixed POST request with `n_results: 8`. Generated summaries and extracted bodies remain distinct through the route, UI and packet. HTTPS link filtering, React text rendering, unreviewed-result language, applicability caveats and miss-is-not-novelty language are aligned.

This review did not repeat broad browser QA or provider retrieval. It makes no claim about search quality, mathematical correctness, applicability, impact or novelty.
