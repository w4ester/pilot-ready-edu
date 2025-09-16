<script lang="ts">
  import { onMount } from 'svelte';
  import { loadMonaco } from '$lib/monaco';

  let head = 'unknown';
  let status = 'loading';
  let error: string | null = null;
  let editorContainer: HTMLDivElement | null = null;

  onMount(async () => {
    const apiBase = import.meta.env.VITE_API_URL ?? 'http://localhost:8000';
    try {
      const response = await fetch(`${apiBase}/health/schema`);
      if (!response.ok) {
        throw new Error(`Unexpected ${response.status}`);
      }
      const payload = await response.json();
      head = payload.head ?? 'unknown';
      status = payload.status ?? 'ok';
    } catch (err) {
      error = err instanceof Error ? err.message : 'Unknown error';
      status = 'error';
    }

    if (editorContainer) {
      const monaco = await loadMonaco();
      monaco.editor.create(editorContainer, {
        value: `-- Welcome to the EDU AI Platform\nSELECT now();`,
        language: 'sql',
        automaticLayout: true,
        minimap: { enabled: false }
      });
    }
  });
</script>

<main class="page">
  <section class="card">
    <h1>EDU AI Platform</h1>
    <p>API status: <strong>{status}</strong></p>
    <p>Alembic head: <code>{head}</code></p>
    {#if error}
      <p class="error">{error}</p>
    {/if}
  </section>

  <section class="editor" bind:this={editorContainer} aria-label="Monaco editor preview"></section>
</main>

<style>
  .page {
    display: grid;
    gap: 1.5rem;
    padding: 2rem;
    grid-template-columns: repeat(auto-fit, minmax(320px, 1fr));
  }

  .card {
    background: #ffffff;
    border-radius: 12px;
    box-shadow: 0 12px 30px rgba(15, 18, 26, 0.08);
    padding: 2rem;
    display: flex;
    flex-direction: column;
    gap: 0.75rem;
  }

  .card h1 {
    margin: 0;
    font-size: 1.8rem;
  }

  .card code {
    background: rgba(15, 18, 26, 0.06);
    padding: 0.25rem 0.5rem;
    border-radius: 6px;
  }

  .error {
    color: #b00020;
  }

  .editor {
    min-height: 360px;
    border-radius: 12px;
    overflow: hidden;
    box-shadow: inset 0 0 0 1px rgba(15, 18, 26, 0.12);
  }

  :global(body) {
    margin: 0;
    font-family: "Inter", system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
    background: #f5f7fb;
  }
</style>
