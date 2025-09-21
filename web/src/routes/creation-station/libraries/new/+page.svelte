<script lang="ts">
  import { creationAPI } from '$lib/api.creationstation';
  import { goto } from '$app/navigation';
  import CreatorChat from '$lib/components/CreatorChat.svelte';

  let libraryName = '';
  let slug = '';
  let description = '';
  let chunkSize = 1000;
  let chunkOverlap = 200;
  let files: FileList | null = null;
  let message: string | null = null;
  let error: string | null = null;
  let submitting = false;
  
  const assistantIntro =
    "Hello! I'm Libby. Let's organize your educational content into a powerful knowledge base. I can help you structure documents, optimize chunks, and set up metadata for better AI retrieval.";
  const quickActions = ['Organize docs', 'Add metadata', 'Optimize chunks'];

  async function handleSubmit(event: SubmitEvent) {
    event.preventDefault();
    submitting = true;
    message = null;
    error = null;

    try {
      await creationAPI.libraries.create({
        slug,
        name: libraryName,
        description,
        chunk_size: chunkSize,
        chunk_overlap: chunkOverlap
      });
      message = 'Library created successfully.';
      setTimeout(() => {
        goto('/creation-station/libraries');
      }, 800);
    } catch (err) {
      error = err instanceof Error ? err.message : 'Failed to create library';
    } finally {
      submitting = false;
    }
  }

  const handleImport = () => {
    // Import functionality
  };

  const handleNewLibrary = () => {
    libraryName = '';
    slug = '';
    description = '';
    chunkSize = 1000;
    chunkOverlap = 200;
    files = null;
    message = null;
    error = null;
  };

  let fileInput: HTMLInputElement;
</script>

<svelte:head>
  <title>New Library · Creation Station</title>
</svelte:head>

