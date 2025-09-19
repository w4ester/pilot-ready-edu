<script lang="ts">
  import { onMount } from 'svelte';
  import { creationAPI } from '$lib/api.creationstation';
  
  interface Prompt {
    slug: string;
    name: string;
    command: string;
    content: string;
    access_level?: string;
    created_at?: string;
    updated_at?: string;
  }
  
  let prompts: Prompt[] = [];
  let loading = true;
  let error: string | null = null;
  let searchQuery = '';
  
  $: filteredPrompts = prompts.filter(prompt => 
    prompt.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
    prompt.command.toLowerCase().includes(searchQuery.toLowerCase()) ||
    prompt.slug.toLowerCase().includes(searchQuery.toLowerCase())
  );
  
  onMount(async () => {
    try {
      prompts = await creationAPI.prompts.list();
    } catch (err) {
      error = err instanceof Error ? err.message : 'Failed to load prompts';
    } finally {
      loading = false;
    }
  });
  
  async function deletePrompt(slug: string) {
    if (!confirm(`Are you sure you want to delete prompt "${slug}"?`)) return;
    
    try {
      await creationAPI.prompts.delete(slug);
      prompts = prompts.filter(p => p.slug !== slug);
    } catch (err) {
      alert(err instanceof Error ? err.message : 'Failed to delete prompt');
    }
  }
</script>

<svelte:head>
  <title>Prompts · Creation Station</title>
</svelte:head>

<main class="prompts-page">
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
          <h1>✏️ Prompts</h1>
          <p class="header-description">Create reusable AI prompts with slash commands for instant access across chats.</p>
        </div>
        
        <a href="/creation-station/prompts/new" class="btn-create">
          <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <line x1="12" y1="5" x2="12" y2="19"></line>
            <line x1="5" y1="12" x2="19" y2="12"></line>
          </svg>
          New Prompt
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
        placeholder="Search prompts..."
        class="search-input"
      />
    </div>

    {#if loading}
      <div class="loading-state">
        <div class="spinner"></div>
        <p>Loading prompts...</p>
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
    {:else if filteredPrompts.length === 0}
      <div class="empty-state">
        <svg width="48" height="48" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <path d="M3 12h1m8 -9v1m8 8h1m-15.4 -6.4l.7 .7m12.1 -.7l-.7 .7"/>
          <path d="M9 16a5 5 0 1 1 6 0a3.5 3.5 0 0 0 -1 3a2 2 0 0 1 -4 0a3.5 3.5 0 0 0 -1 -3"/>
          <line x1="9.7" y1="17" x2="14.3" y2="17"/>
        </svg>
        <h3>{searchQuery ? 'No prompts found' : 'No prompts yet'}</h3>
        <p>{searchQuery ? 'Try adjusting your search' : 'Create your first prompt to get started'}</p>
        {#if !searchQuery}
          <a href="/creation-station/prompts/new" class="btn-primary">Create Prompt</a>
        {/if}
      </div>
    {:else}
      <div class="prompts-grid">
        {#each filteredPrompts as prompt}
          <div class="prompt-card">
            <div class="prompt-header">
              <h3 class="prompt-name">{prompt.name}</h3>
              {#if prompt.access_level}
                <span class="access-badge access-{prompt.access_level.toLowerCase()}">
                  {prompt.access_level}
                </span>
              {/if}
            </div>
            
            <div class="prompt-command">
              <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <polyline points="4 17 10 11 4 5"></polyline>
                <line x1="12" y1="19" x2="20" y2="19"></line>
              </svg>
              <code>{prompt.command}</code>
            </div>
            
            <p class="prompt-preview">{prompt.content.slice(0, 150)}{prompt.content.length > 150 ? '...' : ''}</p>
            
            <div class="prompt-actions">
              <a href="/creation-station/prompts/{prompt.slug}/edit" class="btn-edit">
                <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                  <path d="M11 4H4a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2v-7"/>
                  <path d="M18.5 2.5a2.121 2.121 0 0 1 3 3L12 15l-4 1 1-4 9.5-9.5z"/>
                </svg>
                Edit
              </a>
              <button on:click={() => deletePrompt(prompt.slug)} class="btn-delete">
                <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                  <polyline points="3 6 5 6 21 6"/>
                  <path d="M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6m3 0V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2"/>
                </svg>
                Delete
              </button>
            </div>
          </div>
        {/each}
      </div>
    {/if}
  </div>
</main>

<style>
  .prompts-page {
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

  .prompts-grid {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(350px, 1fr));
    gap: 1.5rem;
  }

  .prompt-card {
    background: rgba(17, 24, 39, 0.8);
    border: 1px solid rgba(139, 92, 246, 0.2);
    border-radius: 1rem;
    padding: 1.5rem;
    transition: all 0.2s;
  }

  .prompt-card:hover {
    border-color: rgba(139, 92, 246, 0.4);
    transform: translateY(-2px);
    box-shadow: 0 10px 30px rgba(139, 92, 246, 0.15);
  }

  .prompt-header {
    display: flex;
    justify-content: space-between;
    align-items: flex-start;
    margin-bottom: 0.75rem;
  }

  .prompt-name {
    margin: 0;
    font-size: 1.125rem;
    font-weight: 600;
    color: white;
  }

  .access-badge {
    padding: 0.25rem 0.5rem;
    border-radius: 0.25rem;
    font-size: 0.75rem;
    font-weight: 600;
    text-transform: uppercase;
  }

  .access-badge.access-private {
    background: rgba(239, 68, 68, 0.2);
    color: #f87171;
  }

  .access-badge.access-classroom {
    background: rgba(59, 130, 246, 0.2);
    color: #60a5fa;
  }

  .access-badge.access-public {
    background: rgba(34, 197, 94, 0.2);
    color: #4ade80;
  }

  .prompt-command {
    display: flex;
    align-items: center;
    gap: 0.5rem;
    margin-bottom: 1rem;
    padding: 0.5rem;
    background: rgba(31, 41, 55, 0.5);
    border-radius: 0.375rem;
    color: #a78bfa;
  }

  .prompt-command code {
    font-family: 'Monaco', 'Menlo', 'Ubuntu Mono', monospace;
    font-size: 0.875rem;
  }

  .prompt-preview {
    margin: 0 0 1rem;
    color: #9ca3af;
    font-size: 0.875rem;
    line-height: 1.5;
  }

  .prompt-actions {
    display: flex;
    gap: 0.5rem;
    padding-top: 1rem;
    border-top: 1px solid rgba(75, 85, 99, 0.3);
  }

  .btn-edit,
  .btn-delete {
    flex: 1;
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
  }

  .btn-edit {
    background: rgba(59, 130, 246, 0.1);
    border: 1px solid rgba(59, 130, 246, 0.3);
    color: #60a5fa;
    text-decoration: none;
  }

  .btn-edit:hover {
    background: rgba(59, 130, 246, 0.2);
    border-color: rgba(59, 130, 246, 0.5);
  }

  .btn-delete {
    background: rgba(239, 68, 68, 0.1);
    border: 1px solid rgba(239, 68, 68, 0.3);
    color: #f87171;
  }

  .btn-delete:hover {
    background: rgba(239, 68, 68, 0.2);
    border-color: rgba(239, 68, 68, 0.5);
  }

  @media (max-width: 768px) {
    .header-main {
      flex-direction: column;
    }

    .prompts-grid {
      grid-template-columns: 1fr;
    }
  }
</style>