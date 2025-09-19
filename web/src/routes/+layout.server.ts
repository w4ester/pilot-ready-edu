import type { LayoutServerLoad } from './$types';
import { apiServer, UnauthorizedError } from '$lib/api.server';
import type { MeResponse } from '$lib/auth';

export const load: LayoutServerLoad = async (event) => {
  try {
    const user = await apiServer.get<MeResponse>(event, '/api/v1/auth/me', {
      redirectOn401: false
    });
    return { user };
  } catch (error) {
    if (error instanceof UnauthorizedError) {
      return { user: null };
    }

    console.error('Failed to resolve current user', error);
    return { user: null };
  }
};
