# Reuse external mathematical search

This branch adds natural-language retrieval through TheoremSearch alongside the existing Loogle declaration-name search. It does not build a second theorem index. Both searches are available in the Search libraries tab and through the page's WebMCP actions.

The implementation follows the [provider's API reference](https://www.theoremsearch.com/docs), read on 2026-09-08: `POST /search` accepts a query and result limit and returns statement identifiers, extracted bodies, generated summaries and source metadata. The adapter requests eight results, validates their representation, limits response bytes and waiting time, and preserves body and summary as different fields. A saved source packet also retains the query, retrieval time, result identifiers, original rank, available similarity/score values, exact request parameters and review tasks. The packet is not an executable mathematical annotation, and ranking scores are not probabilities of mathematical truth.

The provider also offers [statement dependencies](https://www.theoremsearch.com/theorem-graph). Those include parsed candidate dependencies and separately typed formal relationships. A generated match or an informal dependency is not a proof that two statements are equivalent. Dependency traversal is a future reuse opportunity; this adapter implements search only.

## What was checked

`scripts/check-research-search.ts` tests malformed responses, stable identifiers, unsafe source links, absent optional metadata, result limits, query bounds, and separation of the summary from the source body. The live action check used **compact Hausdorff continuous bijection**, outside the frozen network retrieval study. It returned eight results and updated the visible search state; whitespace-only input was rejected while retaining the earlier successful result. The existing Loogle action still switched to its own view and returned 23 declarations for `lapMatrix`.

These are integration checks, not search-quality or mathematical-correctness evaluations. The 24-result prospective source study is recorded separately. The live index can change; retained observations describe a particular retrieval time. No new source packet is automatically promoted into the reviewed concept map.

## Source and runtime boundaries

- The UI tells users that their query goes to TheoremSearch and that the provider logs query text, linking its [privacy policy](https://www.theoremsearch.com/privacy), read on 2026-09-08.
- Results are rendered as text, with an explicit original-source link when a usable HTTPS link was supplied.
- The server contacts a fixed provider endpoint; users cannot supply a fetch destination.
- A timeout, upstream failure, malformed response or response-size overflow returns an explicit error.
- Search responses and errors use `Cache-Control: no-store`; arbitrary parser/network exception text is not sent to users.
- A missing result is not evidence that a problem is unsolved.
- The Python assumption checker is a separate component. This UI does not pretend to interpret arbitrary mathematical prose or run Python inside the browser.
