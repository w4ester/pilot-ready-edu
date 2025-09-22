<script lang="ts">
  import { onMount } from 'svelte';
  import { tools as toolsAPI } from '$lib/api.creationstation';

  let tools: Array<{ id: string; name: string; slug: string; language: string }> = [];
  let status: 'loading' | 'ready' | 'error' = 'loading';
  let error: string | null = null;

  onMount(async () => {
    try {
      const data = await toolsAPI.list();
      tools = data ?? [];
      status = 'ready';
    } catch (err) {
      error = err instanceof Error ? err.message : 'Failed to load tools';
      status = 'error';
    }
  });
</script>

<main class="tools">
  <header>
    <h1>Tools</h1>
    <a class="btn" href="/tools/new">New Tool</a>
  </header>

  {#if status === 'loading'}
    <p>Loading tools…</p>
  {:else if status === 'error'}
    <p class="error">{error}</p>
  {:else if !tools.length}
    <p>No tools yet. Create one to get started.</p>
  {:else}
    <ul>
      {#each tools as tool}
        <li>
          <h2>{tool.name}</h2>
          <p class="meta">Slug: {tool.slug} · Language: {tool.language}</p>
        </li>
      {/each}
    </ul>
  {/if}
</main>

<style>
  .tools {
    padding: 2rem;
    max-width: 720px;
    margin: 0 auto;
    display: flex;
    flex-direction: column;
    gap: 1.5rem;
  }

  header {
    display: flex;
    justify-content: space-between;
    align-items: center;
  }

  .btn {
    background: #4a6cf7;
    color: #fff;
    padding: 0.6rem 1rem;
    border-radius: 8px;
    text-decoration: none;
    font-weight: 600;
  }

  .error {
    color: #b00020;
  }

  ul {
    list-style: none;
    padding: 0;
    display: grid;
    gap: 1rem;
  }

  li {
    background: #fff;
    border-radius: 12px;
    padding: 1.25rem;
    box-shadow: 0 8px 24px rgba(15, 18, 26, 0.08);
  }

  .meta {
    color: rgba(15, 18, 26, 0.6);
    font-size: 0.9rem;
  }
</style>
