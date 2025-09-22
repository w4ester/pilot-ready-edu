<script lang="ts">
  import { onMount } from 'svelte';
  import { creationAPI, type RoomSummary } from '$lib/api.creationstation';


  let rooms: RoomSummary[] = [];
  let loading = true;
  let error: string | null = null;
  let searchQuery = '';
  let filteredRooms: RoomSummary[] = [];
  let normalizedQuery = '';

  $: normalizedQuery = searchQuery.trim().toLowerCase();
  $: filteredRooms = rooms.filter((room) => {
    if (!normalizedQuery) return true;

    const description = (room.description ?? '').toLowerCase();
    return (
      room.name.toLowerCase().includes(normalizedQuery) ||
      description.includes(normalizedQuery)
    );
  });

  onMount(async () => {
    try {
      rooms = await creationAPI.rooms.list();
    } catch (err) {
      error = err instanceof Error ? err.message : 'Failed to load rooms';
    } finally {
      loading = false;
    }
  });

  async function archiveRoom(id: string) {
    if (!confirm(`Are you sure you want to archive room "${id}"?`)) return;

    try {

    } catch (err) {
      alert(err instanceof Error ? err.message : 'Failed to archive room');
    }
  }

  async function restoreRoom(id: string) {
    try {
      const updated = await creationAPI.rooms.restore(id);
      rooms = rooms.map(c => (c.id === id ? updated : c));
    } catch (err) {
      alert(err instanceof Error ? err.message : 'Failed to restore room');
    }
  }

  function formatTimestamp(timestamp?: number | null): string {
    if (!timestamp) {
      return 'Unknown';
    }

    const ms = timestamp < 1_000_000_000_000 ? timestamp * 1000 : timestamp;
    return new Date(ms).toLocaleString();
  }
</script>

<svelte:head>
  <title>Collaborative Rooms · Creation Station</title>
</svelte:head>

