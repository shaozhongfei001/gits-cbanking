import { defineConfig, loadEnv } from 'vite'
import vue from '@vitejs/plugin-vue'

/**
 * 本地后端代理目标：
 * - 优先取进程环境变量（`VITE_API_PROXY_TARGET=… npm run dev`）；
 * - 其次取 `.env.[mode]` / `.env.local`（须经 loadEnv 读取，`process.env` 不会自动包含 env 文件）；
 * - 均未设置时用仓库约定默认值 8080（沙箱内 8080 可能被其他服务占用，此时用上面的方式覆盖）。
 *
 * KERT 对公经营分析服务（CCRM-BA 落地）默认 8107（KERT scripts/serve_analytics_api.py）。
 */
export default defineConfig(({ mode }) => {
  const env = loadEnv(mode, process.cwd(), '')
  const apiProxyTarget =
    process.env.VITE_API_PROXY_TARGET || env.VITE_API_PROXY_TARGET || 'http://127.0.0.1:8080'
  const kertProxyTarget =
    process.env.VITE_KERT_PROXY_TARGET || env.VITE_KERT_PROXY_TARGET || 'http://127.0.0.1:8107'

  return {
    plugins: [vue()],
    server: {
      proxy: {
        '/api': {
          target: apiProxyTarget,
          timeout: 180000,
          proxyTimeout: 180000,
        },
        '/kert-api': {
          target: kertProxyTarget,
          changeOrigin: true,
          rewrite: (path) => path.replace(/^\/kert-api/, ''),
          timeout: 60000,
          proxyTimeout: 60000,
        },
      },
    },
  }
})
