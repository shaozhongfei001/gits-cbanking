/**
 * PC-i1 · 独立 QA 复验 · V-B2 判据规则引擎（live 探针与 pre-fix 回放共用）。
 *
 * 前提：product-knowledge cards 接口被**请求中断**（失败注入，不注入任何假数据）。
 * 判据：来源不可得时，页面**不得**对未读到的制品作事实断言（「未包含第 N 节」），
 * 亦**不得**渲染任何原文；且无关接口（product-center，含 C10 合同字段）不受连带影响。
 */
const norm = (s) => (s ?? '').replace(/\s+/g, ' ').trim()

export function judgeFault(dom, { aborted = 0, expectNoContent = true } = {}) {
  const f = []
  if (!(aborted > 0)) f.push('ABORT_NOT_APPLIED（判据前提不成立：未实际中断卡接口）')

  const metas = { c6: dom.c6meta, c12: dom.c12meta }
  for (const [k, meta] of Object.entries(metas)) {
    if (!meta) continue
    if (!/来源标识不可得/.test(norm(meta))) f.push(`META_NOT_HONEST:${k}`)
    if (!/节号不可判/.test(norm(meta))) f.push(`META_NO_NOT_DISCLAIMED:${k}（未声明节号不可判）`)
    if (/（第\s*\d+\s*节）/.test(norm(meta))) f.push(`META_CLAIMS_SECTION_NO:${k}（来源不可得却断言节号）`)
  }
  const heads = { c6: dom.c6head, c12: dom.c12head }
  for (const [k, head] of Object.entries(heads)) {
    const h = norm(head)
    if (!h) continue
    if (/（卡内第\s*\d+\s*节）/.test(h)) f.push(`HEAD_CLAIMS_SECTION_NO:${k}（来源不可得却标卡内节号）`)
    if (/\d+\s*\./.test(h)) f.push(`HEAD_USES_NUMERIC_NO:${k}（head=「${h}」）`)
  }

  const absents = { c6: dom.c6absent, c12: dom.c12absent, c11: dom.immAbsent }
  for (const [k, txt] of Object.entries(absents)) {
    const t = norm(txt)
    if (!t) continue
    if (/未包含第\s*\d+\s*节/.test(t)) f.push(`ABSENT_STATES_SECTION_NO:${k}`)
    if (/未包含「/.test(t) && !/无法判定/.test(t)) f.push(`ABSENT_ASSERTS_NOT_CONTAINED:${k}`)
    if (!/无法判定/.test(t)) f.push(`ABSENT_NOT_UNDETERMINED:${k}`)
  }
  if (expectNoContent) {
    if (dom.c12content) f.push('CONTENT_DESPITE_ABORT:c12')
    if (dom.immContent) f.push('CONTENT_DESPITE_ABORT:c11')
    if (dom.immSource) f.push('SOURCE_DESPITE_ABORT:c11')
  }
  if (!dom.c10contract) f.push('C10_CONTRACT_LOST（无关接口被连带影响）')
  return f
}
