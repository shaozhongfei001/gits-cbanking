import { test, expect } from '@playwright/test';
import { explorePage, inspectRoute, renderExplore, renderFindings } from './_harness';

/**
 * W2 客户域功能点验收：客户组合 / 组合看板 / 客户全景（含三个 Tab）/ 经营信号 /
 * 互动对象 / 需求与机会 / 需求记录 / 机会计划。
 */

const CUSTOMER_ID = 'CUST-CORP-0001';

const PAGES = [
  { id: 'P02', title: '客户组合', path: '/accounts' },
  { id: 'P03', title: '客户分层与组合看板', path: '/accounts/portfolio' },
  { id: 'P08', title: '经营信号', path: '/signals' },
  { id: 'P10', title: '互动对象主页', path: '/engagements' },
  { id: 'P20', title: '需求与机会', path: '/needs' },
];

test.describe('W2 客户域', () => {
  for (const entry of PAGES) {
    test(`${entry.id} ${entry.title} — 交互与四态`, async ({ browser }) => {
      const ctx = await browser.newContext();
      const p = await ctx.newPage();
      const report = await explorePage(p, entry.path);
      console.log(renderExplore(report));
      const blocking = report.findings.filter(
        item => item.kind !== 'resource_error' && item.kind !== 'requestfailed',
      );
      expect(blocking, renderExplore(report)).toEqual([]);
      await ctx.close();
    });
  }

  test('P04 客户全景 — 三 Tab（集团关系/业务资金/关系人）逐个可达且带真实客户', async ({ page }) => {
    for (const suffix of ['', '/group', '/funds', '/parties']) {
      const path = `/customers/${CUSTOMER_ID}${suffix}`;
      const result = await inspectRoute(page, path);
      const blocking = result.findings.filter(f => f.kind !== 'resource_error' && f.kind !== 'requestfailed');
      expect(blocking, renderFindings(path, result)).toEqual([]);
      expect(result.text, `${path} 未渲染客户身份`).toMatch(/华东精工|CUST-CORP-0001/);
    }
  });

  test('D-4 回归｜经营信号页跨页入口必须真的能到 P10 与经营旅程', async ({ page }) => {
    // 侧栏无 /engagements 菜单项，P10 只能从信号页入口进入 —— 入口缺失即孤儿页
    await page.goto('/signals', { waitUntil: 'networkidle' });
    await expect(page.getByTestId('p08-open-engagements')).toBeVisible({ timeout: 15000 });
    await page.getByTestId('p08-open-engagements').click();
    await expect(page).toHaveURL(/\/engagements/, { timeout: 20000 });
    expect(((await page.locator('#app').innerText()) ?? '').trim().length, '互动对象页白屏').toBeGreaterThan(40);

    await page.goto('/signals', { waitUntil: 'networkidle' });
    await expect(page.getByTestId('p08-open-journey')).toBeVisible({ timeout: 15000 });
    await page.getByTestId('p08-open-journey').click();
    await expect(page).toHaveURL(/\/engagement/, { timeout: 20000 });
    expect(((await page.locator('#app').innerText()) ?? '').trim().length, '经营旅程页白屏').toBeGreaterThan(40);
  });

  test('P02 客户组合 — 搜索框输入后列表必须响应（不得无变化）', async ({ page }) => {
    await page.goto('/accounts', { waitUntil: 'networkidle' });
    const search = page.locator('input[type="text"], .n-input__input-el').first();
    await expect(search).toBeVisible({ timeout: 15000 });
    const before = (await page.locator('#app').innerText()) ?? '';
    await search.fill('绿源');
    await page.waitForTimeout(1500);
    const after = (await page.locator('#app').innerText()) ?? '';
    expect(after.trim().length, '搜索后页面空白').toBeGreaterThan(40);
    // 搜索「绿源」应命中种子客户；若结果完全不变则视为交互无响应
    expect(after === before, '搜索后列表无任何变化（交互无响应）').toBe(false);
  });
});
