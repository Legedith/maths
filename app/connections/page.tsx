import type { Metadata } from 'next';
import { exploreExternalRelations } from '@/lib/external-relations-server';
import { ExternalConnections } from '@/components/external-connections';

export const metadata: Metadata = {
  title: 'Explore connections — Mathematics Atlas',
  description: 'Follow typed connections between mathematical concepts, with original sources and conditions attached.',
};
export default function ConnectionsPage() {
  return <ExternalConnections initial={exploreExternalRelations({ qid: 'Q8366' })} />;
}
