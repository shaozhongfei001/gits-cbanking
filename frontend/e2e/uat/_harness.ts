import type { Page, Request, Response } from '@playwright/test';

/**
 * UAT1 全场景 E2E 巡检底座。
 *
 * 立场（E2E Owner）：只关心浏览器里能不能正常用。断言必须是**用户可见行为**：
 *   - 页面不白屏（#app 渲染出可读文本）；
 *   - 无未捕获异常 / 无 console.error；
 *   - 后端与 KERT 接口无 5xx；
 *   - 数据请求真的发出（不靠 stub）。
 *
 * 该底座只做**观测与判定**，不做 mock、不放宽断言。
 */

export const API_BASE = process.env.UAT_API_BASE ?? 'http://127.0.0.1:18080';
export const KERT_BASE = process.env.UAT_KERT_BASE ?? 'http://127.0.0.1:8107';

export type FindingKind =
  | 'blank'
  | 'no_app_root'
  | 'pageerror'
  | 'console.error'
  | 'http5xx'
  | 'http4xx'
  | 'resource_error'
  | 'requestfailed'
  | 'navigation_failed';

/**
 * 4xx 白名单（显式登记，禁止静默放行）。
 *
 * `/api/v1/engagement/kyc/{customerId}/gap-profile` 404：
 * 种子数据未覆盖全部客户的 KYC 画像（实测 CUST-CORP-0002/0004/0005/0006 返回 404），
 * 属**数据缺失**而非接口错误；前端须自行降级为「KYC 待补充」。
 * 一旦种子数据补全或接口改为返回空画像，本条白名单必须删除。
 */
const CLIENT_ERROR_ALLOWLIST: RegExp[] = [/^\/api\/v1\/engagement\/kyc\/[^/]+\/gap-profile$/];

/** 浏览器网络层回显（Failed to load resource）不单独计失败，避免与 http4xx/http5xx 重复计数。 */
const RESOURCE_ECHO = /Failed to load resource/i;

export interface Finding {
  kind: FindingKind;
  detail: string;
}

/** 静态资源（favicon/字体/图片）的失败不计入业务失败，但会单独登记。 */
const STATIC_ASSET = /\.(png|jpe?g|gif|svg|ico|woff2?|ttf|css|js|map)(\?|$)/i;

/** 观测器：挂在 page 上收集全部异常信号。 */
export interface Watcher {
  findings: Finding[];
  apiCalls: string[];
  detach(): void;
}

export function watch(page: Page, options: { allowHttp4xx?: boolean } = {}): Watcher {
  const findings: Finding[] = [];
  const apiCalls: string[] = [];

  const onConsole = (msg: { type: () => string; text: () => string }) => {
    if (msg.type() !== 'error') return;
    const text = msg.text();
    findings.push({
      kind: RESOURCE_ECHO.test(text) ? 'resource_error' : 'console.error',
      detail: text.slice(0, 400),
    });
  };
  const onPageError = (err: Error) => {
    findings.push({ kind: 'pageerror', detail: String(err).slice(0, 400) });
  };
  const onResponse = (res: Response) => {
    const pathname = safePathname(res.url());
    if (isBackend(pathname)) {
      apiCalls.push(`${res.status()} ${res.request().method()} ${pathname}`);
      if (res.status() >= 500) {
        findings.push({ kind: 'http5xx', detail: `${res.status()} ${res.request().method()} ${res.url()}` });
      } else if (
        res.status() >= 400 &&
        !options.allowHttp4xx &&
        !CLIENT_ERROR_ALLOWLIST.some(rule => rule.test(pathname))
      ) {
        findings.push({ kind: 'http4xx', detail: `${res.status()} ${res.request().method()} ${res.url()}` });
      }
    }
  };
  const onRequestFailed = (req: Request) => {
    const url = req.url();
    if (STATIC_ASSET.test(url)) return;
    if (!isBackend(safePathname(url))) return;
    findings.push({ kind: 'requestfailed', detail: `${url} :: ${req.failure()?.errorText ?? 'unknown'}` });
  };

  page.on('console', onConsole);
  page.on('pageerror', onPageError);
  page.on('response', onResponse);
  page.on('requestfailed', onRequestFailed);

  return {
    findings,
    apiCalls,
    detach() {
      page.off('console', onConsole);
      page.off('pageerror', onPageError);
      page.off('response', onResponse);
      page.off('requestfailed', onRequestFailed);
    },
  };
}

function safePathname(url: string): string {
  try {
    return new URL(url).pathname;
  } catch {
    return url;
  }
}

function isBackend(pathname: string): boolean {
  return pathname.startsWith('/api') || pathname.startsWith('/kert-api') || pathname.startsWith('/v14');
}

export interface InspectOptions {
  /** 至少渲染出的可见文本长度（防白屏）。 */
  minTextLength?: number;
  /** 进入页面后额外等待的稳定时间（ms）。 */
  settleMs?: number;
  /** 允许该页面不发起任何后端请求（纯静态壳层页）。 */
  allowNoApiCall?: boolean;
  /** 允许 4xx：用于**故意构造的无效参数**路由，只验证降级表现，不验证数据正确性。 */
  allowHttp4xx?: boolean;
}

