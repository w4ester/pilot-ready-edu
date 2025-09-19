<script lang="ts">
  export let data: {
    user: {
      email: string | null;
      auth_method?: string;
      requires_password_change?: boolean;
    } | null;
  };
</script>

<header class="site-header">
  <div class="site-header__inner">
    <a class="brand" href="/">Edinfinite</a>
    {#if data.user}
      <div class="user-chip">
        <div class="user-chip__details">
          <span class="user-chip__label">Signed in</span>
          <strong class="user-chip__value">{data.user.email}</strong>
        </div>
        <form method="POST" action="/logout">
          <button type="submit" class="logout">Logout</button>
        </form>
      </div>
    {:else}
      <a class="login-link" href="/login">Sign in</a>
    {/if}
  </div>
</header>

<slot />

<style>
  .site-header {
    background: #ffffff;
    border-bottom: 1px solid rgba(15, 18, 26, 0.08);
    position: sticky;
    top: 0;
    z-index: 10;
  }

  .site-header__inner {
    margin: 0 auto;
    max-width: 960px;
    padding: 1rem 1.5rem;
    display: flex;
    align-items: center;
    justify-content: space-between;
    gap: 1rem;
  }

  .brand {
    font-size: 1.15rem;
    font-weight: 700;
    color: #1b2559;
    text-decoration: none;
  }

  .login-link {
    font-weight: 600;
    color: #4a6cf7;
    text-decoration: none;
  }

  .user-chip {
    display: inline-flex;
    align-items: center;
    gap: 0.75rem;
    padding: 0.5rem 0.75rem;
    border-radius: 999px;
    background: rgba(74, 108, 247, 0.1);
  }

  .user-chip__details {
    display: flex;
    flex-direction: column;
    line-height: 1.1;
  }

  .user-chip__label {
    font-size: 0.75rem;
    color: rgba(27, 37, 89, 0.66);
    text-transform: uppercase;
    letter-spacing: 0.04em;
  }

  .user-chip__value {
    font-size: 0.95rem;
    color: #1b2559;
  }

  .logout {
    border: none;
    border-radius: 999px;
    padding: 0.4rem 0.85rem;
    font-weight: 600;
    color: #fff;
    background: linear-gradient(135deg, #4a6cf7, #6c8bfa);
    cursor: pointer;
  }

  @media (max-width: 640px) {
    .site-header__inner {
      flex-direction: column;
      align-items: stretch;
      gap: 0.75rem;
    }

    .user-chip {
      justify-content: space-between;
    }
  }
</style>
