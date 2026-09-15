import { test, expect } from '@playwright/test';
import { installApiMocks } from './sit-fixtures';

test.describe('P05 客户全景 · 集团关系图谱', () => {
  test('客户全景页签进入集团关系并展示企业图谱', async ({ page }) => {
    await installApiMocks(page);
    await page.goto('/customers/cust-001/group');
    await expect(page.getByTestId('p05-group')).toBeVisible();
    await expect(page.getByTestId('object-header')).toContainText('集团关系');
    await expect(page.getByTestId('tab-p05')).toBeVisible();
    await expect(page.getByTestId('p05-group-graph')).toBeVisible();
    await expect(page.getByTestId('p05-member-table')).toContainText('DKWS上游钢厂');
    await expect(page.getByTestId('p05-metrics')).toContainText('图谱节点');
    await expect(page.getByTestId('p05-gate-panel')).toContainText('发起核验');
    await expect(page.getByTestId('gated-action')).toBeDisabled();
    await expect(page.getByText('董事长')).toHaveCount(0);
  });

  test('经营总览可通过页签切到集团关系', async ({ page }) => {
    await installApiMocks(page);
    await page.goto('/customers/cust-001');
    await page.getByTestId('tab-p05').click();
    await expect(page).toHaveURL(/\/customers\/cust-001\/group/);
    await expect(page.getByTestId('p05-group-graph')).toBeVisible();
  });
});
