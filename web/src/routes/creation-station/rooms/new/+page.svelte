<script lang="ts">
  import { creationAPI } from '$lib/api.creationstation';
  import { goto } from '$app/navigation';
  import CreatorChat from '$lib/components/CreatorChat.svelte';

  let roomName = '';
  let selectedTemplate = '';
  let message: string | null = null;
  let error: string | null = null;
  let submitting = false;
  
  // Active Rooms
  let activeRooms = [
    {
      id: 'general',
      name: 'General Discussion',
      icon: '💬',
      description: 'Main room chat for announcements and Q&A',
      studentCount: 32,
      isAIAssisted: true,
      librariesCount: 3,
      active: true
    }
  ];
  
  // Study Groups  
  let studyGroups = [
    {
      id: 'study-1',
      name: 'Study Groups',
      icon: '👥',
      description: 'Breakout rooms for collaborative learning',
      configured: false
    }
  ];
  
  // Project Teams
  let projectTeams = [
    {
      id: 'project-1', 
      name: 'Project Teams',
      icon: '🚀',
      description: 'Dedicated rooms for group projects',
      configured: false
    }
  ];
  
  // Available Resources
  let resources = {
    prompts: {
      name: 'Prompts Library',
      count: 12,
      enabled: true
    },
    tools: {
      name: 'Tools',
      count: 8,
      enabled: false
    },
    models: {
      name: 'AI Models',
      count: 5,
      enabled: true
    }
  };
  
  // Safety Settings
  let safetySettings = {
    safeMode: true,
    contentFiltering: true,
    moderationQueue: true,
    realTimeMonitoring: true
  };
  
  // Chat with RoomConnect
  const assistantIntro =
    "Welcome! I'm RoomConnect, your collaborative space architect. I'll help you create the perfect collaborative environment with the right mix of freedom and safety. What type of room are you setting up?";

  const quickActions = ['Setup groups', 'Import roster', 'Safety config'];

  async function handleSubmit(event: SubmitEvent) {
    event.preventDefault();
    submitting = true;
    message = null;
    error = null;

    try {
      await creationAPI.rooms.create({
        name: roomName,
        description: selectedTemplate || undefined,
        channel_type: 'collaboration',
        data: {
          active_rooms: activeRooms,
          study_groups: studyGroups,
          project_teams: projectTeams,
        },
        meta: {
          resources,
          safety_settings: safetySettings,
          quick_actions: quickActions,
        },
      });
      message = 'Room created successfully.';
      setTimeout(() => {
        goto('/creation-station/rooms');
      }, 800);
    } catch (err) {
      error = err instanceof Error ? err.message : 'Failed to create room';
    } finally {
      submitting = false;
    }
  }

  function toggleResource(key: string) {
    resources[key].enabled = !resources[key].enabled;
  }
  
  function toggleSafety(key: string) {
    safetySettings[key] = !safetySettings[key];
  }
</script>

<svelte:head>
  <title>New Room · Collaborative Spaces · Creation Station</title>
</svelte:head>

