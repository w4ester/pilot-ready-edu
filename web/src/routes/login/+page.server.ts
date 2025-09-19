import type { PageServerLoad } from './$types';
import { apiServer } from '$lib/api.server';
import { redirect } from '@sveltejs/kit';

function sanitizeNext(url: URL, next: string | null): string {
  if (!next) return '/tools';
  try {
    const resolved = new URL(next, url.origin);
    if (resolved.origin !== url.origin) {
      return '/tools';
    }
    return `${resolved.pathname}${resolved.search}` || '/tools';
  } catch {
    return '/tools';
  }
}

export const load: PageServerLoad = async (event) => {
  try {
    await apiServer.get(event, '/api/v1/auth/me', { redirectOn401: false });
    throw redirect(302, sanitizeNext(event.url, event.url.searchParams.get('next')));
  } catch {
    return {};
  }
};
