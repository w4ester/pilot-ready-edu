<script lang="ts">
  import { onMount } from 'svelte';
  import { tools as toolsAPI, type ToolSummary } from '$lib/api.creationstation';

  const preview = (content: string, limit = 160) =>
    content.length > limit ? `${content.slice(0, limit)}…` : content;

  let tools: ToolSummary[] = [];
  let loading = true;
  let error: string | null = null;
  let deleteError: string | null = null;
  let deletingSlug: string | null = null;
  let searchQuery = '';

  $: filteredTools = tools.filter(tool =>
    tool.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
    tool.slug.toLowerCase().includes(searchQuery.toLowerCase())
  );
  
  async function loadTools() {
    try {
      const result = await toolsAPI.list();
      tools = result;
      error = null;
    } catch (err) {
      error = err instanceof Error ? err.message : 'Failed to load tools';
    }
  }

  onMount(() => {
    void (async () => {
      await loadTools();
      loading = false;
    })();
  });
  
</script>

<svelte:head>
  <title>Tools · Creation Station · Edinfinite</title>
</svelte:head>

<main class="tools-page">
  <div class="page-container">
    <header class="page-header">
      <div class="header-top">
        <a href="/creation-station" class="back-link">
          <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
            <path d="M19 12H5M12 19l-7-7 7-7"/>
          </svg>
          Back to Creation Station
        </a>
      </div>
      
      <div class="header-main">
        <div class="header-content">
          <h1>🧰 Tools</h1>
          <p class="header-description">Build Python functions to extend AI capabilities with custom logic and integrations.</p>
        </div>
        
        <a href="/creation-station/tools/new" class="btn-create">
          <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <line x1="12" y1="5" x2="12" y2="19"></line>
            <line x1="5" y1="12" x2="19" y2="12"></line>
          </svg>
          New Tool
        </a>
      </div>
    </header>

    <div class="search-bar">
      <svg class="search-icon" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
        <circle cx="11" cy="11" r="8"></circle>
        <path d="m21 21-4.35-4.35"></path>
      </svg>
      <input
        type="text"
        bind:value={searchQuery}
        placeholder="Search tools..."
        class="search-input"
      />
    </div>

    {#if deleteError}
      <div class="inline-error" role="alert">
        <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <circle cx="12" cy="12" r="10"></circle>
          <line x1="12" y1="8" x2="12" y2="12"></line>
          <line x1="12" y1="16" x2="12.01" y2="16"></line>
        </svg>
        <span>{deleteError}</span>
      </div>
    {/if}

    {#if loading}
      <div class="loading-state">
        <div class="spinner"></div>
        <p>Loading tools...</p>
      </div>
    {:else if error}
      <div class="error-state">
        <svg width="48" height="48" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <circle cx="12" cy="12" r="10"></circle>
          <line x1="12" y1="8" x2="12" y2="12"></line>
          <line x1="12" y1="16" x2="12.01" y2="16"></line>
        </svg>
        <p>{error}</p>
      </div>
    {:else if filteredTools.length === 0}
      <div class="empty-state">
        <svg width="48" height="48" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <path d="M14.7 6.3a1 1 0 0 0 0 1.4l1.6 1.6a1 1 0 0 0 1.4 0l3.77-3.77a6 6 0 0 1-7.94 7.94l-6.91 6.91a2.12 2.12 0 0 1-3-3l6.91-6.91a6 6 0 0 1 7.94-7.94l-3.76 3.76z"/>
        </svg>
        <h3>{searchQuery ? 'No tools found' : 'No tools yet'}</h3>
        <p>{searchQuery ? 'Try adjusting your search' : 'Create your first tool to get started'}</p>
        {#if !searchQuery}
          <a href="/creation-station/tools/new" class="btn-primary">Create Tool</a>
        {/if}
      </div>
    {:else}
      <div class="tools-grid">
        {#each filteredTools as tool}
          <div class="tool-card">
            <div class="tool-header">
              <h3 class="tool-name">{tool.name}</h3>
              <span class="tool-language">{tool.language}</span>
            </div>
            
            <p class="tool-slug">{tool.slug}</p>
            
            <div class="tool-meta">
              <span class="meta-item">
                <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                  <path d="M13 2L3 14l9 9L22 13z"/>
                  <path d="M3 14l3 3"/>
                </svg>
                {tool.entrypoint}
              </span>
              {#if tool.requirements}
                <span class="meta-item">
                  <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                    <rect x="3" y="11" width="18" height="10" rx="2" ry="2"/>
                    <path d="M7 11V7a5 5 0 0 1 10 0v4"/>
                  </svg>
                  Dependencies
                </span>
              {/if}
            </div>

            <p class="tool-preview">{preview(tool.content)}</p>

            <div class="tool-actions">
              <a href="/creation-station/tools/{tool.slug}/edit" class="btn-edit">
                <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                  <path d="M11 4H4a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2v-7"/>
                  <path d="M18.5 2.5a2.121 2.121 0 0 1 3 3L12 15l-4 1 1-4 9.5-9.5z"/>
                </svg>
                Edit
              </a>

            </div>
          </div>
        {/each}
      </div>
    {/if}
  </div>
</main>

<style>
  .tools-page {
    min-height: 100vh;
    background: linear-gradient(135deg, #0f0f23 0%, #1a0f2e 50%, #0f0f23 100%);
    padding: 2rem;
  }

  .page-container {
    max-width: 1200px;
    margin: 0 auto;
  }

  .page-header {
    margin-bottom: 2rem;
  }

  .header-top {
    margin-bottom: 1.5rem;
  }

  .back-link {
    display: inline-flex;
    align-items: center;
    gap: 0.5rem;
    color: #a78bfa;
    text-decoration: none;
    font-size: 0.875rem;
    transition: color 0.2s;
  }

  .back-link:hover {
    color: #c4b5fd;
  }

  .header-main {
    display: flex;
    justify-content: space-between;
    align-items: flex-start;
    gap: 2rem;
  }

  .header-content h1 {
    margin: 0;
    font-size: 2.5rem;
    font-weight: bold;
    color: white;
  }

  .header-description {
    margin: 0.5rem 0 0;
    color: #9ca3af;
    font-size: 1rem;
  }

  .btn-create {
    display: inline-flex;
    align-items: center;
    gap: 0.5rem;
    padding: 0.75rem 1.5rem;
    background: #7c3aed;
    color: white;
    border-radius: 0.5rem;
    text-decoration: none;
    font-weight: 600;
    transition: all 0.2s;
  }

  .btn-create:hover {
    background: #6d28d9;
    transform: translateY(-1px);
    box-shadow: 0 10px 20px rgba(124, 58, 237, 0.3);
  }

  .search-bar {
    position: relative;
    margin-bottom: 2rem;
  }

  .search-icon {
    position: absolute;
    left: 1rem;
    top: 50%;
    transform: translateY(-50%);
    color: #6b7280;
  }

  .search-input {
    width: 100%;
    padding: 0.75rem 1rem 0.75rem 3rem;
    background: rgba(31, 41, 55, 0.5);
    border: 1px solid rgba(75, 85, 99, 0.3);
    border-radius: 0.5rem;
    color: white;
    font-size: 0.9375rem;
    transition: all 0.2s;
  }

  .search-input::placeholder {
    color: #6b7280;
  }

  .search-input:focus {
    outline: none;
    border-color: rgba(139, 92, 246, 0.5);
    background: rgba(31, 41, 55, 0.7);
  }

  .inline-error {
    display: flex;
    align-items: center;
    gap: 0.5rem;
    margin: 1rem 0 2rem;
    padding: 0.75rem 1rem;
    border-radius: 0.75rem;
    background: rgba(239, 68, 68, 0.15);
    border: 1px solid rgba(239, 68, 68, 0.4);
    color: #fecaca;
    font-size: 0.9rem;
  }

  .inline-error svg {
    flex-shrink: 0;
  }

  .loading-state,
  .error-state,
  .empty-state {
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    padding: 4rem 2rem;
    text-align: center;
    color: #9ca3af;
  }

  .spinner {
    width: 3rem;
    height: 3rem;
    border: 3px solid rgba(139, 92, 246, 0.2);
    border-top-color: #8b5cf6;
    border-radius: 50%;
    animation: spin 1s linear infinite;
  }

  @keyframes spin {
    to { transform: rotate(360deg); }
  }

  .empty-state h3 {
    margin: 1rem 0 0.5rem;
    font-size: 1.25rem;
    color: white;
  }

  .empty-state .btn-primary {
    margin-top: 1.5rem;
    padding: 0.75rem 2rem;
    background: #7c3aed;
    color: white;
    border-radius: 0.5rem;
    text-decoration: none;
    font-weight: 600;
    transition: all 0.2s;
  }

  .empty-state .btn-primary:hover {
    background: #6d28d9;
    transform: translateY(-1px);
    box-shadow: 0 10px 20px rgba(124, 58, 237, 0.3);
  }

  .tools-grid {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
    gap: 1.5rem;
  }

  .tool-card {
    background: rgba(17, 24, 39, 0.8);
    border: 1px solid rgba(139, 92, 246, 0.2);
    border-radius: 1rem;
    padding: 1.5rem;
    transition: all 0.2s;
  }

  .tool-card:hover {
    border-color: rgba(139, 92, 246, 0.4);
    transform: translateY(-2px);
    box-shadow: 0 10px 30px rgba(139, 92, 246, 0.15);
  }

  .tool-header {
    display: flex;
    justify-content: space-between;
    align-items: flex-start;
    margin-bottom: 0.5rem;
  }

  .tool-name {
    margin: 0;
    font-size: 1.125rem;
    font-weight: 600;
    color: white;
  }

  .tool-language {
    padding: 0.25rem 0.5rem;
    background: rgba(139, 92, 246, 0.2);
    color: #a78bfa;
    border-radius: 0.25rem;
    font-size: 0.75rem;
    font-weight: 600;
    text-transform: uppercase;
  }

  .tool-slug {
    margin: 0 0 1rem;
    color: #6b7280;
    font-family: 'Monaco', 'Menlo', 'Ubuntu Mono', monospace;
    font-size: 0.875rem;
  }

  .tool-meta {
    display: flex;
    gap: 1rem;
    margin-bottom: 1rem;
    padding-bottom: 1rem;
    border-bottom: 1px solid rgba(75, 85, 99, 0.3);
  }

  .meta-item {
    display: flex;
    align-items: center;
    gap: 0.375rem;
    color: #9ca3af;
    font-size: 0.875rem;
  }

  .tool-preview {
    margin: 1rem 0;
    color: rgba(226, 232, 240, 0.8);
    font-size: 0.875rem;
    line-height: 1.5;
  }

  .tool-actions {
    display: flex;
    gap: 0.5rem;
    align-items: center;
  }

  .btn-edit {
    flex: 0 0 auto;
    display: flex;
    align-items: center;
    justify-content: center;
    gap: 0.375rem;
    padding: 0.5rem;
    border-radius: 0.375rem;
    font-size: 0.875rem;
    font-weight: 500;
    transition: all 0.2s;
    cursor: pointer;
    background: rgba(59, 130, 246, 0.1);
    border: 1px solid rgba(59, 130, 246, 0.3);
    color: #60a5fa;
    text-decoration: none;
  }

  .btn-edit:hover {
    background: rgba(59, 130, 246, 0.2);
    border-color: rgba(59, 130, 246, 0.5);
  }

  .tool-id {
    margin-left: auto;
    font-size: 0.75rem;
    color: rgba(148, 163, 184, 0.9);
  }

  .btn-delete[disabled] {
    opacity: 0.6;
    cursor: not-allowed;
  }

  .btn-delete[disabled]:hover {
    background: rgba(239, 68, 68, 0.1);
    border-color: rgba(239, 68, 68, 0.3);
  }

  @media (max-width: 768px) {
    .header-main {
      flex-direction: column;
    }

    .tools-grid {
      grid-template-columns: 1fr;
    }
  }
</style>
