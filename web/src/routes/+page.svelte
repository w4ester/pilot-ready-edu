<script lang="ts">
  import { onMount, onDestroy } from 'svelte';
  import { loadMonaco } from '$lib/monaco';

  let head = 'unknown';
  let status = 'loading';
  let error: string | null = null;
  let editorContainer: HTMLDivElement | null = null;
  let editorInstance: import('monaco-editor').editor.IStandaloneCodeEditor | null = null;

  const artifactSnippets: Record<string, string> = {
    'lesson-plan': `{
  "artifact_type": "lesson_plan",
  "title": "Exploring Ecosystems",
  "grade_level": "8",
  "subject_area": "Science",
  "objectives": [
    "Explain biotic and abiotic factors",
    "Model energy transfer in food webs"
  ],
  "tasks": [
    {
      "type": "interactive",
      "description": "Collaborative ecosystem mapping"
    }
  ]
}`,
    rubric: `{
  "artifact_type": "rubric",
  "title": "Argumentative Essay",
  "scales": [
    {
      "criterion": "Claim & Evidence",
      "levels": [
        {"label": "Exceeds", "description": "Claim is compelling and supported with multiple credible sources."},
        {"label": "Meets", "description": "Claim is clear and supported with at least two relevant sources."}
      ]
    }
  ]
}`
  };

  const loadSnippet = (key: string) => {
    const snippet = artifactSnippets[key];
    if (snippet && editorInstance) {
      editorInstance.setValue(snippet);
      editorInstance.focus();
    }
  };

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
      editorInstance = monaco.editor.create(editorContainer, {
        value: `-- Artifact sandbox\n-- Select a template below to begin drafting.`,
        language: 'json',
        automaticLayout: true,
        minimap: { enabled: false }
      });
    }
  });

  onDestroy(() => {
    editorInstance?.dispose();
    editorInstance = null;
  });
</script>

<main class="page">
  <section class="card">
    <h1>Edinfinite Platform</h1>
    <p>API status: <strong>{status}</strong></p>
    <p>Alembic head: <code>{head}</code></p>
    {#if error}
      <p class="error">{error}</p>
    {/if}
    <div class="actions" aria-label="Artifact sandbox controls">
      <button type="button" on:click={() => loadSnippet('lesson-plan')}>
        Lesson plan template
      </button>
      <button type="button" on:click={() => loadSnippet('rubric')}>
        Rubric template
      </button>
    </div>
    <p class="hint">Templates drop into the Monaco editor so you can iterate before saving as an artifact in the main classroom UI.</p>
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

  .actions {
    display: flex;
    flex-wrap: wrap;
    gap: 0.5rem;
  }

  .actions button {
    border: none;
    border-radius: 8px;
    padding: 0.6rem 1rem;
    background: linear-gradient(135deg, #4a6cf7, #6c8bfa);
    color: #fff;
    cursor: pointer;
    font-weight: 600;
    transition: transform 0.15s ease, box-shadow 0.15s ease;
  }

  .actions button:hover {
    transform: translateY(-1px);
    box-shadow: 0 10px 20px rgba(74, 108, 247, 0.25);
  }

  .hint {
    font-size: 0.9rem;
    color: rgba(15, 18, 26, 0.6);
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
