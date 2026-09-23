/**
 * PC-i1 · 独立 QA 复验 · V-B1 判据**规则引擎**（被 live 探针与 pre-fix 回放脚本共用同一代码路径）
 *
 * 期望值来源：调用方必须**从接口事实**推导 `section`（该卡是否含该节）与 `expectedNo`（该节实际节号），
 * 不得照抄实现者断言。判据全部为「DOM 事实 vs 接口事实」的一致性比对。
 */
export const norm = (s) => (s ?? '').replace(/\s+/g, ' ').trim()
export const head20 = (s) => norm(s).replace(/\s/g, '').slice(0, 20)

/**
 * 单章判定。
 * @param ch {key,id,title} 章节（id = R2 登记章号）
 * @param section 接口事实：该卡 sections 中命中的该节（null ⇒ 该卡不含该节）
 * @param dom {head,meta,content,absent} 渲染事实
 * @param partial true ⇒ dom 仅含 head/meta（回放历史制品时），跳过 content/absent 判据
 * @returns 违规码数组
 */
export function judgeChapter({ ch, section, dom, partial = false }) {
  const regNo = Number(ch.id.slice(1))
  const expectedNo = section ? Number((/^(\d+)\./.exec(String(section.title)) ?? [])[1] ?? NaN) : null
  const expectedNoValid = expectedNo !== null && Number.isFinite(expectedNo)
  const headRaw = norm(dom?.head)
  const meta = norm(dom?.meta)
  const headNoSuffix = headRaw.replace(/（卡内第\s*\d+\s*节）/g, '')
  const headHasNumericNo = /\d+\s*\./.test(headNoSuffix)
  const headSaysN = /（卡内第\s*(\d+)\s*节）/.exec(headRaw)
  const metaSaysNo = [...meta.matchAll(/（第\s*(\d+)\s*节）/g)].map((m) => Number(m[1]))
  const v = []

  if (expectedNoValid) {
    if (!headRaw.includes(`卡内第 ${expectedNo} 节`))
      v.push(`HEAD_NO_MISSING:${ch.id}（期望「卡内第 ${expectedNo} 节」，实际 head=「${headRaw}」）`)
    if (headHasNumericNo) v.push(`HEAD_HAS_NUMERIC_NO:${ch.id}（head 残留「${norm(headNoSuffix).slice(0, 40)}」）`)
    if (headSaysN && Number(headSaysN[1]) !== expectedNo) v.push(`HEAD_NO_MISMATCH:${ch.id}`)
    if (!metaSaysNo.includes(expectedNo)) v.push(`META_NO_MISSING:${ch.id}（期望「第 ${expectedNo} 节」，实际 meta=「${meta.slice(0, 120)}」）`)
    if (meta.includes('本卡未含该节')) v.push(`META_SAYS_ABSENT_BUT_PRESENT:${ch.id}`)
    for (const n of metaSaysNo)
      if (n !== expectedNo) v.push(`META_NO_MISMATCH:${ch.id}（第 ${n} 节 ≠ 实际第 ${expectedNo} 节）`)
    if (!partial) {
      if (!dom?.content) v.push(`CONTENT_MISSING:${ch.id}`)
      else if (head20(dom.content) !== head20(section.content)) v.push(`CONTENT_MISMATCH:${ch.id}`)
      if (dom?.absent) v.push(`ABSENT_AND_CONTENT_BOTH:${ch.id}`)
    }
  } else {
    if (headSaysN) v.push(`HEAD_CLAIMS_SECTION_NO:${ch.id}（该卡无此节却标「卡内第 ${headSaysN[1]} 节」）`)
    if (headHasNumericNo) v.push(`HEAD_HAS_REGISTERED_NO:${ch.id}（head 残留「${norm(headNoSuffix).slice(0, 40)}」）`)
    if (metaSaysNo.length > 0) v.push(`META_CLAIMS_SECTION_NO:${ch.id}（第 ${metaSaysNo.join(',')} 节）`)
    if (!meta.includes(`本卡未含该节 · R2 章号 ${ch.id}`)) v.push(`META_ABSENT_NOT_NAMED:${ch.id}（实际 meta=「${meta.slice(0, 120)}」）`)
    if (!partial) {
      if (dom?.content) v.push(`CONTENT_DESPITE_ABSENT:${ch.id}`)
      if (!dom?.absent) v.push(`ABSENT_TEXT_MISSING:${ch.id}`)
      else if (/未包含第\s*\d+\s*节/.test(norm(dom.absent))) v.push(`ABSENT_USES_REGISTERED_NO:${ch.id}（${norm(dom.absent).slice(0, 60)}）`)
    }
    if (regNo && meta.includes(`第 ${regNo} 节`)) v.push(`META_REGISTERED_NO_AS_SECTION:${ch.id}`)
  }
  return v
}

/** 版本区（C11「不可变版本语义」）判定。 */
export function judgeImm({ immSection, dom, partial = false }) {
  const iv = []
  if (immSection) {
    const expectedNo = (/^(\d+)\./.exec(String(immSection.title)) ?? [])[1]
    if (!(norm(dom?.source) ?? '').includes(String(immSection.title)))
      iv.push(`IMM_SOURCE_NOT_ACTUAL_TITLE（期望含「${immSection.title}」，实际「${norm(dom?.source).slice(0, 80)}」）`)
    if (!new RegExp(`（第\\s*${expectedNo}\\s*节）|^${expectedNo}\\.`).test(norm(dom?.source)))
      iv.push(`IMM_SOURCE_NO_MISSING（期望第 ${expectedNo} 节）`)
    if (!partial) {
      if (!dom?.content) iv.push('IMM_CONTENT_MISSING')
      else if (head20(dom.content) !== head20(immSection.content)) iv.push('IMM_CONTENT_MISMATCH')
      if (dom?.absent) iv.push('IMM_ABSENT_DESPITE_PRESENT')
    }
  } else {
    if (!partial) {
      if (dom?.content) iv.push('IMM_CONTENT_DESPITE_NO_SECTION')
      if (!dom?.absent) iv.push('IMM_ABSENT_MISSING')
      else if (/未包含第\s*\d+\s*节/.test(norm(dom.absent))) iv.push('IMM_ABSENT_USES_SECTION_NO')
    }
  }
  return iv
}
