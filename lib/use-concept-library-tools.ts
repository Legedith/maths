'use client';
import { useEffect } from 'react';
import {
  validateLibraryQuery,
  type LibraryQuery,
  type LibraryResult,
} from './concept-library';

type Action = (input: LibraryQuery) => Promise<LibraryResult>;
export function conceptLibraryTool(search: Action) {
  return {
    name: 'search_learning_resources',
    title: 'Find mathematical concepts and resources',
    description:
      'Search the pinned MathGloss concept and resource catalog by recorded name or Wikidata QID, optionally restrict the resource source, and display a result page. These are unreviewed mappings; a miss does not establish novelty.',
    inputSchema: {
      type: 'object',
      properties: {
        query: { type: 'string', maxLength: 500 },
        resource: {
          type: 'string',
          minLength: 1,
          maxLength: 80,
          description: 'All or a source name returned in resources.',
        },
        page: { type: 'integer', minimum: 1, maximum: 1000000 },
      },
      required: ['query'],
      additionalProperties: false,
    },
    annotations: { readOnlyHint: false, untrustedContentHint: true },
    execute: (input: unknown) => search(validateLibraryQuery(input)),
  };
}
export function useConceptLibraryTools(search: Action) {
  useEffect(() => {
    const context = (
      document as Document & {
        modelContext?: {
          registerTool: (
            tool: ReturnType<typeof conceptLibraryTool>,
            options: { signal: AbortSignal },
          ) => void | Promise<void>;
        };
      }
    ).modelContext;
    if (!context?.registerTool) return;
    const lifecycle = new AbortController();
    try {
      void Promise.resolve(
        context.registerTool(conceptLibraryTool(search), {
          signal: lifecycle.signal,
        }),
      ).catch(() => console.warn('Resource search tool registration failed.'));
    } catch {
      console.warn('Resource search tool registration failed.');
    }
    return () => lifecycle.abort();
  }, [search]);
}
