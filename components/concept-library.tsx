'use client';
import Link from 'next/link';
import { useCallback, useRef, useState } from 'react';
import { flushSync } from 'react-dom';
import {
  conceptSourceUrl,
  validateLibraryQuery,
  type LibraryQuery,
  type LibraryResult,
} from '@/lib/concept-library';
import { useConceptLibraryTools } from '@/lib/use-concept-library-tools';
import styles from './concept-library.module.css';

export function ConceptLibrary({ initial }: { initial: LibraryResult }) {
  const [query, setQuery] = useState(initial.query);
  const [resource, setResource] = useState(initial.resource);
  const [result, setResult] = useState<LibraryResult | null>(initial);
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);
  const generation = useRef(0);
  const runSearch = useCallback(
    async (input: LibraryQuery): Promise<LibraryResult> => {
      const request = validateLibraryQuery(input);
      if (
        request.resource !== 'All' &&
        !initial.resources.includes(request.resource)
      )
        throw new Error('Choose an available resource.');
      const current = ++generation.current;
      flushSync(() => {
        setQuery(request.query);
        setResource(request.resource);
        setError('');
        setResult(null);
        setLoading(true);
      });
      try {
        const params = new URLSearchParams({
          q: request.query,
          resource: request.resource,
          page: String(request.page),
        });
        const response = await fetch(
          `/api/concept-library?${params.toString()}`,
          { signal: AbortSignal.timeout(15000) },
        );
        if (!response.ok)
          throw new Error(
            'The library search could not be completed. Please try again.',
          );
        const next = (await response.json()) as LibraryResult;
        if (current !== generation.current)
          throw new Error('A newer search replaced this request.');
        flushSync(() => {
          setResult(next);
          setLoading(false);
        });
        return next;
      } catch (cause) {
        if (current === generation.current)
          flushSync(() => {
            setError(
              'The library search could not be completed. Please try again.',
            );
            setLoading(false);
          });
        throw cause;
      }
    },
    [initial.resources],
  );
  useConceptLibraryTools(runSearch);
  const search = (next: LibraryQuery) => {
    void runSearch(next).catch(() => undefined);
  };

  return (
    <main className={styles.library}>
      <header className={styles.header}>
        <Link href="/">← Mathematics Atlas</Link>
        <span>
          {initial.catalogRecords.toLocaleString('en')} concept records ·{' '}
          {initial.catalogLinks.toLocaleString('en')} resource links
        </span>
      </header>
      <h1>Concept and resource library</h1>
      <p>
        Find an idea by its name, then explore how different resources describe
        it.
      </p>
      <form
        className={styles.search}
        onSubmit={(event) => {
          event.preventDefault();
          search({ query, resource, page: 1 });
        }}
      >
        <label className={styles.query}>
          Concept name or Wikidata QID
          <input
            type="search"
            value={query}
            maxLength={500}
            onChange={(event) => setQuery(event.target.value)}
          />
        </label>
        <label>
          Resource
          <select
            value={resource}
            onChange={(event) => setResource(event.target.value)}
          >
            <option value="All">All resources</option>
            {initial.resources.map((name) => (
              <option key={name} value={name}>
                {name}
              </option>
            ))}
          </select>
        </label>
        <button type="submit" disabled={loading}>
          Search library
        </button>
      </form>
      <div className={styles.examples} aria-label="Example searches">
        <span>Explore:</span>
        {['Fourier', 'Turing', 'probability', 'graph'].map((word) => (
          <button
            key={word}
            type="button"
            onClick={() => search({ query: word, resource: 'All', page: 1 })}
          >
            {word}
          </button>
        ))}
      </div>
      <p className={styles.scope}>
        These mappings come from{' '}
        <a href="https://github.com/MathGloss/MathGloss">MathGloss</a>. They
        have not been individually verified here. Resources vary in difficulty;
        a missing search result does not mean an idea is undiscovered.
      </p>
      {error && <p role="alert">{error}</p>}
      <section aria-label="Library results" aria-busy={loading}>
        <div aria-live="polite">
          {loading ? (
            <p>Searching the library…</p>
          ) : (
            result && (
              <h2>
                {result.total} matching records
                {result.query ? ` for “${result.query}”` : ''}
                {result.resource !== 'All' ? ` in ${result.resource}` : ''}
              </h2>
            )
          )}
        </div>
        {result && result.records.length === 0 && (
          <p>
            No records on this page. Try another name, choose all resources, or
            return to the first page.
          </p>
        )}
        <div className={styles.results}>
          {result?.records.map((record) => (
            <article className={styles.record} key={record.record_key}>
              <div className={styles.recordHeading}>
                <h3>{record.label_as_recorded}</h3>
                <a
                  href={record.identity_candidate.uri}
                  target="_blank"
                  rel="noopener noreferrer"
                >
                  {record.identity_candidate.qid}
                </a>
              </div>
              <ul>
                {record.links.map((link) => (
                  <li key={link.source}>
                    <span>{link.source}</span>
                    <a
                      href={link.url}
                      target="_blank"
                      rel="noopener noreferrer"
                    >
                      {link.name_as_recorded} ↗
                    </a>
                  </li>
                ))}
              </ul>
              <footer>
                <span>Mapping proposed by MathGloss · unreviewed</span>
                <a
                  href={conceptSourceUrl(record)}
                  target="_blank"
                  rel="noopener noreferrer"
                >
                  Source record ↗
                </a>
              </footer>
            </article>
          ))}
        </div>
        {result && (
          <nav className={styles.pagination} aria-label="Result pages">
            <button
              type="button"
              disabled={result.page <= 1}
              onClick={() =>
                search({
                  query: result.query,
                  resource: result.resource,
                  page: result.page - 1,
                })
              }
            >
              Previous
            </button>
            <span>
              Page {result.page} of {Math.max(1, result.pages)}
            </span>
            <button
              type="button"
              disabled={result.page >= result.pages}
              onClick={() =>
                search({
                  query: result.query,
                  resource: result.resource,
                  page: result.page + 1,
                })
              }
            >
              Next
            </button>
            {result.page > 1 && (
              <button
                type="button"
                onClick={() =>
                  search({
                    query: result.query,
                    resource: result.resource,
                    page: 1,
                  })
                }
              >
                First page
              </button>
            )}
          </nav>
        )}
      </section>
      <footer className={styles.attribution}>
        <p>
          MathGloss snapshot: 8 September 2026 import, pinned to{' '}
          <a href="https://github.com/MathGloss/MathGloss/tree/b8f659605486f80f2816515f525af2c395c711fa">
            the recorded source revision
          </a>
          . Search matches words and name fragments in the recorded labels and
          resource names. Linked pages retain their own terms.
        </p>
      </footer>
    </main>
  );
}
