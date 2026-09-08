'use client';
import Link from 'next/link';
import { useCallback, useEffect, useRef, useState } from 'react';
import { flushSync } from 'react-dom';
import { conceptSourceUrl, validateLibraryQuery, type LibraryResult } from '@/lib/concept-library';
import { MATHGLOSS_RELATION_SOURCE, validateRelationQuery, type ExternalEdge, type RelationObservation, type RelationQuery, type RelationResult, type WikidataSnak } from '@/lib/external-relations';
import { useExternalRelationTools } from '@/lib/use-external-relation-tools';
import styles from './external-connections.module.css';

function ItemValue({ snak, labels }: { snak: WikidataSnak; labels: Record<string, string> }) {
  const value = snak.datavalue?.value;
  const id = value && typeof value === 'object' && 'id' in value ? String(value.id) : '';
  if (/^Q[1-9][0-9]*$/.test(id)) return <a href={`https://www.wikidata.org/wiki/${id}`} target="_blank" rel="noreferrer">{labels[id] ?? id} ({id})</a>;
  return <span>{value === undefined ? snak.snaktype : JSON.stringify(value)}</span>;
}

function Conditions({ observation }: { observation?: RelationObservation }) {
  if (!observation) return <p className={styles.condition}>Conditions and references were not retrieved in this export.</p>;
  return <div className={styles.condition}>
    {observation.matching_statements.map((statement) => {
      if (!Object.hasOwn(statement, 'qualifiers')) return <p key={statement.id}>No qualifier field was supplied on this statement in the dated response.</p>;
      const qualifiers = Object.entries(statement.qualifiers ?? {});
      if (!qualifiers.length) return <p key={statement.id}>The qualifier field was supplied as an empty container in the dated response.</p>;
      return qualifiers.map(([property, snaks]) =>
        <p key={`${statement.id}-${property}`}><strong>Condition:</strong>{' '}
          <a href={`https://www.wikidata.org/wiki/Property:${property}`} target="_blank" rel="noreferrer">{observation.display_labels[property] ?? property} ({property})</a>{': '}
          {snaks.length ? snaks.map((snak, index) => <span key={index}>{index > 0 ? '; ' : ''}<ItemValue snak={snak} labels={observation.display_labels} /></span>) : 'An empty value list was supplied.'}
        </p>);
    })}
    <span>Wikidata observation: {observation.retrieved_at_utc.slice(0, 10)}. This does not verify the relationship.</span>
  </div>;
}

function Provenance({ edge, observation }: { edge: ExternalEdge; observation?: RelationObservation }) {
  return <details className={styles.provenance}>
    <summary>Sources and statement details</summary>
    <p><a href={`${MATHGLOSS_RELATION_SOURCE}#L${edge.line_start}-L${edge.line_end}`} target="_blank" rel="noreferrer">Original MathGloss row {edge.record}</a> · <a href={`https://www.wikidata.org/wiki/${edge.source.id}#${edge.property.id}`} target="_blank" rel="noreferrer">Current Wikidata source item</a></p>
    <p>The pinned export records this directed assertion. Its statement conditions, references, rank and revision are unknown.</p>
    {observation && <>
      <p>A separate response retrieved at {observation.retrieved_at_utc} is attached below. <a href={`https://www.wikidata.org/w/index.php?title=${edge.source.id}&oldid=${observation.source_entity.lastrevid}`} target="_blank" rel="noreferrer">Entity revision {observation.source_entity.lastrevid}</a>, last modified {observation.source_entity.modified}.</p>
      <p>Recorded request (opening it fetches the current response): <a href={observation.requested_url} target="_blank" rel="noreferrer">{observation.requested_url}</a></p>
      {observation.matching_statements.map((statement) => <div key={statement.id}>
        <p>Statement: <code>{statement.id}</code><br />Rank: {statement.rank} (editorial rank; no mathematical validity judgement).</p>
        <p>{Object.hasOwn(statement, 'references') ? `${statement.references?.length ?? 0} reference records supplied.` : 'No reference field supplied in this response.'}</p>
        <pre>{JSON.stringify(statement, null, 2)}</pre>
      </div>)}
      <p>Raw response SHA-256: <code>{observation.raw_response_sha256}</code></p>
    </>}
  </details>;
}