export interface InspectResult {
  findings: Finding[];
  apiCalls: string[];
  textLength: number;
  excerpt: string;
  text: string;
}

/**
 * 诚实降级标注（项目红线 E1/E2 的可执行判据）。
 * 无后端数据的页面**必须**显式说明「未接入 / 缺对象 / 未授权」，不得静默空白或伪造数据。
 */
export const DEGRADE_MARK =
  /C2 降级|未授权|禁止|缺对象|暂无|待接入|未接入|解除路径|无\s*\S*\s*合同|未实现|待维护|待接入/;

/** 打开一个路由并完成全部可见性判定。 */
export async function inspectRoute(page: Page, path: string, options: InspectOptions = {}): Promise<InspectResult> {
  const minTextLength = options.minTextLength ?? 40;
  const watcher = watch(page, { allowHttp4xx: options.allowHttp4xx });

  let navigationError: string | null = null;
  try {
    await page.goto(path, { waitUntil: 'domcontentloaded', timeout: 30000 });
  } catch (error) {
    navigationError = String(error).slice(0, 300);
  }
  // 等待异步数据落地（networkidle 可能永不触发，故用短超时兜底）
  try {
    await page.waitForLoadState('networkidle', { timeout: 8000 });
  } catch {
    /* 未在 8s 内静默：由后续断言（白屏/5xx）判定，不在此吞掉 */
  }
  if (options.settleMs) await page.waitForTimeout(options.settleMs);

  if (navigationError) {
    watcher.findings.push({ kind: 'navigation_failed', detail: navigationError });
  }

  const app = page.locator('#app');
  let textLength = 0;
  let excerpt = '';
  let text = '';
  if ((await app.count()) === 0) {
    watcher.findings.push({ kind: 'no_app_root', detail: `#app 挂载点不存在（path=${path}）` });
  } else {
    text = (await app.innerText().catch(() => '')) ?? '';
    textLength = text.trim().length;
    excerpt = text.replace(/\s+/g, ' ').slice(0, 160);
    if (textLength < minTextLength) {
      watcher.findings.push({
        kind: 'blank',
        detail: `#app 可见文本仅 ${textLength} 字符（阈值 ${minTextLength}）path=${path} :: ${excerpt}`,
      });
    }
  }

  watcher.detach();
  return { findings: watcher.findings, apiCalls: watcher.apiCalls, textLength, excerpt, text };
}

/** 断言用：把 findings 渲染成可读文本，便于失败时一眼定位。 */
export function renderFindings(path: string, result: InspectResult): string {
  const lines = result.findings.map(item => `  - [${item.kind}] ${item.detail}`);
  return `route ${path}\n  文本长度=${result.textLength} 摘要="${result.excerpt}"\n  API 调用: ${
    result.apiCalls.length ? result.apiCalls.join(' | ') : '（无）'
  }\n  异常:\n${lines.length ? lines.join('\n') : '  （无）'}`;
}

/**
 * 打开路由并返回渲染文本（**不挂载观测器**，供需要跨步骤连续观测的探索式用例使用）。
 */
export async function openRoute(
  page: Page,
  path: string,
  options: { settleMs?: number } = {},
): Promise<{ textLength: number; excerpt: string; text: string }> {
  await page.goto(path, { waitUntil: 'domcontentloaded', timeout: 30000 });
  try {
    await page.waitForLoadState('networkidle', { timeout: 8000 });
  } catch {
    /* 未静默由后续断言判定 */
  }
  if (options.settleMs) await page.waitForTimeout(options.settleMs);
  const app = page.locator('#app');
  if ((await app.count()) === 0) return { textLength: 0, excerpt: '', text: '' };
  const text = (await app.innerText().catch(() => '')) ?? '';
  return { textLength: text.trim().length, excerpt: text.replace(/\s+/g, ' ').slice(0, 160), text };
}

export function blankFinding(path: string, textLength: number, excerpt: string): Finding | null {
  return textLength < 40
    ? { kind: 'blank', detail: `#app 可见文本仅 ${textLength} 字符 path=${path} :: ${excerpt}` }
    : null;
}

export interface StepResult {
  step: string;
  ok: boolean;
  detail: string;
}

export interface ExploreReport {
  path: string;
  steps: StepResult[];
  findings: Finding[];
  textLength: number;
  excerpt: string;
}

/**
 * 探索式功能点验证：打开页面后，逐个点击**导航型**元素（Tab / 站内链接），
 * 每一步都复检「不白屏 + 无未捕获异常 + 无 5xx」。
 *
 * 只点导航型元素（[role=tab] / .n-tabs-tab / 站内 a[href^="/"]），
 * **不点击表单提交与写操作按钮**（写动作由各业务波次显式、受控地执行）。
 */
