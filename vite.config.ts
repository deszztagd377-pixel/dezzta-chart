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
    // Keep the charting engine and Firebase SDK in separate cacheable chunks.
    // This reduces the initial application entry chunk without changing when
    // either feature is loaded or how the UI behaves.
    rollupOptions: {
      output: {
        manualChunks(id) {
          if (id.includes('/node_modules/firebase/') || id.includes('/node_modules/@firebase/')) {
            return 'firebase-vendor';
          }
          if (id.includes('/node_modules/lightweight-charts/')) {
            return 'chart-vendor';
          }
        }
      }
    },
    // Do not publish production source maps. Frontend bundles are public by
    // design; provider credentials must never be placed in VITE_* variables.
    sourcemap: false
  }
});
