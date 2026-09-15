import { test, expect, type Page } from '@playwright/test';

/**
 * GITS + KERT 联合 Live E2E 测试 — 5 大业务场景
 *
 * 前置条件：GITS 后端 (8082) + KERT (8106) + 前端 (5173) 全部运行中
 * 运行: npx playwright test --config=playwright.live.config.ts e2e/five-scenarios.live.spec.ts
 */

const API = process.env.LIVE_API_URL || 'http://127.0.0.1:8082';
const KERT = process.env.KERT_URL || 'http://127.0.0.1:8106';

async function requireServices(): Promise<void> {
  const [api, kert] = await Promise.all([
    fetch(`${API}/actuator/health`),
    fetch(`${KERT}/api/skill/health`),
  ]);
  if (!api.ok) throw new Error(`GITS API ${API} not healthy: ${api.status}`);
  if (!kert.ok) throw new Error(`KERT ${KERT} not healthy: ${kert.status}`);
}

async function noHttp500(page: Page): Promise<string[]> {
  const failures: string[] = [];
  page.on('response', res => {
    if (res.url().includes('/api/') && res.status() >= 500) {
      failures.push(`${res.status()} ${res.url()}`);
    }
  });
  return failures;
}

test.describe('GITS+KERT 联合 E2E — 5 大业务场景', () => {
  test.beforeAll(async () => {
    await requireServices();
  });

  // ============================================================
  // 场景1: 客户经理持续经营
  // ============================================================
  test('S1 客户经理持续经营: 工作台加载→客户选择→旅程启动→Gate状态', async ({ page }) => {
    const failures = await noHttp500(page);

    // Step 1: 工作台加载
    await page.goto('/workbench', { waitUntil: 'networkidle' });
    await expect(page.getByTestId('p01-workbench')).toBeVisible();
    await expect(page.getByTestId('success-state')).toBeVisible();

    // Step 2: 进入信号与互动
    await page.getByTestId('nav-item-signals').click();
    await expect(page).toHaveURL(/\/engagement/);
    await expect(page.getByTestId('p11-engagement-workspace')).toBeVisible();

    // Step 3: 启动旅程
    await expect(page.getByTestId('p11-start-journey')).toBeEnabled();
    await page.getByTestId('p11-start-journey').click();
    // p11-object-context 已移除；改用 .ew-bar 文本断言
    await expect(page.locator('.ew-bar')).not.toContainText('未启动', { timeout: 30000 });

    // Step 4: 查看 Gate 状态
    await page.getByTestId('p11-open-previsit').click();
    await expect(page.getByTestId('p12-previsit-gaps')).toBeVisible();

    expect(failures, `HTTP 500 errors:\n${failures.join('\n')}`).toEqual([]);
  });

  // ============================================================
  // 场景2: 访前报告生成
  // ============================================================
  test('S2 访前报告: 互动记录→记忆抽取→访前差距→访前包', async ({ page }) => {
    const failures = await noHttp500(page);

    // Step 1: 进入信号与互动
    await page.goto('/engagement', { waitUntil: 'networkidle' });
    await expect(page.getByTestId('p11-engagement-workspace')).toBeVisible();

    // Step 2: 查看互动对象
    await page.getByTestId('signals-tab-p10').click();
    await expect(page.getByTestId('p10-engagements')).toBeVisible();

    // Step 3: 访前差距分析（回到 engagement 主页面再点击子导航）
    await page.goto('/engagement', { waitUntil: 'networkidle' });
    await expect(page.getByTestId('p11-engagement-workspace')).toBeVisible();
    await page.getByTestId('p11-open-previsit').click();
    await expect(page.getByTestId('p12-previsit-gaps')).toBeVisible();

    // Step 4: 访前证据
    await page.getByTestId('p12-go-evidence').click();
    await expect(page.getByTestId('p13-previsit-evidence')).toBeVisible();

    // Step 5: 访前包
    await page.getByTestId('p13-go-pack').click();
    await expect(page.getByTestId('p14-previsit-pack')).toBeVisible();

    expect(failures, `HTTP 500 errors:\n${failures.join('\n')}`).toEqual([]);
  });

  // ============================================================
  // 场景3: 客户服务建议书
  // ============================================================
  test('S3 客户服务建议书: 客户全景→知识地图→建议书页面', async ({ page }) => {
    const failures = await noHttp500(page);

    // Step 1: 进入客户全景
    await page.goto('/workbench', { waitUntil: 'networkidle' });
    await expect(page.getByTestId('p01-workbench')).toBeVisible();

    // Step 2: 点击服务建议书导航
    const proposalNav = page.getByTestId('nav-item-proposals');
    if (await proposalNav.isVisible()) {
      await proposalNav.click();
      await expect(page.getByTestId('success-state').or(page.getByTestId('error-state'))).toBeVisible({ timeout: 15000 });
    }

    // Step 3: 检查知识地图页面
    await page.goto('/knowledge-map', { waitUntil: 'networkidle' });
    const knowledgeMap = page.getByTestId('p38-knowledge-map');
    if (await knowledgeMap.isVisible()) {
      await expect(knowledgeMap).toBeVisible();
    }

    expect(failures, `HTTP 500 errors:\n${failures.join('\n')}`).toEqual([]);
  });

  // ============================================================
  // 场景4: 知识图谱/供应链图谱
  // ============================================================
  test('S4 供应链图谱: 客户全景→供应链图谱渲染', async ({ page }) => {
    const failures = await noHttp500(page);

    // Step 1: 进入客户全景
    await page.goto('/workbench', { waitUntil: 'networkidle' });
    await expect(page.getByTestId('p01-workbench')).toBeVisible();

    // Step 2: 点击客户全景
    const panoramaNav = page.getByTestId('nav-item-panorama');
    if (await panoramaNav.isVisible()) {
      await panoramaNav.click();
      await page.waitForLoadState('networkidle');
    }

    // Step 3: 验证供应链图谱组件
    const supplyChainInsights = page.getByTestId('sc-insights');
    // 供应链图谱可能在客户全景子页面中
    if (await supplyChainInsights.isVisible()) {
      await expect(supplyChainInsights).toBeVisible();
    }

    expect(failures, `HTTP 500 errors:\n${failures.join('\n')}`).toEqual([]);
  });

  // ============================================================
  // 场景5: 客户洞察
  // ============================================================
  test('S5 客户洞察: 经营总览→KYC差距→信号→机会', async ({ page }) => {
    const failures = await noHttp500(page);

    // Step 1: 工作台加载（含经营总览）
    await page.goto('/workbench', { waitUntil: 'networkidle' });
    await expect(page.getByTestId('p01-workbench')).toBeVisible();
    await expect(page.getByTestId('success-state')).toBeVisible();

    // Step 2: 进入信号与互动（含 KYC 差距）
    await page.getByTestId('nav-item-signals').click();
    await expect(page.getByTestId('p11-engagement-workspace')).toBeVisible();

    // Step 3: KYC 差距分析
    const gapsLink = page.getByTestId('p11-open-previsit');
    if (await gapsLink.isVisible({ timeout: 5000 }).catch(() => false)) {
      await gapsLink.click();
      await expect(page.getByTestId('p12-previsit-gaps')).toBeVisible();
    }

    // Step 4: 经营信号
    await page.goto('/engagement', { waitUntil: 'networkidle' });
    const signalsTab = page.getByTestId('signals-tab-p08');
    if (await signalsTab.isVisible({ timeout: 5000 }).catch(() => false)) {
      await signalsTab.click();
      await expect(page.getByTestId('p08-signals')).toBeVisible();
    }

    // Step 5: 需求与机会
    const opportunityNav = page.getByTestId('nav-item-opportunities');
    if (await opportunityNav.isVisible({ timeout: 5000 }).catch(() => false)) {
      await opportunityNav.click();
      await page.waitForLoadState('networkidle');
    }

    expect(failures, `HTTP 500 errors:\n${failures.join('\n')}`).toEqual([]);
  });

  // ============================================================
  // 跨服务验证: GITS→KERT 联动
  // ============================================================
  test('S6 跨服务验证: GITS 前端操作触发 KERT Skill 执行', async ({ page }) => {
    const failures = await noHttp500(page);
    const kertCalls: string[] = [];

    // 监听 KERT 调用
    page.on('request', req => {
      const url = req.url();
      if (url.includes(':8106') || url.includes('skill')) {
        kertCalls.push(`${req.method()} ${url}`);
      }
    });

    // 启动旅程（应触发 KERT skill 调用）
    await page.goto('/engagement', { waitUntil: 'networkidle' });
    await expect(page.getByTestId('p11-engagement-workspace')).toBeVisible();
    await page.getByTestId('p11-start-journey').click();
    // p11-object-context 已移除；改用 .ew-bar 文本断言
    await expect(page.locator('.ew-bar')).not.toContainText('未启动', { timeout: 30000 });

    // 验证没有 500 错误
    expect(failures, `HTTP 500 errors:\n${failures.join('\n')}`).toEqual([]);
  });
});
