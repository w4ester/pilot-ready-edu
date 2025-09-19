<script lang="ts">
  let promptTitle = '';
  let slashCommand = '';
  let promptContent = '';
  let accessControl = 'Private - Only me';
  
  let chatMessage = '';
  let chatHistory = [
    {
      role: 'assistant',
      content: "Hi! I'm PromptCrafter, your prompt engineering specialist. I can help you create effective prompts for any educational scenario. What kind of prompt would you like to create today?"
    }
  ];

  const handleImport = () => {
    // Import functionality
  };

  const handleNewPrompt = () => {
    promptTitle = '';
    slashCommand = '';
    promptContent = '';
    accessControl = 'Private - Only me';
  };

  const sendMessage = () => {
    if (chatMessage.trim()) {
      chatHistory = [...chatHistory, { role: 'user', content: chatMessage }];
      chatMessage = '';
      // Add AI response logic here
      setTimeout(() => {
        chatHistory = [...chatHistory, { 
          role: 'assistant', 
          content: "I can help you improve that prompt! Consider adding more specific instructions and examples to make it clearer for the AI."
        }];
      }, 500);
    }
  };

  const quickActions = [
    'Improve clarity',
    'Add examples',
    'Better structure'
  ];
</script>

<svelte:head>
  <title>New Prompt · Creation Station</title>
</svelte:head>

<main class="prompts-page">
  <div class="page-container">
    <!-- Left Panel - Form -->
    <section class="form-panel">
      <header class="panel-header">
        <div class="header-left">
          <a href="/creation-station/prompts" class="back-link">
            <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
              <path d="M19 12H5M12 19l-7-7 7-7"/>
            </svg>
          </a>
          <h1>New Prompt</h1>
        </div>
        <p class="subtitle">Create a reusable prompt with AI assistance</p>
      </header>

      <div class="form-actions">
        <button class="btn-secondary" on:click={handleImport}>Import</button>
        <button class="btn-primary" on:click={handleNewPrompt}>
          <span>+</span> New Prompt
        </button>
      </div>

      <form class="prompt-form">
        <div class="form-group">
          <label for="prompt-title">PROMPT TITLE</label>
          <input 
            id="prompt-title"
            type="text" 
            bind:value={promptTitle}
            placeholder="e.g., Essay Writing Assistant"
            class="form-input"
          />
        </div>

        <div class="form-group">
          <label for="slash-command">SLASH COMMAND</label>
          <input 
            id="slash-command"
            type="text" 
            bind:value={slashCommand}
            placeholder="/essay-helper"
            class="form-input"
          />
        </div>

        <div class="form-group">
          <label for="prompt-content">PROMPT CONTENT</label>
          <textarea 
            id="prompt-content"
            bind:value={promptContent}
            placeholder="You are an expert essay writing assistant..."
            rows="10"
            class="form-textarea"
          ></textarea>
        </div>

        <div class="form-group">
          <label for="access-control">ACCESS CONTROL</label>
          <select 
            id="access-control"
            bind:value={accessControl}
            class="form-select"
          >
            <option>Private - Only me</option>
            <option>Classroom - My students</option>
            <option>Public - All users</option>
          </select>
        </div>
      </form>
    </section>

    <!-- Right Panel - Chat -->
    <section class="chat-panel">
      <header class="chat-header">
        <div class="assistant-info">
          <div class="assistant-avatar">
            <span>✨</span>
          </div>
          <div>
            <h2>PromptCraft</h2>
            <p>Your prompt engineering assistant</p>
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
                  <span>U</span>
                {/if}
              </div>
              <div class="message-content">
                {message.content}
              </div>
            </div>
          {/each}
        </div>

        <div class="chat-input">
          <input 
            type="text" 
            bind:value={chatMessage}
            placeholder="Ask PromptCraft..."
            on:keydown={(e) => e.key === 'Enter' && sendMessage()}
            class="chat-input-field"
          />
          <button on:click={sendMessage} class="send-btn">
            <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
              <path d="M22 2L11 13M22 2l-7 20-4-9-9-4 20-7z"/>
            </svg>
          </button>
        </div>
      </div>
    </section>
  </div>
</main>

