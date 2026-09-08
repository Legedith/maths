export type RdfTerm = { kind: 'uri' | 'literal'; value: string; language?: string | null; datatype?: string | null };
export type Subject = {
  code: string; label_as_recorded: string; description_as_recorded: string;
  kind: string; hierarchy_level: number; is_leaf: boolean; navigation_parent_code: string | null; uri: string;
  classification_status: 'upstream_subject_classification';
  source_locator: { source_id: string; data_record: number; physical_lines: { start: number; end: number } };
  rdf_source_id: string; rdf_labels: RdfTerm[]; rdf_broader_uris: string[];
  hierarchy_disagreement: boolean; exact_label_difference: boolean;
  rdf_scope_notes: { term: RdfTerm; source_statements?: { predicate_uri: string; objects: RdfTerm[] }[] }[];
};
export type SubjectIndex = { metadata: { attribution: string; data_license: string; data_license_url: string; limitations: string[] }; subjects: Subject[] };
export type SubjectReference = {
  from_uri: string; predicate_uri: string; to_uri: string; target_kind: 'subject' | 'collection';
  status: 'upstream_classification_reference'; source_id: string;
  scope_records: { uri: string; scopes: RdfTerm[] }[];
};
export type SubjectCollection = { uri: string; kind: string; labels: RdfTerm[]; member_uris: string[]; source_id: string };
export type ReferenceIndex = { relations: SubjectReference[]; collections: SubjectCollection[] };
export type SubjectQuery = { query: string; parent: string; page: number };
export const SUBJECT_PAGE_SIZE = 24;
const codePattern = /^[0-9]{2}(?:-XX|-[0-9]{2}|[A-Z](?:xx|[0-9]{2}))$/;
export const normalizeSubjectQuery = (value: string) => value.normalize('NFKC').toLowerCase().replace(/[^\p{L}\p{N}]+/gu, ' ').trim();

export function validateSubjectQuery(value: unknown): SubjectQuery {
  if (!value || typeof value !== 'object' || Array.isArray(value)) throw new Error('Use a subject search object.');
  const input = value as Record<string, unknown>;
  if (Object.keys(input).some(key => !['query', 'parent', 'page'].includes(key))) throw new Error('Unsupported search field.');
  if (typeof input.query !== 'string' || input.query.length > 300) throw new Error('Use a query of at most 300 characters.');
  const parent = input.parent === undefined ? (input.query.trim() ? 'all' : 'root') : input.parent;
  if (typeof parent !== 'string' || !(['root', 'all'].includes(parent) || codePattern.test(parent))) throw new Error('Choose an existing parent subject, root or all.');
  const page = input.page === undefined ? 1 : input.page;
  if (typeof page !== 'number' || !Number.isSafeInteger(page) || page < 1 || page > 1000000) throw new Error('Page must be a positive integer no greater than 1000000.');
  return { query: input.query.trim(), parent, page };
}

export function validateSubjectCode(value: unknown): string {
  if (typeof value !== 'string' || !codePattern.test(value)) throw new Error('Use an MSC2020 subject code.');
  return value;
}

export const subjectSummary = (row: Subject) => ({ code: row.code, label: row.label_as_recorded, kind: row.kind, parent: row.navigation_parent_code });

