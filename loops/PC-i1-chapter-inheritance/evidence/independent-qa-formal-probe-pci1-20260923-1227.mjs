/**
 * PC-i1 独立 QA 探针（W1-a/b/c/d/e + 卡间节号错位）— 自研，不复用实现者断言。
 *
 * 判据来源：真实接口（18080，经 15173 代理）+ 真实页面 DOM（15173）。
 * 期望值的推导**独立实现**（标题关键字为唯一语义锚；另记录节号前缀兜底路径是否与之冲突）。
 * 不使用 page.route / stub。
 *
 * 用法：node probe-pci1.mjs <outDir>
 */
import { chromium } from 'playwright'
import { writeFileSync, mkdirSync } from 'node:fs'

const OUT = process.argv[2] || '.'
const BASE = 'http://127.0.0.1:15173'
const API = 'http://127.0.0.1:18080'
mkdirSync(OUT, { recursive: true })

// ── 变异复验开关（仅用于证明本探针对缺陷类有鉴别力；不改产品代码） ──
// QA_MUTATE=prefix   : 期望改用「节号前缀」推导（复现被修复前的错位 bug）⇒ FIN 卡必须被判违规
// QA_MUTATE=c10wrong : 期望的 C10 文本故意改错 ⇒ C10 比较必须被判违规
const MUTATE = process.env.QA_MUTATE || ''

/** 章号 → 语义锚（唯一关键字）。C1/C4/C5/C7 不在本区（由八章承接），此处不涉。 */
const SPEC = [
  { key: 'c2', no: 2, kw: '适用客户与适用场景' },
  { key: 'c3', no: 3, kw: '产品能力' },
  { key: 'c6', no: 6, kw: '前置、互斥、替代与配套产品' },
  { key: 'c8', no: 8, kw: '价格边界' },
  { key: 'c9', no: 9, kw: '风险提示与人工复核' },
  { key: 'c10', no: 10, kw: '销售边界' },
  { key: 'c12', no: 12, kw: 'EvidenceRef' }
]
const C11 = { no: 11, kw: '不可变版本语义' }

const norm = (s) => String(s ?? '').replace(/\s+/g, '')
const head = (s) => norm(s).slice(0, 20)
const secNo = (title) => {
  const m = String(title).trim().match(/^(\d+)\./)
  return m ? Number(m[1]) : null
}

const violations = []
const notes = []
const perProduct = []

function v(productId, code, detail) {
  violations.push({ productId, code, detail })
}

const browser = await chromium.launch()
const page = await browser.newPage({ viewport: { width: 1600, height: 1000 } })

const listResp = await fetch(`${API}/api/v1/product-center/products`)
const products = await listResp.json()
const ids = products.map((p) => p.productId)

