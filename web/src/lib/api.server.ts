import { redirect, type RequestEvent } from '@sveltejs/kit';

export class UnauthorizedError extends Error {
  constructor(detail?: string) {
    super(detail ?? 'unauthenticated');
    this.name = 'UnauthorizedError';
  }
}

export type ServerMethod = 'GET' | 'POST' | 'PATCH' | 'PUT' | 'DELETE';

const needsCsrf = (method: ServerMethod) => method !== 'GET';

function buildHeaders(event: RequestEvent, method: ServerMethod): Headers {
  const headers = new Headers();

  if (needsCsrf(method)) {
    const csrf = event.cookies.get('csrf');
    if (csrf) {
      headers.set('X-CSRF-Token', csrf);
    }
  }

  if (!headers.has('Accept')) {
    headers.set('Accept', 'application/json');
  }

  return headers;
}

interface RequestOptions {
  body?: unknown;
  redirectOn401?: boolean;
}

export async function requestServer<T>(
  event: RequestEvent,
  method: ServerMethod,
  path: string,
  { body, redirectOn401 = true }: RequestOptions = {}
): Promise<T> {
  const headers = buildHeaders(event, method);
  const payload =
    body === undefined
      ? undefined
      : body instanceof FormData || body instanceof Blob || typeof body === 'string'
      ? body
      : JSON.stringify(body);

  if (payload !== undefined && !headers.has('Content-Type') && !(payload instanceof FormData) && !(payload instanceof Blob)) {
    headers.set('Content-Type', 'application/json');
  }

  // Use relative URL so SvelteKit forwards cookies from the incoming request.
  const response = await event.fetch(path, {
    method,
    credentials: 'include',
    headers,
    body: payload as BodyInit | undefined
  });

  if (response.status === 401) {
    if (redirectOn401) {
      const next = encodeURIComponent(`${event.url.pathname}${event.url.search}`);
      throw redirect(302, `/login?next=${next}`);
    }
    throw new UnauthorizedError();
  }

  if (!response.ok) {
    if (response.status === 403) {
      throw new Error('CSRF validation failed');
    }

    let detail: string | undefined;
    const contentType = response.headers.get('content-type') ?? '';
    if (contentType.includes('application/json')) {
      try {
        const json = await response.json();
        detail = json?.detail ?? json?.message ?? JSON.stringify(json);
      } catch {
        detail = undefined;
      }
    }
    throw new Error(detail ?? `Request failed with ${response.status}`);
  }

  if (response.status === 204) {
    return undefined as T;
  }

  const contentType = response.headers.get('content-type') ?? '';
  if (contentType.includes('application/json')) {
    return (await response.json()) as T;
  }

  return undefined as T;
}

export const apiServer = {
  get: <T>(event: RequestEvent, path: string, options?: RequestOptions) =>
    requestServer<T>(event, 'GET', path, options),
  post: <T>(event: RequestEvent, path: string, body?: unknown, options?: RequestOptions) =>
    requestServer<T>(event, 'POST', path, { body, ...(options ?? {}) }),
  patch: <T>(event: RequestEvent, path: string, body?: unknown, options?: RequestOptions) =>
    requestServer<T>(event, 'PATCH', path, { body, ...(options ?? {}) }),
  put: <T>(event: RequestEvent, path: string, body?: unknown, options?: RequestOptions) =>
    requestServer<T>(event, 'PUT', path, { body, ...(options ?? {}) }),
  delete: <T>(event: RequestEvent, path: string, body?: unknown, options?: RequestOptions) =>
    requestServer<T>(event, 'DELETE', path, { body, ...(options ?? {}) })
};
