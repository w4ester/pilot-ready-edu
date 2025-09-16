<script lang="ts">
  import { creationAPI } from '$lib/api.creationstation';
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
        goto('/tools');
      }, 800);
    } catch (err) {
      error = err instanceof Error ? err.message : 'Failed to create tool';
    } finally {
      submitting = false;
    }
  }
</script>

<main class="page">
  <h1>New Tool</h1>
  <form on:submit|preventDefault={handleSubmit}>
    <label for="slug">Slug</label>
    <input id="slug" bind:value={slug} required placeholder="summarize_tool" />

    <label for="name">Display name</label>
    <input id="name" bind:value={name} required />

    <div class="row">
      <div>
        <label for="language">Language</label>
        <input id="language" bind:value={language} required />
      </div>
      <div>
        <label for="entrypoint">Entrypoint</label>
        <input id="entrypoint" bind:value={entrypoint} required />
      </div>
    </div>

    <label for="content">Content</label>
    <textarea id="content" bind:value={content} rows={10}></textarea>

    <label for="requirements">Requirements (optional)</label>
    <textarea id="requirements" bind:value={requirements} rows={3}></textarea>

    {#if error}
      <p class="error">{error}</p>
    {/if}
    {#if message}
      <p class="success">{message}</p>
    {/if}

    <button type="submit" disabled={submitting}>
      {submitting ? 'Saving…' : 'Create tool'}
    </button>
  </form>
</main>

<style>
  .page {
    max-width: 720px;
    margin: 0 auto;
    padding: 2rem;
    display: flex;
    flex-direction: column;
    gap: 1.5rem;
  }

  form {
    display: flex;
    flex-direction: column;
    gap: 1rem;
  }

  label {
    font-weight: 600;
  }

  input,
  textarea {
    border-radius: 8px;
    border: 1px solid rgba(15, 18, 26, 0.2);
    padding: 0.6rem;
    font-family: inherit;
  }

  .row {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(140px, 1fr));
    gap: 1rem;
  }

  button {
    width: fit-content;
    background: #4a6cf7;
    color: #fff;
    padding: 0.75rem 1.5rem;
    border: none;
    border-radius: 999px;
    font-weight: 600;
    cursor: pointer;
  }

  .error {
    color: #b00020;
  }

  .success {
    color: #0f8c2f;
  }
</style>