<main class="room-page">
  <div class="page-container-split">
    <!-- Left Panel - Configuration -->
    <section class="config-panel">
      <header class="panel-header">
        <div class="header-left">
          <a href="/creation-station/rooms" class="back-link">
            <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
              <path d="M19 12H5M12 19l-7-7 7-7"/>
            </svg>
          </a>
          <h1>Collaborative Rooms</h1>
        </div>
        <p class="subtitle">Configure collaborative learning spaces</p>
      </header>

      <div class="form-actions">
        <button class="btn-secondary">Templates</button>
        <button class="btn-primary">
          <span>+</span> New Room
        </button>
      </div>

      <form class="room-form" on:submit|preventDefault={handleSubmit}>
        <div class="form-group">
          <label for="room-name">ROOM NAME</label>
          <input 
            id="room-name" 
            bind:value={roomName} 
            required 
            placeholder="e.g., Biology 101 - Period 3"
            class="form-input" 
          />
        </div>

        <!-- Active Rooms Section -->
        <div class="section">
          <h3 class="section-title">ACTIVE ROOMS</h3>
          <div class="rooms-list">
            {#each activeRooms as room}
              <div class="room-card" class:active={room.active}>
                <div class="room-header">
                  <div class="room-icon">{room.icon}</div>
                  <div class="room-info">
                    <h4>{room.name}</h4>
                    <p>{room.description}</p>
                  </div>
                  <div class="room-toggle">
                    <div class="toggle-switch" class:active={room.active}></div>
                  </div>
                </div>
                <div class="room-stats">
                  <span>👥 {room.studentCount} students</span>
                  {#if room.isAIAssisted}
                    <span>🤖 AI Assisted Active</span>
                  {/if}
                  <span>📚 {room.librariesCount} Libraries</span>
                </div>
              </div>
            {/each}
            
            {#each studyGroups as group}
              <div class="room-card">
                <div class="room-header">
                  <div class="room-icon">{group.icon}</div>
                  <div class="room-info">
                    <h4>{group.name}</h4>
                    <p>{group.description}</p>
                  </div>
                  <button class="btn-configure">+ Configure Groups</button>
                </div>
              </div>
            {/each}
            
            {#each projectTeams as team}
              <div class="room-card">
                <div class="room-header">
                  <div class="room-icon">{team.icon}</div>
                  <div class="room-info">
                    <h4>{team.name}</h4>
                    <p>{team.description}</p>
                  </div>
                  <button class="btn-configure">+ Create Team</button>
                </div>
              </div>
            {/each}
          </div>
        </div>

        <!-- Available Resources Section -->
        <div class="section">
          <h3 class="section-title">AVAILABLE RESOURCES</h3>
          <p class="section-subtitle">What can users access in this room?</p>
          
          <div class="resources-list">
            {#each Object.entries(resources) as [key, resource]}
              <div class="resource-item">
                <div class="resource-info">
                  <span class="resource-icon">📚</span>
                  <div>
                    <h4>{resource.name}</h4>
                    <p>{resource.count} {resource.count === 1 ? 'item' : 'items'} available</p>
                  </div>
                </div>
                <button 
                  type="button"
                  class="toggle-btn {resource.enabled ? 'enabled' : 'disabled'}"
                  on:click={() => toggleResource(key)}
                >
                  <div class="toggle-slider"></div>
                </button>
              </div>
            {/each}
          </div>
        </div>

        <!-- Safety Settings Section -->
        <div class="section">
          <h3 class="section-title">SAFETY SETTINGS</h3>
          
          <div class="safety-list">
            <div class="safety-item">
              <span class="safety-icon">🔒</span>
              <span>Safe Mode Enabled</span>
            </div>
            
            <div class="safety-option">
              <input 
                type="checkbox" 
                id="content-filtering"
                bind:checked={safetySettings.contentFiltering}
              />
              <label for="content-filtering">Content filtering for age-appropriate discussions</label>
            </div>
            
            <div class="safety-option">
              <input 
                type="checkbox" 
                id="moderation-queue"
                bind:checked={safetySettings.moderationQueue}
              />
              <label for="moderation-queue">Moderation queue for sensitive topics</label>
            </div>
            
            <div class="safety-option">
              <input 
                type="checkbox" 
                id="real-time-monitoring"
                bind:checked={safetySettings.realTimeMonitoring}
              />
              <label for="real-time-monitoring">Real-time monitoring for bullying prevention</label>
            </div>
          </div>
        </div>

        {#if error}
          <div class="alert alert-error">
            <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <circle cx="12" cy="12" r="10"></circle>
              <line x1="12" y1="8" x2="12" y2="12"></line>
              <line x1="12" y1="16" x2="12.01" y2="16"></line>
            </svg>
            {error}
          </div>
        {/if}
        
        {#if message}
          <div class="alert alert-success">
            <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <path d="M22 11.08V12a10 10 0 1 1-5.93-9.14"></path>
              <polyline points="22 4 12 14.01 9 11.01"></polyline>
            </svg>
            {message}
          </div>
        {/if}

        <div class="form-submit">
          <button type="submit" class="btn-primary" disabled={submitting}>
            {submitting ? 'Creating...' : 'Create Room'}
          </button>
        </div>
      </form>
    </section>

    <!-- Right Panel - Chat -->
    <CreatorChat
      helperKey="rooms"
      assistantName="RoomConnect"
      assistantDescription="Your room orchestrator"
      assistantAvatar="👨‍🏫"
      initialMessage={assistantIntro}
      quickActions={quickActions}
      placeholder="Ask RoomConnect..."
    >
      <div slot="beforeMessages" class="quick-templates">
        <button class="template-btn">Room templates</button>
      </div>
    </CreatorChat>
  </div>
</main>

<style>
  .room-page {
    min-height: 100vh;
    background: linear-gradient(135deg, #0f0f23 0%, #1a0f2e 50%, #0f0f23 100%);
    padding: 2rem;
  }

  .page-container-split {
    max-width: 1400px;
    margin: 0 auto;
    display: grid;
    grid-template-columns: 1.5fr 1fr;
    gap: 2rem;
    height: calc(100vh - 8rem);
  }

  /* Left Panel Styles */
  .config-panel {
    background: rgba(17, 24, 39, 0.8);
    border-radius: 1rem;
    padding: 2rem;
    border: 1px solid rgba(139, 92, 246, 0.2);
    overflow-y: auto;
    display: flex;
    flex-direction: column;
  }

  .panel-header {
    margin-bottom: 1.5rem;
  }

  .header-left {
    display: flex;
    align-items: center;
    gap: 1rem;
    margin-bottom: 0.5rem;
  }

  .back-link {
    display: inline-flex;
    align-items: center;
    color: #a78bfa;
    transition: color 0.2s;
  }

  .back-link:hover {
    color: #c4b5fd;
  }

  .panel-header h1 {
    margin: 0;
    font-size: 1.75rem;
    font-weight: bold;
    color: white;
  }

  .subtitle {
    margin: 0;
    color: #9ca3af;
    font-size: 0.875rem;
  }

  .form-actions {
    display: flex;
    gap: 0.75rem;
    margin-bottom: 1.5rem;
  }

  .btn-secondary {
    padding: 0.5rem 1rem;
    background: transparent;
    border: 1px solid rgba(139, 92, 246, 0.3);
    color: #a78bfa;
    border-radius: 0.5rem;
    font-weight: 500;
    cursor: pointer;
    transition: all 0.2s;
  }

  .btn-secondary:hover {
    background: rgba(139, 92, 246, 0.1);
    border-color: rgba(139, 92, 246, 0.5);
  }

  .btn-primary {
    padding: 0.5rem 1rem;
    background: #7c3aed;
    border: none;
    color: white;
    border-radius: 0.5rem;
    font-weight: 600;
    cursor: pointer;
    transition: all 0.2s;
  }

  .btn-primary:hover:not(:disabled) {
    background: #6d28d9;
    transform: translateY(-1px);
    box-shadow: 0 10px 20px rgba(124, 58, 237, 0.3);
  }

  .btn-primary:disabled {
    opacity: 0.5;
    cursor: not-allowed;
  }

  .room-form {
    display: flex;
    flex-direction: column;
    gap: 1.5rem;
  }

  .form-group {
    display: flex;
    flex-direction: column;
    gap: 0.5rem;
  }

  .form-group label {
    font-size: 0.75rem;
    font-weight: 600;
    color: #d1d5db;
    text-transform: uppercase;
    letter-spacing: 0.05em;
  }

  .form-input {
    width: 100%;
    padding: 0.75rem;
    background: rgba(31, 41, 55, 0.5);
    border: 1px solid rgba(75, 85, 99, 0.5);
    border-radius: 0.5rem;
    color: white;
    font-size: 0.9375rem;
    transition: all 0.2s;
  }

  .form-input::placeholder {
    color: #6b7280;
  }

  .form-input:focus {
    outline: none;
    border-color: rgba(139, 92, 246, 0.5);
    background: rgba(31, 41, 55, 0.7);
  }

  /* Sections */
  .section {
    display: flex;
    flex-direction: column;
    gap: 1rem;
  }

  .section-title {
    margin: 0;
    font-size: 0.75rem;
    font-weight: 600;
    color: #d1d5db;
    text-transform: uppercase;
    letter-spacing: 0.05em;
  }

  .section-subtitle {
    margin: -0.5rem 0 0;
    color: #6b7280;
    font-size: 0.875rem;
  }

  /* Rooms */
  .rooms-list {
    display: flex;
    flex-direction: column;
    gap: 0.75rem;
  }

  .room-card {
    background: rgba(31, 41, 55, 0.5);
    border: 1px solid rgba(75, 85, 99, 0.3);
    border-radius: 0.75rem;
    padding: 1rem;
    transition: all 0.2s;
  }

  .room-card.active {
    border-color: rgba(139, 92, 246, 0.5);
    background: rgba(139, 92, 246, 0.05);
  }

  .room-header {
    display: flex;
    align-items: center;
    gap: 1rem;
    margin-bottom: 0.75rem;
  }

  .room-icon {
    width: 40px;
    height: 40px;
    background: rgba(139, 92, 246, 0.2);
    border-radius: 0.5rem;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 1.25rem;
  }

  .room-info {
    flex: 1;
  }

  .room-info h4 {
    margin: 0;
    color: white;
    font-size: 0.9375rem;
    font-weight: 600;
  }

  .room-info p {
    margin: 0.25rem 0 0;
    color: #9ca3af;
    font-size: 0.8125rem;
  }

  .room-toggle {
    display: flex;
    align-items: center;
  }

  .toggle-switch {
    width: 24px;
    height: 24px;
    border-radius: 50%;
    background: rgba(75, 85, 99, 0.5);
    transition: all 0.2s;
  }

  .toggle-switch.active {
    background: #10b981;
  }

  .room-stats {
    display: flex;
    gap: 1rem;
    font-size: 0.8125rem;
    color: #9ca3af;
  }

  .btn-configure {
    padding: 0.375rem 0.75rem;
    background: transparent;
    border: 1px solid rgba(139, 92, 246, 0.3);
    color: #a78bfa;
    border-radius: 0.375rem;
    font-size: 0.8125rem;
    font-weight: 500;
    cursor: pointer;
    transition: all 0.2s;
  }

  .btn-configure:hover {
    background: rgba(139, 92, 246, 0.1);
    border-color: rgba(139, 92, 246, 0.5);
  }

  /* Resources */
  .resources-list {
    display: flex;
    flex-direction: column;
    gap: 0.75rem;
  }

  .resource-item {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 0.75rem;
    background: rgba(31, 41, 55, 0.5);
    border-radius: 0.5rem;
  }

  .resource-info {
    display: flex;
    align-items: center;
    gap: 0.75rem;
  }

  .resource-icon {
    font-size: 1.25rem;
  }

  .resource-info h4 {
    margin: 0;
    color: white;
    font-size: 0.875rem;
    font-weight: 500;
  }

  .resource-info p {
    margin: 0.125rem 0 0;
    color: #6b7280;
    font-size: 0.75rem;
  }

  .toggle-btn {
    position: relative;
    width: 44px;
    height: 24px;
    background: rgba(75, 85, 99, 0.5);
    border: none;
    border-radius: 999px;
    cursor: pointer;
    transition: all 0.2s;
  }

  .toggle-btn.enabled {
    background: #8b5cf6;
  }

  .toggle-slider {
    position: absolute;
    top: 2px;
    left: 2px;
    width: 20px;
    height: 20px;
    background: white;
    border-radius: 50%;
    transition: all 0.2s;
  }

  .toggle-btn.enabled .toggle-slider {
    transform: translateX(20px);
  }

  /* Safety Settings */
  .safety-list {
    display: flex;
    flex-direction: column;
    gap: 0.75rem;
    padding: 1rem;
    background: rgba(31, 41, 55, 0.5);
    border-radius: 0.75rem;
  }

  .safety-item {
    display: flex;
    align-items: center;
    gap: 0.75rem;
    padding-bottom: 0.75rem;
    border-bottom: 1px solid rgba(75, 85, 99, 0.3);
    color: #fbbf24;
    font-weight: 600;
  }

  .safety-icon {
    font-size: 1.25rem;
  }

  .safety-option {
    display: flex;
    align-items: center;
    gap: 0.75rem;
  }

  .safety-option input[type="checkbox"] {
    width: 18px;
    height: 18px;
    accent-color: #10b981;
  }

  .safety-option label {
    color: #d1d5db;
    font-size: 0.875rem;
  }

  .alert {
    display: flex;
    align-items: center;
    gap: 0.75rem;
    padding: 1rem;
    border-radius: 0.5rem;
    font-size: 0.875rem;
  }

  .alert-error {
    background: rgba(239, 68, 68, 0.1);
    border: 1px solid rgba(239, 68, 68, 0.3);
    color: #fca5a5;
  }

  .alert-success {
    background: rgba(34, 197, 94, 0.1);
    border: 1px solid rgba(34, 197, 94, 0.3);
    color: #86efac;
  }

  .form-submit {
    display: flex;
    justify-content: flex-end;
  }

  /* Right Panel - Chat Styles */
  :global(.chat-panel) {
    background: rgba(17, 24, 39, 0.8);
    border-radius: 1rem;
    border: 1px solid rgba(139, 92, 246, 0.2);
    display: flex;
    flex-direction: column;
    overflow: hidden;
  }

  :global(.chat-header) {
    padding: 1.5rem;
    border-bottom: 1px solid rgba(75, 85, 99, 0.3);
  }

  :global(.assistant-info) {
    display: flex;
    align-items: center;
    gap: 1rem;
  }

  :global(.assistant-avatar) {
    width: 48px;
    height: 48px;
    background: linear-gradient(135deg, rgba(59, 130, 246, 0.2), rgba(139, 92, 246, 0.2));
    border-radius: 0.75rem;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 1.5rem;
  }

  :global(.assistant-info h2) {
    margin: 0;
    color: white;
    font-size: 1.125rem;
    font-weight: 600;
  }

  :global(.assistant-info p) {
    margin: 0.25rem 0 0;
    color: #9ca3af;
    font-size: 0.875rem;
  }

  :global(.quick-actions) {
    display: flex;
    gap: 0.5rem;
    padding: 1rem 1.5rem;
    border-bottom: 1px solid rgba(75, 85, 99, 0.3);
  }

  :global(.quick-action-btn) {
    padding: 0.375rem 0.75rem;
    background: rgba(139, 92, 246, 0.1);
    border: 1px solid rgba(139, 92, 246, 0.3);
    border-radius: 999px;
    color: #a78bfa;
    font-size: 0.875rem;
    cursor: pointer;
    transition: all 0.2s;
    white-space: nowrap;
  }

  :global(.quick-action-btn:hover) {
    background: rgba(139, 92, 246, 0.2);
    border-color: rgba(139, 92, 246, 0.5);
  }

  :global(.quick-templates) {
    padding: 0 1.5rem 1rem;
    border-bottom: 1px solid rgba(75, 85, 99, 0.3);
  }

  :global(.template-btn) {
    padding: 0.375rem 0.75rem;
    background: rgba(20, 184, 166, 0.1);
    border: 1px solid rgba(20, 184, 166, 0.3);
    border-radius: 0.375rem;
    color: #14b8a6;
    font-size: 0.875rem;
    font-weight: 500;
    cursor: pointer;
    transition: all 0.2s;
  }

  :global(.template-btn:hover) {
    background: rgba(20, 184, 166, 0.2);
    border-color: rgba(20, 184, 166, 0.5);
  }

  :global(.chat-container) {
    flex: 1;
    display: flex;
    flex-direction: column;
    overflow: hidden;
  }

  :global(.chat-messages) {
    flex: 1;
    padding: 1.5rem;
    overflow-y: auto;
    display: flex;
    flex-direction: column;
    gap: 1rem;
  }

  :global(.message) {
    display: flex;
    gap: 0.75rem;
    animation: messageSlide 0.3s ease;
  }

  @keyframes messageSlide {
    from {
      opacity: 0;
      transform: translateY(10px);
    }
    to {
      opacity: 1;
      transform: translateY(0);
    }
  }

  :global(.message-avatar) {
    width: 32px;
    height: 32px;
    background: rgba(139, 92, 246, 0.2);
    border-radius: 0.5rem;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 0.75rem;
    font-weight: 600;
    color: #a78bfa;
    flex-shrink: 0;
  }

  :global(.message-user .message-avatar) {
    background: rgba(59, 130, 246, 0.2);
    color: #60a5fa;
  }

  :global(.message-content) {
    flex: 1;
    padding: 0.75rem;
    background: rgba(31, 41, 55, 0.5);
    border-radius: 0.5rem;
    color: #e5e7eb;
    font-size: 0.9375rem;
    line-height: 1.5;
  }

  :global(.message-user .message-content) {
    background: rgba(59, 130, 246, 0.1);
  }

  :global(.chat-input) {
    display: flex;
    gap: 0.75rem;
    padding: 1.5rem;
    border-top: 1px solid rgba(75, 85, 99, 0.3);
  }

  :global(.chat-input-field) {
    flex: 1;
    padding: 0.75rem;
    background: rgba(31, 41, 55, 0.5);
    border: 1px solid rgba(75, 85, 99, 0.5);
    border-radius: 0.5rem;
    color: white;
    font-size: 0.9375rem;
    transition: all 0.2s;
  }

  :global(.chat-input-field::placeholder) {
    color: #6b7280;
  }

  :global(.chat-input-field:focus) {
    outline: none;
    border-color: rgba(139, 92, 246, 0.5);
    background: rgba(31, 41, 55, 0.7);
  }

  :global(.send-btn) {
    padding: 0.75rem;
    background: #7c3aed;
    border: none;
    border-radius: 0.5rem;
    color: white;
    cursor: pointer;
    transition: all 0.2s;
  }

  :global(.send-btn:hover) {
    background: #6d28d9;
    transform: translateY(-1px);
  }

  @media (max-width: 1024px) {
    .page-container-split {
      grid-template-columns: 1fr;
      height: auto;
    }

    :global(.chat-panel) {
      height: 500px;
    }
  }
</style>