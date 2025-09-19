<script lang="ts">
  import { creationAPI } from '$lib/api.creationstation';
  import type { ChatMessage } from '$lib/api.creationstation';
  import { goto } from '$app/navigation';

  let slug = '';
  let name = '';
  let language = 'python';
  let entrypoint = 'run';
  let content = 'def run(input):\n    return input';
  let requirements = '';
  let message: string | null = null;
  let error: string | null = null;
  let submitting = false;

  let chatMessage = '';
  let assistantLoading = false;
  let chatError: string | null = null;
  let chatHistory: ChatMessage[] = [
    {
      role: 'assistant',
      content: "Hi! I'm ToolForge, your AI assistant for creating powerful educational tools. I can help you write Python functions, suggest integrations, and optimize your code. What kind of tool would you like to create?"
    }
  ];

  const STREAM_DELAY_MS = 20;

  const delay = (ms: number) => new Promise((resolve) => setTimeout(resolve, ms));

  const streamAssistantMessage = async (content: string) => {
    const insertionIndex = chatHistory.length;
    chatHistory = [...chatHistory, { role: 'assistant', content: '' }];

    const tokens = content.split(/(\s+)/);
    let assembled = '';
    for (const token of tokens) {
      assembled += token;
      chatHistory = chatHistory.map((message, index) =>
        index === insertionIndex ? { ...message, content: assembled } : message
      );
      await delay(STREAM_DELAY_MS);
    }
  };

  async function handleSubmit(event: SubmitEvent) {
    event.preventDefault();
    submitting = true;
    message = null;
    error = null;

    try {
      await creationAPI.tools.create({
        slug,
        name,
        language,
        entrypoint,
        content,
        requirements: requirements || undefined,
      });
      message = 'Tool created successfully.';
      setTimeout(() => {
        goto('/creation-station/tools');
      }, 800);
    } catch (err) {
      error = err instanceof Error ? err.message : 'Failed to create tool';
    } finally {
      submitting = false;
    }
  }

  const handleImport = () => {
    // Import functionality
  };

  const handleNewTool = () => {
    slug = '';
    name = '';
    language = 'python';
    entrypoint = 'run';
    content = 'def run(input):\n    return input';
    requirements = '';
    message = null;
    error = null;
  };

  const sendMessage = async () => {
    const trimmed = chatMessage.trim();
    if (!trimmed || assistantLoading) {
      return;
    }

    const userMessage: ChatMessage = { role: 'user', content: trimmed };
    chatHistory = [...chatHistory, userMessage];
    chatMessage = '';
    chatError = null;
    assistantLoading = true;

    const historyForRequest = [...chatHistory];

    try {
      const response = await creationAPI.tools.assistant({ messages: historyForRequest });
      const assistantMessages = Array.isArray(response?.messages) ? response.messages : [];

      if (assistantMessages.length === 0) {
        await streamAssistantMessage("I'm thinking, but I don't have any suggestions right now. Try rephrasing your request.");
        return;
      }

      for (const assistantMessage of assistantMessages) {
        await streamAssistantMessage(assistantMessage.content);
      }
    } catch (err) {
      chatError = err instanceof Error ? err.message : 'Failed to fetch assistant suggestions.';
      chatHistory = [
        ...historyForRequest,
        {
          role: 'assistant',
          content: 'Sorry, I ran into an issue retrieving suggestions. Please try again.',
        },
      ];
    } finally {
      assistantLoading = false;
    }
  };

  const quickActions = [
    'Debug code',
    'Add error handling',
    'Optimize performance',
    'Generate tests'
  ];
</script>

<svelte:head>
  <title>New Tool · Creation Station</title>
</svelte:head>

