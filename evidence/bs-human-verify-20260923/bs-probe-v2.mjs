/** 业务场景「人工可验证性」探针 v2：**剔除导航/侧栏**后测正文，并统计空态与实质数据特征。只读。 */
import { chromium } from 'playwright'
import { writeFileSync, mkdirSync } from 'node:fs'

const BASE = process.env.BS_BASE || 'http://127.0.0.1:15173'
const OUT = process.argv[2] || '/tmp/bs-feasibility'
mkdirSync(OUT, { recursive: true })

const ROUTES = [
  ['P01 我的客户经营', '/workbench'],
  ['P02 客户对象主页', '/accounts'],
  ['P04 客户记录·经营总览', '/customers/CUST-CORP-0003'],
  ['P08 经营信号对象主页', '/signals'],
  ['P10 互动对象主页', '/engagements'],
  ['P11 互动记录·访前路径', '/engagement'],
  ['P12 访前目标与信息缺口', '/engagement/previsit/gaps'],
  ['P13 访前知识证据装配', '/engagement/previsit/evidence'],
  ['P14 访前包预览', '/engagement/previsit/pack'],
  ['P15 会中工作区', '/in-meeting/CUST-CORP-0003'],
  ['P23 建议书对象主页', '/proposals'],
  ['P32 审批工作中心', '/approvals'],
  ['P38 知识卡与产品适用边界', '/knowledge-map'],
  ['P39 审计与权限', '/audit-trace'],
  ['PI 产品中心·产品解读（PC-i1）', '/product-center/PROD-CM-003'],
  ['P40 服务降级与异常恢复', '/degrade'],
  ['P41 移动端·今日客户行动', '/m/today']
]

const EMPTY_WORDS = ['暂无', '无数据', '空态', '未启动', '待接入', '未接入', '请选择', '尚未', '加载失败', '未加载', '待核验']

const browser = await chromium.launch()
const rows = []
for (const [name, path] of ROUTES) {
  const page = await browser.newPage({ viewport: { width: 1600, height: 1000 } })
  let status = 0, err = null
  try {
    const resp = await page.goto(BASE + path, { waitUntil: 'domcontentloaded', timeout: 25000 })
    status = resp ? resp.status() : 0
    await page.waitForTimeout(2800)
  } catch (e) { err = String(e).slice(0, 140) }
  const m = await page.evaluate((EMPTY) => {
    const clone = document.body.cloneNode(true)
    clone.querySelectorAll('aside,nav,header,script,style,.n-layout-sider,[class*=sidebar]').forEach((e) => e.remove())
    const raw = (clone.innerText || '').replace(/\s+/g, ' ').trim()
    const nodes = document.querySelectorAll('[data-testid]').length
    const tables = document.querySelectorAll('table').length
    const lists = document.querySelectorAll('ul li').length
    const hits = EMPTY.filter((w) => raw.includes(w))
    return { bodyText: raw, dataTestIds: nodes, tables, listItems: lists, emptyWords: hits }
  }, EMPTY_WORDS)
  rows.push({
    name, path, status, mainLen: m.bodyText.length, dataTestIds: m.dataTestIds,
    tables: m.tables, listItems: m.listItems, emptyWords: m.emptyWords,
    head: m.bodyText.slice(0, 220), error: err
  })
  await page.close()
}
await browser.close()
writeFileSync(`${OUT}/bs-feasibility-v2.json`, JSON.stringify({ base: BASE, rows }, null, 2))
console.log('场景 | HTTP | 正文(去导航) | testid数 | 表 | 列表项 | 空态词')
for (const r of rows) {
  console.log(`${r.name} | ${r.status} | ${r.mainLen} | ${r.dataTestIds} | ${r.tables} | ${r.listItems} | ${r.emptyWords.join(',')}`)
}
