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

export type ChatMessage = {
  role: 'system' | 'user' | 'assistant';
  content: string;
};

export type AssistantResponse = {
  messages: ChatMessage[];
  suggestions: string[];
};

export const creationAPI = {
  prompts: {

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
  rooms: {
    list: () => api.get<RoomSummary[]>('/api/v1/rooms'),
    create: (body: RoomCreatePayload) => api.post<RoomSummary>('/api/v1/rooms', body),
    update: (roomId: string, body: RoomUpdatePayload) => api.patch<RoomSummary>(`/api/v1/rooms/${roomId}`, body),
    archive: (roomId: string) => api.post<RoomSummary>(`/api/v1/rooms/${roomId}/archive`, {}),
    remove: (roomId: string) => api.delete<void>(`/api/v1/rooms/${roomId}`),
    messages: {
      list: (roomId: string, limit = 50) => api.get<RoomMessageOut[]>(`/api/v1/rooms/${roomId}/messages?limit=${limit}`),
      create: (roomId: string, body: RoomMessageIn) =>
        api.post<RoomMessageOut>(`/api/v1/rooms/${roomId}/messages`, body),
    },
  },
};
