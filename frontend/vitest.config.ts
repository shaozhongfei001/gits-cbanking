import { defineConfig } from 'vitest/config'
import vue from '@vitejs/plugin-vue'

export default defineConfig({
  plugins: [vue()],
  test: {
    globals: true,
    environment: 'happy-dom',
    // E2E 测试（e2e/*.spec.ts）由 Playwright 单独运行（package.json 的 e2e script），
    // vitest 只负责单元/组件测试，故显式排除 e2e/ 目录。
    exclude: ['e2e/**', 'scripts/**', 'node_modules/**', 'dist/**'],
    coverage: {
      provider: 'v8',
      reporter: ['text', 'json', 'html'],
    },
  },
})
