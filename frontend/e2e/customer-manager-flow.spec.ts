import { test, expect } from '@playwright/test';
import { installApiMocks } from './sit-fixtures';

test.describe('客户经理路径 — 已实现页 smoke（mock API）', () => {
  test('访前路径：工作台打开且禁用正式 Claim 写', async ({ page }) => {
    await installApiMocks(page);
    await page.goto('/engagement');
    await expect(page.getByTestId('p11-engagement-workspace')).toBeVisible();
    // p11-subnav 已移除；改用 signals-domain-tabs
    await expect(page.getByTestId('signals-domain-tabs')).toBeVisible();
    await expect(page.locator('body')).not.toHaveText(/^$/);
    await expect(page.getByRole('button', { name: '记为正式 Claim' })).toBeDisabled();
  });

  test('访前切片导航 stays on implemented routes', async ({ page }) => {
    await installApiMocks(page);
    await page.goto('/engagement');
    await page.getByTestId('p11-open-previsit').click();
    await expect(page).toHaveURL(/\/engagement\/previsit\/gaps/);
    // P12→P13 导航
    const goEvidence = page.getByTestId('p12-go-evidence');
    if (await goEvidence.isVisible({ timeout: 3000 }).catch(() => false)) {
      await goEvidence.click();
      await expect(page).toHaveURL(/\/engagement\/previsit\/evidence/);
    }
    // P13→P14 导航
    const goPack = page.getByTestId('p13-go-pack');
    if (await goPack.isVisible({ timeout: 3000 }).catch(() => false)) {
      await goPack.click();
      await expect(page).toHaveURL(/\/engagement\/previsit\/pack/);
    }
  });

  test('承诺中心：展示 mock 承诺/任务，不把 Need 派生写解开', async ({ page }) => {
    await installApiMocks(page);
    await page.goto('/commitments');
    await expect(page.getByTestId('p36-commitments')).toHaveAttribute('data-page-id', 'P36');
    await expect(page.getByText('提供三年期融资结构建议')).toBeVisible();
    await expect(page.getByText('跟进设备清单')).toBeVisible();
    await expect(page.getByRole('heading', { name: '机会管线' })).toBeVisible();
    await expect(page.getByTestId('gated-action')).toBeDisabled();
    await expect(page.getByTestId('p36-create-commitment')).toBeVisible();
  });

  test('外部事件监控：mock 列表可见', async ({ page }) => {
    await installApiMocks(page);
    await page.goto('/external-events');
    await expect(page.getByRole('heading', { name: '外部事件监控' })).toBeVisible();
    await expect(page.getByText('事件总数')).toBeVisible();
    await expect(page.getByText('行业产能公告')).toBeVisible();
  });

  test('工作台队列进入客户经营总览', async ({ page }) => {
    await installApiMocks(page);
    await page.goto('/');
    await expect(page.getByTestId('p01-action-queue')).toContainText('测试企业A');
    await page.getByRole('button', { name: '测试企业A' }).click();
    await expect(page).toHaveURL(/\/customers\/cust-001/);
    await expect(page.getByTestId('p04-customer-record')).toBeVisible();
  });

  test('主导航在已实现页之间切换且非空白', async ({ page }) => {
    await installApiMocks(page);
    const pages = [
      { path: '/', testId: 'p01-workbench' },
      { path: '/engagement', testId: 'p11-engagement-workspace' },
      { path: '/commitments', testId: 'p36-commitments' },
    ];
    for (const item of pages) {
      await page.goto(item.path);
      await expect(page.getByTestId(item.testId)).toBeVisible();
    }
  });

  test('边界：客户列表 API 失败时工作台展示错误态', async ({ page }) => {
    await installApiMocks(page, 'error');
    await page.goto('/engagement');
    await expect(page.getByTestId('p11-engagement-workspace')).toBeVisible();
    await expect(page.getByTestId('error-state')).toBeVisible();
  });
});
