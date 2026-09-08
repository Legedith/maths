import type { Metadata } from 'next';
import raw from '@/data/mathgloss/candidate-index.json';
import { searchConceptLibrary, type ConceptIndex } from '@/lib/concept-library';
import { ConceptLibrary } from '@/components/concept-library';

export const metadata: Metadata = {
  title: 'Concept and resource library — Mathematics Atlas',
  description:
    'Find mathematical concepts and explore the resources linked by MathGloss.',
};
export default function LibraryPage() {
  const initial = searchConceptLibrary(raw as ConceptIndex, {
    query: 'Fourier',
  });
  return <ConceptLibrary initial={initial} />;
}
