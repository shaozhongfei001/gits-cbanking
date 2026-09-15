import { test, expect } from '@playwright/test';
import { installApiMocks } from './sit-fixtures';

test.describe('P30 Experience Shell', () => {
  test('workbench opens with GITS Bank shell and left groups', async ({ page }) => {
    await installApiMocks(page);
    await page.goto('/workbench');
    await expect(page.getByTestId('shell-brand')).toContainText('GITS Bank');
    await expect(page.getByTestId('shell-sidebar')).toBeVisible();
    await expect(page.getByTestId('nav-group-daily')).toBeVisible();
    await expect(page.getByTestId('nav-item-workbench')).toContainText('客户经营作战台');
    const sidebar = page.getByTestId('shell-sidebar');
    // 本清单必须与 src/layouts/navConfig.ts 的 SHELL_NAV_GROUPS 保持一致。
    // 它曾发生漂移：提交 11bd3d9（IA 改名 + 新增产品推荐菜单）把 '证据与知识' 改名为
    // '产品解读与知识' 并新增 '产品推荐'，只同步更新了单测 AppSidebar.spec.ts，
    // 本用例未同步 → E2E job 长期红（CI run 34870734027）。改导航时请一并改这里。
    for (const label of [
      '客户经营作战台',
      '我的任务与承诺',
      '客户组合',
      '客户全景',
      '信号与互动',
      '需求与机会',
      '服务建议书',
      '产品推荐',
      '专家协同',
      '账户计划与价值',
      '产品解读与知识',
      '审批与审计',
    ]) {
      await expect(sidebar.getByRole('button', { name: label, exact: true })).toBeVisible();
    }
    await expect(sidebar.getByRole('button', { name: '访前路径' })).toHaveCount(0);
    await expect(sidebar.getByRole('button', { name: '会中工作区' })).toHaveCount(0);
    await expect(sidebar.getByRole('button', { name: 'CRM受控回写' })).toHaveCount(0);
    await expect(sidebar.getByRole('button', { name: '今日客户行动' })).toHaveCount(0);
    const siderBg = await sidebar.evaluate(el => getComputedStyle(el).backgroundColor);
    expect(siderBg).toBe('rgb(8, 35, 59)');
    await expect(page.getByTestId('p01-workbench')).toBeVisible();
    await expect(page.getByTestId('success-state')).toBeVisible();
    await expect(page.getByTestId('object-header')).toContainText('首页·我的客户经营');
  });

  test('legacy / still opens the workbench', async ({ page }) => {
    await installApiMocks(page);
    await page.goto('/');
    await expect(page.getByTestId('p01-workbench')).toBeVisible();
    await expect(page.getByTestId('p01-action-queue')).toContainText('测试企业A');
  });

  test('API 500 is an error state, not a pass', async ({ page }) => {
    await installApiMocks(page, 'error');
    await page.goto('/workbench');
    await expect(page.getByTestId('error-state')).toBeVisible();
    await expect(page.getByTestId('success-state')).toHaveCount(0);
  });

  test('P01 confirmation write stays DisabledAction', async ({ page }) => {
    await installApiMocks(page);
    await page.goto('/workbench');
    await expect(page.getByTestId('gated-action')).toBeDisabled();
    await expect(page.getByTestId('disabled-reason')).toContainText(/原因|解除路径/);
  });
});
