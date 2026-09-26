/**
 * 人工验证（走查）包生成器 —— 生成**机器证据 + 人工判定**的可用工具。
 *
 * 只读：不改仓内文件、不注入假数据、不做写操作（写路径由人工在应用里执行）。
 * 产出（默认 out/）：
 *   · data.js          —— `window.WALKTHROUGH_DATA = {...}`（含每场景证据/判据/红线检查）
 *   · shots/<id>.png   —— 每场景整页截图
 * 用法：
 *   node tools/walkthrough/run.mjs [--base http://127.0.0.1:15173] [--out tools/walkthrough/out]
 * 判定在 `tools/walkthrough/viewer/index.html` 里完成（PASS/FAIL/BLOCKED + 备注，可导出 JSON/MD）。
 */
import { chromium } from 'playwright'
import { mkdirSync, writeFileSync } from 'node:fs'
import { dirname, resolve } from 'node:path'

const arg = (k, d) => {
  const i = process.argv.indexOf(k)
  return i > -1 ? process.argv[i + 1] : d
}
const BASE = arg('--base', 'http://127.0.0.1:15173')
const OUT = resolve(arg('--out', 'tools/walkthrough/viewer'))
mkdirSync(`${OUT}/shots`, { recursive: true })

/** 场景清单：`howto`＝人工怎么走；`expect`＝**外部判据**（不得凭"看起来对"）。 */
const SCENARIOS = [
  {
    id: 'flow-previsit-1', flow: '访前链', level: 'L1', name: '① 从列表启动旅程（写路径）', path: '/engagement',
    howto: '「经营旅程」列表 → 点「启动旅程」→ 选客户（启动后自动进入该旅程工作区）',
    expect: 'URL 变为 /engagement/workspace/{journeyId}；顶部状态条显示客户 + 旅程阶段（不再出现「未启动」）',
    assertHint: '应发出 201 POST /api/v1/engagement/journey/start'
  },
  {
    id: 'flow-previsit-2', flow: '访前链', level: 'L1', name: '② 访前目标与信息缺口', path: '/engagement/previsit/gaps',
    howto: '在①点「打开访前工作区 →」',
    expect: '列出「已知 / 未知 / 优先问题」（如未知 ESG、冲突：实控人持股比例）；URL 带 journeyId',
    assertHint: '数据源 GET /api/v1/engagement/kyc/{customerId}/gap-profile'
  },
  {
    id: 'flow-previsit-3', flow: '访前链', level: 'L1', name: '③ 生成访前包（跨服务 KERT）', path: '/engagement/previsit/evidence',
    howto: '在②点「去证据装配」→ 点「生成访前包」',
    expect: '空态文案「尚未执行一键访前」消失，出现**装配轨迹**（skillId / KM-CORP-RM-PREVISIT）',
    assertHint: '应发出 200 POST /api/v1/engagement/journey/{id}/prepare-previsit'
  },
  {
    id: 'flow-previsit-4', flow: '访前链', level: 'L1', name: '④ 访前包预览', path: '/engagement/previsit/pack',
    howto: '在③点「去访前包」',
    expect: '出现「外联脚本 / 会面脚本」等**实质交付物**文本，不再是「尚未生成访前包」',
    assertHint: '同③的返回；不得为空态'
  },
  {
    id: 'pc-interpretation', flow: '产品解读（PC-i1）', level: 'L1', name: '产品中心 · 产品解读', path: '/product-center/PROD-CM-003',
    howto: '左栏「产品中心」→ 选产品 → 滚到「P38 章级承接」',
    expect: '8 章二选一（有数据渲正文 / 无数据具名「待接入」）；承接区标题为「章节标题 + 卡内第 N 节」；无绝对路径',
    assertHint: '期望值来源 GET /api/v1/product-center/products/PROD-CM-003'
  },
  {
    id: 'an-operating', flow: '经营分析', level: 'L1', name: '经营指标分析', path: '/analytics/operating-metrics',
    howto: '侧栏「经营指标分析」',
    expect: '机构表格有真实数据（非 503/空态）；可切换分布维度与时间',
    assertHint: 'GET /kert-api/v1/analytics/metrics… 应 200'
  },
  { id: 'an-monitors', flow: '经营分析', level: 'L1', name: '指标监视器', path: '/analytics/monitors', howto: '侧栏「指标监视器」', expect: '表格 + 告警图例；点击行联动趋势图', assertHint: 'GET /kert-api/v1/analytics/metrics?screen=monitor-balance 应 200' },
  { id: 'an-segments', flow: '经营分析', level: 'L1', name: '细分客群分析', path: '/analytics/segments', howto: '侧栏「细分客群分析」', expect: '客群结构画像（数量/户均价值）有真实数据', assertHint: 'GET /kert-api/v1/analytics/metrics?screen=segment-distribution 应 200' },
  { id: 'an-combo', flow: '经营分析', level: 'L1', name: '组合查询工具', path: '/analytics/combo-query', howto: '侧栏「组合查询工具」→ 设条件 → 查询', expect: '返回客户清单（白名单校验 fail-closed）', assertHint: '查询走 KERT 白名单；无结果须具名' },
  { id: 'acct-overview', flow: '客户', level: 'L2', name: '客户记录 · 经营总览', path: '/customers/CUST-CORP-0003', howto: '侧栏「客户全景」→ 选客户', expect: '经营总览有真实数据；缺失项具名「待核验」', assertHint: '—' },
  { id: 'audit', flow: '治理', level: 'L2', name: '审计与权限', path: '/audit-trace', howto: '侧栏「审批与审计」→ 审计与权限', expect: '审计条目可读；导出/验证权限为设计性禁用并具名原因', assertHint: '禁用入口**不得**计为故障' },
  { id: 'signals', flow: '信号', level: 'C', name: '经营信号对象主页', path: '/signals', howto: '侧栏「经营信号」', expect: '信号卡可读；对无画像客户（CUST-CORP-0004/0005）的请求会 404 ⇒ 记 BLOCKED（数据缺口）', assertHint: '已定性：数据缺口非接口缺陷' }
]

