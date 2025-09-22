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
  updated_at?: string | number | null;
}

export type PromptUpdatePayload = Partial<PromptPayload>;

type PromptResponse = {
  id: string;
  command: string;
  title?: string | null;
  content: string;
  updated_at?: string | number | null;
};

const mapPromptSummary = (prompt: PromptResponse): PromptSummary => ({
  id: prompt.id,
  command: prompt.command,
  title: prompt.title ?? undefined,
  content: prompt.content,
  updated_at: prompt.updated_at ?? undefined,
});

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
  updated_at?: string | number | null;
  content: string;
  requirements?: string | null;
}

export type ToolUpdatePayload = Partial<ToolPayload>;

type ToolResponse = {
  id: string;
  slug: string;
  name: string;
  language?: string | null;
  entrypoint?: string | null;
  is_active?: boolean | null;
  updated_at?: string | number | null;
  content: string;
  requirements?: string | null;
};

const mapToolSummary = (tool: ToolResponse): ToolSummary => ({
  id: tool.id,
  slug: tool.slug,
  name: tool.name,
  language: tool.language ?? 'python',
  entrypoint: tool.entrypoint ?? 'run',
  is_active: tool.is_active ?? true,
  updated_at: tool.updated_at ?? undefined,
  content: tool.content,
  requirements: tool.requirements ?? undefined,
});

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

export type RoomUpdatePayload = Partial<Omit<RoomCreatePayload, 'member_ids'>>;

export interface RoomMessageIn {
  content: string;
  parent_id?: string | null;
  target_user_id?: string | null;
  data?: Record<string, unknown>;
  meta?: Record<string, unknown>;
}

export interface RoomMessageOut {
  id: string;
  user_id: string;
  class_room_id: string;
  content: string;
  created_at?: number | null;
  parent_id?: string | null;
}

export type ChatMessage = {
  role: 'system' | 'user' | 'assistant';
  content: string;
};

export type AssistantResponse = {
  messages: ChatMessage[];
  suggestions: string[];
};

export const prompts = {
  list: async (): Promise<PromptSummary[]> => {
    const response = await api.get<PromptResponse[]>('/api/v1/prompts');
    return response.map(mapPromptSummary);
  },
  get: async (promptId: string): Promise<PromptSummary> => {
    const response = await api.get<PromptResponse>(`/api/v1/prompts/${promptId}`);
    return mapPromptSummary(response);
  },
  create: async (body: PromptPayload): Promise<PromptSummary> => {
    const response = await api.post<PromptResponse>('/api/v1/prompts', body);
    return mapPromptSummary(response);
  },
  update: async (
    promptId: string,
    body: PromptUpdatePayload,
  ): Promise<PromptSummary> => {
    const response = await api.patch<PromptResponse>(`/api/v1/prompts/${promptId}`, body);
    return mapPromptSummary(response);
  },
  remove: (promptId: string) => api.delete<void>(`/api/v1/prompts/${promptId}`),
};

export const tools = {
  list: async (): Promise<ToolSummary[]> => {
    const response = await api.get<ToolResponse[]>('/api/v1/tools');
    return response.map(mapToolSummary);
  },
  get: async (toolId: string): Promise<ToolSummary> => {
    const response = await api.get<ToolResponse>(`/api/v1/tools/${toolId}`);
    return mapToolSummary(response);
  },
  create: async (body: ToolPayload): Promise<ToolSummary> => {
    const response = await api.post<ToolResponse>('/api/v1/tools', body);
    return mapToolSummary(response);
  },
  update: async (toolId: string, body: ToolUpdatePayload): Promise<ToolSummary> => {
    const response = await api.patch<ToolResponse>(`/api/v1/tools/${toolId}`, body);
    return mapToolSummary(response);
  },
  remove: (toolId: string) => api.delete<void>(`/api/v1/tools/${toolId}`),
};

export const creationAPI = {
  prompts,
  tools,
  libraries: {
    list: () => api.get<LibrarySummary[]>('/api/v1/libraries'),
    create: (body: LibraryPayload) => api.post<LibrarySummary>('/api/v1/libraries', body),
  },
  rooms: {
    list: () => api.get<RoomSummary[]>('/api/v1/rooms'),
    create: (body: RoomCreatePayload) => api.post<RoomSummary>('/api/v1/rooms', body),
<
    archive: (roomId: string) => api.post<RoomSummary>(`/api/v1/rooms/${roomId}/archive`, {}),
    restore: (roomId: string) => api.post<RoomSummary>(`/api/v1/rooms/${roomId}/restore`, {}),
    remove: (roomId: string) => api.delete<void>(`/api/v1/rooms/${roomId}`),
    messages: {
      list: (roomId: string, limit = 50) =>
        api.get<RoomMessageOut[]>(`/api/v1/rooms/${roomId}/messages?limit=${limit}`),
      create: (roomId: string, body: RoomMessageIn) =>
        api.post<RoomMessageOut>(`/api/v1/rooms/${roomId}/messages`, body),
    },
  },
};
