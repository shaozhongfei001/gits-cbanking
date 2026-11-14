import { defineConfig } from '@playwright/test';

const DEMO_BASE_URL = process.env.QA_BASE_URL ?? 'http://127.0.0.1:15173'
const API_PROXY_TARGET = process.env.VITE_API_PROXY_TARGET ?? 'http://127.0.0.1:18080'
const KERT_PROXY_TARGET = process.env.VITE_KERT_PROXY_TARGET ?? 'http://127.0.0.1:8107'

export default defineConfig({
  testDir: './e2e',
  // 真实 LLM 链路（建议书 ~30s / 访前准备 60s+）+ fullPage 截图需要更大的预算。
  // 只调时间预算，不动任何断言口径（断言见 e2e/uat/_harness.ts）。
  timeout: 120000,
  // 单后端(18080) + 单 KERT(8107) + 真实 LLM 链路：默认 8 worker 会把服务打慢，
  // 实测出现「详情响应未落地 / 路由视图未挂载」的时序红灯（A4 / W4-P32 / PC1）。
  // 压到 4 worker 并给异步断言更大预算，换取可重复演示；判据本身不放宽。
  workers: 4,
  expect: { timeout: 30000 },
  retries: 0,
  testIgnore: ['**/*.live.spec.ts'],
  // Playwright 每轮会清空 outputDir。把原始产物收敛到子目录，
  // 避免把 QA_EVIDENCE_DIR 下的截图证据一并删掉（分多轮跑 uat / qa / 全量时尤其重要）。
  outputDir: 'test-results/raw',
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
    // 与演示同一条链路（15173 → vite 代理 → 18080/8107），避免"测的和演的"不一致。
    baseURL: DEMO_BASE_URL,
    trace: 'on-first-retry',
    // 全局仍是 only-on-failure；每场景证据由 e2e/uat/_harness.ts 显式截图，
    // 不给所有用例（尤其 W8 故障注入）增加无谓的截图开销。
    screenshot: 'only-on-failure',
    video: 'retain-on-failure',
  },
  webServer: {
    // 演示栈已由 scripts/demo-startup.sh 起好时复用；若单独跑 E2E，也按演示端口起，
    // 并显式注入代理目标，避免 vite 默认指向 8080 导致 API 全挂。
    command: `VITE_API_PROXY_TARGET=${API_PROXY_TARGET} VITE_KERT_PROXY_TARGET=${KERT_PROXY_TARGET} npm run dev -- --host 127.0.0.1 --port 15173`,
    url: `${DEMO_BASE_URL}/`,
    reuseExistingServer: !process.env.CI,
    timeout: 60000,
  },
});
