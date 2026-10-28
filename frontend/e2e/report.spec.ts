import { test, expect } from '@playwright/test';
import { installApiMocks } from './sit-fixtures';

// R5A 报告详情当前实现（ReportDetail.vue）：
// 报告不再通过 /reports/:id 独立端点获取，必须携带 journeyId 上下文；
// 缺失上下文时渲染 report-not-found 引导态，而不是空白页或伪内容。
test.describe('Report Detail', () => {
  test('无 journeyId 上下文时渲染引导态而非空白页', async ({ page }) => {
    // 本套件是 mock/SIT 套件（真实后端用例在 *.live.spec.ts，由 playwright.live.config.ts 运行）。
    // 必须安装 mock：否则 AppSidebar 的 fetchCommitments 会经 vite 代理打到无人监听的
    // 127.0.0.1:8080，日志出现 `http proxy error: /api/v1/commitments` + `ECONNREFUSED`
    // （真实 CI run 34870734027 即如此），从而误导排障为"缺后端"。
    await installApiMocks(page);
    await page.goto('/reports/rpt-001');
    await expect(page.locator('.report-detail')).toBeVisible();
    await expect(page.getByTestId('report-not-found')).toBeVisible();
    await expect(page.getByTestId('report-not-found')).toContainText('报告只能随旅程查看');
  });

  test('引导态明确说明需要 journeyId 才能定位报告', async ({ page }) => {
    await installApiMocks(page);
    await page.goto('/reports/rpt-001');
    const guide = page.getByTestId('report-not-found');
    await expect(guide).toContainText('报告详情未接入独立端点');
    await expect(guide).toContainText('journeyId');
    // 无上下文时不应渲染任何报告正文容器
    await expect(page.locator('.report-content')).toHaveCount(0);
  });
});
