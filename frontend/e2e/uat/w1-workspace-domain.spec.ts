import { test, expect } from '@playwright/test';
import { explorePage, pickJourneyId, inspectRoute, renderExplore, renderFindings } from './_harness';

/**
 * W1 经营域功能点验收：经营总览 / 我的任务 / 经营旅程列表 / 进入旅程 / 互动工作区。
 *
 * 每个功能点都走真实浏览器交互（Tab 切换 + 站内链接进入），逐步复检可见性。
 */

const PAGES = [
  { id: 'P01', title: '经营总览', path: '/workbench' },
  { id: 'P36', title: '我的任务', path: '/commitments' },
  { id: 'P45', title: '经营旅程', path: '/engagement' },
];

test.describe('W1 经营域', () => {
  let journeyId = 'jny-001';
  let customerId = 'CUST-CORP-0001';

  test.beforeAll(async () => {
    // 按种子客户精确挑选，避免被「启动旅程」用例写入的新旅程污染（F-UAT2-01）
    journeyId = (await pickJourneyId()) ?? journeyId;
  });

  for (const page of PAGES) {
    test(`${page.id} ${page.title} — 交互与四态`, async ({ browser }) => {
      const ctx = await browser.newContext();
      const p = await ctx.newPage();
      const report = await explorePage(p, page.path);
      console.log(renderExplore(report));
      const blocking = report.findings.filter(
        item => item.kind !== 'resource_error' && item.kind !== 'requestfailed',
      );
      expect(blocking, renderExplore(report)).toEqual([]);
      await ctx.close();
    });
  }

  test('P45 经营旅程列表 — 启动旅程必须产出真实 journeyId 并进入工作区', async ({ page }) => {
    const result = await inspectRoute(page, '/engagement');
    expect(result.findings.filter(f => f.kind !== 'resource_error' && f.kind !== 'requestfailed'), renderFindings('/engagement', result)).toEqual([]);

    // 旅程列表须渲染出真实旅程行（不得为空壳）
    await expect(page.locator('text=经营旅程名称')).toBeVisible({ timeout: 15000 });

    // 工具栏「启动旅程」→ 选客户 → 进入该旅程工作区（journeyId 必须进 URL）
    const startBtn = page.getByTestId('p45-start-journey');
    await expect(startBtn, '旅程列表缺少「启动旅程」入口').toBeVisible({ timeout: 15000 });
    await startBtn.click();
    const pick = page.locator('[data-testid^="p45-pick-"]').first();
    await expect(pick, '启动旅程后未出现客户选择').toBeVisible({ timeout: 20000 });
    await pick.click();
    await expect(page).toHaveURL(/\/engagement\/(workspace|enter)/, { timeout: 30000 });
    const text = (await page.locator('#app').innerText()) ?? '';
    expect(text.trim().length, '进入旅程后白屏').toBeGreaterThan(40);
  });

  test('P11 互动工作区 — 旅程上下文与访前入口', async ({ page }) => {
    const result = await inspectRoute(page, `/engagement/workspace/${journeyId}`);
    expect(result.findings.filter(f => f.kind !== 'resource_error' && f.kind !== 'requestfailed'), renderFindings(`/engagement/workspace/${journeyId}`, result)).toEqual([]);
    // 工作区必须带出客户名（证明拿的是真实旅程，不是空壳）
    expect(result.text).toMatch(/华东精工|装备|CUST-CORP-0001/);
    void customerId;
  });
});
