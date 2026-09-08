import subjects from '@/data/msc/subjects.json';
import references from '@/data/msc/references.json';
import { createSubjectCatalog, type SubjectIndex, type ReferenceIndex } from './subject-index';

export const subjectCatalog = createSubjectCatalog(subjects as unknown as SubjectIndex, references as unknown as ReferenceIndex);
