import { pathToFileURL } from 'node:url';

const ADAPTER = pathToFileURL(
  'D:/CodexWorkspaces/mathematics-atlas/project/lib/research-search.ts',
).href;

export async function resolve(specifier, context, nextResolve) {
  if (specifier === '@/lib/research-search') {
    return { url: ADAPTER, shortCircuit: true };
  }
  return nextResolve(specifier, context);
}
