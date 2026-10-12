import { test, expect } from '@playwright/test';
import { installApiMocks } from './sit-fixtures';

test.describe('Journey Timeline', () => {
  test('should display journey record on current /journeys/:id route', async ({ page }) => {
    await installApiMocks(page);
    await page.goto('/journeys/jrn-001');
    await expect(page.locator('.journey-timeline')).toBeVisible();
    await expect(page.getByRole('heading', { name: '经营旅程' })).toBeVisible();
    await expect(page.locator('.journey-timeline')).toContainText('测试企业A');
  });

  test('should display interaction timeline after mocked journey load', async ({ page }) => {
    await installApiMocks(page);
    await page.goto('/journeys/jrn-001');
    await expect(page.getByText('了解企业融资需求')).toBeVisible();
    await expect(page.getByText('交互时间线')).toBeVisible();
  });
});