for (const pid of ids) {
  const cardResp = await fetch(`${API}/api/v1/product-knowledge/cards/${pid}`)
  const card = cardResp.ok ? await cardResp.json() : null
  const detailResp = await fetch(`${API}/api/v1/product-center/products/${pid}`)
  const detail = detailResp.ok ? await detailResp.json() : null

  const sections = card?.sections ?? []
  const sourceFile = card?.sourceFile ?? null

  // 独立推导期望：关键字命中 + 节号前缀兜底，并记录两者是否一致（错位检测）
  const expectMap = {}
  for (const spec of [...SPEC, { key: 'c11', ...C11 }]) {
    const byKw = sections.find((s) => s.title.includes(spec.kw)) ?? null
    const byNo = sections.find((s) => secNo(s.title) === spec.no) ?? null
    const picked = MUTATE === 'prefix' ? byNo : byKw
    expectMap[spec.key] = {
      kwTitle: picked?.title ?? null,
      kwContent: picked?.content ?? null,
      noTitle: byNo?.title ?? null,
      kwRealTitle: byKw?.title ?? null,
      conflict: !!byKw && !!byNo && byKw.title !== byNo.title
    }
  }

  await page.goto(`${BASE}/product-center/${pid}`, { waitUntil: 'domcontentloaded' })
  await page
    .locator('[data-testid="pc-inherited-chapters"]')
    .waitFor({ state: 'attached', timeout: 20000 })
    .catch(() => {})

  const dom = await page.evaluate(() => {
    const txt = (sel, root = document) => root.querySelector(sel)?.textContent ?? null
    const t = (sel, root = document) =>
      root.querySelector(sel)?.textContent?.trim() ?? null

    const root = document.querySelector('[data-testid="pc-inherited-chapters"]')
    const out = { hasRoot: !!root, blocks: {}, immutable: null, compare: null }

    for (const key of ['c2', 'c3', 'c6', 'c8', 'c9', 'c10', 'c12']) {
      const el = document.querySelector(`[data-testid="pc-inherited-${key}"]`)
      out.blocks[key] = el
        ? {
            present: true,
            meta: t(`[data-testid="pc-inherited-${key}-meta"]`),
            content: txt(`[data-testid="pc-inherited-${key}-content"]`),
            absent: t(`[data-testid="pc-inherited-${key}-absent"]`),
            contract: t(`[data-testid="pc-inherited-${key}-contract"]`),
            contractEmpty: t(`[data-testid="pc-inherited-${key}-contract-empty"]`),
            boundaries: Array.from(
              document.querySelectorAll(`[data-testid="pc-inherited-${key}-boundary"]`)
            ).map((li) => li.textContent.replace(/\s+/g, ' ').trim()),
            inInheritedRoot: !!root && root.contains(el),
            // 「未被比较表替代」：不得位于任何 table 内，且必须落在承接区（而非八章比较表）
            insideTable: !!el.closest('table'),
            insideCompare: !!el.closest('[data-section-key="COMPARE"]'),
            tag: el.tagName
          }
        : { present: false }
    }

    const imm = document.querySelector('[data-testid="pc-immutable-version"]')
    out.immutable = imm
      ? {
          present: true,
          statement: t('[data-testid="pc-immutable-statement"]'),
          facts: t('[data-testid="pc-immutable-facts"]'),
          source: t('[data-testid="pc-immutable-source"]'),
          content: txt('[data-testid="pc-immutable-content"]'),
          absent: t('[data-testid="pc-immutable-absent"]'),
          inRightCol: !!document.querySelector('[data-testid="pc-col-right"]')?.contains(imm)
        }
      : { present: false }

    const cmp = document.querySelector('[data-section-key="COMPARE"]')
    out.compare = cmp
      ? {
          present: true,
          hasTable: !!cmp.querySelector('table'),
          inheritedInside: !!cmp.querySelector('[data-testid^="pc-inherited-"]')
        }
      : { present: false }

    out.bodyText = document.body.innerText
    return out
  })

  const rec = {
    productId: pid,
    sourceFile,
    sectionCount: sections.length,
    sectionTitles: sections.map((s) => s.title),
    expect: expectMap,
    violations: []
  }

  const push = (code, detail) => {
    rec.violations.push({ code, detail })
    v(pid, code, detail)
  }

  // ── 前置：承接区必须存在 ──
  if (!dom.hasRoot) push('NO_INHERITED_ROOT', '承接区未渲染')

  for (const spec of SPEC) {
    const got = dom.blocks[spec.key]
    const exp = expectMap[spec.key]
    if (!got.present) {
      push(`BLOCK_MISSING:${spec.key}`, '承接块未渲染')
      continue
    }
    // ① 独立区块：必须在承接区根内，且不被比较表替代
    if (!got.inInheritedRoot) push(`NOT_INDEPENDENT:${spec.key}`, '不在承接区根内')
    if (got.insideTable) push(`REPLACED_BY_TABLE:${spec.key}`, '位于比较表 <table> 内')
    if (got.insideCompare) push(`REPLACED_BY_COMPARE:${spec.key}`, '位于 COMPARE 章内')

    // ② 承接位置（指名引用）
    if (!/承接位置：/.test(got.meta ?? '')) push(`NO_LANDING:${spec.key}`, `meta=${got.meta}`)

    // ③ 相对来源 + 实际节号 + 有效状态
    if (!/来源：/.test(got.meta ?? '')) push(`NO_SOURCE:${spec.key}`, `meta=${got.meta}`)
    if (/来源：\s*\//.test(got.meta ?? '')) push(`ABS_SOURCE:${spec.key}`, '来源为绝对路径')
    if (!/有效状态：/.test(got.meta ?? '')) push(`NO_VALIDITY:${spec.key}`, `meta=${got.meta}`)

    // ④ 原文：与接口该节 content 一致（关键字命中节）
    if (exp.kwContent) {
      if (!got.content) {
        push(`NO_ORIGINAL_TEXT:${spec.key}`, `接口有该节(${exp.kwTitle})但页面无原文`)
      } else if (!norm(got.content).includes(head(exp.kwContent))) {
        push(`ORIGINAL_MISMATCH:${spec.key}`, `页面原文与 ${exp.kwTitle} 不一致`)
      }
      const no = secNo(exp.kwTitle)
      if (no !== null && !new RegExp(`第\\s*${no}\\s*节`).test(got.meta ?? '')) {
        push(`SECTION_NO_MISMATCH:${spec.key}`, `meta 未标注实际节号 §${no}（${exp.kwTitle}）`)
      }
    } else {
      // 接口无该节 ⇒ 必须具名缺失，不得空白
      if (!got.absent) push(`SILENT_ABSENT:${spec.key}`, '接口无该节但页面未具名标注缺失')
      if (got.content) push(`PHANTOM_CONTENT:${spec.key}`, '接口无该节但页面渲染了原文')
    }

    // ⑤ C10：产品级 salesBoundaries（合同字段）
    if (spec.key === 'c10') {
      const sb = detail?.salesBoundaries ?? []
      if (sb.length > 0) {
        if (!got.contract) push('C10_NO_CONTRACT', '有合同字段但未渲染产品级销售边界')
        if (!/salesBoundaries/.test(got.contract ?? '')) push('C10_NO_FIELDNAME', '未标注字段名')
        if (got.boundaries.length !== sb.length)
          push('C10_BOUNDARY_COUNT', `页面 ${got.boundaries.length} 条 ≠ 合同 ${sb.length} 条`)
        for (let i = 0; i < sb.length; i++) {
          const b = sb[i]
          const shown = got.boundaries[i] ?? ''
          if (!shown.includes(b.boundaryKind)) push('C10_KIND', `第${i + 1}条缺 boundaryKind`)
          if (!shown.includes(b.riskCategory)) push('C10_RISK', `第${i + 1}条缺 riskCategory`)
          if (b.mandatoryDisplay && !/强制展示/.test(shown))
            push('C10_MANDATORY', `第${i + 1}条 mandatoryDisplay=true 但未展示标记`)
          if (MUTATE === 'c10wrong') {
            if ((shown || '').includes('__QA_MUTANT__')) push('C10_TEXT_MUTANT', '变异串意外出现')
            else push('C10_TEXT', `变异复验：期望含 __QA_MUTANT__ 的文本`)
          } else if (!norm(shown).includes(head(b.text))) push('C10_TEXT', `第${i + 1}条文本不一致`)
        }
      } else {
        if (!got.contractEmpty) push('C10_EMPTY_NOT_NAMED', '合同字段为空但未具名标注')
        if (got.contract) push('C10_FAKE_CONTRACT', '合同字段为空却渲染了内容')
      }
    }
  }

  // ── C11：版本区语义（pc-immutable-version） ──
  const imm = dom.immutable
  const exp11 = expectMap.c11
  if (!imm?.present) {
    push('NO_IMMUTABLE_BLOCK', 'pc-immutable-version 不存在')
  } else {
    if (!imm.statement) push('C11_NO_STATEMENT', '缺语义陈述')
    if (!/生效日/.test(imm.facts ?? '')) push('C11_NO_FACTS', `缺版本事实字段：${imm.facts}`)
    if (exp11.kwContent) {
      if (!imm.source) push('C11_NO_SOURCE', '缺相对来源行')
      else {
        if (!imm.source.includes(exp11.kwTitle))
          push('C11_SOURCE_TITLE', `来源行未含实际节标题「${exp11.kwTitle}」`)
        if (!sourceFile || !imm.source.includes(sourceFile))
          push('C11_SOURCE_FILE', '来源行未含相对 sourceFile')
        if (/来源：\s*\//.test(imm.source)) push('C11_ABS_SOURCE', '来源为绝对路径')
      }
      if (!imm.content) push('C11_NO_ORIGINAL', '缺该节原文')
      else if (!norm(imm.content).includes(head(exp11.kwContent)))
        push('C11_ORIGINAL_MISMATCH', `版本区原文非「${exp11.kwTitle}」`)
    } else if (!imm.absent) {
      push('C11_SILENT_ABSENT', '接口无该节但未具名标注')
    }
    if (!imm.inRightCol) push('C11_NOT_IN_RIGHT_COL', '版本区不在右栏')
  }

  // ── 错位检测（独立）：关键字命中节号 ≠ 登记节号时必须按实际节号呈现 ──
  for (const spec of [...SPEC, { key: 'c11', ...C11 }]) {
    const e = expectMap[spec.key]
    if (e.conflict) notes.push({ productId: pid, key: spec.key, ...e })
  }
  // FIN 卡专项：C12=§11 且 C11=§12
  const finMisaligned = sections.some((s) => s.title.startsWith('11. EvidenceRef')) &&
    sections.some((s) => s.title.startsWith('12. 不可变版本语义'))
  rec.finMisaligned = finMisaligned
  if (finMisaligned) {
    const c12No = secNo(expectMap.c12.kwTitle)
    const c11No = secNo(expectMap.c11.kwTitle)
    if (c12No !== 11) push('FIN_C12_BIND', `C12 应绑 §11，实为 §${c12No}`)
    if (c11No !== 12) push('FIN_C11_BIND', `C11 应绑 §12，实为 §${c11No}`)
    if (!new RegExp(`第\\s*11\\s*节`).test(dom.blocks.c12.meta ?? ''))
      push('FIN_C12_META', `C12 meta 未标 §11：${dom.blocks.c12.meta}`)
    if (imm?.source && !imm.source.includes('12.'))
      push('FIN_C11_META', `C11 来源未标 §12：${imm.source}`)
  }

  // ── 比较表与承接区的关系（C6/C9 不得被比较表替代） ──
  if (dom.compare?.present && dom.compare.inheritedInside)
    push('C6C9_IN_COMPARE', '承接块被嵌入 COMPARE 章内')
  if (dom.compare?.hasTable) {
    const tableText = await page
      .locator('[data-section-key="COMPARE"] table')
      .first()
      .innerText()
      .catch(() => '')
    rec.compareTableTextLen = tableText.length
    if (tableText.includes('前置、互斥、替代与配套产品') && !dom.hasRoot)
      push('C6_ONLY_IN_TABLE', 'C6 仅出现在比较表')
  }

  // ── 诚实性红线 ──
  const body = dom.bodyText ?? ''
  if (/\/home\//.test(body)) push('ABS_PATH_LEAK', '页面泄露本机绝对路径')
  for (const bad of ['有证据支撑', '已生效', '已验证通过', 'PRODUCTION_READY=YES']) {
    if (body.includes(bad)) push('FORBIDDEN_CLAIM', `出现不当表述：${bad}`)
  }
  if (!/DEMO/.test(body)) push('NO_DEMO_TAG', '页面未标注 DEMO')

  perProduct.push(rec)
}

const totals = {
  products: perProduct.length,
  violations: violations.length,
  misalignedCards: perProduct.filter((p) => p.finMisaligned).map((p) => p.productId),
  conflictNotes: notes.length
}

const outFile = `${OUT}/probe-pci1.json`
writeFileSync(outFile, JSON.stringify({ totals, violations, notes, perProduct }, null, 2))

console.log(JSON.stringify({ totals, violations }, null, 2))

await browser.close()
process.exit(violations.length === 0 ? 0 : 1)
