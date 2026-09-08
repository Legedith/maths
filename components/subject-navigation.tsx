import Link from 'next/link';
import { subjectCatalog } from '@/lib/subject-data';
import styles from './subject-navigation.module.css';

export { styles as subjectStyles };
export function SubjectHeader() {
  return <header className={styles.header}><Link href="/">← Mathematics Atlas</Link><span>{subjectCatalog.stats.subjects.toLocaleString('en')} subject categories · MSC2020</span></header>;
}
export function SubjectFooter() {
  return <footer className={styles.footer}><p>MSC2020 by Mathematical Reviews and zbMATH. Linked-data conversion by the MSC2020 SKOS contributors. Adapted under <a href="https://creativecommons.org/licenses/by-nc-sa/4.0/">CC BY-NC-SA 4.0</a>.</p><p><a href="https://msc2020.org/">Official classification</a> · <a href="https://github.com/TIBHannover/MSC2020_SKOS/tree/33972ddb6a72c3660a6e499ee5f881b57fa92d41">Linked-data source revision</a> · <a href="https://github.com/Legedith/maths/tree/codex/subject-classification/data/msc">Data and adaptation notes</a></p></footer>;
}
export function SubjectSearch({ query = '' }: { query?: string }) {
  return <form action="/subjects" className={styles.search}><label>Subject name, phrase or MSC code<input type="search" name="q" defaultValue={query} maxLength={300} placeholder="Try algorithms, biology or 68Q25" /></label><input type="hidden" name="parent" value="all" /><button type="submit">Search subjects</button></form>;
}
export function SubjectCards({ records }: { records: { code: string; label: string; kind: string }[] }) {
  return <ul className={styles.cards}>{records.map(record => <li key={record.code}><Link href={`/subjects/${encodeURIComponent(record.code)}`}><span className={styles.code}>{record.code}</span><span>{record.label}</span></Link></li>)}</ul>;
}
