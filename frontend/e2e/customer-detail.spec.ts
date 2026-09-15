import { test, expect } from '@playwright/test';
import { installApiMocks } from './sit-fixtures';

test.describe('Customer Detail / P04', () => {
  test('should display customer basic info on current /customers/:id route', async ({ page }) => {
    await installApiMocks(page);
    await page.goto('/customers/cust-001');
    await expect(page.getByTestId('p04-customer-record')).toBeVisible();
    await expect(page.getByTestId('success-state')).toBeVisible();
    await expect(page.getByTestId('p04-customer-record')).toContainText('测试企业A');
    await expect(page.getByTestId('customer-slice-tabs')).toBeVisible();
  });

  test('should display KYC gap profile section', async ({ page }) => {
    await installApiMocks(page);
    await page.goto('/customers/cust-001');
    await expect(page.getByText('KYC缺口摘要')).toBeVisible();
    await expect(page.getByText('实控人信息')).toBeVisible();
  });

  test('should display opportunity signals and keep write gated', async ({ page }) => {
    await installApiMocks(page);
    await page.goto('/customers/cust-001');
    await expect(page.getByText('机会信号')).toBeVisible();
    await expect(page.getByTestId('gated-action')).toBeDisabled();
    await expect(page.getByTestId('disabled-reason')).toContainText(/原因|解除路径/);
  });
});
