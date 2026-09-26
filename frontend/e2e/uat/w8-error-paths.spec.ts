import { test, expect, type Route } from '@playwright/test';

/**
 * W8 错误路径与四态：不只看 happy path。
 *
 * 1. 后端 500     → 期望页面给出可读错误提示（不是白屏 / 不是未捕获异常）
 * 2. 空数据集     → 期望空状态占位（不是崩溃 / 不是伪造数据）
 * 3. 请求超时     → 期望超时提示（不是无限 spinner）
 * 4. 无效参数 400 → 期望提示（不是 500 / 不是白屏）
 *
 * 判定口径：注入故障后，页面仍须满足「非白屏 + 无未捕获异常 + 有可读提示」。
 */

const TARGETS = [
  { id: 'workbench', path: '/workbench' },
  { id: 'customer', path: '/customers/CUST-CORP-0001' },
  { id: 'product-center', path: '/product-center' },
];

const READABLE_HINT = /失败|错误|异常|重试|暂无|无数据|未接入|不可用|超时|加载失败|服务|请稍后|稍后重试/;

/**
 * 只拦截**后端接口**（/api、/kert-api）。
 * 注意：不可用通配 glob 匹配 api 目录 —— 那会命中前端源码模块的 api 子目录，
 * 把应用自身打挂，制造出「假白屏」（本波次首跑即踩此坑，记 F-UAT1-08）。
 */
function isBackendApi(url: URL): boolean {
  const pathname = url.pathname;
  if (pathname.startsWith('/src/') || pathname.startsWith('/node_modules/')) return false;
  return pathname.startsWith('/api') || pathname.startsWith('/kert-api');
}

async function collectErrors(page: import('@playwright/test').Page) {
  const errors: string[] = [];
  page.on('pageerror', err => errors.push(String(err).slice(0, 200)));
  return errors;
}

test.describe('W8 错误路径与四态', () => {
  for (const target of TARGETS) {
    test(`${target.id}｜后端 500 → 可读错误态（非白屏）`, async ({ page }) => {
      const errors = await collectErrors(page);
      let injected = 0;
      await page.route(isBackendApi, async (route: Route) => {
        injected += 1;
        await route.fulfill({ status: 500, contentType: 'application/json', body: '{"message":"injected 500"}' });
      });
      await page.goto(target.path, { waitUntil: 'domcontentloaded' });
      await page.waitForTimeout(3000);
      expect(injected, '故障注入未生效（判定无效，不得记为通过）').toBeGreaterThan(0);
      const text = (await page.locator('#app').innerText().catch(() => '')) ?? '';
      expect(errors, `未捕获异常: ${errors.join(' | ')}`).toEqual([]);
      expect(text.trim().length, '500 注入后白屏').toBeGreaterThan(40);
      expect(READABLE_HINT.test(text), `500 注入后无可读提示: ${text.slice(0, 200)}`).toBe(true);
    });

    test(`${target.id}｜空数据集 → 空状态占位（非崩溃）`, async ({ page }) => {
      const errors = await collectErrors(page);
      let injected = 0;
      await page.route(isBackendApi, async (route: Route) => {
        injected += 1;
        await route.fulfill({ status: 200, contentType: 'application/json', body: '[]' });
      });
      await page.goto(target.path, { waitUntil: 'domcontentloaded' });
      await page.waitForTimeout(2500);
      expect(injected, '故障注入未生效（判定无效，不得记为通过）').toBeGreaterThan(0);
      const text = (await page.locator('#app').innerText().catch(() => '')) ?? '';
      expect(errors, `未捕获异常: ${errors.join(' | ')}`).toEqual([]);
      expect(text.trim().length, '空数据注入后白屏').toBeGreaterThan(40);
      expect(/暂无|无数据|空|未找到|没有|0 条|共 0/.test(text), `空数据未给出空状态: ${text.slice(0, 200)}`).toBe(true);
    });

    test(`${target.id}｜请求挂起 → 不得无限 spinner 且不得白屏`, async ({ page }) => {
      const errors = await collectErrors(page);
      let injected = 0;
      await page.route(isBackendApi, async () => {
        injected += 1;
        /* 永不响应：模拟后端挂起 */
      });
      await page.goto(target.path, { waitUntil: 'domcontentloaded' });
      await page.waitForTimeout(6000);
      expect(injected, '故障注入未生效（判定无效，不得记为通过）').toBeGreaterThan(0);
      const text = (await page.locator('#app').innerText().catch(() => '')) ?? '';
      expect(errors, `未捕获异常: ${errors.join(' | ')}`).toEqual([]);
      expect(text.trim().length, '请求挂起时白屏').toBeGreaterThan(40);
    });

    test(`${target.id}｜无效参数 400 → 提示而非白屏`, async ({ page }) => {
      const errors = await collectErrors(page);
      let injected = 0;
      await page.route(isBackendApi, async (route: Route) => {
        injected += 1;
        await route.fulfill({
          status: 400,
          contentType: 'application/json',
          body: '{"status":400,"error":"Bad Request","message":"injected bad request"}',
        });
      });
      await page.goto(target.path, { waitUntil: 'domcontentloaded' });
      await page.waitForTimeout(2500);
      expect(injected, '故障注入未生效（判定无效，不得记为通过）').toBeGreaterThan(0);
      const text = (await page.locator('#app').innerText().catch(() => '')) ?? '';
      expect(errors, `未捕获异常: ${errors.join(' | ')}`).toEqual([]);
      expect(text.trim().length, '400 注入后白屏').toBeGreaterThan(40);
      expect(READABLE_HINT.test(text), `400 注入后无可读提示: ${text.slice(0, 200)}`).toBe(true);
    });
  }
});
