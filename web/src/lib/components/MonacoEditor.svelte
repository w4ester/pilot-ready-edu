<script lang="ts">
  import { onDestroy, onMount } from 'svelte';
  import { browser } from '$app/environment';
  import { loadMonaco } from '$lib/monaco';
  import type * as Monaco from 'monaco-editor';

  declare global {
    interface Window {
      __monacoCssPromise?: Promise<unknown>;
    }
  }

  let container: HTMLDivElement | null = null;

  export let value = '';
  export let language: Monaco.editor.IStandaloneEditorConstructionOptions['language'] = 'text';
  export let options: Monaco.editor.IStandaloneEditorConstructionOptions = {};
  export let instance: Monaco.editor.IStandaloneCodeEditor | null = null;

  const baseOptions: Monaco.editor.IStandaloneEditorConstructionOptions = {
    automaticLayout: true,
    minimap: { enabled: false }
  };

  let isMounted = false;

  const ensureMonacoCss = async () => {
    if (!browser) {
      return;
    }
    if (!window.__monacoCssPromise) {
      window.__monacoCssPromise = import('monaco-editor/min/vs/editor/editor.main.css');
    }
    await window.__monacoCssPromise;
  };

  onMount(async () => {
    if (!container) return;
    isMounted = true;
    await ensureMonacoCss();
    const monaco = await loadMonaco();
    instance = monaco.editor.create(container, {
      ...baseOptions,
      ...options,
      value,
      language
    });
  });

  $: if (instance && isMounted && value !== instance.getValue()) {
    instance.setValue(value);
  }

  onDestroy(() => {
    instance?.dispose();
    instance = null;
    isMounted = false;
  });
</script>

<div class="monaco-editor-root" bind:this={container}></div>

<style>
  .monaco-editor-root {
    width: 100%;
    height: 100%;
    flex: 1 1 auto;
    min-height: inherit;
  }
</style>
