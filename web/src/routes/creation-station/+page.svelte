<script lang="ts">
  import type { PageData } from './$types';
  export let data: PageData;

  let viewMode: 'grid' | 'list' = 'grid';

  const toggleView = (mode: 'grid' | 'list') => {
    viewMode = mode;
  };
</script>

<svelte:head>
  <title>Creation Station · Edinfinite</title>
</svelte:head>

<main class="creation">
  <div class="creation__backdrop"></div>

  <section class="hero">
    <div class="hero__glow"></div>
    <div class="hero__grid"></div>
    <div class="hero__content">
      <span class="hero__eyebrow">AI-Powered Education Platform</span>
      <h1>Creation Station</h1>
      <p class="hero__subtitle">
        Build powerful educational resources in seconds with specialized AI assistants tailored for your classroom.
      </p>
      <div class="hero__stats" aria-label="Creation Station metrics">
        {#each data.stats as stat}
          <article class="stat" aria-live="polite">
            <span class="stat__icon" aria-hidden="true">{stat.icon}</span>
            <span class="stat__value" title={String(stat.value)}>{stat.display}</span>
            <span class="stat__label">{stat.label}</span>
          </article>
        {/each}
      </div>
    </div>

    <div class="hero__view" role="radiogroup" aria-label="Toggle view mode">
      <span class="hero__view-label">View</span>
      <button type="button" class:selected={viewMode === 'grid'} on:click={() => toggleView('grid')} aria-pressed={viewMode === 'grid'}>
        Grid
      </button>
      <button type="button" class:selected={viewMode === 'list'} on:click={() => toggleView('list')} aria-pressed={viewMode === 'list'}>
        List
      </button>
    </div>
  </section>

  <section class="tools" aria-labelledby="tools-heading">
    <header class="tools__header">
      <div>
        <h2 id="tools-heading">Creation Tools</h2>
        <p>Explore assistants and workspace extensions to accelerate lesson building.</p>
      </div>
    </header>

    {#if viewMode === 'grid'}
      <div class="card-grid">
        {#each data.tiles as tile}
          <article
            class={`tool-card tool-card--${tile.accent} ${tile.disabled ? 'tool-card--disabled' : ''}`}
            style={`--accent-start:${tile.gradient[0]}; --accent-end:${tile.gradient[1]};`}
          >
            <header class="tool-card__header">
              <div>
                <h3>{tile.title}</h3>
                {#if tile.badge}
                  <span class={`badge badge--${tile.badge.tone}`}>{tile.badge.label}</span>
                {/if}
              </div>

              <span class="tool-card__icon" aria-hidden="true">{tile.icon}</span>

              {#if tile.href && !tile.disabled}
                <a class="tool-card__action" href={tile.href} aria-label={`Open ${tile.title}`}>
                  <span aria-hidden="true">+</span>
                </a>
              {:else}
                <span class="tool-card__action tool-card__action--muted" aria-hidden="true">+</span>
              {/if}
            </header>

            <p class="tool-card__description">{tile.description}</p>

            <div class="tool-card__meta">
              {#if tile.countLabel && tile.countValue !== undefined}
                <span class="tool-card__meta-item"><strong>{tile.countValue}</strong> {tile.countLabel}</span>
              {/if}
              {#if tile.meta}
                {#each tile.meta as meta}
                  <span class="tool-card__meta-item">
                    {#if meta.icon}
                      <span class="tool-card__meta-icon" aria-hidden="true">{meta.icon}</span>
                    {/if}
                    <span>{meta.label}</span>
                  </span>
                {/each}
              {/if}
            </div>

            {#if tile.statusText && tile.disabled}
              <div class="tool-card__status" role="status">{tile.statusText}</div>
            {/if}
          </article>
        {/each}
      </div>
    {:else}
      <ul class="card-list">
        {#each data.tiles as tile}
          <li
            class={`list-item list-item--${tile.accent} ${tile.disabled ? 'list-item--disabled' : ''}`}
            style={`--accent-start:${tile.gradient[0]}; --accent-end:${tile.gradient[1]};`}
          >
            <div class="list-item__text">
              <h3>{tile.title}</h3>
              <p>{tile.description}</p>
              {#if tile.statusText && tile.disabled}
                <span class="list-item__status">{tile.statusText}</span>
              {/if}
            </div>
            <div class="list-item__meta">
              <span class="list-item__icon" aria-hidden="true">{tile.icon}</span>
              {#if tile.countLabel && tile.countValue !== undefined}
                <span><strong>{tile.countValue}</strong> {tile.countLabel}</span>
              {/if}
              {#if tile.meta}
                {#each tile.meta as meta}
                  <span>{meta.icon ? `${meta.icon} ` : ''}{meta.label}</span>
                {/each}
              {/if}
            </div>
            {#if tile.href && !tile.disabled}
              <a class="list-item__cta" href={tile.href}>Open</a>
            {:else}
              <span class="list-item__cta list-item__cta--disabled">Unavailable</span>
            {/if}
          </li>
        {/each}
      </ul>
    {/if}
  </section>
</main>

<style>
  :global(body) {
    background: #050712;
    color: #f8f9ff;
  }

  .creation {
    position: relative;
    min-height: calc(100vh - 72px);
    padding: 3.5rem clamp(1.5rem, 4vw, 4rem) 4.5rem;
    display: flex;
    flex-direction: column;
    gap: 3.5rem;
  }

  .creation__backdrop {
    position: fixed;
    inset: 0;
    pointer-events: none;
    background:
      radial-gradient(circle at 15% 10%, rgba(140, 98, 255, 0.18), transparent 55%),
      radial-gradient(circle at 85% 15%, rgba(43, 224, 255, 0.18), transparent 50%),
      linear-gradient(180deg, rgba(8, 12, 32, 0.92), rgba(8, 11, 22, 0.98));
    z-index: -2;
  }

  .creation__backdrop::after {
    content: '';
    position: absolute;
    inset: 0;
    background-image: url('data:image/svg+xml,%3Csvg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 160 160"%3E%3Cfilter id="n"%3E%3CfeTurbulence type="fractalNoise" baseFrequency="0.9" numOctaves="4" stitchTiles="stitch"/%3E%3C/filter%3E%3Crect width="160" height="160" filter="url(%23n)" opacity="0.08"/%3E%3C/svg%3E');
    opacity: 0.5;
  }

  .hero {
    position: relative;
    border-radius: 28px;
    padding: clamp(2.75rem, 5vw, 3.5rem) clamp(2.2rem, 5vw, 3.7rem);
    overflow: hidden;
    isolation: isolate;
    border: 1px solid rgba(124, 84, 255, 0.22);
    box-shadow: 0 60px 120px rgba(24, 15, 48, 0.45);
  }

  .hero__glow {
    position: absolute;
    inset: -40%;
    background:
      radial-gradient(circle at 20% 30%, rgba(123, 91, 255, 0.45), transparent 55%),
      radial-gradient(circle at 80% 25%, rgba(63, 209, 255, 0.25), transparent 60%);
    z-index: -2;
  }

  .hero__grid {
    position: absolute;
    inset: 0;
    background-image: linear-gradient(rgba(255, 255, 255, 0.08) 1px, transparent 1px),
      linear-gradient(90deg, rgba(255, 255, 255, 0.08) 1px, transparent 1px);
    background-size: 48px 48px;
    opacity: 0.15;
    z-index: -1;
    mask-image: radial-gradient(circle at center, rgba(0, 0, 0, 0.8), rgba(0, 0, 0, 0));
  }

  .hero__content {
    max-width: 560px;
    display: flex;
    flex-direction: column;
    gap: 1.35rem;
  }

  .hero__eyebrow {
    text-transform: uppercase;
    letter-spacing: 0.35em;
    font-size: 0.75rem;
    font-weight: 600;
    color: rgba(255, 255, 255, 0.65);
  }

  .hero h1 {
    margin: 0;
    font-size: clamp(2.9rem, 5vw, 3.75rem);
    font-weight: 800;
    color: #f8f9ff;
    letter-spacing: 0.01em;
  }

  .hero__subtitle {
    margin: 0;
    font-size: 1.12rem;
    line-height: 1.6;
    color: rgba(248, 249, 255, 0.8);
  }

  .hero__stats {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(140px, 1fr));
    gap: 1.25rem;
    margin-top: 0.5rem;
  }

  .stat {
    position: relative;
    border-radius: 20px;
    padding: 1.2rem 1.35rem;
    background: rgba(13, 16, 35, 0.32);
    backdrop-filter: blur(14px);
    border: 1px solid rgba(255, 255, 255, 0.12);
    box-shadow: inset 0 0 0 1px rgba(255, 255, 255, 0.05), 0 18px 40px rgba(10, 14, 46, 0.35);
    overflow: hidden;
    display: grid;
    grid-template-columns: auto 1fr;
    grid-template-rows: auto auto;
    column-gap: 0.75rem;
    row-gap: 0.35rem;
    align-items: center;
  }

  .stat::after {
    content: '';
    position: absolute;
    inset: 0;
    background: radial-gradient(circle at top, rgba(143, 117, 255, 0.22), transparent 65%);
    opacity: 0.6;
    pointer-events: none;
  }

  .stat__icon {
    width: 38px;
    height: 38px;
    border-radius: 14px;
    background: rgba(255, 255, 255, 0.15);
    display: inline-flex;
    align-items: center;
    justify-content: center;
    font-size: 1.3rem;
    box-shadow: inset 0 0 0 1px rgba(255, 255, 255, 0.18);
    grid-row: span 2;
  }

  .stat__value {
    font-size: 1.9rem;
    font-weight: 700;
    color: #ffffff;
  }

  .stat__label {
    font-size: 0.9rem;
    color: rgba(248, 249, 255, 0.7);
  }

  .hero__view {
    position: absolute;
    top: 2rem;
    right: 2rem;
    display: inline-flex;
    align-items: center;
    gap: 0.4rem;
    background: rgba(8, 10, 28, 0.6);
    border-radius: 999px;
    padding: 0.4rem 0.6rem;
    border: 1px solid rgba(255, 255, 255, 0.14);
    backdrop-filter: blur(12px);
    box-shadow: 0 12px 24px rgba(12, 12, 30, 0.35);
  }

  .hero__view-label {
    font-size: 0.72rem;
    text-transform: uppercase;
    letter-spacing: 0.18em;
    color: rgba(255, 255, 255, 0.68);
  }

  .hero__view button {
    border: none;
    border-radius: 999px;
    padding: 0.32rem 0.95rem;
    background: transparent;
    color: rgba(255, 255, 255, 0.55);
    font-weight: 600;
    cursor: pointer;
    transition: background 0.25s ease, color 0.25s ease;
  }

  .hero__view button.selected {
    background: linear-gradient(135deg, rgba(114, 103, 255, 0.65), rgba(83, 99, 255, 0.48));
    color: #ffffff;
    box-shadow: 0 10px 20px rgba(90, 106, 255, 0.35);
  }

  .tools {
    max-width: 1200px;
    margin: 0 auto;
    width: 100%;
  }

  .tools__header {
    display: flex;
    flex-direction: column;
    gap: 0.6rem;
    margin-bottom: 1.75rem;
  }

  .tools__header h2 {
    margin: 0;
    font-size: 1.85rem;
    color: #eef2ff;
    letter-spacing: 0.01em;
  }

  .tools__header p {
    margin: 0;
    color: rgba(226, 231, 255, 0.72);
  }

  .card-grid {
    display: grid;
    gap: 1.5rem;
    grid-template-columns: repeat(auto-fit, minmax(240px, 1fr));
  }

  .tool-card {
    position: relative;
    background: linear-gradient(140deg, rgba(8, 10, 26, 0.82), rgba(13, 16, 39, 0.92));
    border-radius: 26px;
    padding: 1.9rem;
    border: 1px solid rgba(255, 255, 255, 0.08);
    box-shadow: 0 35px 65px rgba(5, 6, 18, 0.6);
    display: flex;
    flex-direction: column;
    gap: 1rem;
    overflow: hidden;
    transition: transform 0.25s ease, box-shadow 0.25s ease;
  }

  .tool-card::before {
    content: '';
    position: absolute;
    inset: 0;
    background: radial-gradient(circle at top right, rgba(255, 255, 255, 0.15), transparent 55%);
    opacity: 0.6;
  }

  .tool-card::after {
    content: '';
    position: absolute;
    inset: 1px;
    border-radius: 24px;
    background: linear-gradient(135deg, var(--accent-start), var(--accent-end));
    opacity: 0.28;
    filter: blur(18px);
    z-index: -1;
  }

  .tool-card:hover {
    transform: translateY(-6px);
    box-shadow: 0 45px 85px rgba(5, 6, 20, 0.65);
  }

  .tool-card--disabled {
    opacity: 0.82;
  }

  .tool-card__header {
    display: flex;
    justify-content: space-between;
    gap: 1rem;
    align-items: flex-start;
  }

  .tool-card__header h3 {
    margin: 0;
    font-size: 1.25rem;
    color: #ffffff;
  }

  .tool-card__icon {
    display: inline-flex;
    align-items: center;
    justify-content: center;
    width: 48px;
    height: 48px;
    border-radius: 16px;
    font-size: 1.5rem;
    background: linear-gradient(135deg, rgba(255, 255, 255, 0.22), rgba(255, 255, 255, 0.05));
    box-shadow: inset 0 0 0 1px rgba(255, 255, 255, 0.18), 0 12px 24px rgba(0, 0, 0, 0.15);
  }

  .badge {
    display: inline-block;
    margin-top: 0.35rem;
    padding: 0.25rem 0.65rem;
    border-radius: 999px;
    font-size: 0.7rem;
    font-weight: 600;
    letter-spacing: 0.08em;
    text-transform: uppercase;
  }

  .badge--accent { background: rgba(142, 95, 255, 0.25); color: #d7c8ff; }
  .badge--info { background: rgba(76, 201, 240, 0.2); color: #9ce6ff; }
  .badge--warning { background: rgba(255, 184, 77, 0.25); color: #ffe0ab; }
  .badge--neutral { background: rgba(148, 163, 184, 0.25); color: #d2d9e6; }

  .tool-card__action {
    width: 36px;
    height: 36px;
    border-radius: 12px;
    background: rgba(255, 255, 255, 0.18);
    display: grid;
    place-items: center;
    color: #ffffff;
    text-decoration: none;
    font-size: 1.4rem;
    transition: transform 0.2s ease, background 0.2s ease;
  }

  .tool-card__action:hover {
    transform: translateY(-2px);
    background: rgba(255, 255, 255, 0.28);
  }

  .tool-card__action--muted {
    background: rgba(255, 255, 255, 0.08);
    color: rgba(255, 255, 255, 0.4);
    cursor: default;
  }

  .tool-card__description {
    margin: 0;
    color: rgba(244, 245, 255, 0.82);
    line-height: 1.6;
    min-height: 3.6rem;
    font-size: 0.98rem;
  }

  .tool-card__meta {
    display: flex;
    flex-wrap: wrap;
    gap: 0.6rem 1.1rem;
    color: rgba(232, 235, 255, 0.72);
    font-size: 0.9rem;
  }

  .tool-card__meta-item {
    display: inline-flex;
    align-items: center;
    gap: 0.35rem;
  }

  .tool-card__meta-icon {
    display: inline-flex;
  }

  .tool-card__status {
    margin-top: auto;
    display: inline-flex;
    align-items: center;
    gap: 0.35rem;
    font-size: 0.85rem;
    color: rgba(255, 255, 255, 0.6);
    background: rgba(255, 255, 255, 0.08);
    border-radius: 999px;
    padding: 0.3rem 0.75rem;
    align-self: flex-start;
  }

  .tool-card__status::before {
    content: '';
    width: 8px;
    height: 8px;
    border-radius: 50%;
    background: rgba(255, 255, 255, 0.6);
  }

  .card-list {
    list-style: none;
    margin: 0;
    padding: 0;
    display: flex;
    flex-direction: column;
    gap: 1rem;
  }

  .list-item {
    position: relative;
    background: linear-gradient(120deg, rgba(11, 13, 29, 0.82), rgba(13, 16, 36, 0.88));
    border-radius: 22px;
    padding: 1.6rem 1.8rem;
    border: 1px solid rgba(255, 255, 255, 0.05);
    display: grid;
    grid-template-columns: minmax(0, 1fr) auto auto;
    gap: 1.2rem;
    align-items: center;
    overflow: hidden;
    transition: transform 0.2s ease, box-shadow 0.2s ease;
  }

  .list-item::after {
    content: '';
    position: absolute;
    inset: 1px;
    border-radius: 20px;
    background: linear-gradient(135deg, var(--accent-start), var(--accent-end));
    opacity: 0.22;
    filter: blur(18px);
    z-index: -1;
  }

  .list-item__text h3 {
    margin: 0 0 0.4rem;
    color: #ffffff;
  }

  .list-item__text p {
    margin: 0;
    color: rgba(232, 234, 255, 0.75);
  }

  .list-item__status {
    margin-top: 0.5rem;
    display: inline-block;
    color: rgba(255, 255, 255, 0.58);
    font-size: 0.85rem;
  }

  .list-item__meta {
    display: flex;
    flex-direction: column;
    gap: 0.4rem;
    color: rgba(232, 235, 255, 0.72);
    font-size: 0.9rem;
  }

  .list-item__icon {
    font-size: 1.5rem;
    display: inline-flex;
  }

  .list-item__meta span {
    display: inline-flex;
    align-items: center;
    gap: 0.35rem;
  }

  .list-item__cta {
    padding: 0.5rem 1.1rem;
    border-radius: 12px;
    text-decoration: none;
    background: rgba(255, 255, 255, 0.18);
    color: #ffffff;
    font-weight: 600;
  }

  .list-item__cta--disabled {
    background: rgba(255, 255, 255, 0.08);
    color: rgba(255, 255, 255, 0.5);
  }

  .list-item--disabled .list-item__icon {
    opacity: 0.55;
  }

  .list-item:hover {
    transform: translateY(-4px);
    box-shadow: 0 28px 48px rgba(6, 7, 18, 0.55);
  }

  @media (max-width: 960px) {
    .hero {
      padding: 2.25rem;
    }

    .hero__view {
      position: static;
      margin-top: 1.5rem;
    }
  }

  @media (max-width: 720px) {
    .list-item {
      grid-template-columns: 1fr;
      text-align: left;
      gap: 0.8rem;
    }

    .hero__stats {
      grid-template-columns: repeat(auto-fit, minmax(120px, 1fr));
    }
  }
</style>
