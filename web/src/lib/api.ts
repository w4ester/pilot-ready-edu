const API_BASE = import.meta.env.VITE_API_URL ?? 'http://localhost:8000';
const DEV_USER_ID = import.meta.env.VITE_DEV_USER_ID;

type Method = 'GET' | 'POST' | 'PATCH';

async function request<T>(method: Method, path: string, body?: unknown): Promise<T> {
  const headers: Record<string, string> = {
    'Content-Type': 'application/json'
  };

  if (DEV_USER_ID) {
    headers['X-Dev-User-Id'] = DEV_USER_ID;
  }

  const response = await fetch(`${API_BASE}${path}`, {
    method,
    headers,
    body: body ? JSON.stringify(body) : undefined
  });

  if (!response.ok) {
    const message = await response.text();
    throw new Error(message || `Request failed with ${response.status}`);
  }

  if (response.status === 204) {
    return undefined as T;
  }

  return (await response.json()) as T;
}

export const api = {
  get: <T>(path: string) => request<T>('GET', path),
  post: <T>(path: string, body?: unknown) => request<T>('POST', path, body),
  patch: <T>(path: string, body?: unknown) => request<T>('PATCH', path, body)
};