function Neighborhood({ result, select }: { result: RelationResult; select: (qid: string) => void }) {
  const incoming = result.edges.filter((edge) => edge.target.id === result.qid).slice(0, 6);
  const outgoing = result.edges.filter((edge) => edge.target.id !== result.qid).slice(0, 6);
  const height = Math.max(240, Math.max(incoming.length, outgoing.length) * 76 + 60);
  const shown = incoming.length + outgoing.length;
  const draw = (edge: ExternalEdge, index: number, left: boolean) => {
    const neighbor = left ? edge.source : edge.target;
    const y = 40 + index * 76;
    const x = left ? 12 : 686;
    const line = left ? `M 264 ${y + 20} L 350 ${height / 2}` : `M 590 ${height / 2} L 676 ${y + 20}`;
    return <g key={edge.id}>
      <path d={line} fill="none" stroke={edge.property.id === 'P1889' ? '#b86318' : '#7898bc'} strokeWidth="1.7" markerEnd="url(#relation-arrow)" />
      <a href={`/connections?qid=${neighbor.id}`} aria-label={`Explore ${neighbor.label}`} onClick={(event) => { event.preventDefault(); select(neighbor.id); }} className={styles.graphNode}>
        <title>{`${edge.source.label} — ${edge.property.label} (${edge.property.id}) → ${edge.target.label}`}</title>
        <rect x={x} y={y} width="242" height="47" rx="7" />
        <text x={x + 12} y={y + 20}>{neighbor.label.length > 27 ? `${neighbor.label.slice(0, 26)}…` : neighbor.label}</text>
        <text x={x + 12} y={y + 38} className={styles.graphProperty}>{edge.property.label.length > 29 ? `${edge.property.label.slice(0, 28)}…` : edge.property.label} · {edge.property.id}</text>
      </a>
    </g>;
  };
  if (!shown) return null;
  return <figure className={styles.neighborhood}>
    <figcaption>Directed neighborhood · {shown} of {result.total} matching relations, drawn from this page. The full list follows.</figcaption>
    <div className={styles.diagramScroll}><svg viewBox={`0 0 940 ${height}`} aria-label={`Directed connections around ${result.concept.label_as_recorded}`}>
      <defs><marker id="relation-arrow" markerWidth="8" markerHeight="8" refX="7" refY="4" orient="auto"><path d="M 0 0 L 8 4 L 0 8 z" fill="#7898bc" /></marker></defs>
      {incoming.map((edge, index) => draw(edge, index, true))}
      {outgoing.map((edge, index) => draw(edge, index, false))}
      <rect x="350" y={height / 2 - 34} width="240" height="68" rx="10" fill="#12385e" />
      <text x="470" y={height / 2 - 4} textAnchor="middle" fill="white" fontSize="16">{result.concept.label_as_recorded.length > 25 ? `${result.concept.label_as_recorded.slice(0, 24)}…` : result.concept.label_as_recorded}</text>
      <text x="470" y={height / 2 + 20} textAnchor="middle" fill="#c2dcf7" fontSize="14">{result.qid}</text>
    </svg></div>
  </figure>;
}

