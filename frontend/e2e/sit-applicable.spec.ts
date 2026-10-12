import { test, expect } from '@playwright/test';
import { installApiMocks } from './sit-fixtures';

test.describe('P37 applicable SIT smoke — implemented pages only', () => {
  test('/workbench four-state and disabled write', async ({ page }) => {
    await installApiMocks(page);
    await page.goto('/workbench');
    await expect(page.getByTestId('p01-workbench')).toBeVisible();
    await expect(page.getByTestId('success-state')).toBeVisible();
    await expect(page.getByTestId('gated-action')).toBeDisabled();
  });

  test('/commitments keeps pageId P36 and Need-derived write disabled', async ({ page }) => {
    await installApiMocks(page);
    await page.goto('/commitments');
    await expect(page.getByTestId('p36-commitments')).toHaveAttribute('data-page-id', 'P36');
    await expect(page.getByTestId('object-header')).toContainText('任务与承诺中心');
    await expect(page.getByTestId('success-state')).toBeVisible();
    await expect(page.getByTestId('gated-action')).toBeDisabled();
  });

  test('/proposals is C2 empty shell, import stays disabled', async ({ page }) => {
    await installApiMocks(page);
    await page.goto('/proposals');
    await expect(page.getByTestId('p23-proposals')).toBeVisible();
    await expect(page.getByTestId('success-state')).toBeVisible();
    await expect(page.getByTestId('p23-empty')).toBeVisible();
    await expect(page.getByTestId('gated-action')).toBeDisabled();
    await expect(page.getByTestId('disabled-reason')).toContainText(/建议书|解除路径|原因/);
  });

  test('/approvals lists mocked HumanGate without inventing a new gate', async ({ page }) => {
    await installApiMocks(page);
    await page.goto('/approvals');
    await expect(page.getByTestId('p32-approvals')).toBeVisible();
    await expect(page.getByTestId('success-state')).toBeVisible();
    await expect(page.getByTestId('p32-gate-g-pending')).toBeVisible();
    await expect(page.getByTestId('p32-open-first')).toBeEnabled();
  });

  test('/m/today is online-only C2 and offline queue stays disabled', async ({ page }) => {
    await installApiMocks(page);
    await page.goto('/m/today');
    await expect(page.getByTestId('p41-mobile-today')).toBeVisible();
    await expect(page.getByTestId('success-state')).toBeVisible();
    await expect(page.getByTestId('p41-today-queue')).toContainText('测试企业A');
    await expect(page.getByTestId('gated-action')).toBeDisabled();
    await expect(page.getByTestId('disabled-reason')).toContainText(/离线|缓存|解除路径|原因/);
    await expect(page.getByTestId('p41-open-first')).toHaveAttribute('href', '/customers/cust-001');
  });

  test('/approvals error state is visible when HumanGate API fails', async ({ page }) => {
    await installApiMocks(page, 'error');
    await page.goto('/approvals');
    await expect(page.getByTestId('error-state')).toBeVisible();
    await expect(page.getByTestId('retry-action')).toBeVisible();
  });
});