<main class="libraries-page">
  <div class="page-container-split">
    <!-- Left Panel - Form -->
    <section class="form-panel">
      <header class="panel-header">
        <div class="header-left">
          <a href="/creation-station/libraries" class="back-link">
            <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
              <path d="M19 12H5M12 19l-7-7 7-7"/>
            </svg>
          </a>
          <h1>Knowledge Libraries</h1>
        </div>
        <p class="subtitle">Build RAG knowledge bases from documents</p>
      </header>

      <div class="form-actions">
        <button class="btn-secondary" on:click={handleImport}>Import</button>
        <button class="btn-primary" on:click={handleNewLibrary}>
          <span>+</span> New Library
        </button>
      </div>

      <form class="library-form" on:submit|preventDefault={handleSubmit}>
        <div class="form-group">
          <label for="library-name">LIBRARY NAME</label>
          <input 
            id="library-name" 
            bind:value={libraryName} 
            required 
            placeholder="e.g., US History Resources"
            class="form-input" 
          />
        </div>

        <div class="form-group">
          <label for="slug">SLUG</label>
          <input 
            id="slug" 
            bind:value={slug} 
            required
            placeholder="us_history_resources"
            class="form-input" 
          />
        </div>

        <div class="form-group">
          <label for="description">DESCRIPTION</label>
          <textarea 
            id="description" 
            bind:value={description} 
            rows="3"
            placeholder="A comprehensive collection of US History documents, timelines, and primary sources..."
            class="form-textarea"
          ></textarea>
        </div>

        <div class="form-row">
          <div class="form-group">
            <label for="chunk-size">CHUNK SIZE</label>
            <input 
              id="chunk-size" 
              type="number"
              bind:value={chunkSize} 
              required
              class="form-input" 
            />
          </div>
          <div class="form-group">
            <label for="chunk-overlap">CHUNK OVERLAP</label>
            <input 
              id="chunk-overlap" 
              type="number"
              bind:value={chunkOverlap} 
              required
              class="form-input" 
            />
          </div>
        </div>

        <div class="form-group">
          <label for="files">DOCUMENTS</label>
          <div class="file-upload-area">
            <input 
              id="files"
              type="file" 
              bind:files
              bind:this={fileInput}
              multiple
              accept=".pdf,.txt,.md,.docx"
              class="file-input"
            />
            <div class="file-upload-label" on:click={() => fileInput.click()}>
              <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/>
                <polyline points="17 8 12 3 7 8"/>
                <line x1="12" y1="3" x2="12" y2="15"/>
              </svg>
              <span>Click to upload or drag and drop</span>
              <small>PDF, TXT, MD, DOCX files accepted</small>
            </div>
            {#if files && files.length > 0}
              <div class="file-list">
                {#each Array.from(files) as file}
                  <div class="file-item">
                    <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                      <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/>
                      <polyline points="14 2 14 8 20 8"/>
                    </svg>
                    <span>{file.name}</span>
                    <span class="file-size">({(file.size / 1024).toFixed(1)} KB)</span>
                  </div>
                {/each}
              </div>
            {/if}
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
            {submitting ? 'Creating...' : 'Create Library'}
          </button>
        </div>
      </form>
    </section>

    <!-- Right Panel - Chat -->
    <CreatorChat
      helperKey="libraries"
      assistantName="LibraryBuilder"
      assistantDescription="Your knowledge architect"
      assistantAvatar="📚"
      initialMessage={assistantIntro}
      quickActions={quickActions}
      placeholder="Ask LibraryBuilder..."
    />
  </div>
</main>

<style>
  .libraries-page {
    min-height: 100vh;
    background: linear-gradient(135deg, #0f0f23 0%, #1a0f2e 50%, #0f0f23 100%);
    padding: 2rem;
  }

  .page-container-split {
    max-width: 1400px;
    margin: 0 auto;
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 2rem;
    height: calc(100vh - 8rem);
  }

  /* Left Panel Styles */
  .form-panel {
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

  .library-form {
    display: flex;
    flex-direction: column;
    gap: 1.25rem;
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

  .form-input,
  .form-textarea {
    width: 100%;
    padding: 0.75rem;
    background: rgba(31, 41, 55, 0.5);
    border: 1px solid rgba(75, 85, 99, 0.5);
    border-radius: 0.5rem;
    color: white;
    font-size: 0.9375rem;
    transition: all 0.2s;
  }

  .form-input::placeholder,
  .form-textarea::placeholder {
    color: #6b7280;
  }

  .form-input:focus,
  .form-textarea:focus {
    outline: none;
    border-color: rgba(139, 92, 246, 0.5);
    background: rgba(31, 41, 55, 0.7);
  }

  .form-textarea {
    resize: vertical;
    font-family: inherit;
    line-height: 1.5;
  }

  .form-row {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 1rem;
  }

  .file-upload-area {
    position: relative;
  }

  .file-input {
    position: absolute;
    width: 0;
    height: 0;
    opacity: 0;
  }

  .file-upload-label {
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    gap: 0.5rem;
    padding: 2rem;
    background: rgba(31, 41, 55, 0.3);
    border: 2px dashed rgba(139, 92, 246, 0.3);
    border-radius: 0.5rem;
    cursor: pointer;
    transition: all 0.2s;
  }

  .file-upload-label:hover {
    background: rgba(31, 41, 55, 0.5);
    border-color: rgba(139, 92, 246, 0.5);
  }

  .file-upload-label span {
    color: #d1d5db;
    font-weight: 500;
  }

  .file-upload-label small {
    color: #6b7280;
    font-size: 0.75rem;
  }

  .file-list {
    margin-top: 1rem;
    display: flex;
    flex-direction: column;
    gap: 0.5rem;
  }

  .file-item {
    display: flex;
    align-items: center;
    gap: 0.5rem;
    padding: 0.5rem;
    background: rgba(31, 41, 55, 0.5);
    border-radius: 0.375rem;
    color: #d1d5db;
    font-size: 0.875rem;
  }

  .file-size {
    margin-left: auto;
    color: #6b7280;
    font-size: 0.75rem;
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
    background: linear-gradient(135deg, rgba(20, 184, 166, 0.2), rgba(139, 92, 246, 0.2));
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