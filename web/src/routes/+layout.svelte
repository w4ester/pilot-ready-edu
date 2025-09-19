<script lang="ts">
  import "../app.css";
  import { page } from '$app/stores';

  export let data: {
    user: {
      email: string | null;
      auth_method?: string;
      requires_password_change?: boolean;
    } | null;
  };

  $: currentPath = $page.url.pathname;
</script>

<header class="site-header">
  <div class="site-header__glow"></div>
  <div class="site-header__inner">
    {#if !currentPath.startsWith('/creation-station')}
      <nav class="nav" aria-label="Primary navigation">
        <a class:selected={currentPath.startsWith('/creation-station')} href="/creation-station">Creation Station</a>
      </nav>
    {/if}
    {#if data.user}
      <div class="user-chip" aria-label="Account">
        <div class="user-chip__avatar" aria-hidden="true">{data.user.email?.slice(0, 1)?.toUpperCase() ?? 'U'}</div>
        <div class="user-chip__details">
          <span class="user-chip__label">Teacher</span>
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
    position: sticky;
    top: 0;
    z-index: 20;
    backdrop-filter: blur(22px);
    background: linear-gradient(135deg, rgba(48, 24, 94, 0.95), rgba(16, 22, 53, 0.97));
    border-bottom: 1px solid rgba(141, 112, 255, 0.24);
  }

  .site-header__glow {
    position: absolute;
    inset: 0;
    background: radial-gradient(circle at 8% 12%, rgba(166, 118, 255, 0.32), transparent 55%),
      radial-gradient(circle at 88% 20%, rgba(66, 204, 255, 0.28), transparent 60%);
    opacity: 0.6;
    pointer-events: none;
  }

  .site-header__inner {
    position: relative;
    margin: 0 auto;
    max-width: 100%;
    padding: 0.9rem clamp(1.5rem, 4vw, 2.75rem);
    display: flex;
    align-items: center;
    justify-content: flex-end;
    gap: 1rem;
    color: #f6f8ff;
  }

  .brand {
    display: inline-flex;
    align-items: center;
    gap: 0.65rem;
    text-decoration: none;
    color: inherit;
    font-weight: 700;
    letter-spacing: 0.05em;
  }

  .brand__glyph {
    width: 32px;
    height: 32px;
    border-radius: 12px;
    display: grid;
    place-items: center;
    font-size: 1.2rem;
    background: radial-gradient(circle at 30% 20%, rgba(132, 94, 255, 0.9), rgba(65, 105, 255, 0.72));
    box-shadow: 0 10px 24px rgba(76, 102, 255, 0.35);
  }

  .brand__word {
    font-size: 1.1rem;
  }

  .nav {
    display: inline-flex;
    gap: 0.8rem;
    align-items: center;
    background: rgba(12, 14, 38, 0.5);
    border-radius: 999px;
    padding: 0.32rem 0.45rem;
    border: 1px solid rgba(255, 255, 255, 0.14);
    position: absolute;
    left: 50%;
    transform: translateX(-50%);
  }

  .nav a {
    text-decoration: none;
    font-weight: 600;
    color: rgba(243, 244, 255, 0.75);
    padding: 0.4rem 0.9rem;
    border-radius: 999px;
    transition: background 0.2s ease, color 0.2s ease, box-shadow 0.2s ease;
  }

  .nav a:hover {
    background: rgba(255, 255, 255, 0.14);
    color: #ffffff;
  }

  .nav a.selected {
    background: linear-gradient(135deg, rgba(116, 97, 255, 0.85), rgba(92, 183, 255, 0.7));
    color: #fff;
    box-shadow: 0 12px 24px rgba(88, 123, 255, 0.32);
  }

  .login-link {
    font-weight: 600;
    color: #f6f8ff;
    text-decoration: none;
  }

  .user-chip {
    display: inline-flex;
    align-items: center;
    gap: 0.65rem;
    padding: 0.55rem 0.8rem;
    border-radius: 16px;
    background: rgba(10, 12, 32, 0.6);
    border: 1px solid rgba(140, 120, 255, 0.3);
    box-shadow: 0 18px 32px rgba(14, 10, 40, 0.35);
  }

  .user-chip__avatar {
    width: 36px;
    height: 36px;
    border-radius: 12px;
    background: linear-gradient(135deg, rgba(116, 97, 255, 0.92), rgba(90, 184, 255, 0.85));
    display: inline-flex;
    align-items: center;
    justify-content: center;
    font-weight: 700;
    color: #fff;
  }

  .user-chip__details {
    display: flex;
    flex-direction: column;
    line-height: 1.1;
  }

  .user-chip__label {
    font-size: 0.7rem;
    letter-spacing: 0.08em;
    text-transform: uppercase;
    color: rgba(233, 236, 255, 0.6);
  }

  .user-chip__value {
    font-size: 0.92rem;
    color: #f7f8ff;
  }

  .logout {
    border: none;
    border-radius: 12px;
    padding: 0.3rem 0.8rem;
    font-weight: 600;
    color: #121735;
    background: linear-gradient(135deg, #ffffff, #d8e4ff);
    cursor: pointer;
    transition: transform 0.2s ease;
  }

  .logout:hover {
    transform: translateY(-1px);
  }

  @media (max-width: 720px) {
    .site-header__inner {
      flex-direction: column;
      align-items: stretch;
      gap: 0.9rem;
    }

    .nav {
      justify-content: center;
      align-self: center;
    }

    .user-chip {
      justify-content: space-between;
    }
  }
</style>
