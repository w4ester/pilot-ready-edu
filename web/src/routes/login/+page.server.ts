import type { PageServerLoad } from './$types';
import { apiServer } from '$lib/api.server';
import { redirect } from '@sveltejs/kit';

export const load: PageServerLoad = async (event) => {
  try {
    await apiServer.get(event, '/api/v1/auth/me', { redirectOn401: false });
    const next = event.url.searchParams.get('next') ?? '/tools';
    throw redirect(302, next);
  } catch {
    return {};
  }
};