<main class="tools-page">
  <div class="page-container-split">
    <!-- Left Panel - Form -->
    <section class="form-panel">
      <header class="panel-header">
        <div class="header-left">
          <a href="/creation-station/tools" class="back-link">
            <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
              <path d="M19 12H5M12 19l-7-7 7-7"/>
            </svg>
          </a>
          <h1>New Tool</h1>
        </div>
        <p class="subtitle">Create a Python function with AI assistance</p>
      </header>

      <div class="form-actions">
        <button class="btn-secondary" on:click={handleImport}>Import</button>
        <button class="btn-primary" on:click={handleNewTool}>
          <span>+</span> New Tool
        </button>
      </div>

      <form class="tool-form" on:submit|preventDefault={handleSubmit}>
        <div class="form-group">
          <label for="slug">SLUG</label>
          <input 
            id="slug" 
            bind:value={slug} 
            required 
            placeholder="summarize_tool"
            class="form-input" 
          />
        </div>

        <div class="form-group">
          <label for="name">DISPLAY NAME</label>
          <input 
            id="name" 
            bind:value={name} 
            required
            placeholder="Summarize Tool"
            class="form-input" 
          />
        </div>

        <div class="form-row">
          <div class="form-group">
            <label for="language">LANGUAGE</label>
            <input 
              id="language" 
              bind:value={language} 
              required
              class="form-input" 
            />
          </div>
          <div class="form-group">
            <label for="entrypoint">ENTRYPOINT</label>
            <input 
              id="entrypoint" 
              bind:value={entrypoint} 
              required
              class="form-input" 
            />
          </div>
        </div>

        <div class="form-group">
          <label for="content">CODE</label>
          <textarea 
            id="content" 
            bind:value={content} 
            rows="12"
            class="form-textarea code-editor"
            spellcheck="false"
          ></textarea>
        </div>

        <div class="form-group">
          <label for="requirements">REQUIREMENTS (OPTIONAL)</label>
          <textarea 
            id="requirements" 
            bind:value={requirements} 
            rows="3"
            placeholder="numpy==1.21.0&#10;pandas==1.3.0"
            class="form-textarea"
          ></textarea>
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
            {submitting ? 'Creating...' : 'Create Tool'}
          </button>
        </div>
      </form>
    </section>

    <!-- Right Panel - Chat -->
    <section class="chat-panel">
      <header class="chat-header">
        <div class="assistant-info">
          <div class="assistant-avatar">
            <span>🛠️</span>
          </div>
          <div>
            <h2>ToolForge</h2>
            <p>Your code assistant</p>
          </div>
        </div>
      </header>

      <div class="quick-actions">
        {#each quickActions as action}
          <button class="quick-action-btn">{action}</button>
        {/each}
      </div>

      <div class="chat-container">
        <div class="chat-messages">
          {#each chatHistory as message}
            <div class="message message-{message.role}">
              <div class="message-avatar">
                {#if message.role === 'assistant'}
                  <span>AI</span>
                {:else}
                  <span>You</span>
                {/if}
              </div>
              <div class="message-content">
                {message.content}
              </div>
            </div>
          {/each}
        </div>

        {#if chatError}
          <div class="chat-error" role="alert">
            <span aria-hidden="true">⚠️</span>
            <span>{chatError}</span>
          </div>
        {/if}

        <div class="chat-input-container">
          <input
            type="text"
            bind:value={chatMessage}
            on:keydown={(e) => {
              if (e.key === 'Enter') {
                e.preventDefault();
                void sendMessage();
              }
            }}
            placeholder="Ask ToolForge for help..."
            class="chat-input"
            disabled={assistantLoading}
          />
          <button
            on:click={() => {
              void sendMessage();
            }}
            class="send-btn"
            disabled={assistantLoading || !chatMessage.trim()}
          >
            <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <line x1="22" y1="2" x2="11" y2="13"></line>
              <polygon points="22 2 15 22 11 13 2 9 22 2"></polygon>
            </svg>
          </button>
        </div>
      </div>
    </section>
  </div>
</main>

<style>
  .tools-page {
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

  .tool-form {
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

  .code-editor {
    font-family: 'Monaco', 'Menlo', 'Ubuntu Mono', monospace;
    font-size: 0.875rem;
  }

  .form-row {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 1rem;
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
  .chat-panel {
    background: rgba(17, 24, 39, 0.8);
    border-radius: 1rem;
    border: 1px solid rgba(139, 92, 246, 0.2);
    display: flex;
    flex-direction: column;
    overflow: hidden;
  }

  .chat-header {
    padding: 1.5rem;
    border-bottom: 1px solid rgba(75, 85, 99, 0.3);
  }

  .assistant-info {
    display: flex;
    align-items: center;
    gap: 1rem;
  }

  .assistant-avatar {
    width: 48px;
    height: 48px;
    background: linear-gradient(135deg, rgba(236, 72, 153, 0.2), rgba(139, 92, 246, 0.2));
    border-radius: 0.75rem;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 1.5rem;
  }

  .assistant-info h2 {
    margin: 0;
    color: white;
    font-size: 1.125rem;
    font-weight: 600;
  }

  .assistant-info p {
    margin: 0.25rem 0 0;
    color: #9ca3af;
    font-size: 0.875rem;
  }

  .quick-actions {
    display: flex;
    gap: 0.5rem;
    padding: 1rem 1.5rem;
    border-bottom: 1px solid rgba(75, 85, 99, 0.3);
  }

  .quick-action-btn {
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

  .quick-action-btn:hover {
    background: rgba(139, 92, 246, 0.2);
    border-color: rgba(139, 92, 246, 0.5);
  }

  .chat-container {
    flex: 1;
    display: flex;
    flex-direction: column;
    overflow: hidden;
  }

  .chat-messages {
    flex: 1;
    padding: 1.5rem;
    overflow-y: auto;
    display: flex;
    flex-direction: column;
    gap: 1rem;
  }

  .message {
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

  .message-avatar {
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

  .message-user .message-avatar {
    background: rgba(59, 130, 246, 0.2);
    color: #60a5fa;
  }

  .message-content {
    flex: 1;
    padding: 0.75rem;
    background: rgba(31, 41, 55, 0.5);
    border-radius: 0.5rem;
    color: #e5e7eb;
    font-size: 0.9375rem;
    line-height: 1.5;
  }

  .message-user .message-content {
    background: rgba(59, 130, 246, 0.1);
  }

  .chat-input-container {
    display: flex;
    gap: 0.75rem;
    padding: 1.5rem;
    border-top: 1px solid rgba(75, 85, 99, 0.3);
  }

  .chat-input {
    flex: 1;
    padding: 0.75rem;
    background: rgba(31, 41, 55, 0.5);
    border: 1px solid rgba(75, 85, 99, 0.5);
    border-radius: 0.5rem;
    color: white;
    font-size: 0.9375rem;
    transition: all 0.2s;
  }

  .chat-input::placeholder {
    color: #6b7280;
  }

  .chat-input:focus {
    outline: none;
    border-color: rgba(139, 92, 246, 0.5);
    background: rgba(31, 41, 55, 0.7);
  }

  .chat-input:disabled {
    opacity: 0.6;
    cursor: not-allowed;
  }

  .chat-error {
    margin: 0 1.5rem;
    padding: 0.75rem 1rem;
    background: rgba(239, 68, 68, 0.15);
    color: #fca5a5;
    border-radius: 0.5rem;
    display: flex;
    align-items: center;
    gap: 0.5rem;
    font-size: 0.875rem;
  }

  .send-btn {
    padding: 0.75rem;
    background: #7c3aed;
    border: none;
    border-radius: 0.5rem;
    color: white;
    cursor: pointer;
    transition: all 0.2s;
  }

  .send-btn:hover {
    background: #6d28d9;
    transform: translateY(-1px);
  }

  .send-btn:disabled {
    opacity: 0.6;
    cursor: not-allowed;
    transform: none;
  }

  @media (max-width: 1024px) {
    .page-container-split {
      grid-template-columns: 1fr;
      height: auto;
    }

    .chat-panel {
      height: 500px;
    }
  }
</style>