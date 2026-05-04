import { fileURLToPath, URL } from 'node:url'

import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import vueDevTools from 'vite-plugin-vue-devtools'

// https://vite.dev/config/
export default defineConfig({
  plugins: [
    vue(),
    vueDevTools(),
  ],
  resolve: {
    alias: {
      '@': fileURLToPath(new URL('./src', import.meta.url))
    },
  },
  server: {
    host: true, // Listen on all addresses
    port: 5173,
    strictPort: false, // Allow fallback to next available port
    hmr: {
      overlay: false, // Disable error overlay for WebSocket issues
      clientPort: 5173
    },
    watch: {
      usePolling: false // Disable polling to avoid conflicts
    },
    cors: true
  },
  preview: {
    port: 5173,
    host: true
  }
})
