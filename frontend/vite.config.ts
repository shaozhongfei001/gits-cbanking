import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'

// 本地后端端口可由环境变量覆盖（默认 8080）；沙箱内 8080 可能被代理占用。
const apiProxyTarget = process.env.VITE_API_PROXY_TARGET || 'http://127.0.0.1:8080'

export default defineConfig({
  plugins: [vue()],
  server: {
    proxy: {
      '/api': {
        target: apiProxyTarget,
        timeout: 180000,
        proxyTimeout: 180000,
      },
    },
  },
})
