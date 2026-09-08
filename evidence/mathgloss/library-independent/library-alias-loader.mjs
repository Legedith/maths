import { readFile } from 'node:fs/promises';
import { pathToFileURL } from 'node:url';

const PROJECT = 'D:/CodexWorkspaces/mathematics-atlas/project';
const CONCEPT_LIBRARY = pathToFileURL(`${PROJECT}/lib/concept-library.ts`).href;
const CANDIDATE_INDEX = pathToFileURL(
  `${PROJECT}/data/mathgloss/candidate-index.json`,
).href;

export async function resolve(specifier, context, nextResolve) {
  if (/^[A-Za-z]:[\\/]/.test(specifier))
    return { url: pathToFileURL(specifier).href, shortCircuit: true };
  if (specifier === '@/lib/concept-library')
    return { url: CONCEPT_LIBRARY, shortCircuit: true };
  if (specifier === '@/data/mathgloss/candidate-index.json')
    return { url: CANDIDATE_INDEX, shortCircuit: true };
  if (
    specifier === './concept-library' &&
    context.parentURL?.endsWith('/lib/use-concept-library-tools.ts')
  )
    return { url: CONCEPT_LIBRARY, shortCircuit: true };
  return nextResolve(specifier, context);
}

export async function load(url, context, nextLoad) {
  if (/^[A-Za-z]:[\\/]/.test(url)) {
    return {
      format: 'module',
      source: await readFile(url, 'utf8'),
      shortCircuit: true,
    };
  }
  if (url === CANDIDATE_INDEX) {
    const source = await readFile(new URL(url), 'utf8');
    return {
      format: 'module',
      source: `export default ${source};`,
      shortCircuit: true,
    };
  }
  return nextLoad(url, context);
}
