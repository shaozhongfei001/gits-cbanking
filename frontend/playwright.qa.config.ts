import { defineConfig } from '@playwright/test'
import base from './playwright.config'

/**
 * E2E QA 专用配置（QA 只读验收）。**不改 playwright.config.ts 的任何默认值。**
 *
 * 存在的理由（已核实的环境事实，不是猜测）：
 * 1. 基线 config 的 testIgnore 会排除 live 用例，而本次验收要求跑它们；
 * 2. 基线 config 的 webServer 会另起 5173，其 vite 代理默认指向 127.0.0.1:8080，
 *    实测 8080 返回 401，并非本次被测后端；
 * 3. 本次被测的「已运行环境」是 15173(frontend) / 18080(backend) / 8107(KERT) / 9621(LightRAG)。
 *
 * 因此：覆盖 testIgnore 与 baseURL，禁用 webServer，证据全开（trace/screenshot/video）。
 *
 * 用法：
 *   QA_BASE_URL=http://127.0.0.1:15173 npx playwright test --config playwright.qa.config.ts
 *   QA_BASE_URL=http://127.0.0.1:15173 QA_INCLUDE_LIVE=1 npx playwright test --config playwright.qa.config.ts
 */
const includeLive = process.env.QA_INCLUDE_LIVE === '1'
const reportDir = process.env.QA_REPORT_DIR ?? 'test-results/qa-latest'

export default defineConfig(base, {
  testIgnore: includeLive ? [] : ['**/*.live.spec.ts'],
  webServer: undefined,
  // 可覆盖：复跑时用新的子目录，避免 Playwright 清理旧产物目录
  outputDir: process.env.QA_OUTPUT_DIR ?? `${reportDir}/raw`,
  reporter: [['list'], ['html', { outputFolder: reportDir, open: 'never' }]],
  use: {
    ...base.use,
    baseURL: process.env.QA_BASE_URL ?? 'http://127.0.0.1:15173',
    trace: 'on',
    screenshot: 'on',
    video: 'on',
  },
})
