import Link from 'next/link';
import { notFound } from 'next/navigation';
import type { Metadata } from 'next';
import { subjectCatalog } from '@/lib/subject-data';
import { SubjectCards, SubjectFooter, SubjectHeader, SubjectSearch, subjectStyles as styles } from '@/components/subject-navigation';

type PageInput = { params: Promise<{ code: string }> };
type Detail = ReturnType<typeof subjectCatalog.detail>;
type Reference = Detail['outgoing'][number];
export async function generateMetadata({ params }: PageInput): Promise<Metadata> {
  try { const { code } = await params; const subject = subjectCatalog.detail(code).subject; return { title: `${subject.code} ${subject.label_as_recorded} — Mathematics Atlas` }; }
  catch { return { title: 'Subject not found — Mathematics Atlas' }; }
}
function ReferenceRow({ reference }: { reference: Reference }) {
  const relation = reference.predicate_uri.split('#').at(-1);
  const label = relation === 'seeAlso' ? 'See also' : relation === 'seeMainly' ? 'See mainly' : 'Conditional cross-reference';
  const endpoint = (item: Reference['from']) => item.kind === 'subject'
    ? <Link href={`/subjects/${item.code}`}>{item.code} · {item.label}</Link>
    : <a href={`#collection-${item.uri.split('/').at(-1)}`}>{item.label}</a>;
  return <article className={styles.reference}>
    <h3>{label}</h3><p>{endpoint(reference.from)} → {endpoint(reference.to)}</p>
    {reference.scope_records.map(record => <div className={styles.condition} key={record.uri}>{record.scopes.map((scope, index) => <p key={index}>{scope.value}</p>)}</div>)}
    <details><summary>Source reference and conditions</summary><pre>{JSON.stringify({ from: reference.from_uri, relation: reference.predicate_uri, to: reference.to_uri, scope_records: reference.scope_records }, null, 2)}</pre></details>
  </article>;
}
export default async function SubjectPage({ params }: PageInput) {
  const { code } = await params;
  let detail: Detail;
  try { detail = subjectCatalog.detail(code); } catch { notFound(); }
  const row = detail.subject;
  return <main className={styles.page}>
    <SubjectHeader />
    <nav className={styles.breadcrumbs} aria-label="Subject hierarchy"><Link href="/subjects">All major subjects</Link>{detail.ancestors.map(ancestor => <Link key={ancestor.code} href={`/subjects/${ancestor.code}`}>{ancestor.code} · {ancestor.label}</Link>)}</nav>
    <span className={styles.code}>{row.code} · MSC2020 classification</span><h1>{row.label_as_recorded}</h1>
    <p>{row.description_as_recorded}</p>
    <p className={styles.scope}>A category for organizing mathematical literature. The references below are subject links from the source; they do not establish equivalent problems or interchangeable solutions.</p>
    <SubjectSearch />
    <section aria-label="More specific subjects"><h2>Within this subject</h2>
      {detail.childCount ? <><SubjectCards records={detail.children} />{detail.childCount > detail.children.length && <Link href={`/subjects?parent=${row.code}`}>Browse all {detail.childCount} categories within this subject →</Link>}</> : <p>This is a leaf category in this classification. More detailed knowledge may exist within it.</p>}
    </section>
    <section aria-label="Outgoing source cross-references"><h2>Related subjects from this entry</h2>
      {detail.outgoing.length ? detail.outgoing.map(reference => <ReferenceRow key={`${reference.predicate_uri}|${reference.to_uri}`} reference={reference} />) : <p>No outgoing cross-reference is recorded in this source snapshot.</p>}
    </section>
    {detail.incoming.length > 0 && <section aria-label="Incoming source cross-references"><h2>Other entries pointing here</h2><p className={styles.scope}>Each arrow keeps the direction and condition recorded by the source.</p>{detail.incoming.map(reference => <ReferenceRow key={`${reference.from_uri}|${reference.predicate_uri}`} reference={reference} />)}</section>}
    {detail.collections.map(collection => <section key={collection.uri} id={`collection-${collection.uri.split('/').at(-1)}`} aria-label="Referenced classification collection"><h2>{collection.labels.find(label => label.language === 'en')?.value ?? 'Classification collection'}</h2><p>{collection.members.length} categories grouped by the source. Membership is distinct from a direct subject cross-reference.</p><SubjectCards records={collection.members} /></section>)}
    <section aria-label="Classification sources"><h2>Sources and recorded differences</h2>
      <p><a href={`https://mathscinet.ams.org/msc/msc2020.html?btn=Current&t=${encodeURIComponent(row.code)}`}>Browse {row.code} at MathSciNet</a> · <a href={`/api/subjects?code=${encodeURIComponent(row.code)}`}>Complete subject record</a></p>
      {row.hierarchy_disagreement && <p>The linked-data source records additional parents for this entry. Navigation follows the classification-code hierarchy; the original parent records are retained below.</p>}
      {row.exact_label_difference && <p>The official download and linked-data snapshot use different label text. This page uses the official download; both versions are retained below.</p>}
      <details><summary>Original labels, parent records and scope notes</summary><pre>{JSON.stringify({ official_label: row.label_as_recorded, official_description: row.description_as_recorded, official_source_locator: row.source_locator, rdf_labels: row.rdf_labels, navigation_parent_code: row.navigation_parent_code, rdf_broader_uris: row.rdf_broader_uris, rdf_scope_notes: row.rdf_scope_notes }, null, 2)}</pre></details>
    </section>
    <SubjectFooter />
  </main>;
}
