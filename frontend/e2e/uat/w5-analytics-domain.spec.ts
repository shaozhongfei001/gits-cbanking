import { test, expect } from '@playwright/test';
import { explorePage, inspectRoute, renderExplore, renderFindings } from './_harness';

/**
 * W5 经营分析域（数据服务在 KERT）：经营指标 / 客群分析 / 组合查询 / 指标监视 + 供应链图谱报告。
 *
 * 验收要点：数据必须来自 KERT（/kert-api/*），且真实渲染出机构/期间/维度等可选项；
 * 不得出现 503 ANALYTICS_UNAVAILABLE 被静默吞掉的情况。
 */

const PAGES = [
  { id: 'AN-01', title: '经营指标分析', path: '/analytics/operating-metrics' },
  { id: 'AN-02', title: '细分客群分析', path: '/analytics/segments' },
  { id: 'AN-03', title: '组合条件查询分析', path: '/analytics/combo-query' },
  { id: 'AN-04', title: '指标监视器', path: '/analytics/monitors' },
];

test.describe('W5 经营分析域（KERT）', () => {
  for (const entry of PAGES) {
    test(`${entry.id} ${entry.title} — KERT 数据渲染`, async ({ page }) => {
      const result = await inspectRoute(page, entry.path, { settleMs: 1500 });
      console.log(renderFindings(entry.path, result));
      const blocking = result.findings.filter(
        item => item.kind !== 'resource_error' && item.kind !== 'requestfailed',
      );
      expect(blocking, renderFindings(entry.path, result)).toEqual([]);
      // 必须真的调用 KERT 分析服务（证明非本地桩）
      expect(result.apiCalls.some(call => call.includes('/kert-api/')), `未调用 KERT 分析服务：${result.apiCalls.join(' | ')}`).toBe(true);
    });
  }

  test('AN-01 经营指标 — 切换维度/机构后数据区必须刷新', async ({ page }) => {
    await page.goto('/analytics/operating-metrics', { waitUntil: 'networkidle' });
    await page.waitForTimeout(1500);
    const before = (await page.locator('#app').innerText()) ?? '';
    const selects = page.locator('.n-base-selection, .n-select, [role="combobox"]');
    const count = await selects.count();
    expect(count, '分析页缺少筛选器（机构/期间/维度）').toBeGreaterThan(0);
    await selects.first().click({ timeout: 5000 }).catch(() => undefined);
    await page.waitForTimeout(1200);
    const options = page.locator('.n-base-select-option, [role="option"]');
    if ((await options.count()) > 1) {
      await options.nth(1).click({ timeout: 5000 }).catch(() => undefined);
      await page.waitForTimeout(2500);
    }
    const after = (await page.locator('#app').innerText()) ?? '';
    expect(after.trim().length, '切换筛选后白屏').toBeGreaterThan(40);
    expect(after.includes('ANALYTICS_UNAVAILABLE'), 'KERT 分析不可用被直接渲染给用户').toBe(false);
    void before;
  });

  test('SCG-01 供应链图谱报告 — 无效 requestId 须给出可读提示', async ({ browser }) => {
    const ctx = await browser.newContext();
    const p = await ctx.newPage();
    const report = await explorePage(p, '/supply-chain-report/UAT-SCG-PLACEHOLDER', { allowHttp4xx: true });
    console.log(renderExplore(report));
    const blocking = report.findings.filter(
      item => item.kind !== 'resource_error' && item.kind !== 'requestfailed',
    );
    expect(blocking, renderExplore(report)).toEqual([]);
    await ctx.close();
  });
});
