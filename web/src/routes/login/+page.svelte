<script lang="ts">
  import { onMount } from 'svelte';
  import { goto } from '$app/navigation';
  import { page } from '$app/stores';
  import { authAPI, AuthError } from '$lib/auth';

  let email = '';
  let password = '';
  let loading = false;
  let error: string | null = null;
  let emailInput: HTMLInputElement | null = null;

  $: next = sanitizeNext($page.url.searchParams.get('next'));

  onMount(() => {
    if (emailInput) {
      emailInput.focus();
    }
  });

  function sanitizeNext(raw: string | null): string {
    if (!raw) return '/tools';
    const trimmed = raw.trim();
    return trimmed.startsWith('/') ? trimmed : '/tools';
  }

  function mapError(err: unknown): string {
    if (err instanceof AuthError) {
      if (err.status === 423 || err.detail?.includes('locked')) {
        return 'Too many attempts—try again in 15 minutes.';
      }
      return 'Check your email and password.';
    }
    if (err instanceof Error && err.message) {
      return err.message;
    }
    return 'Login failed. Please try again.';
  }

  const handleSubmit = async (event: SubmitEvent) => {
    event.preventDefault();
    if (loading) return;

    loading = true;
    error = null;

    try {
      await authAPI.login(email, password);
      await goto(next, { replaceState: true });
    } catch (err) {
      error = mapError(err);
    } finally {
      loading = false;
    }
  };
</script>

<main class="auth-page">
  <section class="card" aria-labelledby="login-title">
    <h1 id="login-title">Sign in to Edinfinite</h1>
    <p class="hint">Use the access credentials provided for tonight&apos;s demo.</p>
    <p class="trust">We keep your classroom data private and never sell it.</p>

    <form class="form" on:submit={handleSubmit} autocomplete="on" aria-busy={loading}>
      <label class="field" for="email">
        <span>Email</span>
        <input
          id="email"
          name="email"
          type="email"
          inputmode="email"
          autocomplete="username"
          placeholder="teacher@example.edu"
          bind:this={emailInput}
          bind:value={email}
          required
          enterkeyhint="next"
        />
      </label>

      <label class="field" for="password">
        <span>Password</span>
        <input
          id="password"
          name="password"
          type="password"
          autocomplete="current-password"
          placeholder="••••••••"
          bind:value={password}
          required
          enterkeyhint="send"
        />
      </label>

      {#if error}
        <p class="error" role="alert" aria-live="polite">{error}</p>
      {/if}

      <button type="submit" class="submit" disabled={loading}>
        {#if loading}
          Signing in…
        {:else}
          Sign in
        {/if}
      </button>
    </form>

    <p class="note">
      Need access? <a href="mailto:support@edinfinite.com">Contact the facilitator</a> and we&apos;ll help you get started.
    </p>
  </section>
</main>

<style>
  .auth-page {
    min-height: calc(100vh - 72px);
    display: flex;
    align-items: center;
    justify-content: center;
    background: linear-gradient(160deg, #f4f6ff 0%, #eef2fb 100%);
    padding: 3rem 1.5rem;
  }

  .card {
    background: #ffffff;
    border-radius: 16px;
    box-shadow: 0 18px 40px rgba(33, 41, 72, 0.12);
    padding: 2.5rem 2.75rem;
    width: min(440px, 100%);
    display: flex;
    flex-direction: column;
    gap: 1.5rem;
  }

  h1 {
    margin: 0;
    font-size: 1.9rem;
    color: #1b2559;
  }

  .hint,
  .trust,
  .note {
    margin: 0;
    font-size: 0.95rem;
    color: rgba(27, 37, 89, 0.72);
  }

  .trust {
    font-style: italic;
  }

  .form {
    display: flex;
    flex-direction: column;
    gap: 1rem;
  }

  .field {
    display: flex;
    flex-direction: column;
    gap: 0.4rem;
    font-weight: 600;
    color: #1b2559;
  }

  input {
    border: 1px solid rgba(27, 37, 89, 0.25);
    border-radius: 10px;
    padding: 0.75rem 1rem;
    font-size: 1rem;
    transition: border-color 0.15s ease, box-shadow 0.15s ease;
  }

  input:focus {
    outline: none;
    border-color: #4a6cf7;
    box-shadow: 0 0 0 3px rgba(74, 108, 247, 0.18);
  }

  .error {
    margin: 0;
    color: #b00020;
    font-weight: 500;
  }

  .submit {
    border: none;
    border-radius: 10px;
    padding: 0.75rem 1rem;
    font-size: 1rem;
    font-weight: 600;
    color: #fff;
    background: linear-gradient(135deg, #4a6cf7, #6c8bfa);
    cursor: pointer;
    transition: transform 0.15s ease, box-shadow 0.15s ease;
  }

  .submit:hover:enabled {
    transform: translateY(-1px);
    box-shadow: 0 12px 24px rgba(74, 108, 247, 0.25);
  }

  .submit:disabled {
    opacity: 0.7;
    cursor: not-allowed;
  }

  @media (max-width: 600px) {
    .card {
      padding: 2rem;
    }
  }
</style>
