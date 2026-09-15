import { test, expect } from '@playwright/test';
import { installApiMocks } from './sit-fixtures';

test.describe('Report Detail', () => {
  test('should display report content on current /reports/:id route', async ({ page }) => {
    // 本套件是 mock/SIT 套件（真实后端用例在 *.live.spec.ts，由 playwright.live.config.ts 运行）。
    // 必须安装 mock：否则 AppSidebar 的 fetchCommitments 会经 vite 代理打到无人监听的
    // 127.0.0.1:8080，日志出现 `http proxy error: /api/v1/commitments` +
    // `ECONNREFUSED`（真实 CI run 34870734027 即如此），从而**误导排障**为"缺后端"。
    // 本用例的断言只涉及 ReportDetail，与侧边栏无关。
    await installApiMocks(page);
    await page.goto('/reports/rpt-001');
    await expect(page.locator('.report-detail')).toBeVisible();
    await expect(page.getByRole('heading', { name: 'R5A 内部关系报告' })).toBeVisible();
  });

  test('should display report type from placeholder fetchReport', async ({ page }) => {
    await installApiMocks(page);
    await page.goto('/reports/rpt-001');
    await expect(page.locator('.report-detail')).toContainText('INTERNAL_RELATIONSHIP');
    await expect(page.locator('.report-content')).toContainText('报告内容加载中');
  });
});
