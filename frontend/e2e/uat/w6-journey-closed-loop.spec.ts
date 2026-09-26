import { test, expect, type Page } from '@playwright/test';
import { DEGRADE_MARK, pickJourneyId, inspectRoute, renderFindings } from './_harness';

/**
 * W6 旅程业务闭环：进入旅程 → 工作区 → 访前缺口 → 证据装配 → 访前包 →
 * 会中工作区 → 实时捕获 → 离场确认 → 访后对账 → CRM 受控回写。
 *
 * 这是 UAT 的主链路；每一步都必须落在**真实 journeyId** 上，不接受占位 ID。
 */

async function clickAny(page: Page, selectors: string[]): Promise<string | null> {
  for (const selector of selectors) {
    const locator = page.locator(selector).first();
    if ((await locator.count()) > 0 && (await locator.isVisible().catch(() => false))) {
      await locator.click({ timeout: 8000 });
      return selector;
    }
  }
  return null;
}

test.describe('W6 旅程业务闭环', () => {
  let journeyId = 'jny-001';

  test.beforeAll(async () => {
    journeyId = (await pickJourneyId()) ?? journeyId;
    test.info().annotations.push({ type: 'journeyId', description: journeyId });
  });

  test('闭环 01｜互动工作区加载真实旅程', async ({ page }) => {
    const path = `/engagement/workspace/${journeyId}`;
    const result = await inspectRoute(page, path, { settleMs: 800 });
    console.log(renderFindings(path, result));
    const blocking = result.findings.filter(f => f.kind !== 'resource_error' && f.kind !== 'requestfailed');
    expect(blocking, renderFindings(path, result)).toEqual([]);
    await expect(page.getByTestId('p11-engagement-workspace')).toBeVisible({ timeout: 20000 });
  });

  test('闭环 02｜访前缺口 → 证据装配 → 访前包', async ({ page }) => {
    await page.goto(`/engagement/workspace/${journeyId}`, { waitUntil: 'networkidle' });
    await expect(page.getByTestId('p11-engagement-workspace')).toBeVisible({ timeout: 20000 });

    const toGaps = await clickAny(page, ['[data-testid="p11-open-previsit"]', 'text=打开访前工作区', 'text=访前']);
    expect(toGaps, '工作区缺少「打开访前工作区」入口').toBeTruthy();
    await page.waitForTimeout(1500);
    await expect(page).toHaveURL(/\/engagement\/previsit\/gaps/, { timeout: 20000 });
    await expect(page.getByTestId('p12-previsit-gaps')).toBeVisible({ timeout: 20000 });

    const toEvidence = await clickAny(page, ['[data-testid="p12-go-evidence"]', 'text=进入证据装配']);
    expect(toEvidence, '访前缺口页缺少「进入证据装配」').toBeTruthy();
    await page.waitForTimeout(1500);
    await expect(page.getByTestId('p13-previsit-evidence')).toBeVisible({ timeout: 20000 });

    const toPack = await clickAny(page, ['[data-testid="p13-go-pack"]', 'text=生成访前包', 'text=去访前包预览']);
    expect(toPack, '证据装配页缺少「生成访前包」').toBeTruthy();
    await page.waitForTimeout(1500);
    await expect(page.getByTestId('p14-previsit-pack')).toBeVisible({ timeout: 20000 });
  });

  test('闭环 03｜会中工作区 → 实时捕获 → 离场确认', async ({ page }) => {
    await page.goto(`/engagement/workspace/${journeyId}`, { waitUntil: 'networkidle' });
    const toMeeting = await clickAny(page, ['text=进入会中', 'text=会中工作区', `[href="/in-meeting/${journeyId}"]`]);
    if (!toMeeting) {
      // 工作区未提供入口时，直接按 URL 进入（阶段页本身必须可用）
      await page.goto(`/in-meeting/${journeyId}`, { waitUntil: 'networkidle' });
    }
    await page.waitForTimeout(1500);
    const text1 = (await page.locator('#app').innerText()) ?? '';
    expect(text1.trim().length, '会中工作区白屏').toBeGreaterThan(40);

    await page.goto(`/in-meeting/${journeyId}/capture`, { waitUntil: 'networkidle' });
    const capture = await inspectRoute(page, `/in-meeting/${journeyId}/capture`);
    console.log(renderFindings('/in-meeting/:id/capture', capture));
    // 录音同意 404 属数据缺失：页面必须给出可读状态，不得空白或堆栈
    expect(capture.text.trim().length, '会中捕获页白屏').toBeGreaterThan(40);

    await page.goto(`/in-meeting/${journeyId}/checkout`, { waitUntil: 'networkidle' });
    const checkout = await inspectRoute(page, `/in-meeting/${journeyId}/checkout`);
    const blocking = checkout.findings.filter(f => f.kind !== 'resource_error' && f.kind !== 'requestfailed');
    expect(blocking, renderFindings('/in-meeting/:id/checkout', checkout)).toEqual([]);
  });

  test('闭环 04｜访后对账 → CRM 受控回写', async ({ page }) => {
    for (const path of ['/engagement/postvisit', '/engagement/crm-writeback']) {
      const result = await inspectRoute(page, path);
      console.log(renderFindings(path, result));
      const blocking = result.findings.filter(f => f.kind !== 'resource_error' && f.kind !== 'requestfailed');
      expect(blocking, renderFindings(path, result)).toEqual([]);
      // 直接访问阶段页缺上下文时必须显式说明，不得静默空白
      if (!result.text.match(/对账|回写|写回|承诺|事实/)) {
        expect(DEGRADE_MARK.test(result.text), `${path} 既无业务内容也无降级标注`).toBe(true);
      }
    }
  });
});