<style>
  .prompts-page {
    min-height: 100vh;
    background: linear-gradient(135deg, #0f0f23 0%, #1a0f2e 50%, #0f0f23 100%);
  }

  .page-container {
    display: grid;
    grid-template-columns: 1fr 1fr;
    height: 100vh;
  }

  /* Left Panel - Form */
  .form-panel {
    padding: 2rem 3rem;
    background: rgba(17, 24, 39, 0.8);
    border-right: 1px solid rgba(139, 92, 246, 0.2);
    overflow-y: auto;
  }

  .panel-header {
    margin-bottom: 2rem;
  }

  .header-left {
    display: flex;
    align-items: center;
    gap: 1rem;
    margin-bottom: 0.5rem;
  }

  .back-link {
    display: flex;
    align-items: center;
    justify-content: center;
    width: 36px;
    height: 36px;
    border-radius: 0.5rem;
    background: rgba(139, 92, 246, 0.1);
    border: 1px solid rgba(139, 92, 246, 0.2);
    color: #a78bfa;
    transition: all 0.2s;
  }

  .back-link:hover {
    background: rgba(139, 92, 246, 0.2);
    color: #c4b5fd;
  }

  .panel-header h1 {
    margin: 0;
    font-size: 1.5rem;
    font-weight: bold;
    color: white;
  }

  .subtitle {
    margin: 0;
    font-size: 0.875rem;
    color: #9ca3af;
  }

  .form-actions {
    display: flex;
    gap: 1rem;
    margin-bottom: 2rem;
  }

  .btn-secondary {
    padding: 0.625rem 1.25rem;
    background: transparent;
    border: 1px solid rgba(139, 92, 246, 0.3);
    color: #a78bfa;
    border-radius: 0.5rem;
    font-size: 0.875rem;
    font-weight: 500;
    cursor: pointer;
    transition: all 0.2s;
  }

  .btn-secondary:hover {
    background: rgba(139, 92, 246, 0.1);
    border-color: rgba(139, 92, 246, 0.5);
  }

  .btn-primary {
    padding: 0.625rem 1.25rem;
    background: #7c3aed;
    border: none;
    color: white;
    border-radius: 0.5rem;
    font-size: 0.875rem;
    font-weight: 500;
    cursor: pointer;
    display: flex;
    align-items: center;
    gap: 0.5rem;
    transition: all 0.2s;
  }

  .btn-primary:hover {
    background: #6d28d9;
  }

  .btn-primary span {
    font-size: 1.25rem;
    line-height: 1;
  }

  /* Form Styles */
  .prompt-form {
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
    text-transform: uppercase;
    letter-spacing: 0.1em;
    color: #9ca3af;
  }

  .form-input,
  .form-textarea,
  .form-select {
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
  .form-textarea:focus,
  .form-select:focus {
    outline: none;
    border-color: rgba(139, 92, 246, 0.5);
    background: rgba(31, 41, 55, 0.7);
  }

  .form-textarea {
    resize: vertical;
    min-height: 200px;
    font-family: inherit;
  }

  .form-select {
    cursor: pointer;
  }

  /* Right Panel - Chat */
  .chat-panel {
    padding: 2rem;
    background: rgba(10, 10, 20, 0.9);
    display: flex;
    flex-direction: column;
    overflow: hidden;
  }

  .chat-header {
    margin-bottom: 1.5rem;
  }

  .assistant-info {
    display: flex;
    align-items: center;
    gap: 1rem;
  }

  .assistant-avatar {
    width: 48px;
    height: 48px;
    border-radius: 0.75rem;
    background: linear-gradient(135deg, #a78bfa, #6366f1);
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 1.5rem;
  }

  .assistant-info h2 {
    margin: 0;
    font-size: 1.125rem;
    font-weight: bold;
    color: white;
  }

  .assistant-info p {
    margin: 0;
    font-size: 0.875rem;
    color: #9ca3af;
  }

  .quick-actions {
    display: flex;
    gap: 0.75rem;
    margin-bottom: 1.5rem;
  }

  .quick-action-btn {
    padding: 0.5rem 1rem;
    background: rgba(31, 41, 55, 0.8);
    border: 1px solid rgba(75, 85, 99, 0.5);
    border-radius: 0.5rem;
    color: #d1d5db;
    font-size: 0.875rem;
    cursor: pointer;
    transition: all 0.2s;
  }

  .quick-action-btn:hover {
    background: rgba(31, 41, 55, 1);
    border-color: rgba(139, 92, 246, 0.3);
  }

  .chat-container {
    flex: 1;
    display: flex;
    flex-direction: column;
    background: rgba(17, 24, 39, 0.5);
    border-radius: 1rem;
    padding: 1.5rem;
    border: 1px solid rgba(75, 85, 99, 0.3);
  }

  .chat-messages {
    flex: 1;
    overflow-y: auto;
    padding-right: 0.5rem;
    margin-bottom: 1.5rem;
  }

  .message {
    display: flex;
    gap: 1rem;
    margin-bottom: 1.5rem;
  }

  .message-avatar {
    width: 32px;
    height: 32px;
    border-radius: 0.5rem;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 0.75rem;
    font-weight: bold;
    flex-shrink: 0;
  }

  .message-assistant .message-avatar {
    background: linear-gradient(135deg, #3b82f6, #6366f1);
    color: white;
  }

  .message-user .message-avatar {
    background: linear-gradient(135deg, #10b981, #14b8a6);
    color: white;
  }

  .message-content {
    flex: 1;
    padding: 0.875rem;
    background: rgba(31, 41, 55, 0.5);
    border-radius: 0.75rem;
    color: #e5e7eb;
    font-size: 0.9375rem;
    line-height: 1.6;
  }

  .chat-input {
    display: flex;
    gap: 0.75rem;
  }

  .chat-input-field {
    flex: 1;
    padding: 0.75rem;
    background: rgba(31, 41, 55, 0.8);
    border: 1px solid rgba(75, 85, 99, 0.5);
    border-radius: 0.5rem;
    color: white;
    font-size: 0.9375rem;
  }

  .chat-input-field::placeholder {
    color: #6b7280;
  }

  .chat-input-field:focus {
    outline: none;
    border-color: rgba(139, 92, 246, 0.5);
  }

  .send-btn {
    padding: 0.75rem;
    background: #7c3aed;
    border: none;
    border-radius: 0.5rem;
    color: white;
    cursor: pointer;
    display: flex;
    align-items: center;
    justify-content: center;
    transition: all 0.2s;
  }

  .send-btn:hover {
    background: #6d28d9;
  }

  /* Scrollbar Styles */
  .chat-messages::-webkit-scrollbar {
    width: 6px;
  }

  .chat-messages::-webkit-scrollbar-track {
    background: rgba(31, 41, 55, 0.3);
    border-radius: 3px;
  }

  .chat-messages::-webkit-scrollbar-thumb {
    background: rgba(139, 92, 246, 0.3);
    border-radius: 3px;
  }

  .chat-messages::-webkit-scrollbar-thumb:hover {
    background: rgba(139, 92, 246, 0.5);
  }

  @media (max-width: 1024px) {
    .page-container {
      grid-template-columns: 1fr;
    }

    .chat-panel {
      display: none;
    }
  }
</style>