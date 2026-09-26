import { test, expect } from '@playwright/test';
import { explorePage, firstId, inspectRoute, renderExplore, renderFindings } from './_harness';

/**
 * W7 移动端四页 + 治理页：Claim/Evidence 中心、审计与权限、服务降级、
 * 外部事件监控、旅程时间线、报告详情。
 *
 * 移动端按 390×844 窄屏验收（移动端优先原则）。
 */

const MOBILE_PAGES = [
  { id: 'P41', title: '移动端·今日客户行动', path: '/m/today' },
  { id: 'P42', title: '移动端·访前包', path: '/m/previsit' },
  { id: 'P43', title: '移动端·会中速记', path: '/m/notes' },
  { id: 'P44', title: '移动端·离场确认与任务', path: '/m/checkout' },
];

const GOVERNANCE_PAGES = [
  { id: 'P37', title: 'Claim / Evidence 中心', path: '/claims' },
  { id: 'P39', title: '审计与权限', path: '/audit-trace' },
  { id: 'P40', title: '服务降级与异常恢复', path: '/degrade' },
  { id: 'EV-01', title: '外部事件监控', path: '/external-events' },
];

test.describe('W7 移动端与治理页', () => {
  test.describe('移动端 390x844', () => {
    for (const entry of MOBILE_PAGES) {
      test(`${entry.id} ${entry.title} — 窄屏可用`, async ({ browser }) => {
        const ctx = await browser.newContext({ viewport: { width: 390, height: 844 } });
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
  });

  for (const entry of GOVERNANCE_PAGES) {
    test(`${entry.id} ${entry.title} — 数据与交互`, async ({ browser }) => {
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

  test('JT-01 旅程时间线 — 真实 journeyId 可渲染时间线', async ({ page }) => {
    const journeyId = (await firstId('/api/v1/engagement/journey', 'journeyId')) ?? 'jny-001';
    const path = `/journeys/${journeyId}`;
    const result = await inspectRoute(page, path);
    console.log(renderFindings(path, result));
    const blocking = result.findings.filter(f => f.kind !== 'resource_error' && f.kind !== 'requestfailed');
    expect(blocking, renderFindings(path, result)).toEqual([]);
    expect(result.text.trim().length).toBeGreaterThan(40);
  });
});
