import { test, expect } from '@playwright/test';

test.describe('Report Detail', () => {
  test('should display report content on current /reports/:id route', async ({ page }) => {
    await page.goto('/reports/rpt-001');
    await expect(page.locator('.report-detail')).toBeVisible();
    await expect(page.getByRole('heading', { name: 'R5A 内部关系报告' })).toBeVisible();
  });

  test('should display report type from placeholder fetchReport', async ({ page }) => {
    await page.goto('/reports/rpt-001');
    await expect(page.locator('.report-detail')).toContainText('INTERNAL_RELATIONSHIP');
    await expect(page.locator('.report-content')).toContainText('报告内容加载中');
  });
});
