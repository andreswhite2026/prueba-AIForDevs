// vite.config.ts
import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import tailwindcss from '@tailwindcss/vite'

export default defineConfig({
  plugins: [
    vue(),
    tailwindcss(),
  ],
  server: {
    // Keep the browser, Vite proxy, and Uvicorn on the same IPv4 loopback.
    // Access the dev site at http://127.0.0.1:3000 (not localhost).
    host: '127.0.0.1',
    port: 3000,
    strictPort: true,
    proxy: {
      '/api': {
        // Use IPv4 explicitly: Uvicorn normally listens on 127.0.0.1 and
        // some systems resolve localhost to ::1 first.
        target: 'http://127.0.0.1:8000',
        changeOrigin: true,
        rewrite: (path) => path.replace(/^\/api/, ''),
        configure: (proxy) => {
          proxy.on('error', (error, request) => {
            console.error(
              `[API proxy] ${request.method} ${request.url}: ${error.message}`
            )
          })
        }
      }
    }
  }
})
