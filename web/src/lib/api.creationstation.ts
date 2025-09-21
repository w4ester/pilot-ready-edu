// web/src/lib/api.creationstation.ts
import { api } from '$lib/api';

export type PromptPayload = { command: string; title: string; content: string; access_control?: any };
export type ToolPayload = {
  slug: string;
  name: string;
  language?: string;
  entrypoint?: string;
  content: string;
  requirements?: string;
  valves?: any;
  meta?: any;
  access_control?: any;
  sandbox_profile?: string;
  timeout_ms?: number;
  memory_limit_mb?: number;
};

export type ModelPayload = {
  base_model_id: string;
  name: string;
  params?: any;
  meta?: any;
  access_control?: any;
};

export type RoomSummary = {
  id: string;
  name: string;
  description?: string | null;
  member_count: number;
  is_archived: boolean;
  created_at?: number | null;
};

export type RoomCreatePayload = {
  name: string;
  description?: string;
  channel_type?: string;
  data?: Record<string, any>;
  meta?: Record<string, any>;
  access_control?: Record<string, any>;
  member_ids?: string[];
};

export type RoomUpdatePayload = Partial<Omit<RoomCreatePayload, 'member_ids'>>;

export type RoomMessageIn = {
  content: string;
  parent_id?: string | null;
  target_user_id?: string | null;
  data?: Record<string, any>;
  meta?: Record<string, any>;
};

export type RoomMessageOut = {
  id: string;
  user_id: string;
  class_room_id: string;
  content: string;
  created_at?: number | null;
  parent_id?: string | null;
};

export const creationAPI = {
  prompts: {
    list: () => api.get<any[]>('/api/v1/prompts'),
    get: (id: string) => api.get<any>(`/api/v1/prompts/${id}`),
    create: (body: PromptPayload) => api.post<any>('/api/v1/prompts', body),
    update: (id: string, body: Partial<PromptPayload>) => api.patch<any>(`/api/v1/prompts/${id}`, body),
    test: (body: { model_id?: string; input: string; prompt_id?: string; prompt_content?: string }) => api.post<any>('/api/v1/prompts/test', body),
  },
  tools: {
    list: () => api.get<any[]>('/api/v1/tools'),
    create: (body: ToolPayload) => api.post<any>('/api/v1/tools', body),
    publishVersion: (id: string, body: { content: string }) => api.post<any>(`/api/v1/tools/${id}/versions`, body),
    testRun: (body: { code: string; input?: any }) => api.post<any>('/api/v1/tools/test-run', body),
    delete: (slug: string) => api.delete<{ slug: string; status: string }>(`/api/v1/tools/${slug}`),
  },
  models: {
    list: () => api.get<any[]>('/api/v1/models'),
    create: (body: ModelPayload) => api.post<any>('/api/v1/models', body),
    attachTools: (id: string, toolIds: string[]) => api.post<any>(`/api/v1/models/${id}/tools`, { tool_ids: toolIds }),
    attachLibraries: (id: string, libraryIds: string[]) => api.post<any>(`/api/v1/models/${id}/libraries`, { library_ids: libraryIds }),
    exportOllama: (id: string) => api.post<{ modelfile: string }>(`/api/v1/models/${id}/export/ollama`, {}),
  },
  libraries: {
    list: () => api.get<any[]>('/api/v1/libraries'),
  },
  rooms: {
    list: () => api.get<RoomSummary[]>('/api/v1/rooms'),
    create: (body: RoomCreatePayload) => api.post<RoomSummary>('/api/v1/rooms', body),
    update: (roomId: string, body: RoomUpdatePayload) => api.patch<RoomSummary>(`/api/v1/rooms/${roomId}`, body),
    archive: (roomId: string) => api.post<RoomSummary>(`/api/v1/rooms/${roomId}/archive`, {}),
    remove: (roomId: string) => api.delete<void>(`/api/v1/rooms/${roomId}`),
    messages: {
      list: (roomId: string, limit = 50) => api.get<RoomMessageOut[]>(`/api/v1/rooms/${roomId}/messages?limit=${limit}`),
      post: (roomId: string, body: RoomMessageIn) => api.post<RoomMessageOut>(`/api/v1/rooms/${roomId}/messages`, body),
    },
  },
};
