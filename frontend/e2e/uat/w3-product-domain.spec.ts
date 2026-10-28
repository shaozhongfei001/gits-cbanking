import { test, expect } from '@playwright/test';
import { explorePage, inspectRoute, renderExplore, renderFindings } from './_harness';

/**
 * W3 产品域功能点验收：产品中心（目录/章节/产品详情）/ 产品解读 / 知识地图 / 受控推荐三段式。
 */

test.describe('W3 产品域', () => {
  test('PC-01 产品中心 — 目录、族、产品详情三段联动', async ({ browser }) => {
    const ctx = await browser.newContext();
    const p = await ctx.newPage();
    const report = await explorePage(p, '/product-center', { maxTabs: 12, maxLinks: 8 });
    console.log(renderExplore(report));
    const blocking = report.findings.filter(
      item => item.kind !== 'resource_error' && item.kind !== 'requestfailed',
    );
    expect(blocking, renderExplore(report)).toEqual([]);
    await ctx.close();
  });

  test('PC-01 产品中心 — 点击产品卡必须切换产品详情（URL 与首屏一致）', async ({ page }) => {
    await page.goto('/product-center', { waitUntil: 'networkidle' });
    await expect(page.locator('#app')).toContainText('产品目录', { timeout: 15000 });
    const cards = page.locator('[data-testid="pc-catalog-product"]');
    await expect(cards.first(), '产品目录为空（pc-catalog-product 无渲染）').toBeVisible({ timeout: 15000 });
    const count = await cards.count();
    expect(count, '产品目录为空').toBeGreaterThan(0);
    const first = cards.first();
    await first.click();
    await page.waitForTimeout(1800);
    const text = (await page.locator('#app').innerText()) ?? '';
    expect(text.trim().length).toBeGreaterThan(40);
    // 选中产品后 URL 应带 productId（证明状态可 URL 化、可分享）
    expect(page.url(), '点击产品后 URL 未带 productId').toMatch(/\/product-center\/.+/);
  });

  test('知识地图 — 数据可渲染（P38 产品解读页已下线）', async ({ browser }) => {
    const ctx = await browser.newContext();
    const p = await ctx.newPage();
    for (const path of ['/knowledge-map']) {
      const report = await explorePage(p, path);
      console.log(renderExplore(report));
      const blocking = report.findings.filter(
        item => item.kind !== 'resource_error' && item.kind !== 'requestfailed',
      );
      expect(blocking, renderExplore(report)).toEqual([]);
    }
    await ctx.close();
  });

  test('REC-01 受控推荐工作区 — 无效 runId 必须给出可读提示而非白屏', async ({ page }) => {
    const result = await inspectRoute(page, '/recommendation/UAT-RUN-PLACEHOLDER', { allowHttp4xx: true });
    const blocking = result.findings.filter(f => f.kind !== 'resource_error' && f.kind !== 'requestfailed');
    expect(blocking, renderFindings('/recommendation/UAT-RUN-PLACEHOLDER', result)).toEqual([]);
    // 无效 ID 下不得把占位内容伪装成真实推荐结果
    expect(result.text, '无效 runId 页面未给出可读提示').toMatch(/不存在|未找到|暂无|失败|错误|不可用|未接入|加载失败/);
  });
});
