import { defineConfig } from '@playwright/test';

export default defineConfig({
  testDir: './e2e',
  timeout: 30000,
  retries: 0,
  testIgnore: ['**/*.live.spec.ts'],
  // 无条件产出两种机器/人类可读报告：
  //   - json：`scripts/check-e2e-ran.mjs` 据此做 fail-closed 计数判定（CI 用）；
  //   - html：作为 artifact 上传，供失败时人工定位。
  // 刻意**不加** `process.env.CI` 分支：判定所需的 JSON 必须是结构性产物，
  // 不能依赖某个环境变量恰好被设置（否则会退化成"文件不存在"的静默失败）。
  // 两者都落在 .gitignore 已忽略的 playwright-report/ 下。
  reporter: [
    ['list'],
    ['html', { open: 'never', outputFolder: 'playwright-report' }],
    ['json', { outputFile: 'playwright-report/e2e-results.json' }],
  ],
  use: {
    baseURL: 'http://127.0.0.1:5173',
    trace: 'on-first-retry',
    screenshot: 'only-on-failure',
    video: 'retain-on-failure',
  },
  webServer: {
    command: 'npm run dev -- --host 127.0.0.1 --port 5173',
    url: 'http://127.0.0.1:5173/',
    reuseExistingServer: !process.env.CI,
    timeout: 60000,
  },
});
