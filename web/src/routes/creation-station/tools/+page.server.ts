import type { PageServerLoad } from './$types';
import { apiServer } from '$lib/api.server';
import { redirect } from '@sveltejs/kit';

export const load: PageServerLoad = async (event) => {
  const parent = await event.parent();
  if (!parent.user) {
    const next = encodeURIComponent(`${event.url.pathname}${event.url.search}`);
    throw redirect(302, `/login?next=${next}`);
  }

  try {
    const tools = await apiServer.get<any[]>(event, '/api/v1/tools');
    return { tools };
  } catch (error) {
    console.error('Failed to load tools:', error);
    return { tools: [] };
  }
};