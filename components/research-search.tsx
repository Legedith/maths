'use client';
import { ArrowUpRight, Download, LoaderCircle, Search } from 'lucide-react';
import { Input } from '@/components/ui/input';
import { Button } from '@/components/ui/button';
import {
  researchPacket,
  type ResearchHit,
  type ResearchSearchResult,
} from '@/lib/research-search';
export function ResearchSearch({
  query,
  setQuery,
  result,
  loading,
  error,
  search,
}: {
  query: string;
  setQuery: (value: string) => void;
  result: ResearchSearchResult | null;
  loading: boolean;
  error: string;
  search: (query: string) => Promise<ResearchSearchResult>;
}) {
  function download(hit: ResearchHit) {
    if (!result) return;
    const url = URL.createObjectURL(
      new Blob([JSON.stringify(researchPacket(result, hit), null, 2) + '\n'], {
        type: 'application/json',
      }),
    );
    const anchor = document.createElement('a');
    anchor.href = url;
    anchor.download = `statement-${hit.theoremId}.json`;
    anchor.click();
    URL.revokeObjectURL(url);
  }
  return (
    <section
      className="content-page research-search-section"
      aria-labelledby="research-search-heading"
    >
      <div className="page-heading">
        <span className="eyebrow">FIND EXISTING RESEARCH</span>
        <h1 id="research-search-heading">Describe the mathematics you need.</h1>
        <p>
          Search existing statements across mathematical papers and other
          sources. Then inspect the definitions that make a result applicable.
        </p>
      </div>
      <form
        className="formal-search-form"
        onSubmit={(e) => {
          e.preventDefault();
          void search(query).catch(() => {});
        }}
      >
        <label htmlFor="research-query">
          Describe a problem, theorem, or connection
        </label>
        <div>
          <Input
            id="research-query"
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            maxLength={500}
            placeholder="For example: random walks and electrical resistance"
          />
          <Button type="submit" disabled={loading || !query.trim()}>
            {loading ? (
              <LoaderCircle size={16} className="animate-spin" />
            ) : (
              <Search size={16} />
            )}{' '}
            Search research
          </Button>
        </div>
        <p className="fine-print">
          Your query is sent to{' '}
          <a
            href="https://www.theoremsearch.com/"
            target="_blank"
            rel="noreferrer"
          >
            TheoremSearch
          </a>
          . Results come from its existing index.
        </p>
      </form>
      {error && (
        <p className="error-message" role="alert">
          {error}
        </p>
      )}
      <div aria-live="polite">
        {loading ? (
          <p>Searching existing mathematical research…</p>
        ) : result ? (
          <>
            <div className="research-result-heading">
              <h2>{result.hits.length} research results</h2>
              <p>These results have not been added to the reviewed map.</p>
            </div>
            {result.hits.length === 0 ? (
              <p className="no-results">
                No result returned. Different terminology or another source may
                help; this does not establish that the problem is unsolved.
              </p>
            ) : (
              <div className="research-results">
                {result.hits.map((hit, index) => (
                  <article key={`${hit.theoremId}:${hit.sloganId}:${index}`}>
                    <span className="eyebrow">EXTERNAL RESEARCH RESULT</span>
                    <h3>{hit.name}</h3>
                    <p className="research-paper-title">{hit.paper.title}</p>
                    <p className="fine-print">
                      {[
                        hit.paper.authors.join(', '),
                        hit.paper.year,
                        hit.paper.source,
                      ]
                        .filter(Boolean)
                        .join(' · ')}
                    </p>
                    <div className="summary-box">
                      <strong>Generated search summary</strong>
                      <p>
                        {hit.generatedSummary ??
                          'No generated summary was supplied.'}
                      </p>
                    </div>
                    <details>
                      <summary>Inspect the extracted statement</summary>
                      <pre>
                        {hit.statement || 'No statement text was supplied.'}
                      </pre>
                      <p className="fine-print">
                        Definitions and assumptions may appear elsewhere in the
                        original source. The summary and extraction can contain
                        errors.
                      </p>
                    </details>
                    <div className="research-result-actions">
                      {hit.sourceUrl ? (
                        <a
                          href={hit.sourceUrl}
                          target="_blank"
                          rel="noreferrer"
                        >
                          Read original source <ArrowUpRight size={15} />
                        </a>
                      ) : (
                        <span className="fine-print">
                          Original-source link unavailable
                        </span>
                      )}
                      <Button
                        variant="outline"
                        size="sm"
                        onClick={() => download(hit)}
                      >
                        <Download size={15} /> Save source packet
                      </Button>
                    </div>
                  </article>
                ))}
              </div>
            )}
            <p className="fine-print">
              Retrieved {result.retrievedAt}. Saving a packet preserves the
              query, result IDs and supplied text; it does not certify a
              mathematical connection.
            </p>
          </>
        ) : (
          <div className="external-start">
            <h2>Start with a question. Follow the source.</h2>
            <p>
              Compare the generated summary with the statement, then read its
              definitions and assumptions before applying it to your problem.
            </p>
          </div>
        )}
      </div>
    </section>
  );
}
