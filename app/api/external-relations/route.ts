import { relationApiResponse } from '@/lib/external-relations';
import { exploreExternalRelations } from '@/lib/external-relations-server';

export function GET(request: Request): Response {
  return relationApiResponse(request, exploreExternalRelations);
}