const RED_LINES = ['适配分', '立即推荐', '加入客户方案', '测算适配度', '下一最佳行动', '胜率']
const EMPTY_WORDS = ['暂无', '尚未', '未启动', '待接入', '未接入', '待核验', '只读', '降级']

const browser = await chromium.launch()
const scenarios = []
for (const s of SCENARIOS) {
  const page = await browser.newPage({ viewport: { width: 1600, height: 1100 } })
  const api = []
  page.on('response', async (r) => {
    if (!r.url().includes('/api/') && !r.url().includes('/kert-api/')) return
    let body = null
    try { body = (await r.text()).slice(0, 600) } catch { /* ignore */ }
    api.push({ status: r.status(), method: r.request().method(), url: r.url().replace(BASE, ''), body })
  })
  let http = 0
  try {
    const r = await page.goto(BASE + s.path, { waitUntil: 'domcontentloaded', timeout: 30000 })
    http = r ? r.status() : 0
    await page.waitForTimeout(2800)
  } catch { /* 记 http=0 */ }
  const info = await page.evaluate((EMPTY) => {
    const clone = document.body.cloneNode(true)
    clone.querySelectorAll('aside,nav,header,script,style,[class*=sidebar]').forEach((e) => e.remove())
    const text = (clone.innerText || '').replace(/\s+/g, ' ').trim()
    return { text, emptyWords: EMPTY.filter((w) => text.includes(w)) }
  }, EMPTY_WORDS)
  await page.screenshot({ path: `${OUT}/shots/${s.id}.jpg`, type: 'jpeg', quality: 70, fullPage: true })
  await page.close()

  const bad = api.filter((a) => a.status >= 400)
  scenarios.push({
    ...s,
    captured: {
      http,
      apiCount: api.length,
      apiBad: bad.map((b) => `${b.status} ${b.method} ${b.url}`),
      api: api.filter((a) => a.status < 400).slice(0, 8).map((a) => `${a.status} ${a.url}`),
      mainLen: info.text.length,
      main: info.text.slice(0, 500),
      emptyWords: info.emptyWords,
      redLineHits: RED_LINES.filter((w) => info.text.includes(w)),
      absolutePaths: (info.text.match(/\/home\/[^\s]*/g) || []).slice(0, 2),
      shot: `shots/${s.id}.jpg`
    }
  })
  console.log(`${s.flow} | ${s.name} | HTTP ${http} | api ${api.length}（4xx/5xx ${bad.length}） | 正文 ${info.text.length} 字`)
}
await browser.close()

writeFileSync(
  `${OUT}/data.js`,
  'window.WALKTHROUGH_DATA = ' + JSON.stringify({ base: BASE, generatedAt: new Date().toISOString(), scenarios }, null, 2) + ';\n'
)
console.log(`\n产出：${OUT}/data.js 与 ${OUT}/shots/*.jpg（共 ${scenarios.length} 场景）`)
