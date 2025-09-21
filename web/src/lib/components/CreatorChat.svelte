<script lang="ts">
  import { onMount, tick } from 'svelte';
  import { page } from '$app/stores';
  import { get } from 'svelte/store';
  import { creationAPI } from '$lib/api.creationstation';
  import type { RoomMessageOut } from '$lib/api.creationstation';

  type QuickAction = string | { label: string; prompt?: string };

  type ChatMessage = {
    id: string;
    role: 'assistant' | 'user';
    content: string;
    created_at?: number | null;
    isSynthetic?: boolean;
  };

  const HELPER_ROOM_PREFIX = 'Creator Helper · ';

  export let helperKey: string;
  export let assistantName: string;
  export let assistantDescription: string;
  export let assistantAvatar: string = '✨';
  export let initialMessage: string = '';
  export let placeholder: string = 'Ask the assistant…';
  export let quickActions: QuickAction[] = [];
  export let roomDescription: string | undefined = undefined;
  export let messageLimit = 50;

  const initialSyntheticMessage: ChatMessage | null = initialMessage
    ? {
        id: 'creator-chat-initial',
        role: 'assistant',
        content: initialMessage,
        isSynthetic: true
      }
    : null;

  let roomId: string | null = null;
  let chatHistory: ChatMessage[] = initialSyntheticMessage ? [initialSyntheticMessage] : [];
  let messageText = '';
  let isInitializing = false;
  let isReady = false;
  let isSending = false;
  let isAwaitingAssistant = false;
  let error: string | null = null;
  let transcriptEl: HTMLDivElement | null = null;
  let inputEl: HTMLInputElement | null = null;
  let pollTimer: ReturnType<typeof setTimeout> | null = null;

  const helperRoomName = `${HELPER_ROOM_PREFIX}${helperKey}`;

  function currentUserId(): string | null {
    return get(page).data?.user?.user_id ?? null;
  }

  function scrollToBottom(): void {
    if (!transcriptEl) return;
    transcriptEl.scrollTop = transcriptEl.scrollHeight;
  }

  function applyMessages(messages: ChatMessage[]): void {
    if (initialSyntheticMessage) {
      chatHistory = [initialSyntheticMessage, ...messages];
    } else {
      chatHistory = messages;
    }
    void tick().then(() => scrollToBottom());
  }

  function cancelPoll(): void {
    if (pollTimer) {
      clearTimeout(pollTimer);
      pollTimer = null;
    }
  }

  function schedulePoll(): void {
    if (pollTimer) return;
    pollTimer = setTimeout(async () => {
      pollTimer = null;
      try {
        await refreshMessages();
      } catch (err) {
        console.error('Failed to refresh chat messages', err);
      }
      if (isAwaitingAssistant) {
        schedulePoll();
      }
    }, 2000);
  }

  function updateAwaitingAssistant(): void {
    const messages = chatHistory.filter((msg) => !msg.isSynthetic);
    if (messages.length === 0) {
      isAwaitingAssistant = false;
      cancelPoll();
      return;
    }

    const lastUserMessage = [...messages].reverse().find((msg) => msg.role === 'user');
    if (!lastUserMessage) {
      isAwaitingAssistant = false;
      cancelPoll();
      return;
    }

    const lastUserTimestamp = lastUserMessage.created_at ?? 0;
    const hasAssistantReply = messages.some(
      (msg) =>
        msg.role === 'assistant' &&
        (msg.created_at ?? 0) >= lastUserTimestamp &&
        msg.id !== lastUserMessage.id
    );

    const waiting = !hasAssistantReply;
    if (waiting !== isAwaitingAssistant) {
      isAwaitingAssistant = waiting;
      if (waiting) {
        schedulePoll();
      } else {
        cancelPoll();
      }
    } else if (waiting) {
      schedulePoll();
    }
  }

  function mapMessages(raw: RoomMessageOut[]): ChatMessage[] {
    const userId = currentUserId();
    const ordered = [...raw].reverse();
    return ordered.map((msg) => ({
      id: msg.id,
      role: userId && msg.user_id === userId ? 'user' : 'assistant',
      content: msg.content,
      created_at: msg.created_at
    }));
  }

  async function ensureRoom(): Promise<string> {
    if (roomId) {
      return roomId;
    }

    const rooms = await creationAPI.rooms.list();
    const existing = rooms.find((room) => room.name === helperRoomName);
    if (existing) {
      roomId = existing.id;
      return existing.id;
    }

    const created = await creationAPI.rooms.create({
      name: helperRoomName,
      description: roomDescription ?? `Helper chat for ${helperKey}`,
      channel_type: 'assistant_helper',
      data: { helper_key: helperKey },
      meta: { assistant_name: assistantName }
    });
    roomId = created.id;
    return created.id;
  }

  async function refreshMessages(): Promise<void> {
    if (!roomId) return;
    const messages = await creationAPI.rooms.messages.list(roomId, messageLimit);
    applyMessages(mapMessages(messages));
    updateAwaitingAssistant();
  }

  async function initialize(): Promise<void> {
    isInitializing = true;
    error = null;
    try {
      await ensureRoom();
      await refreshMessages();
      isReady = true;
    } catch (err) {
      const message = err instanceof Error ? err.message : 'Failed to initialize chat';
      error = message;
      console.error('Creator chat failed to initialize', err);
    } finally {
      isInitializing = false;
    }
  }

  async function handleSend(): Promise<void> {
    const trimmed = messageText.trim();
    if (!trimmed || !roomId || isSending) {
      return;
    }

    const localId = `local-${Date.now()}`;
    const localMessage: ChatMessage = {
      id: localId,
      role: 'user',
      content: trimmed,
      created_at: Date.now()
    };
    chatHistory = [...chatHistory, localMessage];
    messageText = '';
    await tick();
    scrollToBottom();

    isSending = true;
    error = null;
    try {
      await creationAPI.rooms.messages.create(roomId, { content: trimmed });
      await refreshMessages();
    } catch (err) {
      chatHistory = chatHistory.filter((msg) => msg.id !== localId);
      const message = err instanceof Error ? err.message : 'Failed to send message';
      error = message;
      console.error('Creator chat send failed', err);
    } finally {
      isSending = false;
      updateAwaitingAssistant();
    }
  }

  function handleQuickAction(action: QuickAction): void {
    const text = typeof action === 'string' ? action : action.prompt ?? action.label;
    messageText = text;
    void tick().then(() => {
      inputEl?.focus();
    });
  }

  function handleKeyDown(event: KeyboardEvent): void {
    if (event.key === 'Enter' && !event.shiftKey) {
      event.preventDefault();
      void handleSend();
    }
  }

  onMount(() => {
    void initialize();
    return () => {
      cancelPoll();
    };
  });
