import { test, expect } from '@playwright/test';
import { DEGRADE_MARK, firstId, inspectRoute, renderFindings } from './_harness';
import { ROUTES, type RouteIds } from './_routes';

/**
 * W0 全路由巡检：59 条路由逐条开浏览器验证「用户可见行为」。
 *
 * 判定口径（fail-closed，且区分「产品缺陷」与「诚实降级」）：
 *   1. 不白屏（#app 可见文本 ≥ 40 字符）；
 *   2. 无未捕获异常（pageerror）；
 *   3. 后端 /api、/kert-api 无 5xx；
 *   4. 真实数据路由无未预期 4xx（白名单见 `_harness.ts` CLIENT_ERROR_ALLOWLIST）；
 *   5. **无后端数据的页面必须显式降级标注**（C2 降级 / 未授权 / 缺对象 / 暂无 / 解除路径），
 *      不得静默空白或伪造数据 —— 这是项目诚实性红线 E1/E2 的可执行判据。
 *
 * 合成 ID（synthetic）路由只验证「无效参数下的降级表现」：允许 4xx，但不得 5xx / 白屏 / 未捕获异常。
 */

const FALLBACK_IDS: RouteIds = {
  customerId: 'CUST-CORP-0001',
  journeyId: 'jny-001',
  opportunityId: 'e2a1c3d4-e5f6-7890-abcd-ef0123456006',
  eventId: 'E-EXT-006',
  interactionId: '48597ec0-d5db-4dbd-9c28-acdd4e5a5597',
};

test.describe('W0 全路由巡检', () => {
  let ids: RouteIds = FALLBACK_IDS;

  test.beforeAll(async () => {
    const [journeyId, opportunityId, eventId, interactionId] = await Promise.all([
      firstId('/api/v1/engagement/journey', 'journeyId'),
      firstId('/api/v1/opportunities', 'opportunityId'),
      firstId('/api/v1/external-events', 'eventId'),
      firstId('/api/v1/interactions', 'interactionId'),
    ]);
    ids = {
      customerId: FALLBACK_IDS.customerId,
      journeyId: journeyId ?? FALLBACK_IDS.journeyId,
      opportunityId: opportunityId ?? FALLBACK_IDS.opportunityId,
      eventId: eventId ?? FALLBACK_IDS.eventId,
      interactionId: interactionId ?? FALLBACK_IDS.interactionId,
    };
  });

  for (const route of ROUTES) {
    test(`${route.id} ${route.title} — ${route.synthetic ? '合成ID降级' : '真实数据'}`, async ({ page }) => {
      const path = route.build(ids);
      const result = await inspectRoute(page, path, { allowHttp4xx: route.synthetic });

      const echoes = result.findings.filter(item => item.kind === 'resource_error').length;
      const report = `${renderFindings(path, result)}\n  浏览器资源回显(不计失败): ${echoes}`;
      console.log(report);

      const blocking = result.findings.filter(
        item => item.kind !== 'resource_error' && item.kind !== 'requestfailed',
      );
      expect(blocking, report).toEqual([]);

      // 无后端数据 ⇒ 必须显式降级标注（不得静默空白 / 不得伪造数据）
      if (!route.allowNoApiCall && result.apiCalls.length === 0) {
        expect(
          DEGRADE_MARK.test(result.text),
          `${path} 未发起后端请求且未显式标注降级（疑似静默空白或伪造数据）。页面文本：${result.excerpt}`,
        ).toBe(true);
      }
    });
  }
});
