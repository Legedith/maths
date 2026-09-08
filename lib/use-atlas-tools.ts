'use client';
import { useEffect } from 'react';
import { flushSync } from 'react-dom';
import { atlas, connectionPath, domains, nodeById, searchNodes } from './atlas';
import { analyzeGraph, type GraphInput, type GraphResult } from './exact-graph';
import { validateFormalQuery, type FormalSearchResult } from './formal-search';
import {
  validateResearchQuery,
  type ResearchSearchResult,
} from './research-search';
type Tool = {
  name: string;
  title: string;
  description: string;
  inputSchema: object;
  annotations: { readOnlyHint: boolean; untrustedContentHint: boolean };
  execute: (input: unknown) => unknown;
};
type Context = {
  registerTool: (
    tool: Tool,
    options: { signal: AbortSignal },
  ) => void | Promise<void>;
};
type Actions = {
  researchSearch: (query: string) => Promise<ResearchSearchResult>;
  formalSearch: (query: string) => Promise<FormalSearchResult>;
  search: (query: string, domain: string) => void;
  show: (id: string) => void;
  path: (from: string, to: string) => void;
  run: (input: GraphInput, result: GraphResult) => void;
};
const schema = (properties: Record<string, object>, required: string[]) => ({
  type: 'object',
  properties,
  required,
  additionalProperties: false,
});
function object(input: unknown, allowed: string[]) {
  if (!input || typeof input !== 'object' || Array.isArray(input))
    throw new Error('Input must be an object.');
  const p = input as Record<string, unknown>;
  if (Object.keys(p).some((k) => !allowed.includes(k)))
    throw new Error('Unsupported input field.');
  return p;
}
const navigate = { readOnlyHint: false, untrustedContentHint: false };
export function atlasTools(actions: Actions): Tool[] {
  return [
    {
      name: 'search_research_statements',
      title: 'Find existing mathematical research',
      description:
        'Send a natural-language mathematical query to TheoremSearch and display external research results. Return generated summaries separately from extracted statements and original-source links. These are unreviewed retrievals, not proofs of applicability or novelty.',
      inputSchema: schema(
        { query: { type: 'string', minLength: 1, maxLength: 500 } },
        ['query'],
      ),
      annotations: { readOnlyHint: false, untrustedContentHint: true },
      async execute(input) {
        const p = object(input, ['query']);
        return actions.researchSearch(validateResearchQuery(p.query));
      },
    },
    {
      name: 'search_formal_library',
      title: 'Search the existing Mathlib index',
      description:
        'Send a declaration-name fragment to the external Loogle service, then display returned formal-library statements and their assumptions in Search libraries. This is name search, not natural-language or novelty detection; returned content is external and not promoted to the curated atlas.',
      inputSchema: schema(
        { query: { type: 'string', minLength: 1, maxLength: 120 } },
        ['query'],
      ),
      annotations: { readOnlyHint: false, untrustedContentHint: true },
      async execute(input) {
        const p = object(input, ['query']);
        const result = await actions.formalSearch(validateFormalQuery(p.query));
        return {
          provider: result.provider,
          query: result.query,
          count: result.count,
          hits: result.hits.map((h) => ({ name: h.name, url: h.url })),
          scope: result.scope,
        };
      },
    },
    {
      name: 'search_concepts',
      title: 'Search atlas concepts',
      description:
        'Search the curated region using lexical terms and update the visible catalogue. A miss does not establish novelty.',
      inputSchema: schema(
        {
          query: { type: 'string', maxLength: 500 },
          domain: { type: 'string', enum: ['All', ...domains] },
        },
        ['query'],
      ),
      annotations: navigate,
      execute(input) {
        const p = object(input, ['query', 'domain']);
        if (
          typeof p.query !== 'string' ||
          p.query.length > 500 ||
          (p.domain !== undefined &&
            (typeof p.domain !== 'string' ||
              !['All', ...domains].includes(p.domain)))
        )
          throw new Error(
            'Provide a query up to 500 characters and a supported domain.',
          );
        const domain = (p.domain as string) || 'All';
        const results = searchNodes(p.query, domain);
        actions.search(p.query, domain);
        return {
          scope: atlas.scope,
          results: results.map((r) => ({
            id: r.node.id,
            label: r.node.label,
            score: r.score,
          })),
        };
      },
    },
    {
      name: 'show_concept',
      title: 'Open a concept',
      description:
        'Navigate the map to one curated concept and display its assumptions and source-backed connections.',
      inputSchema: schema({ id: { type: 'string' } }, ['id']),
      annotations: navigate,
      execute(input) {
        const p = object(input, ['id']);
        if (typeof p.id !== 'string' || !Object.hasOwn(nodeById, p.id))
          throw new Error('Unknown concept ID.');
        actions.show(p.id);
        return {
          id: p.id,
          label: nodeById[p.id].label,
          status: nodeById[p.id].status,
        };
      },
    },
    {
      name: 'find_connection',
      title: 'Find a navigation path',
      description:
        'Display a shortest undirected navigation path between two curated concepts. Relation directions are retained; a path is not a composed mathematical implication.',
      inputSchema: schema(
        { from: { type: 'string' }, to: { type: 'string' } },
        ['from', 'to'],
      ),
      annotations: navigate,
      execute(input) {
        const p = object(input, ['from', 'to']);
        if (
          typeof p.from !== 'string' ||
          typeof p.to !== 'string' ||
          !Object.hasOwn(nodeById, p.from) ||
          !Object.hasOwn(nodeById, p.to)
        )
          throw new Error('Unknown concept ID.');
        const path = connectionPath(p.from, p.to);
        actions.path(p.from, p.to);
        return { from: p.from, to: p.to, edges: path, kind: 'navigation_only' };
      },
    },
    {
      name: 'run_graph_experiment',
      title: 'Run an exact graph experiment',
      description:
        'Compute resistance, hitting times and enumerated spanning-tree counts for a connected simple unweighted graph with 2 to 6 vertices, and display the input and exact result in the lab.',
      inputSchema: schema(
        {
          n: { type: 'integer', minimum: 2, maximum: 6 },
          edges: {
            type: 'array',
            maxItems: 15,
            items: {
              type: 'array',
              items: { type: 'integer', minimum: 0, maximum: 5 },
              minItems: 2,
              maxItems: 2,
            },
          },
          source: { type: 'integer', minimum: 0, maximum: 5 },
          target: { type: 'integer', minimum: 0, maximum: 5 },
        },
        ['n', 'edges', 'source', 'target'],
      ),
      annotations: navigate,
      execute(input) {
        const result = analyzeGraph(input);
        actions.run(
          {
            n: result.n,
            edges: result.edges,
            source: result.source,
            target: result.target,
          },
          result,
        );
        return result;
      },
    },
  ];
}
export function useAtlasTools(actions: Actions) {
  useEffect(() => {
    const context = (document as Document & { modelContext?: Context })
      .modelContext;
    if (!context?.registerTool) return;
    const lifecycle = new AbortController();
    const synchronized: Actions = {
      researchSearch: actions.researchSearch,
      formalSearch: actions.formalSearch,
      search: (query, domain) => flushSync(() => actions.search(query, domain)),
      show: (id) => flushSync(() => actions.show(id)),
      path: (from, to) => flushSync(() => actions.path(from, to)),
      run: (input, result) => flushSync(() => actions.run(input, result)),
    };
    for (const tool of atlasTools(synchronized)) {
      try {
        void Promise.resolve(
          context.registerTool(tool, { signal: lifecycle.signal }),
        ).catch((error) =>
          console.warn(`Atlas tool registration failed: ${tool.name}`, error),
        );
      } catch (error) {
        console.warn(`Atlas tool registration failed: ${tool.name}`, error);
      }
    }
    return () => lifecycle.abort();
  }, [actions]);
}