export function createSubjectCatalog(index: SubjectIndex, references: ReferenceIndex) {
  const byCode = new Map(index.subjects.map(row => [row.code, row]));
  const byUri = new Map(index.subjects.map(row => [row.uri, row]));
  const collections = new Map(references.collections.map(row => [row.uri, row]));
  const children = new Map<string | null, Subject[]>();
  const outgoing = new Map<string, SubjectReference[]>(), incoming = new Map<string, SubjectReference[]>();
  const searchRows = index.subjects.map(row => ({ row, text: normalizeSubjectQuery(`${row.code} ${row.label_as_recorded} ${row.description_as_recorded}`) }));
  for (const row of index.subjects) {
    if (row.navigation_parent_code && !byCode.has(row.navigation_parent_code)) throw new Error('Subject parent is missing.');
    const group = children.get(row.navigation_parent_code) ?? [];
    group.push(row); children.set(row.navigation_parent_code, group);
  }
  for (const relation of references.relations) {
    if (!byUri.has(relation.from_uri) || !(byUri.has(relation.to_uri) || collections.has(relation.to_uri))) throw new Error('Subject reference endpoint is missing.');
    const from = outgoing.get(relation.from_uri) ?? [], to = incoming.get(relation.to_uri) ?? [];
    from.push(relation); to.push(relation);
    outgoing.set(relation.from_uri, from); incoming.set(relation.to_uri, to);
  }
  for (const row of index.subjects) if ((outgoing.get(row.uri)?.length ?? 0) + (incoming.get(row.uri)?.length ?? 0) > 512) throw new Error('Subject reference limit exceeded.');
  for (const collection of collections.values()) if (collection.member_uris.length > 512 || collection.member_uris.some(uri => !byUri.has(uri))) throw new Error('Collection members are invalid or oversized.');
  const stats = { subjects: index.subjects.length, topLevels: children.get(null)?.length ?? 0, references: references.relations.length };
  const get = (code: unknown) => {
    const row = byCode.get(validateSubjectCode(code));
    if (!row) throw new Error('Unknown MSC2020 subject.');
    return row;
  };
  const endpoint = (uri: string) => {
    const subject = byUri.get(uri);
    if (subject) return { kind: 'subject' as const, uri, code: subject.code, label: subject.label_as_recorded };
    const collection = collections.get(uri);
    if (!collection) throw new Error('Unknown reference endpoint.');
    return { kind: 'collection' as const, uri, code: null, label: collection.labels.find(label => label.language === 'en')?.value ?? uri };
  };
  return {
    stats,
    metadata: index.metadata,
    search(value: unknown) {
      const request = validateSubjectQuery(value);
      if (!['all', 'root'].includes(request.parent)) get(request.parent);
      const terms = normalizeSubjectQuery(request.query).split(/\s+/).filter(Boolean);
      const matches = searchRows.filter(({row, text}) => (request.parent === 'all' || row.navigation_parent_code === (request.parent === 'root' ? null : request.parent)) && terms.every(term => text.includes(term)));
      return { ...request, ...stats, metadata: index.metadata, total: matches.length, pageSize: SUBJECT_PAGE_SIZE, pages: Math.ceil(matches.length / SUBJECT_PAGE_SIZE), records: matches.slice((request.page - 1) * SUBJECT_PAGE_SIZE, request.page * SUBJECT_PAGE_SIZE).map(({row}) => subjectSummary(row)) };
    },
    detail(code: unknown) {
      const row = get(code), descendants = children.get(row.code) ?? [];
      const ancestors: ReturnType<typeof subjectSummary>[] = [];
      const visited = new Set([row.code]);
      let next = row.navigation_parent_code;
      while (next) {
        if (visited.has(next)) throw new Error('Classification parent cycle.');
        visited.add(next);
        const ancestor = get(next); ancestors.unshift(subjectSummary(ancestor)); next = ancestor.navigation_parent_code;
      }
      const decorate = (relation: SubjectReference) => ({ ...relation, from: endpoint(relation.from_uri), to: endpoint(relation.to_uri) });
      const out = outgoing.get(row.uri) ?? [], back = incoming.get(row.uri) ?? [];
      const relatedCollections = [...new Set(out.filter(r => r.target_kind === 'collection').map(r => r.to_uri))].map(uri => {
        const collection = collections.get(uri)!;
        return { ...collection, members: collection.member_uris.map(member => subjectSummary(byUri.get(member)!)) };
      });
      return { ...stats, metadata: index.metadata, subject: row, ancestors, childCount: descendants.length, children: descendants.slice(0, SUBJECT_PAGE_SIZE).map(subjectSummary), outgoing: out.map(decorate), incoming: back.map(decorate), collections: relatedCollections };
    },
  };
}
