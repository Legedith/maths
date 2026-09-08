'use client';
import { useCallback, useMemo, useRef, useState } from 'react';
import { flushSync } from 'react-dom';
import Link from 'next/link';
import {
  ArrowUpRight,
  BookOpen,
  GitBranch,
  Search,
  Map,
  FlaskConical,
  HandHelping,
  ArrowRight,
  Download,
} from 'lucide-react';
import { Input } from '@/components/ui/input';
import { Button } from '@/components/ui/button';
import { Tabs, TabsList, TabsTrigger, TabsContent } from '@/components/ui/tabs';
import {
  NativeSelect,
  NativeSelectOption,
} from '@/components/ui/native-select';
import { AtlasMap, colors } from '@/components/atlas-map';
import { AtlasLab, presets } from '@/components/atlas-lab';
import { FormalSearch } from '@/components/formal-search';
import { ResearchSearch } from '@/components/research-search';
import {
  validateResearchQuery,
  type ResearchSearchResult,
} from '@/lib/research-search';
import {
  validateFormalQuery,
  type FormalSearchResult,
} from '@/lib/formal-search';
import { atlas, domains, nodeById, sourceById, searchNodes } from '@/lib/atlas';
import {
  analyzeGraph,
  type GraphInput,
  type GraphResult,
} from '@/lib/exact-graph';
import { useAtlasTools } from '@/lib/use-atlas-tools';
export default function Home() {
  const [libraryMode, setLibraryMode] = useState<'research' | 'formal'>(
    'research',
  );
  const [researchQuery, setResearchQuery] = useState('');
  const [researchResult, setResearchResult] =
    useState<ResearchSearchResult | null>(null);
  const [researchLoading, setResearchLoading] = useState(false);
  const [researchError, setResearchError] = useState('');
  const researchGeneration = useRef(0);
  const [formalQuery, setFormalQuery] = useState('lapMatrix');
  const [formalResult, setFormalResult] = useState<FormalSearchResult | null>(
    null,
  );
  const [formalLoading, setFormalLoading] = useState(false);
  const [formalError, setFormalError] = useState('');
  const formalGeneration = useRef(0);
  const [query, setQuery] = useState(''),
    [domain, setDomain] = useState('All');
  const [selected, setSelected] = useState('laplacian'),
    [tab, setTab] = useState('map');
  const [pathFrom, setPathFrom] = useState('electrical-flow'),
    [destination, setDestination] = useState('spectral-sparsifier');
  const [journeyId, setJourneyId] = useState(atlas.journeys[0].id),
    [step, setStep] = useState(0);
  const [input, setInput] = useState<GraphInput>(presets[0].input),
    [result, setResult] = useState<GraphResult | null>(() =>
      analyzeGraph(presets[0].input),
    ),
    [error, setError] = useState('');
  const select = useCallback((id: string) => {
    setSelected(id);
    setTab('map');
  }, []);
  const changeInput = useCallback((value: GraphInput) => {
    setInput(value);
    setResult(null);
    setError('');
  }, []);
  const runFormalSearch = useCallback(
    async (rawQuery: string): Promise<FormalSearchResult> => {
      const q = validateFormalQuery(rawQuery);
      const generation = ++formalGeneration.current;
      flushSync(() => {
        setTab('search');
        setLibraryMode('formal');
        setFormalQuery(q);
        setFormalLoading(true);
        setFormalError('');
        setFormalResult(null);
      });
      try {
        const response = await fetch(
          `/api/formal-search?q=${encodeURIComponent(q)}`,
          { signal: AbortSignal.timeout(15000) },
        );
        const value: unknown = await response.json();
        if (!response.ok)
          throw new Error(
            value &&
              typeof value === 'object' &&
              'error' in value &&
              typeof value.error === 'string'
              ? value.error
              : 'External search failed.',
          );
        if (generation !== formalGeneration.current)
          throw new Error('This search was superseded by a newer query.');
        const result = value as FormalSearchResult;
        flushSync(() => {
          setFormalResult(result);
          setFormalLoading(false);
        });
        return result;
      } catch (error) {
        if (generation === formalGeneration.current)
          flushSync(() => {
            setFormalError(
              error instanceof Error
                ? error.message
                : 'External search failed.',
            );
            setFormalLoading(false);
          });
        throw error;
      }
    },
    [],
  );
  const runResearchSearch = useCallback(
    async (rawQuery: string): Promise<ResearchSearchResult> => {
      const q = validateResearchQuery(rawQuery);
      const generation = ++researchGeneration.current;
      flushSync(() => {
        setTab('search');
        setLibraryMode('research');
        setResearchQuery(q);
        setResearchLoading(true);
        setResearchError('');
        setResearchResult(null);
      });
      try {
        const response = await fetch(
          `/api/research-search?q=${encodeURIComponent(q)}`,
          { signal: AbortSignal.timeout(20000) },
        );
        const value: unknown = await response.json();
        if (!response.ok)
          throw new Error(
            value &&
              typeof value === 'object' &&
              'error' in value &&
              typeof value.error === 'string'
              ? value.error
              : 'Research search failed.',
          );
        if (generation !== researchGeneration.current)
          throw new Error('This search was superseded by a newer query.');
        const result = value as ResearchSearchResult;
        flushSync(() => {
          setResearchResult(result);
          setResearchLoading(false);
        });
        return result;
      } catch (error) {
        if (generation === researchGeneration.current)
          flushSync(() => {
            setResearchError(
              error instanceof Error
                ? error.message
                : 'Research search failed.',
            );
            setResearchLoading(false);
          });
        throw error;
      }
    },
    [],
  );
  const actions = useMemo(
    () => ({
      search: (q: string, d: string) => {
        setQuery(q);
        setDomain(d);
        setTab('map');
      },
      show: select,
      formalSearch: runFormalSearch,
      researchSearch: runResearchSearch,
      path: (from: string, to: string) => {
        setPathFrom(from);
        setDestination(to);
        select(from);
      },
      run: (value: GraphInput, computed: GraphResult) => {
        setInput(value);
        setResult(computed);
        setError('');
        setTab('lab');
      },
    }),
    [select, runFormalSearch, runResearchSearch],
  );
  useAtlasTools(actions);
  const results = searchNodes(query, domain),
    journey = atlas.journeys.find((j) => j.id === journeyId)!;
  const lesson = journey.steps[step],
    concept = nodeById[lesson.node];
  return (
    <main className="atlas-shell">
      <a className="skip-link" href="#workspace-content">
        Skip to workspace
      </a>
      <header className="atlas-header">
        <Link className="brand" href="/">
          <span className="brand-mark">
            <GitBranch size={21} />
          </span>
          <span>
            Mathematics<span className="brand-light"> Atlas</span>
          </span>
        </Link>
        <span className="scope-label">NETWORKS & BOOLEAN RELATIONS</span>
        <a
          className="repo-link"
          href="https://github.com/Legedith/maths"
          target="_blank"
          rel="noreferrer"
        >
          Open repository <ArrowUpRight size={15} />
        </a>
      </header>
      <div className="workspace">
        <aside className="catalogue">
          <div className="catalogue-heading">
            <h1>Explore connections</h1>
            <p>Start with an idea. See where it leads.</p>
            <Link
              href="/subjects"
              className="mt-3 inline-flex items-center gap-1 text-sm text-blue-700 underline underline-offset-4"
            >
              Browse mathematical subjects <ArrowRight size={14} />
            </Link>
            <Link
              href="/library"
              className="mt-3 inline-flex items-center gap-1 text-sm text-blue-700 underline underline-offset-4"
            >
              Browse concept resources <ArrowRight size={14} />
            </Link>
            <Link
              href="/connections"
              className="mt-3 ml-5 inline-flex items-center gap-1 text-sm text-blue-700 underline underline-offset-4"
            >
              Explore external connections <ArrowRight size={14} />
            </Link>
          </div>
          <div className="search-box">
            <Search size={18} />
            <Input
              aria-label="Search mathematical concepts"
              placeholder="Try resistance or random walk"
              maxLength={500}
              value={query}
              onChange={(e) => setQuery(e.target.value)}
            />
          </div>
          <label className="domain-filter">
            Field
            <NativeSelect
              value={domain}
              onChange={(e) => setDomain(e.target.value)}
            >
              <NativeSelectOption value="All">
                All fields in this region
              </NativeSelectOption>
              {domains.map((d) => (
                <NativeSelectOption value={d} key={d}>
                  {d}
                </NativeSelectOption>
              ))}
            </NativeSelect>
          </label>
          <div className="list-heading">
            <span>IN THIS REGION</span>
            <span aria-live="polite">{results.length} concepts</span>
          </div>
          <div className="concept-list">
            {results.map(({ node: n }) => (
              <button
                key={n.id}
                className={`concept-row ${n.id === selected && tab === 'map' ? 'active' : ''}`}
                aria-pressed={n.id === selected && tab === 'map'}
                onClick={() => select(n.id)}
              >
                <span
                  className="domain-dot"
                  style={{ background: colors[n.cluster] }}
                />
                <span>
                  <strong>{n.label}</strong>
                  <small>{n.domains.join(' · ')}</small>
                </span>
                <span className="row-arrow">↗</span>
              </button>
            ))}
            {!results.length && (
              <div className="no-results">
                <p>
                  No match in this region. A search miss does not mean the idea
                  is unknown.
                </p>
                <Button
                  variant="link"
                  onClick={() => {
                    setQuery('');
                    setDomain('All');
                  }}
                >
                  Clear search and filter
                </Button>
              </div>
            )}
          </div>
          <div className="coverage-note">
            <BookOpen size={18} />
            <div>
              <strong>A growing map</strong>
              <p>
                {atlas.nodes.length} concepts, {atlas.edges.length} connections,{' '}
                {atlas.sources.length} sources. Explore networks and Boolean
                relations; most mathematics is still to be mapped.
              </p>
              <a href="/api/atlas" target="_blank" rel="noreferrer">
                Get the open dataset <Download size={12} />
              </a>
            </div>
          </div>
        </aside>
        <Tabs
          id="workspace-content"
          className="workspace-tabs"
          value={tab}
          onValueChange={(value) => setTab(String(value))}
        >
          <div className="workspace-nav">
            <TabsList variant="line" aria-label="Atlas workspace">
              <TabsTrigger value="map">
                <Map /> Map
              </TabsTrigger>
              <TabsTrigger value="learn">
                <BookOpen /> Learn
              </TabsTrigger>
              <TabsTrigger value="search">
                <Search /> Search libraries
              </TabsTrigger>
              <TabsTrigger value="lab">
                <FlaskConical /> Experiment
              </TabsTrigger>
              <TabsTrigger value="contribute">
                <HandHelping /> Contribute
              </TabsTrigger>
            </TabsList>
            <span>Curated connections · source backed</span>
          </div>
          <TabsContent value="map">
            <AtlasMap
              selected={selected}
              select={select}
              destination={destination}
              setDestination={setDestination}
              pathFrom={pathFrom}
              setPathFrom={setPathFrom}
            />
          </TabsContent>
          <TabsContent value="search">
            <fieldset className="library-switch">
              <legend className="sr-only">Choose a research library</legend>
              <Button
                variant={libraryMode === 'research' ? 'default' : 'outline'}
                aria-pressed={libraryMode === 'research'}
                onClick={() => setLibraryMode('research')}
              >
                Describe an idea
              </Button>
              <Button
                variant={libraryMode === 'formal' ? 'default' : 'outline'}
                aria-pressed={libraryMode === 'formal'}
                onClick={() => setLibraryMode('formal')}
              >
                Search Lean names
              </Button>
            </fieldset>
            {libraryMode === 'research' ? (
              <ResearchSearch
                query={researchQuery}
                setQuery={setResearchQuery}
                result={researchResult}
                loading={researchLoading}
                error={researchError}
                search={runResearchSearch}
              />
            ) : (
              <FormalSearch
                query={formalQuery}
                setQuery={setFormalQuery}
                result={formalResult}
                loading={formalLoading}
                error={formalError}
                search={runFormalSearch}
              />
            )}
          </TabsContent>
          <TabsContent value="learn">
            <section className="content-page">
              <div className="page-heading">
                <span className="eyebrow">GUIDED CONNECTIONS</span>
                <h1>A way into the mathematics.</h1>
                <p>
                  Follow a short sequence of ideas. Each stop explains a
                  concept, shows its assumptions, and points you to the source.
                </p>
              </div>
              <div className="journey-choices">
                {atlas.journeys.map((j) => (
                  <button
                    key={j.id}
                    aria-pressed={journeyId === j.id}
                    className={journeyId === j.id ? 'chosen' : ''}
                    onClick={() => {
                      setJourneyId(j.id);
                      setStep(0);
                    }}
                  >
                    <span>{j.steps.length} STOPS</span>
                    <strong>{j.title}</strong>
                    <p>{j.description}</p>
                    <ArrowRight size={18} />
                  </button>
                ))}
              </div>
              <div className="lesson-layout">
                <ol className="lesson-steps">
                  {journey.steps.map((s, i) => (
                    <li key={s.node}>
                      <button
                        aria-current={step === i ? 'step' : undefined}
                        onClick={() => setStep(i)}
                      >
                        <span>{i + 1}</span>
                        {nodeById[s.node].label}
                      </button>
                    </li>
                  ))}
                </ol>
                <article className="lesson-card">
                  <span className="eyebrow">
                    STOP {step + 1} OF {journey.steps.length}
                  </span>
                  <h2>{concept.label}</h2>
                  <p className="lesson-prompt">{lesson.prompt}</p>
                  <p>{concept.explanation}</p>
                  {concept.formula && (
                    <div className="formula">{concept.formula}</div>
                  )}
                  <details>
                    <summary>Assumptions at this stop</summary>
                    <ul>
                      {concept.assumptions.map((a) => (
                        <li key={a}>{a}</li>
                      ))}
                    </ul>
                  </details>
                  {concept.evidence.map((v, i) => (
                    <a
                      className="lesson-source"
                      href={sourceById[v.source].url}
                      target="_blank"
                      rel="noreferrer"
                      key={i}
                    >
                      {sourceById[v.source].title} · {v.locator} ↗
                    </a>
                  ))}
                  <div className="lesson-actions">
                    <Button
                      variant="outline"
                      onClick={() => select(concept.id)}
                    >
                      Explore on the map
                    </Button>
                    {step < journey.steps.length - 1 ? (
                      <Button onClick={() => setStep(step + 1)}>
                        Next connection <ArrowRight size={15} />
                      </Button>
                    ) : (
                      <Button onClick={() => setTab('lab')}>
                        Try an experiment <FlaskConical size={15} />
                      </Button>
                    )}
                  </div>
                </article>
              </div>
            </section>
          </TabsContent>
          <TabsContent value="lab">
            <AtlasLab
              input={input}
              change={changeInput}
              result={result}
              error={error}
              select={select}
              run={() => {
                try {
                  setResult(analyzeGraph(input));
                  setError('');
                } catch (e) {
                  setResult(null);
                  setError(
                    e instanceof Error ? e.message : 'Computation failed.',
                  );
                }
              }}
            />
          </TabsContent>
          <TabsContent value="contribute">
            <section className="content-page">
              <div className="page-heading">
                <span className="eyebrow">WHERE YOU CAN ADD VALUE</span>
                <h1>Help connect the next idea.</h1>
                <p>
                  Build an example, examine an assumption, or connect a new
                  field. These are concrete project tasks; a gap in our map is
                  not an unsolved problem in mathematics.
                </p>
              </div>
              <div className="contribution-policy">
                <BookOpen size={22} />
                <div>
                  <h2>Every connection needs a reason.</h2>
                  <p>
                    Include a precise statement, its assumptions, and a source
                    or proof. Mark analogies as analogies. Candidate discoveries
                    stay provisional until their proof and prior art have been
                    reviewed independently.
                  </p>
                </div>
              </div>
              <div className="opportunities">
                {atlas.opportunities.map((o) => (
                  <article key={o.id} className="opportunity">
                    <div className="opportunity-meta">
                      <span>{o.kind.replaceAll('-', ' ')}</span>
                      <span>{o.difficulty}</span>
                    </div>
                    <h2>{o.title}</h2>
                    <p>{o.description}</p>
                    <h3>What a useful contribution includes</h3>
                    <ul>
                      {o.acceptance.map((a) => (
                        <li key={a}>{a}</li>
                      ))}
                    </ul>
                    <div className="topic-chips">
                      {o.nodes.map((id) => (
                        <Button
                          key={id}
                          variant="outline"
                          size="sm"
                          onClick={() => select(id)}
                        >
                          {nodeById[id].label}
                        </Button>
                      ))}
                    </div>
                    <a
                      className="task-link"
                      href={`https://github.com/Legedith/maths/issues/new?title=${encodeURIComponent(o.title)}&body=${encodeURIComponent(`Contribution task: ${o.id}\n\nProposed statement or change:\n\nAssumptions:\n\nSources and precise locators:\n\nProof or reproducible verification:\n\nWhat I checked for prior art:\n\nAcceptance criteria:\n${o.acceptance.map((a) => `- [ ] ${a}`).join('\n')}`)}`}
                      target="_blank"
                      rel="noreferrer"
                    >
                      Draft a contribution on GitHub <ArrowUpRight size={15} />
                    </a>
                  </article>
                ))}
              </div>
              <p className="fine-print">
                GitHub opens a draft for you to review and submit. No
                contribution is published automatically.
              </p>
            </section>
          </TabsContent>
        </Tabs>
      </div>
    </main>
  );
}
