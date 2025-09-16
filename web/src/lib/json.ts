// web/src/lib/json.ts
export function safeParseJSON(text: string): any | undefined {
  try { return JSON.parse(text); } catch { return undefined; }
}
export function prettyJSON(obj: any): string {
  try { return JSON.stringify(obj ?? {}, null, 2); } catch { return '{}'; }
}
