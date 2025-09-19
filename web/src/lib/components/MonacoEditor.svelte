<script lang="ts">
  import { createEventDispatcher, onDestroy, onMount } from 'svelte';
  import type { editor as EditorNS, IDisposable } from 'monaco-editor';

  type Monaco = typeof import('monaco-editor');

  export let value = '';
  export let language = 'python';
  export let theme = 'vs-dark';
  export let readOnly = false;
  export let ariaLabel = 'Code editor';
  export let ariaLabelledby: string | undefined = undefined;
  export let options: Partial<EditorNS.IStandaloneEditorConstructionOptions> = {};
  export let height: number | string = '320px';
  export let id: string | undefined = undefined;
  export let className = '';
  export let loadingMessage = 'Loading editor…';

  const dispatch = createEventDispatcher<{
    change: { value: string };
    input: { value: string };
  }>();

  let container: HTMLDivElement | null = null;
  let editor: EditorNS.IStandaloneCodeEditor | null = null;
  let monaco: Monaco | null = null;
  let ready = false;
  let disposables: IDisposable[] = [];
  let hiddenTextarea: HTMLTextAreaElement | null = null;

  const resolveHeight = () => (typeof height === 'number' ? `${height}px` : height);
  let containerStyle = `height: ${resolveHeight()};`;

  $: containerStyle = `height: ${resolveHeight()};`;

  async function initializeEditor() {
    if (!container) return;
    const monacoModule = await import('monaco-editor');
    if (!container) return;

    monaco = monacoModule;
    monaco.editor.setTheme(theme);

    editor = monaco.editor.create(container, {
      value,
      language,
      readOnly,
      automaticLayout: true,
      minimap: { enabled: false },
      scrollBeyondLastLine: false,
      fontSize: 14,
      tabSize: 2,
      smoothScrolling: true,
      accessibilitySupport: 'on',
      ...options,
    });

    const domNode = editor.getDomNode();
    if (domNode) {
      domNode.setAttribute('aria-label', ariaLabel);
      if (ariaLabelledby) {
        domNode.setAttribute('aria-labelledby', ariaLabelledby);
      } else {
        domNode.removeAttribute('aria-labelledby');
      }
    }

    disposables = [
      editor.onDidChangeModelContent(() => {
        const newValue = editor?.getValue() ?? '';
        if (newValue !== value) {
          value = newValue;
          dispatch('input', { value: newValue });
          dispatch('change', { value: newValue });
        }
      }),
    ];

    ready = true;
  }

  function cleanup() {
    disposables.forEach((d) => d.dispose());
    disposables = [];
    editor?.dispose();
    editor = null;
    ready = false;
  }

  export function focus() {
    if (editor) {
      editor.focus();
    } else if (hiddenTextarea) {
      hiddenTextarea.focus();
    } else if (container) {
      container.focus();
    }
  }

  function handleHiddenFocus() {
    if (editor) {
      editor.focus();
    }
    if (hiddenTextarea) {
      hiddenTextarea.blur();
    }
  }

  onMount(() => {
    initializeEditor();
    return () => cleanup();
  });

  onDestroy(() => {
    cleanup();
  });

  $: if (editor && value !== editor.getValue()) {
    editor.setValue(value ?? '');
  }

  $: if (editor) {
    editor.updateOptions({ readOnly, ...options });
    const domNode = editor.getDomNode();
    if (domNode) {
      domNode.setAttribute('aria-label', ariaLabel);
      if (ariaLabelledby) {
        domNode.setAttribute('aria-labelledby', ariaLabelledby);
      } else {
        domNode.removeAttribute('aria-labelledby');
      }
    }
  }

  $: if (editor && monaco) {
    const model = editor.getModel();
    if (model && model.getLanguageId() !== language) {
      monaco.editor.setModelLanguage(model, language);
    }
  }

  $: if (monaco) {
    monaco.editor.setTheme(theme);
  }

  $: if (hiddenTextarea && hiddenTextarea.value !== value) {
    hiddenTextarea.value = value ?? '';
  }
</script>

{#if id}
  <textarea
    bind:this={hiddenTextarea}
    id={id}
    class="monaco-editor-hidden-textarea"
    value={value}
    tabindex="0"
    aria-hidden="true"
    on:focus={handleHiddenFocus}
    readonly
  ></textarea>
{/if}

<div
  bind:this={container}
  class={`monaco-editor-shell ${className}`.trim()}
  style={containerStyle}
  data-ready={ready}
  role="group"
  aria-busy={ready ? 'false' : 'true'}
  aria-label={!ready ? ariaLabel : undefined}
  aria-labelledby={ariaLabelledby}
>
  {#if !ready}
    <span class="editor-loading" aria-live="polite">{loadingMessage}</span>
  {/if}
</div>

<style>
  .monaco-editor-hidden-textarea {
    position: absolute;
    width: 1px;
    height: 1px;
    padding: 0;
    margin: -1px;
    overflow: hidden;
    clip: rect(0 0 0 0);
    clip-path: inset(50%);
    border: 0;
    white-space: nowrap;
  }

  .monaco-editor-shell {
    width: 100%;
    position: relative;
    border-radius: 0.5rem;
    overflow: hidden;
    min-height: 200px;
  }

  .monaco-editor-shell[data-ready='false'] {
    display: flex;
    align-items: center;
    justify-content: center;
    color: #9ca3af;
    font-size: 0.875rem;
  }

  .monaco-editor-shell :global(.monaco-editor),
  .monaco-editor-shell :global(.monaco-editor-background),
  .monaco-editor-shell :global(.monaco-editor .overflow-guard) {
    position: absolute;
    inset: 0;
  }

  .editor-loading {
    text-align: center;
    padding: 1rem;
  }
</style>
