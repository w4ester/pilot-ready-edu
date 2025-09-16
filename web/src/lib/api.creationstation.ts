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
  specs?: any;
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
};
