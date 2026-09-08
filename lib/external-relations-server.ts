import rawRelations from '@/data/mathgloss/relations/relation-index.json';
import rawConcepts from '@/data/mathgloss/candidate-index.json';
import type { ConceptIndex } from './concept-library';
import { createRelationExplorer, type RelationIndex } from './external-relations';

export const exploreExternalRelations = createRelationExplorer(rawRelations as unknown as RelationIndex, rawConcepts as ConceptIndex);
