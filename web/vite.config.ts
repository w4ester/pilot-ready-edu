import { sveltekit } from '@sveltejs/kit/vite';
import { defineConfig, loadEnv } from 'vite';

export default defineConfig(({ mode }) => {
  const env = loadEnv(mode, process.cwd(), '');

  const defaultTarget = 'http://localhost:3434';
  let apiTarget = defaultTarget;
  let apiPrefix = '/api';

  const base = env.VITE_API_BASE;
  if (base && base.startsWith('http')) {
    try {
      const url = new URL(base);
      apiTarget = url.origin || defaultTarget;
      apiPrefix = url.pathname.replace(/\/$/, '') || '/api';
    } catch (err) {
      apiTarget = defaultTarget;
      apiPrefix = '/api';
    }
  }

  const rewriteApiPath = (path: string) => {
    if (!apiPrefix || apiPrefix === '/api') {
      return path;
    }
    return path.replace(/^\/api/, apiPrefix);
  };

  const rewriteOllamaPath = (path: string) => {
    const basePrefix = apiPrefix || '/api';
    return path.replace(/^\/ollama/, `${basePrefix}/v1/ollama`);
  };

  return {
    plugins: [sveltekit()],
    server: {
      host: true,
      port: 6407,
      proxy: {
        '/api': {
          target: apiTarget,
          changeOrigin: true,
          secure: false,
          ws: false,
          rewrite: rewriteApiPath,
        },
        '/ollama': {
          target: apiTarget,
          changeOrigin: true,
          secure: false,
          rewrite: rewriteOllamaPath,
        },
      },
    },
  };
});
