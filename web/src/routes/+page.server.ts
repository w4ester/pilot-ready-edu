import type { PageServerLoad } from './$types';
import { apiServer, UnauthorizedError } from '$lib/api.server';
import { redirect } from '@sveltejs/kit';

export const load: PageServerLoad = async (event) => {
  try {
    await apiServer.get(event, '/api/v1/auth/me');
    throw redirect(302, '/creation-station');
  } catch (error) {
    if (error instanceof UnauthorizedError) {
      return {};
    }
    throw error;
  }
};
