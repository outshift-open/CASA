import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react-swc'

// https://vite.dev/config/
export default defineConfig({
  server: {
    port: parseInt('5600'),
    strictPort: true,
    open: true
  },
  plugins: [react()],
})
