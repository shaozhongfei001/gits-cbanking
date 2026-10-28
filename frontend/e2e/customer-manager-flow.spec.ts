import { test, expect } from '@playwright/test';
import { installApiMocks, mockJourney } from './sit-fixtures';

test.describe('客户经理路径 — 已实现页 smoke（mock API）', () => {
  test('P45 经营旅程列表：列出旅程且未结束行给出「持续经营」', async ({ page }) => {
    await installApiMocks(page);
    // 列表端点（无 customerId）在全量列表页返回 mock 旅程
    await page.route(url => url.pathname === '/api/v1/engagement/journey', async (route) => {
      if (route.request().method() !== 'GET') {
        await route.fallback();
        return;
      }
      await route.fulfill({ json: [mockJourney] });
    });
    await page.goto('/engagement');
    await expect(page.getByTestId('p45-journey-list')).toBeVisible();
    await expect(page.getByTestId('signals-domain-tabs')).toBeVisible();
    await expect(page.getByTestId('p45-continue-jrn-001')).toBeVisible();
    await expect(page.getByText('测试企业A 经营旅程 #1')).toBeVisible();

    // 「持续经营」必须进入该旅程的工作区（journeyId 进 URL）
    await page.getByTestId('p45-continue-jrn-001').click();
    await expect(page).toHaveURL(/\/engagement\/workspace\/jrn-001/);
    await expect(page.getByTestId('p11-engagement-workspace')).toBeVisible();
  });

  test('访前路径：工作区（URL 带 journeyId）打开且禁用正式 Claim 写', async ({ page }) => {
    await installApiMocks(page);
    await page.goto('/engagement/workspace/jrn-001');
    await expect(page.getByTestId('p11-engagement-workspace')).toBeVisible();
    // p11-subnav 已移除；改用 signals-domain-tabs
    await expect(page.getByTestId('signals-domain-tabs')).toBeVisible();
    await expect(page.locator('body')).not.toHaveText(/^$/);
    await expect(page.getByTestId('p11-journey-bar')).toContainText('测试企业A');
    await expect(page.getByRole('button', { name: '记为正式 Claim' })).toBeDisabled();
  });

  test('访前切片导航 stays on implemented routes', async ({ page }) => {
    await installApiMocks(page);
    await page.goto('/engagement/workspace/jrn-001');
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
    // 机会管线位于折叠面板 <details> 内，需先展开再断言可见
    await page.locator('summary', { hasText: '商机阶段摘要' }).click();
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
    // 页面存在 queue/thread/commitment 三个同名按钮，限定工作台行动队列内点击
    await page.getByTestId('p01-action-queue').getByRole('button', { name: '测试企业A' }).first().click();
    await expect(page).toHaveURL(/\/customers\/cust-001/);
    await expect(page.getByTestId('p04-customer-record')).toBeVisible();
  });

  test('主导航在已实现页之间切换且非空白', async ({ page }) => {
    await installApiMocks(page);
    const pages = [
      { path: '/', testId: 'p01-workbench' },
      // 「经营旅程」第一入口 = 列表（P45）；工作区必须由带 journeyId 的 URL 承载
      { path: '/engagement', testId: 'p45-journey-list' },
      { path: '/engagement/workspace/jrn-001', testId: 'p11-engagement-workspace' },
      { path: '/commitments', testId: 'p36-commitments' },
    ];
    for (const item of pages) {
      await page.goto(item.path);
      await expect(page.getByTestId(item.testId)).toBeVisible();
    }
  });

  test('铁律：无 journeyId 的旧入口 /engagement/workspace 重定向到列表', async ({ page }) => {
    await installApiMocks(page);
    await page.goto('/engagement/workspace');
    await expect(page).toHaveURL(/\/engagement$/);
    await expect(page.getByTestId('p45-journey-list')).toBeVisible();
    await expect(page.getByTestId('p11-engagement-workspace')).toHaveCount(0);
  });

  test('边界：旅程接口失败时工作区展示错误态（不静默降级为空旅程）', async ({ page }) => {
    await installApiMocks(page, 'error');
    await page.goto('/engagement/workspace/jrn-001');
    await expect(page.getByTestId('p11-engagement-workspace')).toBeVisible();
    await expect(page.getByTestId('error-state')).toBeVisible();
  });
});
