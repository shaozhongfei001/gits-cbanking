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
    build: {
      /**
       * 关闭压缩：本机（WSL2，内核 6.18.58.1-microsoft-standard-WSL2）上
       * vite 8.2.0 / rolldown 1.2.8 的 minify 通道会触发原生 SIGBUS
       * （退出码 135：`✓ 3095 modules transformed.` 之后无任何输出即死，无产物）。
       *
       * 实测：`--minify oxc` / `esbuild` / `terser` 三者均为 135；
       * 限核限线程（taskset -c 0-3 + RAYON_NUM_THREADS=2）仍为 135；
       * 原生二进制本身完整（mmap 逐页读 + 顺序读 19,308,352 字节全通）。
       * 仅 `minify: false` 可产出（2.18s / 4.4M）。
       *
       * 压缩交由部署侧（nginx brotli / CDN）承担。若换到非 WSL 环境构建，
       * 可删掉本项恢复默认 'oxc'。
       */
      minify: false,
    },
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
