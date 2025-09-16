import type * as Monaco from 'monaco-editor';

export async function loadMonaco(): Promise<typeof Monaco> {
  const monaco = await import('monaco-editor');
  return monaco;
}