export async function explorePage(
  page: Page,
  path: string,
  options: { maxTabs?: number; maxLinks?: number; settleMs?: number; allowHttp4xx?: boolean } = {},
): Promise<ExploreReport> {
  const maxTabs = options.maxTabs ?? 10;
  const maxLinks = options.maxLinks ?? 6;
  const watcher = watch(page, { allowHttp4xx: options.allowHttp4xx });
  const steps: StepResult[] = [];

  const rendered = await openRoute(page, path, { settleMs: options.settleMs });
  const blank = blankFinding(path, rendered.textLength, rendered.excerpt);
  if (blank) watcher.findings.push(blank);
  steps.push({ step: 'open', ok: !blank, detail: `text=${rendered.textLength}` });

  // ① Tab 切换
  const tabs = page.locator('[role="tab"], .n-tabs-tab, .n-tab');
  const tabCount = Math.min(await tabs.count(), maxTabs);
  for (let i = 0; i < tabCount; i += 1) {
    const tab = tabs.nth(i);
    const label = (await tab.innerText().catch(() => '')).trim().slice(0, 20) || `#${i}`;
    try {
      if (!(await tab.isVisible()) || !(await tab.isEnabled())) {
        steps.push({ step: `tab:${label}`, ok: true, detail: '不可见/禁用，跳过' });
        continue;
      }
      await tab.click({ timeout: 5000 });
      await page.waitForTimeout(900);
      const after = await page.locator('#app').innerText().catch(() => '');
      const ok = (after ?? '').trim().length >= 40;
      if (!ok) {
        watcher.findings.push({ kind: 'blank', detail: `切换 Tab「${label}」后白屏 path=${path}` });
      }
      steps.push({ step: `tab:${label}`, ok, detail: `text=${(after ?? '').trim().length}` });
    } catch (error) {
      steps.push({ step: `tab:${label}`, ok: false, detail: String(error).slice(0, 200) });
      watcher.findings.push({ kind: 'pageerror', detail: `Tab「${label}」点击失败: ${String(error).slice(0, 200)}` });
    }
  }

  // ② 站内链接（回到起点后逐个进入）
  const links = page.locator('a[href^="/"]');
  const seen = new Set<string>();
  const linkCount = await links.count();
  let visited = 0;
  for (let i = 0; i < linkCount && visited < maxLinks; i += 1) {
    const link = links.nth(i);
    const href = await link.getAttribute('href');
    if (!href || seen.has(href) || href === path) continue;
    seen.add(href);
    visited += 1;
    try {
      if (!(await link.isVisible())) continue;
      await link.click({ timeout: 5000 });
      await page.waitForTimeout(1200);
      const after = (await page.locator('#app').innerText().catch(() => '')) ?? '';
      const ok = after.trim().length >= 40;
      if (!ok) watcher.findings.push({ kind: 'blank', detail: `点击站内链接 ${href} 后白屏（来自 ${path}）` });
      steps.push({ step: `link:${href}`, ok, detail: `text=${after.trim().length}` });
      await page.goto(path, { waitUntil: 'domcontentloaded' });
      await page.waitForTimeout(600);
    } catch (error) {
      steps.push({ step: `link:${href}`, ok: false, detail: String(error).slice(0, 200) });
    }
  }

  watcher.detach();
  return { path, steps, findings: watcher.findings, textLength: rendered.textLength, excerpt: rendered.excerpt };
}

export function renderExplore(report: ExploreReport): string {
  const lines = report.findings.map(item => `  - [${item.kind}] ${item.detail}`);
  const steps = report.steps.map(item => `  · ${item.ok ? 'OK ' : 'BAD'} ${item.step} :: ${item.detail}`);
  return [
    `explore ${report.path}（text=${report.textLength}）`,
    ...steps,
    `  异常:\n${lines.length ? lines.join('\n') : '  （无）'}`,
  ].join('\n');
}

/**
 * 挑选**种子客户**的进行中旅程。
 *
 * 不得直接用「列表第一条」：E2E 同批次的「启动旅程」用例会真实写入新旅程，
 * 列表首条随之漂移，造成用例间数据耦合（F-UAT2-01）。
 * 取不到时回退首条并返回 `null` 由调用方显式登记，不静默跳过。
 */
export async function pickJourneyId(customerId = 'CUST-CORP-0001'): Promise<string | null> {
  try {
    const res = await fetch(`${API_BASE}/api/v1/engagement/journey`, { signal: AbortSignal.timeout(8000) });
    if (!res.ok) return null;
    const body = (await res.json()) as unknown;
    if (!Array.isArray(body) || body.length === 0) return null;
    const rows = body as Record<string, unknown>[];
    const seeded = rows.find(row => row['customerId'] === customerId);
    const target = seeded ?? rows[0];
    const value = target['journeyId'];
    return typeof value === 'string' ? value : null;
  } catch {
    return null;
  }
}

/** 从后端列表端点取第一个 ID；取不到返回 null（由调用方显式登记，不静默跳过）。 */
export async function firstId(path: string, idKey: string): Promise<string | null> {
  try {
    const res = await fetch(`${API_BASE}${path}`, { signal: AbortSignal.timeout(8000) });
    if (!res.ok) return null;
    const body = (await res.json()) as unknown;
    if (Array.isArray(body) && body.length > 0) {
      const value = (body[0] as Record<string, unknown>)[idKey];
      return typeof value === 'string' ? value : null;
    }
  } catch {
    return null;
  }
  return null;
}
