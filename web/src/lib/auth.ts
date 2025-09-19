import { API_BASE, api } from '$lib/api';

export class AuthError extends Error {
  status?: number;
  detail?: string;
}

export type LoginResponse = {
  user_id: string;
  email: string;
  requires_password_change: boolean;
};

export type MeResponse = {
  user_id: string;
  email: string | null;
  auth_method: string;
  requires_password_change: boolean;
};

async function login(email: string, password: string): Promise<LoginResponse> {
  const response = await fetch(`${API_BASE}/api/v1/auth/login`, {
    method: 'POST',
    credentials: 'include',
    headers: {
      'Content-Type': 'application/json',
      Accept: 'application/json'
    },
    body: JSON.stringify({ email: email.trim(), password })
  });

  if (!response.ok) {
    const error = new AuthError();
    error.status = response.status;

    const contentType = response.headers.get('content-type') ?? '';
    if (contentType.includes('application/json')) {
      try {
        const payload = await response.json();
        const detail = payload?.detail ?? payload?.message;
        error.detail = detail ? String(detail) : undefined;
      } catch {
        error.detail = undefined;
      }
    }

    if (!error.detail) {
      try {
        const text = await response.text();
        error.detail = text.trim() || undefined;
      } catch {
        error.detail = undefined;
      }
    }

    if (!error.detail) {
      error.detail = response.statusText || undefined;
    }

    error.message = error.detail ?? 'Invalid credentials';
    throw error;
  }

  return (await response.json()) as LoginResponse;
}

async function logout(): Promise<void> {
  await api.post<void>('/api/v1/auth/logout');
}

async function me(): Promise<MeResponse> {
  return api.get<MeResponse>('/api/v1/auth/me');
}

export const authAPI = {
  login,
  logout,
  me
};
