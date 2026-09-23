/**
 * PC-i1 · 独立 QA 复验 · **非空转证明（回放）**：把本轮 live 探针所用的**同一套判据规则**
 * （`rules-heading.mjs` / `rules-fault.mjs`）回放到**修前制品**（上一轮独立 QA reject 正本 +
 * 实现者的 before 副本）与**修后制品**（实现者的 after 副本）上：
 *   · 修前 ⇒ 必须判红（否则说明我的判据是空转/永远为真）；
 *   · 修后 ⇒ 必须判绿。
 * 期望值仍由接口事实推导（`/api/v1/product-knowledge/cards/{id}`），不照抄任何实现者断言。
 *
 * 用法：node probe-reverify-replay-history.mjs <outDir>
 * 退出码：0 = 修前全判红 且 修后全判绿；1 = 任一不满足（说明判据或制品有问题）
 */
import { readFileSync, writeFileSync, mkdirSync } from 'node:fs'
import { judgeChapter, norm } from './rules-heading.mjs'
import { judgeFault } from './rules-fault.mjs'

const OUT = process.argv[2] || '.'
mkdirSync(OUT, { recursive: true })
const REPO = '/home/szf/dev/gits-cbanking'
const API = 'http://127.0.0.1:18080'

const CHAPTER_BY_KEY = {
  c2: { key: 'c2', id: 'C2', title: '适用客户与适用场景' },
  c3: { key: 'c3', id: 'C3', title: '产品能力' },
  c6: { key: 'c6', id: 'C6', title: '前置、互斥、替代与配套产品' },
  c8: { key: 'c8', id: 'C8', title: '价格边界' },
  c9: { key: 'c9', id: 'C9', title: '风险提示与人工复核' },
  c10: { key: 'c10', id: 'C10', title: '销售边界' },
  c12: { key: 'c12', id: 'C12', title: 'EvidenceRef' }
}
const C11_TITLE = '不可变版本语义'

const cards = {}
async function sectionsOf(pid) {
  if (!cards[pid]) {
    const r = await fetch(`${API}/api/v1/product-knowledge/cards/${pid}`)
    cards[pid] = r.ok ? ((await r.json()).sections ?? []) : []
  }
  return cards[pid]
}

const HEADING_SOURCES = [
  { label: 'pre-fix｜独立 QA reject 轮正本（QA 自有制品）', file: `${REPO}/loops/PC-i1-chapter-inheritance/evidence/independent-qa-formal-probe-heading-20260923-1227.json`, expectRed: true },
  { label: 'pre-fix｜实现者 before 副本', file: `${REPO}/frontend/test-results/qa-fix-pci1-20260923/before/probe-heading.json`, expectRed: true },
  { label: 'post-fix｜实现者 after 副本', file: `${REPO}/frontend/test-results/qa-fix-pci1-20260923/after/probe-heading.json`, expectRed: false }
]
const FAULT_SOURCES = [
  { label: 'pre-fix｜独立 QA reject 轮正本（QA 自有制品）', file: `${REPO}/loops/PC-i1-chapter-inheritance/evidence/independent-qa-formal-probe-faultcard-FIN003-20260923-1227.json`, expectRed: true },
  { label: 'pre-fix｜实现者 before 副本', file: `${REPO}/frontend/test-results/qa-fix-pci1-20260923/before/probe-faultcard-PROD-FIN-003.json`, expectRed: true },
  { label: 'post-fix｜实现者 after 副本', file: `${REPO}/frontend/test-results/qa-fix-pci1-20260923/after/probe-faultcard-PROD-FIN-003.json`, expectRed: false }
]

const results = []
let bad = 0

for (const src of HEADING_SOURCES) {
  const data = JSON.parse(readFileSync(src.file, 'utf8'))
  const violations = []
  for (const entry of data) {
    const pid = entry.productId
    const sections = await sectionsOf(pid)
    for (const [key, dom] of Object.entries(entry)) {
      if (key === 'productId') continue
      const ch = CHAPTER_BY_KEY[key]
      if (!ch) continue
      const section = sections.find((s) => String(s.title).includes(ch.title)) ?? null
      for (const v of judgeChapter({ ch, section, dom, partial: true })) violations.push({ productId: pid, code: v })
    }
    // 注：历史 heading 制品**不含**版本区（C11）source 字段 ⇒ 本回放只覆盖 c2/c3/c6/c8/c9/c10/c12 的 head/meta 判据，
    //     C11 的判据仅由 live 探针（含同类接口推导规则，见 judgeImm）覆盖。
    void C11_TITLE
  }
  const red = violations.length > 0
  const ok = red === src.expectRed
  if (!ok) bad += 1
  results.push({
    kind: 'heading（回放：仅 head/meta 判据，partial）',
    label: src.label,
    file: src.file,
    expected: src.expectRed ? '判红(>0 违规)' : '判绿(0 违规)',
    actual: red ? `判红(${violations.length} 违规)` : '判绿(0 违规)',
    pass: ok,
    violations
  })
}

function key12(entry) {
  return false
}

for (const src of FAULT_SOURCES) {
  const data = JSON.parse(readFileSync(src.file, 'utf8'))
  const v = judgeFault(data.dom, { aborted: data.abortedRequests ?? 0 })
  const red = v.length > 0
  const ok = red === src.expectRed
  if (!ok) bad += 1
  results.push({
    kind: 'faultcard（回放：来源不可得判据）',
    label: src.label,
    file: src.file,
    expected: src.expectRed ? '判红(>0 违规)' : '判绿(0 违规)',
    actual: red ? `判红(${v.length} 违规)` : '判绿(0 违规)',
    pass: ok,
    violations: v,
    domExcerpt: { c12absent: norm(data.dom?.c12absent), immAbsent: norm(data.dom?.immAbsent) }
  })
}

const out = {
  probe: 'probe-reverify-replay-history（非空转证明：同一判据回放修前/修后制品）',
  generatedAt: new Date().toISOString(),
  apiOrcale: `${API}/api/v1/product-knowledge/cards/{id}`,
  allAsExpected: bad === 0,
  mismatchCount: bad,
  results
}
writeFileSync(`${OUT}/probe-reverify-replay-history.json`, JSON.stringify(out, null, 2))
console.log(JSON.stringify(out.results.map(({ kind, label, expected, actual, pass, violations }) => ({ kind, label, expected, actual, pass, violations: violations.slice(0, 8) })), null, 2))
console.log(`MISMATCH=${bad}`)
process.exit(bad === 0 ? 0 : 1)
