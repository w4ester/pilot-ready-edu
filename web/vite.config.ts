import { sveltekit } from '@sveltejs/kit/vite';
import { defineConfig } from 'vite';

export default defineConfig({
  plugins: [sveltekit()],
  server: {
    host: true,
    port: 6407,
    proxy: {
      '/api': {
        target: 'http://localhost:3434',
        changeOrigin: false,
        secure: false
      },
      '/ollama': {
        target: 'http://localhost:11434',
        changeOrigin: false,
        secure: false
      }
    }
  }
});