<main class="room-page">
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
          <h1>💬 Collaborative Rooms</h1>
          <p class="header-description">Configure collaborative spaces, manage groups, and share resources.</p>
        </div>
        
        <a href="/creation-station/rooms/new" class="btn-create">
          <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <line x1="12" y1="5" x2="12" y2="19"></line>
            <line x1="5" y1="12" x2="19" y2="12"></line>
          </svg>
          New Room
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
        placeholder="Search rooms..."
        class="search-input"
      />
    </div>

    {#if loading}
      <div class="loading-state">
        <div class="spinner"></div>
        <p>Loading rooms...</p>
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
    {:else if filteredRooms.length === 0}
      <div class="empty-state">
        <svg width="48" height="48" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <path d="M21 11.5a8.38 8.38 0 0 1-.9 3.8 8.5 8.5 0 0 1-7.6 4.7 8.38 8.38 0 0 1-3.8-.9L3 21l1.9-5.7a8.38 8.38 0 0 1-.9-3.8 8.5 8.5 0 0 1 4.7-7.6 8.38 8.38 0 0 1 3.8-.9h.5a8.48 8.48 0 0 1 8 8v.5z"/>
        </svg>
        <h3>{searchQuery ? 'No rooms found' : 'No rooms yet'}</h3>
        <p>{searchQuery ? 'Try adjusting your search' : 'Create your first collaborative room to get started'}</p>
        {#if !searchQuery}
          <a href="/creation-station/rooms/new" class="btn-primary">Create Room</a>
        {/if}
      </div>
    {:else}
      <div class="rooms-grid">
        {#each filteredRooms as room}
          <div class="room-card" class:archived={room.is_archived}>
            <div class="room-header">
              <div>
                <h3 class="room-name">{room.name}</h3>
                {#if room.is_archived}
                  <span class="status-badge archived">Archived</span>
                {:else}
                  <span class="status-badge active">Active</span>
                {/if}
              </div>
            </div>

            {#if room.description}
              <p class="room-description">{room.description}</p>
            {/if}

            <div class="room-stats">
              <div class="stat">
                <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                  <path d="M17 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2"/>
                  <circle cx="9" cy="7" r="4"/>
                  <path d="M23 21v-2a4 4 0 0 0-3-3.87"/>
                  <path d="M16 3.13a4 4 0 0 1 0 7.75"/>
                </svg>
                <span>{room.member_count} members</span>
              </div>
              <div class="stat">
                <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                  <path d="M12 8v4l3 3"/>
                  <circle cx="12" cy="12" r="9"/>
                </svg>
                <span>Created {formatTimestamp(room.created_at)}</span>
              </div>
            </div>

            <div class="room-actions">
              <a href={`/creation-station/rooms/${room.id}`} class="btn-manage">
                <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                  <circle cx="12" cy="12" r="3"/>
                  <path d="M12 1v6m0 6v6m4.22-13.22l4.24 4.24M1.54 9.96l4.24 4.24M18.36 14.18l4.24 4.24M1.54 14.18l4.24-4.24"/>
                </svg>
                Manage
              </a>
              {#if !room.is_archived}
                <button on:click={() => archiveRoom(room.id)} class="btn-archive">
                  <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                    <polyline points="21 8 21 21 3 21 3 8"/>
                    <rect x="1" y="3" width="22" height="5"/>
                    <line x1="10" y1="12" x2="14" y2="12"/>
                  </svg>
                  Archive
                </button>
              {/if}
            </div>
          </div>
        {/each}
      </div>
    {/if}
  </div>
</main>

<style>
  .room-page {
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

  .rooms-grid {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(350px, 1fr));
    gap: 1.5rem;
  }

  .room-card {
    background: rgba(17, 24, 39, 0.8);
    border: 1px solid rgba(139, 92, 246, 0.2);
    border-radius: 1rem;
    padding: 1.5rem;
    transition: all 0.2s;
  }

  .room-card.archived {
    opacity: 0.6;
    border-color: rgba(75, 85, 99, 0.3);
  }

  .room-card:hover {
    border-color: rgba(139, 92, 246, 0.4);
    transform: translateY(-2px);
    box-shadow: 0 10px 30px rgba(139, 92, 246, 0.15);
  }

  .room-header {
    display: flex;
    justify-content: space-between;
    align-items: flex-start;
    margin-bottom: 0.75rem;
  }

  .room-header > div {
    display: flex;
    align-items: center;
    gap: 0.75rem;
  }

  .room-name {
    margin: 0;
    font-size: 1.125rem;
    font-weight: 600;
    color: white;
  }

  .status-badge {
    padding: 0.25rem 0.5rem;
    border-radius: 0.25rem;
    font-size: 0.75rem;
    font-weight: 600;
    text-transform: uppercase;
  }

  .status-badge.active {
    background: rgba(34, 197, 94, 0.2);
    color: #4ade80;
  }

  .status-badge.archived {
    background: rgba(107, 114, 128, 0.2);
    color: #9ca3af;
  }

  .safe-mode-indicator {
    display: flex;
    align-items: center;
    justify-content: center;
    width: 32px;
    height: 32px;
    background: rgba(251, 191, 36, 0.2);
    border-radius: 0.5rem;
    color: #fbbf24;
  }

  .room-description {
    margin: 0 0 1rem;
    color: #9ca3af;
    font-size: 0.875rem;
    line-height: 1.5;
  }

  .room-stats {
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

  .room-actions {
    display: flex;
    gap: 0.5rem;
  }

  .btn-manage,
  .btn-archive,
  .btn-restore {
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

  .btn-manage {
    background: rgba(59, 130, 246, 0.1);
    border: 1px solid rgba(59, 130, 246, 0.3);
    color: #60a5fa;
    text-decoration: none;
  }

  .btn-manage:hover {
    background: rgba(59, 130, 246, 0.2);
    border-color: rgba(59, 130, 246, 0.5);
  }

  .btn-archive {
    background: rgba(251, 191, 36, 0.1);
    border: 1px solid rgba(251, 191, 36, 0.3);
    color: #fbbf24;
  }

  .btn-archive:hover {
    background: rgba(251, 191, 36, 0.2);
    border-color: rgba(251, 191, 36, 0.5);
  }

  .btn-restore {
    background: rgba(34, 197, 94, 0.1);
    border: 1px solid rgba(34, 197, 94, 0.3);
    color: #4ade80;
  }

  .btn-restore:hover {
    background: rgba(34, 197, 94, 0.2);
    border-color: rgba(34, 197, 94, 0.5);
  }

  @media (max-width: 768px) {
    .header-main {
      flex-direction: column;
    }

    .rooms-grid {
      grid-template-columns: 1fr;
    }
  }
</style>
