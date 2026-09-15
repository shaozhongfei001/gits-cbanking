import { test, expect } from '@playwright/test';
import { installApiMocks } from './sit-fixtures';

test.describe('Dashboard / P01 workbench smoke', () => {
  test('should display current workbench title, not legacy 客户经营概览', async ({ page }) => {
    await installApiMocks(page);
    await page.goto('/');
    await expect(page.getByTestId('p01-workbench')).toBeVisible();
    await expect(page.getByTestId('object-header').locator('h1')).toHaveText('首页·我的客户经营');
    await expect(page.locator('h1')).not.toHaveText('客户经营概览');
  });

  test('should render derived action queue from mocked customers', async ({ page }) => {
    await installApiMocks(page);
    await page.goto('/');
    await expect(page.getByTestId('success-state')).toBeVisible();
    const queue = page.getByTestId('p01-action-queue');
    await expect(queue).toBeVisible();
    await expect(queue).toContainText('测试企业A');
    await expect(queue).toContainText('测试企业B');
  });

  test('should expose four-state error, not a silent pass', async ({ page }) => {
    await installApiMocks(page, 'error');
    await page.goto('/');
    await expect(page.getByTestId('error-state')).toBeVisible();
    await expect(page.getByTestId('retry-action')).toBeVisible();
  });
});
