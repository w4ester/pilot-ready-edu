<script lang="ts">
  import { onMount } from 'svelte';
  import { creationAPI } from '$lib/api.creationstation';
  
  interface Library {
    slug: string;
    name: string;
    description?: string;
    document_count?: number;
    chunk_count?: number;
    created_at?: string;
    updated_at?: string;
  }
  
  let libraries: Library[] = [];
  let loading = true;
  let error: string | null = null;
  let searchQuery = '';
  
  $: filteredLibraries = libraries.filter(library => 
    library.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
    library.slug.toLowerCase().includes(searchQuery.toLowerCase())
  );
  
  onMount(async () => {
    try {
      libraries = await creationAPI.libraries.list();
    } catch (err) {
      error = err instanceof Error ? err.message : 'Failed to load libraries';
    } finally {
      loading = false;
    }
  });
  
  async function deleteLibrary(slug: string) {
    if (!confirm(`Are you sure you want to delete library "${slug}"?`)) return;
    
    try {
      await creationAPI.libraries.delete(slug);
      libraries = libraries.filter(l => l.slug !== slug);
    } catch (err) {
      alert(err instanceof Error ? err.message : 'Failed to delete library');
    }
  }
</script>

<svelte:head>
  <title>Libraries · Creation Station</title>
</svelte:head>

<main class="libraries-page">
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
          <h1>📚 Libraries</h1>
          <p class="header-description">Build RAG knowledge bases from documents for contextual AI responses.</p>
        </div>
        
        <a href="/creation-station/libraries/new" class="btn-create">
          <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <line x1="12" y1="5" x2="12" y2="19"></line>
            <line x1="5" y1="12" x2="19" y2="12"></line>
          </svg>
          New Library
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
        placeholder="Search libraries..."
        class="search-input"
      />
    </div>

    {#if loading}
      <div class="loading-state">
        <div class="spinner"></div>
        <p>Loading libraries...</p>
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
    {:else if filteredLibraries.length === 0}
      <div class="empty-state">
        <svg width="48" height="48" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <path d="M4 19.5A2.5 2.5 0 0 1 6.5 17H20"/>
          <path d="M6.5 2H20v20H6.5A2.5 2.5 0 0 1 4 19.5v-15A2.5 2.5 0 0 1 6.5 2z"/>
        </svg>
        <h3>{searchQuery ? 'No libraries found' : 'No libraries yet'}</h3>
        <p>{searchQuery ? 'Try adjusting your search' : 'Create your first knowledge library to get started'}</p>
        {#if !searchQuery}
          <a href="/creation-station/libraries/new" class="btn-primary">Create Library</a>
        {/if}
      </div>
    {:else}
      <div class="libraries-grid">
        {#each filteredLibraries as library}
          <div class="library-card">
            <div class="library-header">
              <h3 class="library-name">{library.name}</h3>
              <div class="library-meta">
                {#if library.document_count}
                  <span class="meta-badge">{library.document_count} docs</span>
                {/if}
                {#if library.chunk_count}
                  <span class="meta-badge">{library.chunk_count} chunks</span>
                {/if}
              </div>
            </div>
            
            <p class="library-slug">{library.slug}</p>
            
            {#if library.description}
              <p class="library-description">{library.description}</p>
            {/if}
            
            <div class="library-stats">
              <div class="stat">
                <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                  <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/>
                  <polyline points="14 2 14 8 20 8"/>
                  <line x1="16" y1="13" x2="8" y2="13"/>
                  <line x1="16" y1="17" x2="8" y2="17"/>
                  <polyline points="10 9 9 9 8 9"/>
                </svg>
                <span>Documents: {library.document_count || 0}</span>
              </div>
              <div class="stat">
                <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                  <rect x="3" y="3" width="18" height="18" rx="2" ry="2"/>
                  <line x1="9" y1="3" x2="9" y2="21"/>
                  <line x1="15" y1="3" x2="15" y2="21"/>
                </svg>
                <span>Chunks: {library.chunk_count || 0}</span>
              </div>
            </div>
            
            <div class="library-actions">
              <a href="/creation-station/libraries/{library.slug}/edit" class="btn-edit">
                <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                  <path d="M11 4H4a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2v-7"/>
                  <path d="M18.5 2.5a2.121 2.121 0 0 1 3 3L12 15l-4 1 1-4 9.5-9.5z"/>
                </svg>
                Edit
              </a>
              <button on:click={() => deleteLibrary(library.slug)} class="btn-delete">
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
  .libraries-page {
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

  .libraries-grid {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(350px, 1fr));
    gap: 1.5rem;
  }

  .library-card {
    background: rgba(17, 24, 39, 0.8);
    border: 1px solid rgba(139, 92, 246, 0.2);
    border-radius: 1rem;
    padding: 1.5rem;
    transition: all 0.2s;
  }

  .library-card:hover {
    border-color: rgba(139, 92, 246, 0.4);
    transform: translateY(-2px);
    box-shadow: 0 10px 30px rgba(139, 92, 246, 0.15);
  }

  .library-header {
    display: flex;
    justify-content: space-between;
    align-items: flex-start;
    margin-bottom: 0.5rem;
  }

  .library-name {
    margin: 0;
    font-size: 1.125rem;
    font-weight: 600;
    color: white;
  }

  .library-meta {
    display: flex;
    gap: 0.5rem;
  }

  .meta-badge {
    padding: 0.25rem 0.5rem;
    background: rgba(20, 184, 166, 0.2);
    color: #14b8a6;
    border-radius: 0.25rem;
    font-size: 0.75rem;
    font-weight: 600;
  }

  .library-slug {
    margin: 0 0 0.75rem;
    color: #6b7280;
    font-family: 'Monaco', 'Menlo', 'Ubuntu Mono', monospace;
    font-size: 0.875rem;
  }

  .library-description {
    margin: 0 0 1rem;
    color: #9ca3af;
    font-size: 0.875rem;
    line-height: 1.5;
  }

  .library-stats {
    display: flex;
    gap: 1.5rem;
    padding: 1rem 0;
    border-top: 1px solid rgba(75, 85, 99, 0.3);
    border-bottom: 1px solid rgba(75, 85, 99, 0.3);
    margin-bottom: 1rem;
  }

  .stat {
    display: flex;
    align-items: center;
    gap: 0.5rem;
    color: #9ca3af;
    font-size: 0.875rem;
  }

  .library-actions {
    display: flex;
    gap: 0.5rem;
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

    .libraries-grid {
      grid-template-columns: 1fr;
    }
  }
</style>