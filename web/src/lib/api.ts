import { browser } from '$app/environment';
import { goto } from '$app/navigation';

export const API_BASE = import.meta.env.VITE_API_URL ?? '';
const DEV_USER_ID = import.meta.env.VITE_DEV_USER_ID;
const IS_DEV = import.meta.env.DEV;

type Method = 'GET' | 'POST' | 'PATCH' | 'PUT' | 'DELETE';

const needsCsrf = (method: Method) => method !== 'GET';

function readCsrfCookie(): string | undefined {
  if (!browser) return undefined;
  const cookie = document.cookie.split('; ').find((chunk) => chunk.startsWith('csrf='));
  return cookie?.split('=')[1];
}

function buildHeaders(method: Method, body?: unknown): Headers {
  const headers = new Headers();

  const shouldSetJson =
    body !== undefined &&
    !(body instanceof FormData) &&
    !(body instanceof Blob) &&
    typeof body !== 'string';

  if (shouldSetJson && !headers.has('Content-Type')) {
    headers.set('Content-Type', 'application/json');
  }

  if (IS_DEV && DEV_USER_ID) {
    headers.set('X-Dev-User-Id', DEV_USER_ID);
  }

  if (!headers.has('Accept')) {
    headers.set('Accept', 'application/json');
  }

  if (needsCsrf(method)) {
    const csrf = readCsrfCookie();
    if (csrf) {
      headers.set('X-CSRF-Token', csrf);
    }
  }

  return headers;
}

async function parseError(response: Response): Promise<Error & { status?: number; detail?: string }> {
  const contentType = response.headers.get('content-type') ?? '';
  let detail: string | undefined;

  if (contentType.includes('application/json')) {
    try {
      const payload = await response.json();
      detail = payload?.detail ?? payload?.message ?? JSON.stringify(payload);
    } catch {
      detail = undefined;
    }
  }

  if (!detail) {
    try {
      const text = await response.text();
      detail = text.trim() || undefined;
    } catch {
      detail = undefined;
    }
  }

  const error = new Error(detail ?? `Request failed with ${response.status}`) as Error & {
    status?: number;
    detail?: string;
  };
  error.status = response.status;
  error.detail = detail;
  return error;
}

function currentPath(): string {
  if (!browser) {
    return '/';
  }
  const url = new URL(window.location.href);
  return `${url.pathname}${url.search}`;
}

function redirectToLogin() {
  if (!browser) return;
  const next = encodeURIComponent(currentPath());
  if (window.location.pathname.startsWith('/login')) {
    return;
  }
  void goto(`/login?next=${next}`);
}

async function request<T>(method: Method, path: string, body?: unknown): Promise<T> {
  const response = await fetch(`${API_BASE}${path}`, {
    method,
    credentials: 'include',
    headers: buildHeaders(method, body),
    body:
      body === undefined
        ? undefined
        : body instanceof FormData || body instanceof Blob || typeof body === 'string'
        ? body
        : JSON.stringify(body)
  });

  if (!response.ok) {
    const error = await parseError(response);
    if (error.status === 401) {
      redirectToLogin();
    } else if (error.status === 403 && (error.detail ?? '').toLowerCase().includes('csrf')) {
      error.message = 'Your session expired. Refresh the page and try again.';
    }
    throw error;
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

export const api = {
  get: <T>(path: string) => request<T>('GET', path),
  post: <T>(path: string, body?: unknown) => request<T>('POST', path, body),
  patch: <T>(path: string, body?: unknown) => request<T>('PATCH', path, body),
  put: <T>(path: string, body?: unknown) => request<T>('PUT', path, body),
  delete: <T>(path: string, body?: unknown) => request<T>('DELETE', path, body)
};
