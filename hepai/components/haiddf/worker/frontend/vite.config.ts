import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

export default defineConfig({
  plugins: [react()],
  server: {
    proxy: {
      '/apiv2': 'http://localhost:42605',
    },
  },
  build: {
    outDir: 'dist',
    assetsDir: 'assets',
  },
})
