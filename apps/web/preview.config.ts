import { defineConfig } from 'vite';

// Preview the deployable static output without a Worker or local bindings.
export default defineConfig({
  build: { outDir: 'dist/client' },
  preview: { host: '127.0.0.1', port: 4180 },
});
