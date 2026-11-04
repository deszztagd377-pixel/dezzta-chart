import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';

// https://vitejs.dev/config/
export default defineConfig({
  plugins: [react()],
  server: {
    port: 3000,
    open: true
  },
  build: {
    outDir: 'dist',
    // Do not publish production source maps. Frontend bundles are public by
    // design; provider credentials must never be placed in VITE_* variables.
    sourcemap: false
  }
});
