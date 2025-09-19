// web/src/lib/api.creationstation.ts
import { api } from '$lib/api';

export interface PromptPayload {
  command: string;
  title?: string;
  content: string;
  variables?: Record<string, unknown>;
  access_control?: Record<string, unknown>;
}

export interface PromptSummary {
  id: string;
  command: string;
  title?: string | null;
  content: string;
  updated_at?: number | null;
}

export interface ToolPayload {
  slug: string;
  name: string;
  language?: string;
  entrypoint?: string;
  content: string;
  requirements?: string;
  valves?: Record<string, unknown>;
  meta?: Record<string, unknown>;
  access_control?: Record<string, unknown>;
  sandbox_profile?: string;
  timeout_ms?: number;
  memory_limit_mb?: number;
}

export interface ToolSummary {
  id: string;
  slug: string;
  name: string;
  language: string;
  entrypoint: string;
  is_active: boolean;
  updated_at?: number | null;
  content: string;
  requirements?: string | null;
}

export interface ModelPayload {
  base_model_id: string;
  name: string;
  params?: Record<string, unknown>;
  meta?: Record<string, unknown>;
  access_control?: Record<string, unknown>;
}

export interface ModelSummary {
  id: string;
  name: string;
  base_model_id: string;
  is_active: boolean;
  updated_at?: number | null;
}

export interface LibraryPayload {
  name: string;
  description?: string;
  data?: Record<string, unknown>;
  meta?: Record<string, unknown>;
  access_control?: Record<string, unknown>;
}

export interface LibrarySummary {
  id: string;
  name: string;
  description?: string | null;
  updated_at?: number | null;
  data: Record<string, unknown>;
  meta: Record<string, unknown>;
}

export interface RoomCreatePayload {
  name: string;
  description?: string;
  channel_type?: string;
  data?: Record<string, unknown>;
  meta?: Record<string, unknown>;
  access_control?: Record<string, unknown>;
}

export interface RoomSummary {
  id: string;
  name: string;
  description?: string | null;
  member_count: number;
  is_archived: boolean;
  created_at?: number | null;
  channel_type?: string | null;
  data: Record<string, unknown>;
  meta: Record<string, unknown>;
}

export const creationAPI = {
  prompts: {
    list: () => api.get<PromptSummary[]>('/api/v1/prompts'),
    create: (body: PromptPayload) => api.post<PromptSummary>('/api/v1/prompts', body),
    update: (id: string, body: Partial<PromptPayload>) => api.put<PromptSummary>(`/api/v1/prompts/${id}`, body),
    test: (body: { content: string; variables?: Record<string, unknown> }) =>
      api.post<{ ok: boolean; rendered?: string; error?: string }>('/api/v1/prompts/test', body),
  },
  tools: {
    list: () => api.get<ToolSummary[]>('/api/v1/tools'),
    create: (body: ToolPayload) => api.post<ToolSummary>('/api/v1/tools', body),
    publishVersion: (id: string, body: { content: string; requirements?: string }) =>
      api.post<{ tool_id: string; version: number }>(`/api/v1/tools/${id}/versions`, body),
    testRun: (body: { code: string; input?: Record<string, unknown> }) =>
      api.post<{ ok: boolean; message: string }>('/api/v1/tools/test-run', body),
  },
  models: {
    list: () => api.get<ModelSummary[]>('/api/v1/models'),
    create: (body: ModelPayload) => api.post<ModelSummary>('/api/v1/models', body),
    attachTools: (id: string, toolIds: string[]) =>
      api.post<{ attached: number; missing: string[] }>(`/api/v1/models/${id}/tools`, { tool_ids: toolIds }),
    attachLibraries: (id: string, libraryIds: string[]) =>
      api.post<{ attached: number; missing: string[] }>(`/api/v1/models/${id}/libraries`, { library_ids: libraryIds }),
    exportOllama: (id: string) => api.post<{ modelfile: string }>(`/api/v1/models/${id}/export/ollama`, {}),
  },
  libraries: {
    list: () => api.get<LibrarySummary[]>('/api/v1/libraries'),
    create: (body: LibraryPayload) => api.post<LibrarySummary>('/api/v1/libraries', body),
  },
  rooms: {
    list: () => api.get<RoomSummary[]>('/api/v1/rooms'),
    create: (body: RoomCreatePayload) => api.post<RoomSummary>('/api/v1/rooms', body),
    archive: (roomId: string) => api.post<RoomSummary>(`/api/v1/rooms/${roomId}/archive`, {}),
    restore: (roomId: string) => api.post<RoomSummary>(`/api/v1/rooms/${roomId}/restore`, {}),
  },
};
