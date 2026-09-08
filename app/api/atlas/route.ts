import { atlas } from '@/lib/atlas';
export function GET() {
  return Response.json(atlas, {
    headers: { 'Cache-Control': 'public, max-age=3600' },
  });
}
