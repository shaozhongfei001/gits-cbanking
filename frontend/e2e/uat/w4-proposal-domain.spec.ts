import { test, expect } from '@playwright/test';
import { explorePage, renderExplore } from './_harness';

/**
 * W4 方案域功能点验收：建议书（列表/向导/记录/编辑器/映射/依据/对照/版本）、
 * 专家协同、审批中心、账户计划、对客交付、客户价值。
 *
 * 立场：方案域多数为 C2 降级壳 —— 验收重点不是「有没有数据」，而是
 * **是否诚实标注降级**（不得空白、不得伪造），以及导航与 Tab 是否可用。
 */

const PAGES = [
  { id: 'P23', title: '建议书对象主页', path: '/proposals' },
  { id: 'P24', title: '新建建议书向导', path: '/proposals/new' },
  { id: 'P31', title: '专家协同记录', path: '/collab' },
  { id: 'P32', title: '审批工作中心', path: '/approvals' },
  { id: 'P34', title: '账户计划', path: '/account-plans' },
  { id: 'P33', title: '对客交付中心', path: '/delivery' },
  { id: 'P35', title: '客户价值实现', path: '/value' },
];

test.describe('W4 方案域', () => {
  for (const entry of PAGES) {
    test(`${entry.id} ${entry.title} — 交互与降级诚实性`, async ({ browser }) => {
      const ctx = await browser.newContext();
      const p = await ctx.newPage();
      const report = await explorePage(p, entry.path, { allowHttp4xx: false });
      console.log(renderExplore(report));
      const blocking = report.findings.filter(
        item => item.kind !== 'resource_error' && item.kind !== 'requestfailed',
      );
      expect(blocking, renderExplore(report)).toEqual([]);
      await ctx.close();
    });
  }

  test('P24 建议书向导 — 逐步推进不得崩溃（降级态也要有可读说明）', async ({ page }) => {
    await page.goto('/proposals/new', { waitUntil: 'networkidle' });
    const steps = page.locator('[role="tab"], .n-tabs-tab, .n-step, .n-steps-item');
    const count = Math.min(await steps.count(), 8);
    for (let i = 0; i < count; i += 1) {
      const step = steps.nth(i);
      if (!(await step.isVisible().catch(() => false))) continue;
      await step.click({ timeout: 5000 }).catch(() => undefined);
      await page.waitForTimeout(800);
      const text = (await page.locator('#app').innerText().catch(() => '')) ?? '';
      expect(text.trim().length, `建议书向导第 ${i + 1} 步白屏`).toBeGreaterThan(40);
    }
  });

  test('P32 审批中心 — 审批动作须受控（不得静默放行）', async ({ page }) => {
    await page.goto('/approvals', { waitUntil: 'networkidle' });
    const text = (await page.locator('#app').innerText()) ?? '';
    expect(text.trim().length).toBeGreaterThan(40);
    // 审批中心若展示门禁项，必须给出「待审批/已拒绝/已通过」等可读状态，而非空白
    expect(text).toMatch(/审批|门禁|待|通过|拒绝|暂无|未授权|降级|C2/);
  });
});
