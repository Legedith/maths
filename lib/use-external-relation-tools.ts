'use client';
import { useEffect } from 'react';
import { validateRelationQuery, type RelationQuery, type RelationResult } from './external-relations';

type Action = (input: RelationQuery) => Promise<RelationResult>;
export function externalRelationTool(select: Action) {
  return {
    name: 'explore_external_connections',
    title: 'Explore a concept’s external connections',
    description: 'Select a library concept by Wikidata QID, filter incoming/outgoing typed MathGloss relations and display a page. These are unreviewed external assertions; they do not prove equivalence or novelty. Updates the visible neighborhood and URL.',
    inputSchema: {
      type: 'object',
      properties: {
        qid: { type: 'string', pattern: '^Q[1-9][0-9]{0,14}$' },
        property: { type: 'string', pattern: '^(All|P[1-9][0-9]{0,14})$', description: 'All or an available Wikidata property ID.' },
        direction: { type: 'string', enum: ['both', 'incoming', 'outgoing'] },
        page: { type: 'integer', minimum: 1, maximum: 1000000 },
      },
      required: ['qid'], additionalProperties: false,
    },
    annotations: { readOnlyHint: false, untrustedContentHint: true },
    execute: (input: unknown) => select(validateRelationQuery(input)),
  };
}
export function useExternalRelationTools(select: Action) {
  useEffect(() => {
    const context = (document as Document & { modelContext?: { registerTool: (tool: ReturnType<typeof externalRelationTool>, options: { signal: AbortSignal }) => void | Promise<void> } }).modelContext;
    if (!context?.registerTool) return;
    const lifecycle = new AbortController();
    try {
      void Promise.resolve(context.registerTool(externalRelationTool(select), { signal: lifecycle.signal }))
        .catch(() => console.warn('Connection tool registration failed.'));
    } catch { console.warn('Connection tool registration failed.'); }
    return () => lifecycle.abort();
  }, [select]);
}
