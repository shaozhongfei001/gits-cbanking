import { test, expect, type Page } from '@playwright/test';
import { writeFileSync } from 'node:fs';
import { dirname, resolve } from 'node:path';
import { fileURLToPath } from 'node:url';
import { installApiMocks } from '../e2e/sit-fixtures';

/**
 * W9-A Tech Lead escort. Not UAT. Not P37 SIT.
 * Run: cd frontend && npx playwright test scripts/w9a-escort.spec.ts
 */
const __dirname = dirname(fileURLToPath(import.meta.url));
const LOG_PATH = resolve(__dirname, '../../docs/dispatch/W9-A_ESCORT_LOG.md');

type PageStop = {
  pageId: string;
  path: string;
  marker: string;
  titleContains: string;
};

const STOPS: PageStop[] = [
  { pageId: 'P01', path: '/workbench', marker: 'p01-workbench', titleContains: '我的客户经营' },
  { pageId: 'P02', path: '/accounts', marker: 'p02-accounts', titleContains: '客户对象主页' },
  { pageId: 'P03', path: '/accounts/portfolio', marker: 'p03-portfolio', titleContains: '客户分层' },
  { pageId: 'P04', path: '/customers/cust-001', marker: 'p04-customer-record', titleContains: '经营总览' },
  { pageId: 'P05', path: '/customers/cust-001/group', marker: 'p05-group', titleContains: '集团关系' },
  { pageId: 'P06', path: '/customers/cust-001/funds', marker: 'p06-funds', titleContains: '资金' },
  { pageId: 'P07', path: '/customers/cust-001/parties', marker: 'p07-parties', titleContains: '关系人' },
  { pageId: 'P08', path: '/signals', marker: 'p08-signals', titleContains: '经营信号' },
  { pageId: 'P09', path: '/signals/sig-001', marker: 'p09-signal-record', titleContains: '经营信号记录' },
  { pageId: 'P10', path: '/engagements', marker: 'p10-engagements', titleContains: '互动' },
  { pageId: 'P11', path: '/engagement', marker: 'p11-engagement-workspace', titleContains: '访前路径' },
  { pageId: 'P12', path: '/engagement/previsit/gaps', marker: 'p12-previsit-gaps', titleContains: '访前目标' },
  { pageId: 'P13', path: '/engagement/previsit/evidence', marker: 'p13-previsit-evidence', titleContains: '证据' },
  { pageId: 'P14', path: '/engagement/previsit/pack', marker: 'p14-previsit-pack', titleContains: '访前包' },
  { pageId: 'P15', path: '/in-meeting/jrn-001', marker: 'p15-in-meeting', titleContains: '会中' },
  { pageId: 'P16', path: '/in-meeting/jrn-001/capture', marker: 'p16-meeting-capture', titleContains: '实时捕获' },
  { pageId: 'P17', path: '/in-meeting/jrn-001/checkout', marker: 'p17-meeting-checkout', titleContains: '离场确认' },
  { pageId: 'P18', path: '/engagement/postvisit', marker: 'p18-postvisit', titleContains: '访后' },
  { pageId: 'P19', path: '/engagement/crm-writeback', marker: 'p19-crm-writeback', titleContains: 'CRM' },
  { pageId: 'P20', path: '/needs', marker: 'p20-needs', titleContains: '需求' },
  { pageId: 'P21', path: '/needs/sig-001', marker: 'p21-need-record', titleContains: '需求记录' },
  { pageId: 'P22', path: '/needs/sig-001/plan', marker: 'p22-need-plan', titleContains: '服务计划' },
  { pageId: 'P23', path: '/proposals', marker: 'p23-proposals', titleContains: '建议书' },
  { pageId: 'P24', path: '/proposals/new', marker: 'p24-proposal-wizard', titleContains: '新建建议书' },
  { pageId: 'P25', path: '/proposals/ph-1', marker: 'p25-proposal-record', titleContains: '建议书记录' },
  { pageId: 'P26', path: '/proposals/ph-1/editor', marker: 'p26-proposal-editor', titleContains: '模块编辑器' },
  { pageId: 'P27', path: '/proposals/ph-1/map', marker: 'p27-proposal-map', titleContains: '映射' },
  { pageId: 'P28', path: '/proposals/ph-1/evidence', marker: 'p28-proposal-evidence', titleContains: '依据' },
  { pageId: 'P29', path: '/proposals/ph-1/project', marker: 'p29-proposal-project', titleContains: '对照' },
  { pageId: 'P30', path: '/proposals/ph-1/versions', marker: 'p30-proposal-versions', titleContains: '版本' },
  { pageId: 'P31', path: '/collab', marker: 'p31-collab', titleContains: '专家协同' },
  { pageId: 'P32', path: '/approvals', marker: 'p32-approvals', titleContains: '审批' },
  { pageId: 'P33', path: '/delivery', marker: 'p33-delivery', titleContains: '对客交付' },
  { pageId: 'P34', path: '/account-plans', marker: 'p34-account-plans', titleContains: '账户计划' },
  { pageId: 'P35', path: '/value', marker: 'p35-value', titleContains: '价值' },
  { pageId: 'P36', path: '/commitments', marker: 'p36-commitments', titleContains: '任务与承诺' },
  { pageId: 'P37', path: '/claims', marker: 'p37-claims', titleContains: 'Claim' },
  { pageId: 'P38', path: '/knowledge-map', marker: 'p38-knowledge-map', titleContains: '知识卡' },
  { pageId: 'P39', path: '/audit-trace', marker: 'p39-audit-trace', titleContains: '审计' },
  { pageId: 'P40', path: '/degrade', marker: 'p40-degrade', titleContains: '降级' },
  { pageId: 'P41', path: '/m/today', marker: 'p41-mobile-today', titleContains: '今日' },
  { pageId: 'P42', path: '/m/previsit', marker: 'p42-mobile-previsit', titleContains: '访前包' },
  { pageId: 'P43', path: '/m/notes', marker: 'p43-mobile-notes', titleContains: '会中速记' },
  { pageId: 'P44', path: '/m/checkout', marker: 'p44-mobile-checkout', titleContains: '离场确认' },
];

