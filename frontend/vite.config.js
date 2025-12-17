import react from '@vitejs/plugin-react'
import { defineConfig } from 'vite'
import path from 'path'

export default defineConfig({
  plugins: [react()],
  
  // Build config para Django
  build: {
    outDir: '../src/static/dist',
    assetsDir: 'assets',
    emptyOutDir: true,
    target: 'es2015',
    minify: 'terser',
    sourcemap: false,
    base: '/static/dist/',
  },
  
  // Dev server config
  server: {
    port: 3000,
    host: '0.0.0.0',
    proxy: {
      '/api': {
        target: 'http://localhost:8000',
        changeOrigin: true,
      },
    },
  },
  
  // Resolve aliases
  resolve: {
    alias: {
      '@': path.resolve(__dirname, './src'),
    },
  },
})
