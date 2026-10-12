import { defineConfig } from '@playwright/test';

/**
 * P24 E2E Owner 全链路验收专用配置。
 *  - 不忽略 *.live.spec.ts（本次验收就是 live 链路）
 *  - 不托管 webServer（前端/后端/KERT 已由外部启动）
 *  - 保留截图与 trace 作为验收证据
 */
export default defineConfig({
  testDir: './e2e',
  testMatch: ['**/p24-s4-wizard.live.spec.ts'],
  timeout: 600000,
  retries: 0,
  workers: 1,
  reporter: [['line'], ['html', { outputFolder: '../evidence/p24-e2e/_report', open: 'never' }]],
  use: {
    baseURL: 'http://127.0.0.1:5173',
    trace: 'on',
    screenshot: 'on',
    video: 'retain-on-failure',
    viewport: { width: 1600, height: 1200 },
    locale: 'zh-CN',
  },
});
