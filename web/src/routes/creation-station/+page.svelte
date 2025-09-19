<script lang="ts">
  import type { PageData } from './$types';
  
  export let data: PageData;

  let viewMode: 'grid' | 'list' = 'grid';

  const toggleView = (mode: 'grid' | 'list') => {
    viewMode = mode;
  };
</script>

<svelte:head>
  <title>Creation Station · Edinfinite</title>
</svelte:head>

<main class="creation-station">
  <!-- Hero Section -->
  <section class="hero-section">
    <div class="hero-container">
      <!-- Platform Badge -->
      <div class="platform-badge">
        <span class="badge-indicator"></span>
        <span class="badge-text">AI-Powered Education Platform</span>
      </div>

      <!-- Title -->
      <h1 class="main-title">Creation Station</h1>

      <!-- Subtitle -->
      <p class="subtitle">
        Build powerful educational resources in seconds with specialized AI assistants
      </p>

      <!-- Stats -->
      <div class="stats-container">
        {#each data.stats as stat}
          <div class="stat-item">
            <div class="stat-value">{stat.display}</div>
            <div class="stat-label">{stat.label}</div>
          </div>
        {/each}
      </div>
    </div>
  </section>

  <!-- Tools Section -->
  <section class="tools-section">
    <div class="tools-container">
      <!-- Section Header -->
      <div class="section-header">
        <h2 class="section-title">Creation Tools</h2>
        
        <!-- View Toggle -->
        <div class="view-toggle">
          <button
            on:click={() => toggleView('grid')}
            class="toggle-btn {viewMode === 'grid' ? 'active' : ''}"
          >
            Grid
          </button>
          <button
            on:click={() => toggleView('list')}
            class="toggle-btn {viewMode === 'list' ? 'active' : ''}"
          >
            List
          </button>
        </div>
      </div>

      <!-- Cards Grid -->
      {#if viewMode === 'grid'}
        <div class="cards-grid">
          {#each data.tiles as tile}
            <article class="tool-card tool-card-{tile.key}">
              <!-- Card Header -->
              <div class="card-header">
                <div class="card-icon card-icon-{tile.key}">
                  <span class="icon-emoji">{tile.icon}</span>
                </div>
                
                {#if tile.badge}
                  <span class="badge badge-{tile.badge.tone}">
                    {tile.badge.label}
                  </span>
                {/if}
              </div>

              <!-- Title -->
              <h3 class="card-title">{tile.title}</h3>

              <!-- Description -->
              <p class="card-description">
                {tile.description}
              </p>

              <!-- Meta Info -->
              <div class="card-meta">
                {#if tile.countValue !== undefined}
                  <span class="meta-item">
                    <span class="meta-value">{tile.countValue}</span>
                    {tile.countLabel}
                  </span>
                {/if}
                
                {#if tile.meta}
                  {#each tile.meta as meta}
                    <span class="meta-item">
                      {#if meta.icon}{meta.icon}{/if}
                      {meta.label}
                    </span>
                  {/each}
                {/if}
              </div>

              <!-- Status or Action -->
              <div class="card-footer">
                {#if tile.disabled}
                  <span class="status-text">
                    {tile.statusText || 'Coming Soon'}
                  </span>
                {:else if tile.href}
                  <a href={tile.href} class="action-link">
                    <span>Open</span>
                    <svg class="arrow-icon" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7" />
                    </svg>
                  </a>
                {/if}
              </div>
            </article>
          {/each}
        </div>
      {:else}
        <!-- List View -->
        <div class="cards-list">
          {#each data.tiles as tile}
            <article class="list-item list-item-{tile.key}">
              <!-- Icon -->
              <div class="list-icon list-icon-{tile.key}">
                <span class="icon-emoji">{tile.icon}</span>
              </div>

              <!-- Content -->
              <div class="list-content">
                <div class="list-header">
                  <h3 class="list-title">{tile.title}</h3>
                  {#if tile.badge}
                    <span class="badge badge-{tile.badge.tone}">
                      {tile.badge.label}
                    </span>
                  {/if}
                </div>
                
                <p class="list-description">
                  {tile.description}
                </p>
                
                <div class="list-meta">
                  {#if tile.countValue !== undefined}
                    <span class="meta-item">
                      <span class="meta-value">{tile.countValue}</span>
                      {tile.countLabel}
                    </span>
                  {/if}
                  
                  {#if tile.meta}
                    {#each tile.meta as meta}
                      <span class="meta-item">
                        {#if meta.icon}{meta.icon}{/if}
                        {meta.label}
                      </span>
                    {/each}
                  {/if}
                </div>
              </div>

              <!-- Action -->
              <div class="list-action">
                {#if tile.disabled}
                  <span class="status-text">
                    {tile.statusText || 'Coming Soon'}
                  </span>
                {:else if tile.href}
                  <a href={tile.href} class="list-action-btn">
                    <span>Open</span>
                    <svg class="arrow-icon" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7" />
                    </svg>
                  </a>
                {/if}
              </div>
            </article>
          {/each}
        </div>
      {/if}
    </div>
  </section>
</main>

<style>
  .creation-station {
    min-height: 100vh;
    background: linear-gradient(135deg, #0f0f23 0%, #1a0f2e 50%, #0f0f23 100%);
    color: #fff;
  }

  /* Hero Section */
  .hero-section {
    padding: 4rem 1.5rem 3rem;
  }

  .hero-container {
    max-width: 1400px;
    margin: 0 auto;
    text-align: center;
  }

  .platform-badge {
    display: inline-flex;
    align-items: center;
    gap: 0.5rem;
    padding: 0.5rem 1rem;
    margin-bottom: 1.5rem;
    background: rgba(139, 92, 246, 0.2);
    border: 1px solid rgba(139, 92, 246, 0.3);
    border-radius: 9999px;
  }

  .badge-indicator {
    width: 0.5rem;
    height: 0.5rem;
    background: #a78bfa;
    border-radius: 50%;
    animation: pulse 2s infinite;
  }

  .badge-text {
    font-size: 0.875rem;
    font-weight: 500;
    color: #c4b5fd;
  }

  .main-title {
    font-size: 4rem;
    font-weight: bold;
    margin: 0 0 1rem;
    background: linear-gradient(to right, #c4b5fd, #f9a8d4);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
  }

  .subtitle {
    font-size: 1.25rem;
    color: #9ca3af;
    max-width: 600px;
    margin: 0 auto 3rem;
  }

  .stats-container {
    display: flex;
    justify-content: center;
    gap: 5rem;
    margin-bottom: 3rem;
  }

  .stat-item {
    text-align: center;
  }

  .stat-value {
    font-size: 2.5rem;
    font-weight: bold;
    color: #60a5fa;
  }

  .stat-label {
    font-size: 0.75rem;
    text-transform: uppercase;
    letter-spacing: 0.1em;
    color: #6b7280;
    margin-top: 0.25rem;
  }

  /* Tools Section */
  .tools-section {
    padding: 0 2rem 5rem;
  }

  .tools-container {
    max-width: 1600px;
    margin: 0 auto;
  }

  .section-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 2rem;
  }

  .section-title {
    font-size: 1.5rem;
    font-weight: bold;
    margin: 0;
  }

  .view-toggle {
    display: flex;
    gap: 0.5rem;
    padding: 0.25rem;
    background: rgba(31, 41, 55, 0.5);
    border: 1px solid rgba(75, 85, 99, 0.5);
    border-radius: 0.5rem;
  }

  .toggle-btn {
    padding: 0.5rem 1rem;
    border: none;
    border-radius: 0.375rem;
    background: transparent;
    color: #9ca3af;
    font-size: 0.875rem;
    font-weight: 500;
    cursor: pointer;
    transition: all 0.2s;
  }

  .toggle-btn.active {
    background: #7c3aed;
    color: white;
  }

  .toggle-btn:hover:not(.active) {
    color: white;
  }

  /* Cards Grid */
  .cards-grid {
    display: grid;
    grid-template-columns: repeat(3, 1fr);
    gap: 2rem;
  }

  .tool-card {
    position: relative;
    padding: 2rem;
    min-height: 280px;
    border-radius: 1.25rem;
    border: 1px solid rgba(139, 92, 246, 0.2);
    background: rgba(17, 24, 39, 0.5);
    backdrop-filter: blur(10px);
    transition: transform 0.3s, border-color 0.3s;
    display: flex;
    flex-direction: column;
  }

  .tool-card:hover {
    transform: scale(1.02);
    border-color: rgba(139, 92, 246, 0.4);
  }

  .tool-card-prompts { background: linear-gradient(135deg, rgba(139, 92, 246, 0.1), rgba(99, 102, 241, 0.1)); }
  .tool-card-tools { background: linear-gradient(135deg, rgba(236, 72, 153, 0.1), rgba(244, 114, 182, 0.1)); }
  .tool-card-models { background: linear-gradient(135deg, rgba(6, 182, 212, 0.1), rgba(59, 130, 246, 0.1)); }
  .tool-card-libraries { background: linear-gradient(135deg, rgba(16, 185, 129, 0.1), rgba(20, 184, 166, 0.1)); }
  .tool-card-cards { background: linear-gradient(135deg, rgba(251, 146, 60, 0.1), rgba(251, 191, 36, 0.1)); }
  .tool-card-class-chat { background: linear-gradient(135deg, rgba(59, 130, 246, 0.1), rgba(99, 102, 241, 0.1)); }

  .card-header {
    display: flex;
    justify-content: space-between;
    align-items: flex-start;
    margin-bottom: 1rem;
  }

  .card-icon {
    width: 3.5rem;
    height: 3.5rem;
    display: flex;
    align-items: center;
    justify-content: center;
    border-radius: 1rem;
    font-size: 1.75rem;
  }

  .card-icon-prompts { background: linear-gradient(135deg, #a78bfa, #6366f1); }
  .card-icon-tools { background: linear-gradient(135deg, #f472b6, #ec4899); }
  .card-icon-models { background: linear-gradient(135deg, #06b6d4, #3b82f6); }
  .card-icon-libraries { background: linear-gradient(135deg, #10b981, #14b8a6); }
  .card-icon-cards { background: linear-gradient(135deg, #fb923c, #fbbf24); }
  .card-icon-class-chat { background: linear-gradient(135deg, #3b82f6, #6366f1); }

  .badge {
    padding: 0.375rem 0.875rem;
    font-size: 0.8125rem;
    font-weight: 500;
    border-radius: 9999px;
    border: 1px solid;
  }

  .badge-accent {
    background: rgba(139, 92, 246, 0.3);
    color: #c4b5fd;
    border-color: rgba(139, 92, 246, 0.5);
  }

  .badge-info {
    background: rgba(59, 130, 246, 0.3);
    color: #93c5fd;
    border-color: rgba(59, 130, 246, 0.5);
  }

  .badge-warning {
    background: rgba(251, 191, 36, 0.3);
    color: #fde047;
    border-color: rgba(251, 191, 36, 0.5);
  }

  .badge-neutral {
    background: rgba(107, 114, 128, 0.3);
    color: #d1d5db;
    border-color: rgba(107, 114, 128, 0.5);
  }

  .card-title {
    font-size: 1.5rem;
    font-weight: bold;
    margin: 0 0 0.75rem;
  }

  .card-description {
    font-size: 0.9375rem;
    color: #9ca3af;
    line-height: 1.6;
    margin: 0 0 1.5rem;
    flex-grow: 1;
  }

  .card-meta {
    display: flex;
    flex-wrap: wrap;
    gap: 1rem;
    font-size: 0.8125rem;
    color: #6b7280;
    margin-bottom: 1.5rem;
  }

  .meta-item {
    display: flex;
    align-items: center;
    gap: 0.25rem;
  }

  .meta-value {
    color: white;
    font-weight: 600;
  }

  .card-footer {
    padding-top: 1.25rem;
    margin-top: auto;
    border-top: 1px solid rgba(75, 85, 99, 0.3);
  }

  .status-text {
    font-size: 0.75rem;
    color: #6b7280;
    font-weight: 500;
  }

  .action-link {
    display: inline-flex;
    align-items: center;
    gap: 0.5rem;
    color: #a78bfa;
    text-decoration: none;
    font-size: 0.875rem;
    font-weight: 500;
    transition: color 0.2s;
  }

  .action-link:hover {
    color: #c4b5fd;
  }

  .arrow-icon {
    width: 1rem;
    height: 1rem;
  }

  /* List View */
  .cards-list {
    display: flex;
    flex-direction: column;
    gap: 1rem;
  }

  .list-item {
    display: flex;
    align-items: center;
    gap: 1.5rem;
    padding: 1.5rem;
    border-radius: 0.75rem;
    border: 1px solid rgba(139, 92, 246, 0.2);
    background: rgba(17, 24, 39, 0.5);
    backdrop-filter: blur(10px);
    transition: transform 0.3s, border-color 0.3s;
  }

  .list-item:hover {
    transform: translateX(0.5rem);
    border-color: rgba(139, 92, 246, 0.4);
  }

  .list-item-prompts { background: linear-gradient(90deg, rgba(139, 92, 246, 0.1), rgba(99, 102, 241, 0.05)); }
  .list-item-tools { background: linear-gradient(90deg, rgba(236, 72, 153, 0.1), rgba(244, 114, 182, 0.05)); }
  .list-item-models { background: linear-gradient(90deg, rgba(6, 182, 212, 0.1), rgba(59, 130, 246, 0.05)); }
  .list-item-libraries { background: linear-gradient(90deg, rgba(16, 185, 129, 0.1), rgba(20, 184, 166, 0.05)); }
  .list-item-cards { background: linear-gradient(90deg, rgba(251, 146, 60, 0.1), rgba(251, 191, 36, 0.05)); }
  .list-item-class-chat { background: linear-gradient(90deg, rgba(59, 130, 246, 0.1), rgba(99, 102, 241, 0.05)); }

  .list-icon {
    flex-shrink: 0;
    width: 3rem;
    height: 3rem;
    display: flex;
    align-items: center;
    justify-content: center;
    border-radius: 0.75rem;
    font-size: 1.5rem;
  }

  .list-icon-prompts { background: linear-gradient(135deg, #a78bfa, #6366f1); }
  .list-icon-tools { background: linear-gradient(135deg, #f472b6, #ec4899); }
  .list-icon-models { background: linear-gradient(135deg, #06b6d4, #3b82f6); }
  .list-icon-libraries { background: linear-gradient(135deg, #10b981, #14b8a6); }
  .list-icon-cards { background: linear-gradient(135deg, #fb923c, #fbbf24); }
  .list-icon-class-chat { background: linear-gradient(135deg, #3b82f6, #6366f1); }

  .list-content {
    flex: 1;
  }

  .list-header {
    display: flex;
    align-items: center;
    gap: 0.75rem;
    margin-bottom: 0.5rem;
  }

  .list-title {
    font-size: 1.125rem;
    font-weight: bold;
    margin: 0;
  }

  .list-description {
    font-size: 0.875rem;
    color: #9ca3af;
    margin: 0 0 0.75rem;
  }

  .list-meta {
    display: flex;
    gap: 1rem;
    font-size: 0.75rem;
    color: #6b7280;
  }

  .list-action {
    flex-shrink: 0;
  }

  .list-action-btn {
    display: inline-flex;
    align-items: center;
    gap: 0.5rem;
    padding: 0.5rem 1rem;
    background: rgba(139, 92, 246, 0.2);
    border: 1px solid rgba(139, 92, 246, 0.3);
    border-radius: 0.5rem;
    color: #a78bfa;
    text-decoration: none;
    font-size: 0.875rem;
    transition: all 0.2s;
  }

  .list-action-btn:hover {
    background: rgba(139, 92, 246, 0.3);
    color: #c4b5fd;
  }

  @keyframes pulse {
    0%, 100% {
      opacity: 1;
    }
    50% {
      opacity: 0.5;
    }
  }

  @media (max-width: 1280px) {
    .cards-grid {
      grid-template-columns: repeat(2, 1fr);
    }
  }

  @media (max-width: 768px) {
    .main-title {
      font-size: 2.5rem;
    }

    .stats-container {
      gap: 1.5rem;
    }

    .cards-grid {
      grid-template-columns: 1fr;
    }

    .list-item {
      flex-direction: column;
      text-align: center;
    }
  }
</style>