</script>

<section class="chat-panel" aria-live="polite">
  <header class="chat-header">
    <div class="assistant-info">
      <div class="assistant-avatar">
        <span>{assistantAvatar}</span>
      </div>
      <div>
        <h2>{assistantName}</h2>
        <p>{assistantDescription}</p>
      </div>
    </div>
  </header>

  {#if quickActions.length > 0}
    <div class="quick-actions">
      {#each quickActions as action, index (typeof action === 'string' ? action : action.label ?? index)}
        <button class="quick-action-btn" type="button" on:click={() => handleQuickAction(action)}>
          {typeof action === 'string' ? action : action.label}
        </button>
      {/each}
    </div>
  {/if}

  <slot name="beforeMessages" />

  <div class="chat-container">
    {#if error && !isReady}
      <div class="chat-messages error-state">
        <p>{error}</p>
      </div>
    {:else if (isInitializing && !isReady)}
      <div class="chat-messages loading-state">
        <p>Loading conversation…</p>
      </div>
    {:else}
      <div class="chat-messages" bind:this={transcriptEl}>
        {#each chatHistory as message (message.id)}
          <div class={`message message-${message.role} ${message.isSynthetic ? 'is-synthetic' : ''}`}>
            <div class="message-avatar">
              {#if message.role === 'assistant'}
                <span>AI</span>
              {:else}
                <span>U</span>
              {/if}
            </div>
            <div class="message-content">{message.content}</div>
          </div>
        {/each}
        {#if isAwaitingAssistant}
          <div class="message message-assistant is-loading">
            <div class="message-avatar"><span>AI</span></div>
            <div class="message-content">Thinking…</div>
          </div>
        {/if}
      </div>
    {/if}

    <div class="chat-input">
      <input
        type="text"
        bind:this={inputEl}
        bind:value={messageText}
        placeholder={placeholder}
        on:keydown={handleKeyDown}
        disabled={!isReady || isSending}
        class="chat-input-field"
      />
      <button
        type="button"
        class="send-btn"
        on:click={handleSend}
        disabled={!isReady || isSending || messageText.trim().length === 0}
        aria-label="Send message"
      >
        <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
          <path d="M22 2L11 13M22 2l-7 20-4-9-9-4 20-7z" />
        </svg>
      </button>
    </div>
  </div>

  {#if error && isReady}
    <p class="chat-error" role="alert">{error}</p>
  {/if}
</section>

<style>
  .chat-messages.loading-state,
  .chat-messages.error-state {
    display: grid;
    place-items: center;
    text-align: center;
    padding: 1.5rem;
    color: rgba(255, 255, 255, 0.72);
  }

  .chat-error {
    margin-top: 0.75rem;
    font-size: 0.85rem;
    color: #fca5a5;
  }

  .is-loading .message-content {
    opacity: 0.7;
    font-style: italic;
  }
</style>
