import Link from 'next/link';
import type { Metadata } from 'next';
import { subjectCatalog } from '@/lib/subject-data';
import { SubjectCards, SubjectFooter, SubjectHeader, SubjectSearch, subjectStyles as styles } from '@/components/subject-navigation';

export const metadata: Metadata = { title: 'Browse mathematical subjects — Mathematics Atlas', description: 'Explore the MSC2020 subject classification and its recorded cross-references.' };
type Params = Record<string, string | string[] | undefined>;
export default async function SubjectsPage({ searchParams }: { searchParams: Promise<Params> }) {
  const params = await searchParams;
  let result: ReturnType<typeof subjectCatalog.search> | null = null, error = '';
  try {
    if (Object.keys(params).some(key => !['q', 'parent', 'page'].includes(key)) || Object.values(params).some(value => Array.isArray(value))) throw new Error('Use one query, parent and page value.');
    const page = params.page ?? '1';
    if (typeof page !== 'string' || !/^[1-9][0-9]{0,6}$/.test(page)) throw new Error('Use a positive page number.');
    result = subjectCatalog.search({ query: params.q ?? '', parent: params.parent, page: Number(page) });
  } catch (cause) { error = cause instanceof Error ? cause.message : 'The subject search could not be completed.'; }
  const pageUrl = (page: number) => `/subjects?${new URLSearchParams({ q: result!.query, parent: result!.parent, page: String(page) })}`;
  const parent = result && !['root', 'all'].includes(result.parent) ? subjectCatalog.detail(result.parent).subject : null;
  return <main className={styles.page}>
    <SubjectHeader />
    <h1>Browse mathematical subjects</h1>
    <p className={styles.scope}>Explore the subject index used to organize mathematical literature. Categories and cross-references help you navigate; they do not describe everything known about a subject.</p>
    <SubjectSearch query={result?.query ?? ''} />
    <nav className={styles.shortcuts} aria-label="Starting subjects">
      <Link href="/subjects">All major subjects</Link><Link href="/subjects/68-XX">Computer science</Link><Link href="/subjects/81-XX">Quantum theory</Link><Link href="/subjects/91-XX">Economics and game theory</Link><Link href="/subjects/92-XX">Biology and natural sciences</Link>
    </nav>
    {error && <p role="alert">{error} <Link href="/subjects">Return to major subjects.</Link></p>}
    {result && <section aria-label="Subject results">
      <h2>{parent ? <>Within <Link href={`/subjects/${parent.code}`}>{parent.label_as_recorded}</Link></> : result.parent === 'root' ? 'Major subjects' : 'Search results'}</h2>
      <p>{result.total.toLocaleString('en')} categories{result.query ? ` matching “${result.query}”` : ''}</p>
      {result.records.length ? <SubjectCards records={result.records} /> : <p>No categories on this page. Try another phrase or return to the first page. A missing result does not establish that a topic is undiscovered.</p>}
      <nav className={styles.pagination} aria-label="Subject result pages">
        <span>{result.page > 1 && <Link href={pageUrl(result.page - 1)}>← Previous</Link>}</span><span>Page {result.page} of {Math.max(1, result.pages)}</span><span>{result.page < result.pages && <Link href={pageUrl(result.page + 1)}>Next →</Link>}</span>
        {result.page > 1 && <Link href={pageUrl(1)}>First page</Link>}
      </nav>
    </section>}
    <SubjectFooter />
  </main>;
}
