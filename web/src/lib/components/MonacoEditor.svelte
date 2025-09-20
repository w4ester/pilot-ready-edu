<script lang="ts">
  import { createEventDispatcher, onDestroy, onMount } from 'svelte';
  import { loadMonaco } from '$lib/monaco';
  import type { IDisposable, editor as MonacoEditor } from 'monaco-editor';

  const dispatch = createEventDispatcher<{
    ready: MonacoEditor.IStandaloneCodeEditor;
    input: string;
  }>();

  export let value = '';
  export let language = 'plaintext';
  export let options: MonacoEditor.IStandaloneEditorConstructionOptions | undefined;
  export let editor: MonacoEditor.IStandaloneCodeEditor | null = null;

  let container: HTMLDivElement | null = null;
  let contentSubscription: IDisposable | null = null;

  let monacoStylesheetPromise: Promise<unknown> | null = null;

  function ensureMonacoStyles(): Promise<unknown> {
    if (typeof window === 'undefined') {
      return Promise.resolve();
    }

    if (!monacoStylesheetPromise) {
      monacoStylesheetPromise = import('monaco-editor/min/vs/editor/editor.main.css');
    }

    return monacoStylesheetPromise;
  }

  onMount(async () => {
    if (!container) return;

    await ensureMonacoStyles();

    const monaco = await loadMonaco();
    editor = monaco.editor.create(container, {
      value,
      language,
      automaticLayout: true,
      ...(options ?? {})
    });

    dispatch('ready', editor);

    contentSubscription = editor.onDidChangeModelContent(() => {
      const currentValue = editor?.getValue() ?? '';
      if (currentValue !== value) {
        value = currentValue;
        dispatch('input', currentValue);
      }
    });

    return () => {
      contentSubscription?.dispose();
      contentSubscription = null;

      editor?.dispose();
      editor = null;
    };
  });

  $: if (editor && value !== editor.getValue()) {
    editor.setValue(value);
  }

  onDestroy(() => {
    contentSubscription?.dispose();
    contentSubscription = null;

    editor?.dispose();
    editor = null;
  });
</script>

<div bind:this={container} class="monaco-editor-container" />

<style>
  .monaco-editor-container {
    width: 100%;
    height: 100%;
  }
</style>
