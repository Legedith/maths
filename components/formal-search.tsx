'use client';
import { ArrowUpRight, Search, LoaderCircle } from 'lucide-react';
import { Input } from '@/components/ui/input';
import { Button } from '@/components/ui/button';
import { type FormalSearchResult } from '@/lib/formal-search';
export function FormalSearch({
  query,
  setQuery,
  result,
  loading,
  error,
  search,
}: {
  query: string;
  setQuery: (q: string) => void;
  result: FormalSearchResult | null;
  loading: boolean;
  error: string;
  search: (q: string) => Promise<FormalSearchResult>;
}) {
  return (
    <section className="content-page formal-page">
      <div className="page-heading">
        <span className="eyebrow">BUILT ON EXISTING MATHEMATICS</span>
        <h1>Search beyond this region.</h1>
        <p>
          Use the existing Loogle search index to find formal definitions and
          theorems in Mathlib. Start with a name fragment such as{' '}
          <code>lapMatrix</code>.
        </p>
      </div>
      <form
        className="formal-search-form"
        onSubmit={(e) => {
          e.preventDefault();
          void search(query).catch(() => {});
        }}
      >
        <label htmlFor="formal-query">Lean declaration name or fragment</label>
        <div>
          <Input
            id="formal-query"
            value={query}
            maxLength={120}
            placeholder="For example: lapMatrix"
            onChange={(e) => setQuery(e.target.value)}
          />
          <Button type="submit" disabled={loading || !query.trim()}>
            {loading ? (
              <LoaderCircle className="animate-spin" size={16} />
            ) : (
              <Search size={16} />
            )}{' '}
            Search Mathlib
          </Button>
        </div>
        <p className="fine-print">
          Your query is sent to{' '}
          <a
            href="https://loogle.lean-lang.org/"
            target="_blank"
            rel="noreferrer"
          >
            Loogle
          </a>
          . This is name search; it does not interpret a natural-language
          research problem.
        </p>
      </form>
      <div className="formal-examples">
        <span>Try:</span>
        {['lapMatrix', 'spanningTree', 'PosSemidef'].map((q) => (
          <Button
            key={q}
            variant="outline"
            size="sm"
            disabled={loading}
            onClick={() => {
              setQuery(q);
              void search(q).catch(() => {});
            }}
          >
            {q}
          </Button>
        ))}
      </div>
      {error && (
        <p className="error-message" role="alert">
          {error}
        </p>
      )}
      <div aria-live="polite">
        {loading ? (
          <p className="formal-loading">
            Searching the existing formal library…
          </p>
        ) : result ? (
          <>
            <div className="formal-result-heading">
              <h2>
                {result.count} declarations found for “{result.query}”
              </h2>
              <p>
                Showing {result.hits.length}. Results come from the live Loogle
                index; they have not been added to the curated map.
              </p>
            </div>
            {result.hits.length === 0 ? (
              <p className="no-results">
                No declaration name matched. The idea may use different
                terminology or be outside this index. This does not establish
                that it is unproved.
              </p>
            ) : (
              <div className="formal-results">
                {result.hits.map((hit) => (
                  <article key={`${hit.module}:${hit.name}`}>
                    <span className="eyebrow">
                      EXTERNAL FORMAL-LIBRARY RESULT
                    </span>
                    <h3>
                      <a href={hit.url} target="_blank" rel="noreferrer">
                        {hit.name}
                        <ArrowUpRight size={16} />
                      </a>
                    </h3>
                    {hit.description && <p>{hit.description}</p>}
                    <details>
                      <summary>
                        Inspect the formal statement and assumptions
                      </summary>
                      <pre>{hit.statement}</pre>
                      <small>{hit.module}</small>
                    </details>
                  </article>
                ))}
              </div>
            )}
            <p className="fine-print">
              Retrieved {result.retrievedAt}. Read the exact assumptions before
              transferring a result. A search hit is not a proof that it applies
              to your problem; this project has not rerun these declarations in
              a pinned Lean environment.
            </p>
          </>
        ) : (
          <div className="external-start">
            <h2>Reuse the library. Check the connection.</h2>
            <p>
              Find a relevant statement, inspect its assumptions, and then
              propose an evidence-backed connection to the map.
            </p>
          </div>
        )}
      </div>
      <div className="reuse-links">
        <h2>Other maps worth building on</h2>
        <a
          href="https://www.theoremsearch.com/theorem-graph"
          target="_blank"
          rel="noreferrer"
        >
          TheoremGraph{' '}
          <span>Statements and dependencies across papers and Lean</span>
          <ArrowUpRight size={16} />
        </a>
        <a
          href="https://github.com/zbMATHOpen/zbmath-open-kg"
          target="_blank"
          rel="noreferrer"
        >
          zbMATH Open KG{' '}
          <span>Literature, subject classifications and research metadata</span>
          <ArrowUpRight size={16} />
        </a>
        <a
          href="https://mathgloss.github.io/MathGloss/database"
          target="_blank"
          rel="noreferrer"
        >
          MathGloss <span>Linked concepts for learning mathematics</span>
          <ArrowUpRight size={16} />
        </a>
      </div>
    </section>
  );
}
