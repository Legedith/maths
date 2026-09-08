export type ResourceLink = {
  source: string;
  name_as_recorded: string;
  url: string;
};
export type ConceptRecord = {
  record_key: string;
  label_as_recorded: string;
  identity_candidate: {
    id: string;
    qid: string;
    uri: string;
    status: 'unreviewed';
  };
  asserted_by: 'MathGloss';
  mapping_status: 'unreviewed';
  links: ResourceLink[];
  source_locator: {
    repository: string;
    commit: string;
    csv_path: string;
    logical_data_record: number;
    physical_lines: { start: number; end: number };
  };
};
export type ConceptIndex = { records: ConceptRecord[] };
export type LibraryQuery = { query: string; resource: string; page: number };
export type LibraryResult = LibraryQuery & {
  records: ConceptRecord[];
  total: number;
  pageSize: number;
  pages: number;
  catalogRecords: number;
  catalogLinks: number;
  resources: string[];
};
export const LIBRARY_PAGE_SIZE = 20;

export function validateLibraryQuery(value: unknown): LibraryQuery {
  if (!value || typeof value !== 'object' || Array.isArray(value))
    throw new Error('Search input must be an object.');
  const p = value as Record<string, unknown>;
  if (
    Object.keys(p).some((key) => !['query', 'resource', 'page'].includes(key))
  )
    throw new Error('Unsupported search field.');
  if (typeof p.query !== 'string' || p.query.length > 500)
    throw new Error('Use a search query of at most 500 characters.');
  const resource = p.resource === undefined ? 'All' : p.resource;
  if (
    typeof resource !== 'string' ||
    resource.length === 0 ||
    resource.length > 80
  )
    throw new Error('Choose an available resource.');
  const page = p.page === undefined ? 1 : p.page;
  if (
    typeof page !== 'number' ||
    !Number.isSafeInteger(page) ||
    page < 1 ||
    page > 1000000
  )
    throw new Error('Page must be a positive integer no greater than 1000000.');
  return { query: p.query.trim(), resource, page };
}

const normalize = (value: string) =>
  value
    .normalize('NFKC')
    .toLowerCase()
    .replace(/[^\p{L}\p{N}]+/gu, ' ')
    .trim();

export function searchConceptLibrary(
  index: ConceptIndex,
  input: unknown,
): LibraryResult {
  const request = validateLibraryQuery(input);
  const resources = [
    ...new Set(
      index.records.flatMap((record) =>
        record.links.map((link) => link.source),
      ),
    ),
  ].sort();
  if (request.resource !== 'All' && !resources.includes(request.resource))
    throw new Error('Choose an available resource.');
  const normalized = normalize(request.query);
  const terms = normalized.split(/\s+/).filter(Boolean);
  const matches = index.records
    .flatMap((record, position) => {
      const links = record.links.filter(
        (link) =>
          request.resource === 'All' || link.source === request.resource,
      );
      if (request.resource !== 'All' && links.length === 0) return [];
      const label = normalize(record.label_as_recorded);
      const names = normalize(
        [
          record.label_as_recorded,
          record.identity_candidate.qid,
          ...links.map((link) => link.name_as_recorded),
        ].join(' '),
      );
      if (!terms.every((term) => names.includes(term))) return [];
      const score =
        normalized && label === normalized
          ? 2
          : normalized && label.startsWith(normalized)
            ? 1
            : 0;
      return [{ record, position, score }];
    })
    .sort((a, b) => b.score - a.score || a.position - b.position);
  const start = (request.page - 1) * LIBRARY_PAGE_SIZE;
  return {
    ...request,
    records: matches
      .slice(start, start + LIBRARY_PAGE_SIZE)
      .map((item) => item.record),
    total: matches.length,
    pageSize: LIBRARY_PAGE_SIZE,
    pages: Math.ceil(matches.length / LIBRARY_PAGE_SIZE),
    catalogRecords: index.records.length,
    catalogLinks: index.records.reduce(
      (sum, record) => sum + record.links.length,
      0,
    ),
    resources,
  };
}

export function conceptSourceUrl(record: ConceptRecord): string {
  const locator = record.source_locator;
  return `${locator.repository}/blob/${locator.commit}/${locator.csv_path}#L${String(locator.physical_lines.start)}-L${String(locator.physical_lines.end)}`;
}
