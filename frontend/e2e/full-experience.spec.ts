import { test, expect } from '@playwright/test';
import { installApiMocks } from './sit-fixtures';

test.describe('GITS Experience Shell — implemented-page smoke', () => {
  test('1. login page — 开发模式进入 workbench', async ({ page }) => {
    await installApiMocks(page);
    await page.goto('/login');
    await expect(page.locator('.login-title')).toContainText('GITS');
    await page.getByRole('button', { name: '开发模式直接进入' }).click();
    await expect(page).not.toHaveURL(/login/);
    await expect(page.getByTestId('p01-workbench')).toBeVisible();
  });

  test('2. workbench shows mocked customers, not 华东精工', async ({ page }) => {
    await installApiMocks(page);
    await page.goto('/');
    await expect(page.getByTestId('p01-workbench')).toBeVisible();
    await expect(page.getByTestId('p01-action-queue')).toContainText('测试企业A');
    await expect(page.getByText('华东精工')).toHaveCount(0);
  });

  test('3. customer record opens from workbench queue', async ({ page }) => {
    await installApiMocks(page);
    await page.goto('/');
    await page.getByRole('button', { name: '测试企业A' }).click();
    await expect(page).toHaveURL(/\/customers\/cust-001/);
    await expect(page.getByTestId('p04-customer-record')).toBeVisible();
    await expect(page.getByTestId('p04-customer-record')).toContainText('测试企业A');
  });

  test('4. engagement workspace keeps stage path and gated Claim write', async ({ page }) => {
    await installApiMocks(page);
    await page.goto('/engagement');
    await expect(page.getByTestId('p11-engagement-workspace')).toBeVisible();
    // p11-object-context 已移除；改用 stage-path 断言
    await expect(page.getByTestId('stage-path')).toBeVisible();
    await expect(page.getByRole('button', { name: '记为正式 Claim' })).toBeDisabled();
  });

  test('5. commitments center keeps pageId P36 and Need-derived write disabled', async ({ page }) => {
    await installApiMocks(page);
    await page.goto('/commitments');
    await expect(page.getByTestId('p36-commitments')).toBeVisible();
    await expect(page.getByTestId('p36-commitments')).toHaveAttribute('data-page-id', 'P36');
    await expect(page.getByTestId('success-state')).toBeVisible();
    await expect(page.getByRole('heading', { name: '承诺列表' })).toBeVisible();
    await expect(page.getByText('提供三年期融资结构建议')).toBeVisible();
    await expect(page.getByRole('heading', { name: '任务列表' })).toBeVisible();
    await expect(page.getByText('跟进设备清单')).toBeVisible();
    await expect(page.getByRole('heading', { name: '机会管线' })).toBeVisible();
    await expect(page.getByTestId('gated-action')).toBeDisabled();
    await expect(page.getByTestId('disabled-reason')).toContainText(/Need|解除路径|原因/);
  });

  test('6. external events page shows mocked events or empty, not a blank shell', async ({ page }) => {
    await installApiMocks(page);
    await page.goto('/external-events');
    await expect(page.getByRole('heading', { name: '外部事件监控' })).toBeVisible();
    await expect(page.getByText('事件总数')).toBeVisible();
    await expect(page.getByText('行业产能公告')).toBeVisible();
  });

  test('7. shell sidebar navigates implemented routes', async ({ page }) => {
    await installApiMocks(page);
    await page.goto('/');
    const menu = page.getByTestId('shell-sidebar');
    await menu.getByRole('button', { name: '信号与互动' }).click();
    await expect(page).toHaveURL(/\/engagement/);
    await menu.getByRole('button', { name: '我的任务与承诺' }).click();
    await expect(page).toHaveURL(/\/commitments/);
    await menu.getByRole('button', { name: '客户组合' }).click();
    await expect(page).toHaveURL(/\/accounts/);
    await page.getByTestId('shell-brand').click();
    await expect(page).toHaveURL(/\/workbench\/?$/);
  });

  test('8. mocked APIs populate implemented pages without live backend writes', async ({ page }) => {
    await installApiMocks(page);
    await page.goto('/workbench');
    await expect(page.getByTestId('p01-action-queue')).toContainText('测试企业A');
    await page.goto('/commitments');
    await expect(page.getByText('提供三年期融资结构建议')).toBeVisible();
    await page.goto('/engagements');
    await expect(page.getByTestId('p10-engagements')).toBeVisible();
    await expect(page.getByTestId('success-state')).toBeVisible();
  });

  test('9. implemented pages do not crash the shell', async ({ page }) => {
    const criticalErrors: string[] = [];
    page.on('pageerror', err => criticalErrors.push(err.message));
    await installApiMocks(page);
    for (const path of ['/', '/engagement', '/commitments', '/external-events', '/proposals', '/approvals', '/m/today']) {
      await page.goto(path);
      await expect(page.getByTestId('experience-shell')).toBeVisible();
    }
    const crashErrors = criticalErrors.filter(
      e => !e.includes('favicon') && !e.includes('ResizeObserver') && !e.includes('Resize observer'),
    );
    expect(crashErrors, crashErrors.join('\n')).toEqual([]);
  });
});
