import { redirect, type Actions, type PageServerLoad } from '@sveltejs/kit';
import { apiServer, UnauthorizedError } from '$lib/api.server';

export const actions: Actions = {
  default: async (event) => {
    try {
      await apiServer.post<void>(event, '/api/v1/auth/logout', undefined, {
        redirectOn401: false
      });
    } catch (error) {
      if (!(error instanceof UnauthorizedError)) {
        console.error('Logout failed', error);
      }
    }

    throw redirect(303, '/login');
  }
};

export const load: PageServerLoad = async () => {
  throw redirect(302, '/');
};