export function ExternalConnections({ initial }: { initial: RelationResult }) {
  const [result, setResult] = useState(initial);
  const [query, setQuery] = useState('algorithm');
  const [matches, setMatches] = useState<LibraryResult | null>(null);
  const [searching, setSearching] = useState(false);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const generation = useRef(0);
  const searchGeneration = useRef(0);
  const invalidateRequests = useCallback(() => { generation.current++; searchGeneration.current++; }, []);
  const visibleResult = useRef(initial);
  const restoreVisibleUrl = useCallback(() => {
    const current = visibleResult.current;
    const params = new URLSearchParams({ qid: current.qid, property: current.property, direction: current.direction, page: String(current.page) });
    window.history.replaceState(null, '', `/connections?${params}`);
  }, []);
  const select = useCallback(async (input: RelationQuery, updateHistory = true): Promise<RelationResult> => {
    const validated = validateRelationQuery(input);
    if (validated.property !== 'All' && !initial.availableProperties.some((property) => property.id === validated.property)) throw new Error('Choose an available relation type.');
    const current = ++generation.current;
    setLoading(true);
    try {
      const params = new URLSearchParams({ ...validated, page: String(validated.page) });
      const response = await fetch(`/api/external-relations?${params}`, { signal: AbortSignal.timeout(15000) });
      if (!response.ok) throw new Error('The concept or filters could not be opened.');
      const next = await response.json() as RelationResult;
      if (current !== generation.current) throw new Error('A newer selection replaced this request.');
      visibleResult.current = next;
      flushSync(() => { setResult(next); setLoading(false); setError(''); });
      if (updateHistory) window.history.pushState(null, '', `/connections?${params}`);
      else window.history.replaceState(null, '', `/connections?${params}`);
      return next;
    } catch (cause) {
      if (current === generation.current) {
        setLoading(false); setError('Could not open that concept or filter. Your previous selection is still shown.');
        if (!updateHistory) restoreVisibleUrl();
      }
      throw cause;
    }
  }, [initial.availableProperties, restoreVisibleUrl]);
  useExternalRelationTools(select);
  useEffect(() => {
    const restore = () => {
      const params = new URLSearchParams(window.location.search);
      if (!params.size) {
        void select({ qid: initial.qid, property: 'All', direction: 'both', page: 1 }, false).catch(() => undefined);
        return;
      }
      try {
        if ([...params.keys()].some((key) => !['qid', 'property', 'direction', 'page'].includes(key)) || [...params.keys()].some((key) => params.getAll(key).length !== 1)) throw new Error();
        const page = params.get('page') ?? '1';
        if (!/^[1-9][0-9]{0,6}$/.test(page)) throw new Error();
        const next = validateRelationQuery({ qid: params.get('qid'), property: params.get('property') ?? 'All', direction: params.get('direction') ?? 'both', page: Number(page) });
        generation.current++;
        void select(next, false).catch(() => { setLoading(false); setError('Could not restore that link. The previous selection and its URL are shown.'); restoreVisibleUrl(); });
      } catch {
        generation.current++;
        setLoading(false);
        setError('This link has invalid concept or filter values. The previous selection is shown and its URL has been restored.');
        restoreVisibleUrl();
      }
    };
    if (window.location.search) queueMicrotask(restore);
    window.addEventListener('popstate', restore);
    return () => { window.removeEventListener('popstate', restore); invalidateRequests(); };
  }, [initial.qid, select, restoreVisibleUrl, invalidateRequests]);
  const choose = (qid: string) => { void select({ qid, property: 'All', direction: 'both', page: 1 }).catch(() => undefined); };
  const change = (input: RelationQuery) => { void select(input).catch(() => undefined); };
  const search = async (page: number, searchText = query) => {
    const input = validateLibraryQuery({ query: searchText, page });
    const current = ++searchGeneration.current;
    setQuery(input.query);
    setSearching(true);
    try {
      const params = new URLSearchParams({ q: input.query, page: String(input.page) });
      const response = await fetch(`/api/concept-library?${params}`, { signal: AbortSignal.timeout(15000) });
      if (!response.ok) throw new Error();
      const next = await response.json() as LibraryResult;
      if (current === searchGeneration.current) { setMatches(next); setSearching(false); setError(''); }
    } catch { if (current === searchGeneration.current) { setSearching(false); setError('Concept search could not be completed. Please try again.'); } }
  };

  return <main className={styles.page}>
    <header className={styles.top}><Link href="/">← Mathematics Atlas</Link><Link href="/library">Concept library</Link><span>{result.coverage.included_rows.toLocaleString('en')} imported connections</span></header>
    <h1>Explore connections</h1>
    <p className={styles.intro}>Start with an idea. Follow its connections, then read the sources and conditions.</p>
    <div className={styles.workspace}>
      <aside className={styles.finder} aria-label="Find a concept">
        <form onSubmit={(event) => { event.preventDefault(); void search(1); }}>
          <label htmlFor="connection-query">Concept name or QID</label>
          <div className={styles.searchRow}><input id="connection-query" type="search" maxLength={500} value={query} onChange={(event) => setQuery(event.target.value)} /><button disabled={searching} type="submit">{searching ? 'Finding…' : 'Find'}</button></div>
        </form>
        <div className={styles.shortcuts}><span>Try a starting point</span><button onClick={() => choose('Q8366')}>Algorithm</button><button onClick={() => choose('Q176645')}>Markov chain</button><button onClick={() => choose('Q1028292')}>Grover’s algorithm</button></div>
        {matches && <section aria-label="Concept search results"><p>{matches.total} matches for “{matches.query}”</p>
          <ul className={styles.matches}>{matches.records.map((record) => <li key={record.record_key}><button onClick={() => choose(record.identity_candidate.qid)}>{record.label_as_recorded}<small>{record.identity_candidate.qid}</small></button></li>)}</ul>
          <div className={styles.pagination}><button disabled={searching || matches.page <= 1} onClick={() => void search(matches.page - 1, matches.query)}>Previous</button><span>{matches.page} / {Math.max(1, matches.pages)}</span><button disabled={searching || matches.page >= matches.pages} onClick={() => void search(matches.page + 1, matches.query)}>Next</button></div>
        </section>}
        <p className={styles.note}>These connections are external assertions from MathGloss’s Wikidata export. They have not been mathematically reviewed. A missing connection is not evidence that a problem is open.</p>
      </aside>
      <section className={styles.content} aria-busy={loading}>
        {error && <p role="alert" className={styles.error}>{error}</p>}
        <div className={styles.conceptHeading}><div><span className={styles.eyebrow}>Selected concept · {result.qid}</span><h2>{result.concept.label_as_recorded}</h2></div><span className={styles.badge}>External assertions</span></div>
        <details className={styles.resources}><summary>Learn about {result.concept.label_as_recorded} · {result.concept.links.length} resource links</summary><ul>{result.concept.links.map((link, index) => <li key={`${link.source}-${index}`}><a href={link.url} target="_blank" rel="noreferrer">{link.name_as_recorded} — {link.source}</a></li>)}</ul><a href={conceptSourceUrl(result.concept)} target="_blank" rel="noreferrer">Original concept record</a><p>Resource mappings are also unreviewed.</p></details>
        <div className={styles.filters}>
          <label>Relation type<select value={result.property} disabled={loading} onChange={(event) => change({ qid: result.qid, direction: result.direction, property: event.target.value, page: 1 })}><option value="All">All types</option>{result.availableProperties.filter((property) => result.properties.some((present) => present.id === property.id) || result.property === property.id).map((property) => <option key={property.id} value={property.id}>{property.label} ({property.id})</option>)}</select></label>
          <label>Direction<select value={result.direction} disabled={loading} onChange={(event) => change({ qid: result.qid, property: result.property, direction: event.target.value as RelationQuery['direction'], page: 1 })}><option value="both">Incoming and outgoing</option><option value="incoming">Incoming to this concept</option><option value="outgoing">Outgoing from this concept</option></select></label>
          <output aria-live="polite">{loading ? 'Opening connections…' : `${result.total} matching relations`}</output>
        </div>
        <Neighborhood result={result} select={choose} />
        {!result.total && <p className={styles.empty}>No matching relations in this imported snapshot. Try another type or direction, or follow the learning resources above.</p>}
        {result.total > 0 && !result.edges.length && <p className={styles.empty}>This page is beyond the available results. <button onClick={() => change({ qid: result.qid, property: result.property, direction: result.direction, page: 1 })}>Open the first page</button></p>}
        <ol className={styles.edgeList} aria-label="Complete paginated relation list">
          {result.edges.map((edge) => <li key={edge.id}>
            <div className={styles.edgeStatement}><button onClick={() => choose(edge.source.id)}>{edge.source.label}<small>{edge.source.id}</small></button><span><a href={`https://www.wikidata.org/wiki/Property:${edge.property.id}`} target="_blank" rel="noreferrer">{edge.property.label} ({edge.property.id})</a><strong aria-label="points to">→</strong></span><button onClick={() => choose(edge.target.id)}>{edge.target.label}<small>{edge.target.id}</small></button></div>
            {edge.property.id === 'P460' && <p className={styles.sameAs}>“Said to be the same as” may be uncertain or disputed; this is not a proof of equivalence.</p>}
            <Conditions observation={result.observations[edge.id]} />
            <Provenance edge={edge} observation={result.observations[edge.id]} />
          </li>)}
        </ol>
        <div className={styles.pagination}><button disabled={loading || result.page <= 1} onClick={() => change({ qid: result.qid, property: result.property, direction: result.direction, page: result.page - 1 })}>Previous</button><span>Page {result.page} of {Math.max(1, result.pages)} · {result.pageSize} per page</span><button disabled={loading || result.page >= result.pages} onClick={() => change({ qid: result.qid, property: result.property, direction: result.direction, page: result.page + 1 })}>Next</button></div>
        <p className={styles.note}>The URL keeps your selected concept and filters. Search stays on this site and may appear in normal access logs. External sources open only when you follow a link.</p>
      </section>
    </div>
  </main>;
}