type StopResult = {
  pageId: string;
  path: string;
  ok: boolean;
  notes: string;
};

async function inspectStop(page: Page, stop: PageStop): Promise<StopResult> {
  const notes: string[] = [];
  try {
    await page.goto(stop.path);
    await expect(page.getByTestId('experience-shell')).toBeVisible({ timeout: 15000 });
    await expect(page.getByTestId('shell-sidebar')).toBeVisible();
    await expect(page.getByTestId('object-header')).toBeVisible();
    await expect(page.getByTestId('object-header')).toContainText(stop.titleContains);
    await expect(page.getByTestId(stop.marker)).toBeVisible();

    const gated = page.getByTestId('gated-action');
    const gatedCount = await gated.count();
    if (gatedCount > 0) {
      for (let i = 0; i < gatedCount; i += 1) {
        await expect(gated.nth(i)).toBeDisabled();
      }
      notes.push(`gated-action×${gatedCount} disabled`);
    }

    const reasons = page.getByTestId('disabled-reason');
    const reasonCount = await reasons.count();
    if (reasonCount > 0) {
      for (let i = 0; i < reasonCount; i += 1) {
        await expect(reasons.nth(i)).toContainText(/原因/);
        await expect(reasons.nth(i)).toContainText(/解除路径/);
      }
      notes.push(`disabled-reason×${reasonCount}`);
    }

    if (stop.pageId === 'P04') {
      await expect(page.getByTestId('customer-slice-tabs')).toBeVisible();
    }
    if (stop.pageId === 'P05') {
      const graph = page.getByTestId('p05-group-graph');
      const empty = page.getByTestId('p05-empty-graph');
      await expect(graph.or(empty)).toBeVisible();
      await expect(page.getByTestId('tab-p05')).toBeVisible();
    }
    if (stop.pageId === 'P25') {
      await expect(page.getByTestId('p25-stage-notice')).toContainText('阶段机 C3 未授权');
    }
    if (stop.pageId === 'P36') {
      await expect(page.getByTestId('p36-commitments')).toHaveAttribute('data-page-id', 'P36');
    }

    return { pageId: stop.pageId, path: stop.path, ok: true, notes: notes.join('; ') || 'shell+header+marker' };
  } catch (error) {
    const message = error instanceof Error ? error.message.split('\n')[0] : String(error);
    return { pageId: stop.pageId, path: stop.path, ok: false, notes: message };
  }
}

test('W9-A escort walks P01–P44 and writes the Owner log', async ({ page }) => {
  test.setTimeout(180000);
  await installApiMocks(page);
  const results: StopResult[] = [];

  await page.goto('/workbench');
  await expect(page.getByTestId('p01-workbench')).toBeVisible();
  await page.getByRole('button', { name: '客户组合' }).click();
  await expect(page.getByTestId('p02-accounts')).toBeVisible();
  await expect(page.getByTestId('workspace-tabs')).toContainText('客户对象主页');
  await page.getByTestId('p02-open-portfolio').click();
  await expect(page.getByTestId('p03-portfolio')).toBeVisible();
  await expect(page.getByTestId('workspace-tabs')).toContainText('客户分层');
  await page.getByRole('button', { name: '服务建议书' }).click();
  await expect(page.getByTestId('p23-proposals')).toBeVisible();
  await page.getByRole('button', { name: '客户经营作战台' }).click();
  await expect(page.getByTestId('p01-workbench')).toBeVisible();

  await page.goto('/customers/cust-001');
  await expect(page.getByTestId('customer-slice-tabs')).toBeVisible();
  await page.getByTestId('tab-p05').click();
  await expect(page.getByTestId('p05-group')).toBeVisible();
  await expect(page.getByTestId('customer-slice-tabs')).toBeVisible();
  await expect(page.getByTestId('object-header')).toBeVisible();

  for (const stop of STOPS) {
    results.push(await inspectStop(page, stop));
  }

  const failed = results.filter(row => !row.ok);
  const passed = results.filter(row => row.ok);
  const stamp = new Date().toISOString();
  const lines = [
    '# W9-A Tech Lead 陪跑日志',
    '',
    `> 不是 UAT。不是 264 PASS。范围 W9-A。commit \`797f3eb\`。时间 ${stamp}。`,
    '> API 使用 `frontend/e2e/sit-fixtures.ts` mock，清单第 2 项仍需 Owner 对活后端确认。',
    '',
    '| pageId | path | 结果 | 备注 |',
    '|---|---|---|---|',
    ...results.map(row => `| ${row.pageId} | \`${row.path}\` | ${row.ok ? 'PASS' : 'FAIL'} | ${row.notes.replace(/\|/g, '/')} |`),
    '',
    `合计 ${passed.length}/${results.length} PASS。失败 ${failed.length}。`,
    '',
  ];
  writeFileSync(LOG_PATH, `${lines.join('\n')}\n`);
  expect(failed, failed.map(row => `${row.pageId} ${row.notes}`).join('\n')).toEqual([]);
});
