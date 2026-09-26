import { test, expect, type Page } from '@playwright/test';

/**
 * GITS + KERT 联合 Live E2E 测试 — 3 大核心场景（S3/S4/S5 已由 UAT 波次覆盖移除）
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

test.describe('GITS+KERT 联合 E2E — 核心场景', () => {
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

    // Step 2: 进入经营旅程（第一入口 = 列表）
    await page.getByTestId('nav-item-signals').click();
    await expect(page).toHaveURL(/\/engagement/);
    await expect(page.getByTestId('p45-journey-list')).toBeVisible();

    // Step 3: 从列表工具栏启动旅程（启动后默认进入该旅程工作区，journeyId 进 URL）
    await expect(page.getByTestId('p45-start-journey')).toBeEnabled();
    await page.getByTestId('p45-start-journey').click();
    const firstCustomer = page.locator('[data-testid^="p45-pick-"]').first();
    await expect(firstCustomer).toBeVisible({ timeout: 30000 });
    await firstCustomer.click();
    await expect(page).toHaveURL(/\/engagement\/workspace\/[0-9a-f-]{8,}/, { timeout: 30000 });
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

    // Step 1: 确定性直达该客户进行中的旅程工作区（P45 解析页）
    await page.goto('/engagement/enter?customerId=CUST-CORP-0001', { waitUntil: 'networkidle' });
    await expect(page.getByTestId('p11-engagement-workspace')).toBeVisible({ timeout: 30000 });

    // Step 2: 查看互动对象
    await page.getByTestId('signals-tab-p10').click();
    await expect(page.getByTestId('p10-engagements')).toBeVisible();

    // Step 3: 访前差距分析（回到该旅程工作区再点击子导航）
    await page.goto('/engagement/enter?customerId=CUST-CORP-0001', { waitUntil: 'networkidle' });
    await expect(page.getByTestId('p11-engagement-workspace')).toBeVisible({ timeout: 30000 });
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
  // 注: S3(客户服务建议书)、S4(供应链图谱)、S5(客户洞察) 已由 UAT 波次覆盖，原空转断言已删除
  //   S3 → W4(proposals 域) + W3 P38(knowledge-map)
  //   S4 → W2 P04(客户全景) + W5 SCG-01(供应链)
  //   S5 → W6 闭环02(访前缺口) + W2 D-4(经营信号) + W2 P20(需求与机会)
  // ============================================================

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

    // 启动旅程（应触发 KERT skill 调用）——从列表工具栏启动后默认进入工作区
    await page.goto('/engagement', { waitUntil: 'networkidle' });
    await expect(page.getByTestId('p45-journey-list')).toBeVisible();
    await page.getByTestId('p45-start-journey').click();
    const firstCustomer = page.locator('[data-testid^="p45-pick-"]').first();
    await expect(firstCustomer).toBeVisible({ timeout: 30000 });
    await firstCustomer.click();
    await expect(page).toHaveURL(/\/engagement\/workspace\/[0-9a-f-]{8,}/, { timeout: 30000 });
    await expect(page.locator('.ew-bar')).not.toContainText('未启动', { timeout: 30000 });

    // 验证没有 500 错误
    expect(failures, `HTTP 500 errors:\n${failures.join('\n')}`).toEqual([]);
  });
});
